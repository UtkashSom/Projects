from celery_worker import celery
from models import SessionLocal, Reservation, User, ParkingSpot, ParkingLot, SpotStatus
from datetime import datetime, timedelta
from sqlalchemy import func
import os
import io
import csv
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


@celery.task(name="tasks.check_reservations")
def check_reservations():
    session = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(days=30)
        expired = (
            session.query(Reservation)
            .filter(
                Reservation.leaving_timestamp.is_(None),
                Reservation.parking_timestamp <= cutoff,
            )
            .all()
        )
        for reservation in expired:
            spot = session.query(ParkingSpot).get(reservation.spot_id)
            if spot:
                spot.status = SpotStatus.AVAILABLE
            reservation.leaving_timestamp = cutoff
            session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error in check_reservations: {str(e)}")
    finally:
        session.close()


@celery.task(name="tasks.send_daily_reminders")
def send_daily_reminders():
    session = SessionLocal()
    try:
        now = datetime.utcnow()
        cutoff = now - timedelta(days=1)
        users = session.query(User).filter(User.is_admin.is_(False)).all()

        for u in users:

            active_res = (
                session.query(Reservation.id)
                .filter(
                    Reservation.user_id == u.id,
                    Reservation.leaving_timestamp.is_(None)
                )
                .first()
            )

            if active_res:
                continue

            recent = (
                session.query(Reservation.id)
                .filter(
                    Reservation.user_id == u.id,
                    Reservation.parking_timestamp >= cutoff,
                )
                .first()
            )

            if recent:
                continue

            subject = "Parking Reminder"
            msg = (
                f"Hi {u.name}, you haven't used the parking recently. "
                "If you plan to park today, reserve a spot in the app."
            )
            send_notification.delay(u.id, subject, msg)

    except Exception as e:
        print(f"Error in send_daily_reminders: {str(e)}")
    finally:
        session.close()


