from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import SessionLocal, ParkingLot, ParkingSpot, Reservation, User, SpotStatus
from datetime import datetime
import pytz
from sqlalchemy import func
from redis_cache import pull_cache, store_cache, reset_lot_cache
from tasks import export_user_history_and_email

dubai_tz = pytz.timezone("Asia/Dubai")

user_parking_bp = Blueprint("user_parking", __name__)


@user_parking_bp.route("/lots", methods=["GET"])
@jwt_required()
def get_available_lots():
    claims = get_jwt()
    if claims.get("is_admin"):
        return jsonify({"msg": "Users only"}), 403

    cached = pull_cache("user:available_lots")
    if cached is not None:
        return jsonify({"lots": cached})

    session = SessionLocal()
    try:
        lots = session.query(ParkingLot).all()
        result = []
        for lot in lots:
            available_spots = (
                session.query(ParkingSpot)
                .filter(
                    ParkingSpot.lot_id == lot.id,
                    ParkingSpot.status == SpotStatus.AVAILABLE,
                )
                .count()
            )
            result.append(
                {
                    "id": lot.id,
                    "name": lot.prime_location_name,
                    "location": lot.address,
                    "price": lot.price,
                    "available_spots": available_spots,
                    "capacity": lot.maximum_number_of_spots,
                }
            )
    finally:
        session.close()

    store_cache("user:available_lots", result, ttl=60)
    return jsonify({"lots": result})


@user_parking_bp.route("/reserve", methods=["POST"])
@jwt_required()
def reserve_spot():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    lot_id = data.get("lot_id")

    session = SessionLocal()
    try:
        user = session.query(User).get(user_id)
        if user.spot_id:
            return jsonify({"msg": "You already have an active reservation."}), 400

        spot = (
            session.query(ParkingSpot)
            .filter(
                ParkingSpot.lot_id == lot_id,
                ParkingSpot.status == SpotStatus.AVAILABLE,
            )
            .order_by(ParkingSpot.id.asc())
            .first()
        )
        if not spot:
            return jsonify({"msg": "No available spots in this lot."}), 400

        reservation = Reservation(
            user_id=user_id,
            spot_id=spot.id,
            parking_timestamp=datetime.utcnow(),
            leaving_timestamp=None,
        )

        user.spot_id = spot.id
        spot.status = SpotStatus.OCCUPIED

        session.add(reservation)
        session.commit()

        reset_lot_cache()

        return jsonify(
            {"msg": "Spot reserved successfully.", "spot_id": spot.id, "lot_id": lot_id}
        ), 200
    finally:
        session.close()


@user_parking_bp.route("/release", methods=["POST"])
@jwt_required()
def release_spot():
    user_id = int(get_jwt_identity())

    session = SessionLocal()
    try:
        user = session.query(User).get(user_id)
        if not user.spot_id:
            return jsonify({"msg": "You do not have a spot to release."}), 400

        spot_id = user.spot_id
        reservation = (
            session.query(Reservation)
            .filter(
                Reservation.user_id == user_id,
                Reservation.spot_id == spot_id,
                Reservation.leaving_timestamp == None,
            )
            .first()
        )
        if not reservation:
            return jsonify({"msg": "Active reservation not found."}), 400

        now = datetime.utcnow()
        reservation.leaving_timestamp = now

        duration_hours = (
            now - reservation.parking_timestamp
        ).total_seconds() / 3600.0

        lot = session.query(ParkingLot).get(
            session.query(ParkingSpot).get(spot_id).lot_id
        )
        reservation.parking_cost = round(duration_hours * lot.price, 2)

        spot = session.query(ParkingSpot).get(spot_id)
        spot.status = SpotStatus.AVAILABLE
        user.spot_id = None

        session.commit()
        reset_lot_cache()

        return jsonify({"msg": "Spot released successfully."}), 200
    finally:
        session.close()


@user_parking_bp.route("/history", methods=["GET"])
@jwt_required()
def parking_history():
    user_id = int(get_jwt_identity())

    def fmt(dt):
        if not dt:
            return None
        dt_local = dt.replace(tzinfo=pytz.utc).astimezone(dubai_tz)
        return dt_local.strftime("%d %b %Y, %I:%M %p")

    session = SessionLocal()
    try:
        reservations = (
            session.query(Reservation)
            .filter(Reservation.user_id == user_id)
            .order_by(Reservation.id.desc())
            .all()
        )

        output = []
        for r in reservations:
            spot = session.query(ParkingSpot).get(r.spot_id)
            lot = session.query(ParkingLot).get(spot.lot_id) if spot else None
            output.append(
                {
                    "spot_id": r.spot_id,
                    "lot_id": lot.id if lot else None,
                    "lot_name": lot.prime_location_name if lot else None,
                    "parking_timestamp": fmt(r.parking_timestamp),
                    "leaving_timestamp": fmt(r.leaving_timestamp),
                    "parking_cost": r.parking_cost,
                }
            )

        return jsonify({"history": output})
    finally:
        session.close()


@user_parking_bp.route("/analytics/history", methods=["GET"])
@jwt_required()
def user_parking_history():
    user_id = int(get_jwt_identity())

    session = SessionLocal()
    try:
        reservations = (
            session.query(Reservation)
            .filter(
                Reservation.user_id == user_id,
                Reservation.parking_timestamp.isnot(None),
            )
            .all()
        )

        counts = {}
        for r in reservations:
            dt = r.parking_timestamp
            if not dt:
                continue
            local_dt = dt.replace(tzinfo=pytz.utc).astimezone(dubai_tz)
            key = local_dt.date().isoformat()
            counts[key] = counts.get(key, 0) + 1

        data = [
            {"date": d, "count": counts[d]}
            for d in sorted(counts.keys())
        ]

        return jsonify(data)
    finally:
        session.close()



@user_parking_bp.route("/export-history", methods=["POST"])
@jwt_required()
def export_history():
    uid = int(get_jwt_identity())
    export_user_history_and_email.delay(uid)
    return jsonify({"message": "Export started. You will receive an email when it is ready."}), 202