@celery.task(name="tasks.send_monthly_reports")
def send_monthly_reports():
    session = SessionLocal()
    try:
        now = datetime.utcnow()
        first_this_month = datetime(now.year, now.month, 1)
        if now.month == 1:
            first_prev_month = datetime(now.year - 1, 12, 1)
        else:
            first_prev_month = datetime(now.year, now.month - 1, 1)
        start = first_prev_month
        end = first_this_month
        start_display = start.strftime("%d %b %Y")
        end_display = (end - timedelta(days=1)).strftime("%d %b %Y")
        users = session.query(User).filter(User.is_admin.is_(False)).all()
        for user in users:
            total_trips, total_cost = (
                session.query(
                    func.count(Reservation.id),
                    func.coalesce(func.sum(Reservation.parking_cost), 0.0),
                )
                .filter(
                    Reservation.user_id == user.id,
                    Reservation.parking_timestamp >= start,
                    Reservation.parking_timestamp < end,
                )
                .one()
            )
            average_cost = float(total_cost) / total_trips if total_trips else 0.0
            most_used = (
                session.query(
                    ParkingLot.prime_location_name,
                    func.count(Reservation.id).label("c"),
                )
                .join(ParkingSpot, ParkingSpot.lot_id == ParkingLot.id)
                .join(Reservation, Reservation.spot_id == ParkingSpot.id)
                .filter(
                    Reservation.user_id == user.id,
                    Reservation.parking_timestamp >= start,
                    Reservation.parking_timestamp < end,
                )
                .group_by(ParkingLot.id)
                .order_by(func.count(Reservation.id).desc())
                .first()
            )
            fav_lot = most_used[0] if most_used else "No frequent lot"
            body = f"""
<html>
  <body style="margin:0;padding:0;background-color:#020617;font-family:Arial,Helvetica,sans-serif;">
    <table width="100%" cellpadding="0" cellspacing="0" align="center" style="padding:28px 0;">
      <tr>
        <td>
          <table width="640" cellpadding="0" cellspacing="0" align="center" style="background-color:#020617;border-radius:20px;overflow:hidden;border:1px solid #1f2937;box-shadow:0 14px 40px rgba(0,0,0,0.55);">
            <tr>
              <td style="padding:0;background-color:#020617;">
                <div style="height:10px;background-image:linear-gradient(90deg,#e5e7eb 20px,transparent 20px);background-size:40px 10px;"></div>
              </td>
            </tr>
            <tr>
              <td style="padding:18px 24px 16px 24px;background-color:#020617;color:#e5e7eb;">
                <table width="100%" cellpadding="0" cellspacing="0">
                  <tr>
                    <td style="vertical-align:middle;">
                      <div style="display:inline-block;width:26px;height:26px;border-radius:6px;background-color:#0ea5e9;color:#0b1120;font-size:16px;font-weight:bold;line-height:26px;text-align:center;margin-right:10px;">P</div>
                      <span style="font-size:20px;font-weight:bold;vertical-align:middle;">Monthly Parking Summary</span>
                      <div style="margin-top:4px;font-size:11px;letter-spacing:0.18em;text-transform:uppercase;color:#6b7280;">Vehicle Parking App</div>
                    </td>
                    <td align="right" style="vertical-align:middle;font-size:11px;color:#9ca3af;white-space:nowrap;">
                      <div style="font-weight:bold;color:#e5e7eb;margin-bottom:2px;">Period</div>
                      <div>{start_display} – {end_display}</div>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            <tr>
              <td style="padding:10px 24px 4px 24px;background-color:#020617;">
                <div style="font-size:14px;color:#e5e7eb;">Hello {user.name}</div>
                <div style="margin-top:4px;font-size:12px;color:#94a3b8;">Summary of your parking activity for last month.</div>
              </td>
            </tr>
            <tr>
              <td style="padding:16px 24px 10px 24px;background-color:#020617;">
                <table width="100%" cellpadding="0" cellspacing="0">
                  <tr>
                    <td width="50%" style="padding:8px 10px 8px 0;">
                      <table width="100%" cellpadding="0" cellspacing="0" style="border-radius:14px;background-color:#020617;border:1px solid #1f2937;">
                        <tr>
                          <td style="padding:14px 16px 10px 16px;">
                            <div style="height:10px;margin-bottom:10px;background-image:linear-gradient(90deg,#e5e7eb 8px,transparent 8px);background-size:16px 10px;border-radius:4px;"></div>
                            <div style="font-size:11px;text-transform:uppercase;letter-spacing:0.12em;color:#6b7280;">Total Visits</div>
                            <div style="font-size:34px;font-weight:bold;color:#f9fafb;margin-top:8px;">{int(total_trips)}</div>
                            <div style="margin-top:8px;font-size:10px;color:#6b7280;">Completed sessions</div>
                          </td>
                        </tr>
                      </table>
                    </td>
                    <td width="50%" style="padding:8px 0 8px 10px;">
                      <table width="100%" cellpadding="0" cellspacing="0" style="border-radius:14px;background-color:#020617;border:1px solid #1f2937;">
                        <tr>
                          <td style="padding:14px 16px 10px 16px;">
                            <div style="height:10px;margin-bottom:10px;background-color:#0b1120;border-radius:4px;border:1px dashed #e5e7eb;"></div>
                            <div style="font-size:11px;text-transform:uppercase;letter-spacing:0.12em;color:#6b7280;">Total Cost</div>
                            <div style="font-size:34px;font-weight:bold;color:#f9fafb;margin-top:8px;">{float(total_cost):.2f}</div>
                            <div style="margin-top:8px;font-size:10px;color:#6b7280;">Amount charged</div>
                          </td>
                        </tr>
                      </table>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            <tr>
              <td style="padding:4px 24px 18px 24px;background-color:#020617;">
                <table width="100%" cellpadding="0" cellspacing="0" style="border-radius:16px;background-color:#020617;border:1px solid #1f2937;">
                  <tr>
                    <td style="padding:14px 16px;">
                      <table width="100%" cellpadding="0" cellspacing="0">
                        <tr>
                          <td width="33%" style="vertical-align:top;">
                            <div style="font-size:11px;text-transform:uppercase;letter-spacing:0.12em;color:#6b7280;">Average / Visit</div>
                            <div style="margin-top:6px;font-size:18px;font-weight:bold;color:#e5e7eb;">{average_cost:.2f}</div>
                          </td>
                          <td width="34%" style="vertical-align:top;text-align:center;border-left:1px solid #1f2937;border-right:1px solid #1f2937;">
                            <div style="font-size:11px;text-transform:uppercase;letter-spacing:0.12em;color:#6b7280;">Most Used Lot</div>
                            <div style="margin-top:6px;font-size:13px;font-weight:bold;color:#e5e7eb;">{fav_lot}</div>
                          </td>
                          <td width="33%" style="vertical-align:top;text-align:right;">
                            <div style="display:inline-block;padding:4px 10px;border-radius:999px;border:1px solid #38bdf8;font-size:10px;color:#e0f2fe;background-color:#020617;">Monthly overview</div>
                          </td>
                        </tr>
                      </table>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            <tr>
              <td style="background-color:#020617;padding:14px 24px 18px 24px;border-top:1px solid #1f2937;">
                <div style="display:flex;justify-content:center;gap:8px;">
                  <div style="width:40px;height:12px;border-radius:4px;background-color:#0b1120;border:1px solid #1f2937;"></div>
                  <div style="width:40px;height:12px;border-radius:4px;background-color:#111827;border:1px solid #1f2937;"></div>
                  <div style="width:40px;height:12px;border-radius:4px;background-color:#0b1120;border:1px solid #1f2937;"></div>
                </div>
                <div style="margin-top:10px;font-size:11px;color:#6b7280;text-align:center;">Automated summary. Do not reply.</div>
              </td>
            </tr>
            <tr>
              <td style="padding:0;background-color:#020617;">
                <div style="height:10px;background-image:linear-gradient(90deg,#e5e7eb 20px,transparent 20px);background-size:40px 10px;"></div>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
            """
            send_email(user.email, "Parking Report - Last Month", body)
    except Exception as e:
        print(f"Error in send_monthly_reports: {str(e)}")
    finally:
        session.close()


def send_email(to, subject, body):
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("SMTP_FROM", user)
    use_tls = os.getenv("SMTP_USE_TLS", "1") == "1"
    if not host or not user or not password:
        print(f"Email disabled, missing SMTP config for {to}: {subject}")
        return
    msg = MIMEMultipart("alternative")
    msg["From"] = sender
    msg["To"] = to
    msg["Subject"] = subject
    plain_text = "This email contains an HTML report. Please enable HTML view to see the full report."
    part_text = MIMEText(plain_text, "plain")
    part_html = MIMEText(body, "html")
    msg.attach(part_text)
    msg.attach(part_html)
    try:
        server = smtplib.SMTP(host, port, timeout=10)
        if use_tls:
            server.starttls()
        server.login(user, password)
        server.sendmail(sender, [to], msg.as_string())
        server.quit()
        print(f"Email sent to {to}: {subject}")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")


def send_gchat_message(text):
    url = os.getenv("GCHAT_WEBHOOK_URL")
    if not url:
        print("GChat webhook not configured")
        return
    try:
        r = requests.post(url, json={"text": text}, timeout=10)
        print("GChat response:", r.status_code, r.text)
    except Exception as e:
        print(f"Failed to send GChat message: {str(e)}")


def send_email_with_attachment(to, subject, body_text, filename, csv_text):
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("SMTP_FROM", user)
    use_tls = os.getenv("SMTP_USE_TLS", "1") == "1"
    if not host or not user or not password:
        print(f"Email disabled, missing SMTP config for {to}: {subject}")
        return
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body_text, "plain"))
    part = MIMEBase("text", "csv")
    part.set_payload(csv_text.encode("utf-8"))
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
    msg.attach(part)
    try:
        server = smtplib.SMTP(host, port, timeout=10)
        if use_tls:
            server.starttls()
        server.login(user, password)
        server.sendmail(sender, [to], msg.as_string())
        server.quit()
        print(f"Email with CSV sent to {to}: {subject}")
    except Exception as e:
        print(f"Failed to send email with attachment: {str(e)}")


def build_user_history_csv(user_id):
    session = SessionLocal()
    try:
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            [
                "reservation_id",
                "user_id",
                "user_email",
                "lot_name",
                "spot_id",
                "parking_timestamp",
                "leaving_timestamp",
                "parking_cost",
            ]
        )
        reservations = (
            session.query(Reservation)
            .filter(Reservation.user_id == user_id)
            .order_by(Reservation.parking_timestamp.desc())
            .all()
        )
        for r in reservations:
            user = r.user
            spot = r.spot
            lot = spot.lot if spot else None
            writer.writerow(
                [
                    r.id,
                    r.user_id,
                    user.email if user else "",
                    lot.prime_location_name if lot else "",
                    spot.id if spot else "",
                    r.parking_timestamp.isoformat() if r.parking_timestamp else "",
                    r.leaving_timestamp.isoformat() if r.leaving_timestamp else "",
                    r.parking_cost if r.parking_cost is not None else "",
                ]
            )
        return buffer.getvalue()
    except Exception as e:
        print(f"Error in build_user_history_csv: {str(e)}")
        return ""
    finally:
        session.close()


@celery.task(name="tasks.export_user_history_and_email")
def export_user_history_and_email(user_id):
    session = SessionLocal()
    try:
        user = session.query(User).get(user_id)
        if not user:
            return
        csv_data = build_user_history_csv(user_id)
        if not csv_data:
            return
        filename = f"parking_history_user_{user_id}.csv"
        subject = "Your Parking History Export"
        body_text = "Your parking history export is attached as a CSV file."
        send_email_with_attachment(user.email, subject, body_text, filename, csv_data)
    except Exception as e:
        print(f"Error in export_user_history_and_email: {str(e)}")
    finally:
        session.close()


@celery.task(name="tasks.send_notification")
def send_notification(user_id, subject, message):
    session = SessionLocal()
    try:
        user = session.query(User).get(user_id)
        if not user:
            return
        text = f"{subject}\nTo: {user.email}\n{message}"
        print("About to send GChat:", text)
        send_gchat_message(text)
    except Exception as e:
        print(f"Error in send_notification: {str(e)}")
    finally:
        session.close()


@celery.task(name="tasks.export_user_history_csv")
def export_user_history_csv(user_id):
    return build_user_history_csv(user_id)


@celery.task(name="tasks.export_all_reservations_csv")
def export_all_reservations_csv():
    session = SessionLocal()
    try:
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            [
                "reservation_id",
                "user_id",
                "user_email",
                "lot_name",
                "spot_id",
                "parking_timestamp",
                "leaving_timestamp",
                "parking_cost",
            ]
        )
        reservations = (
            session.query(Reservation)
            .order_by(Reservation.parking_timestamp.desc())
            .all()
        )
        for r in reservations:
            user = r.user
            spot = r.spot
            lot = spot.lot if spot else None
            writer.writerow(
                [
                    r.id,
                    r.user_id,
                    user.email if user else "",
                    lot.prime_location_name if lot else "",
                    spot.id if spot else "",
                    r.parking_timestamp.isoformat() if r.parking_timestamp else "",
                    r.leaving_timestamp.isoformat() if r.leaving_timestamp else "",
                    r.parking_cost if r.parking_cost is not None else "",
                ]
            )
        return buffer.getvalue()
    except Exception as e:
        print(f"Error in export_all_reservations_csv: {str(e)}")
        return ""
    finally:
        session.close()
