from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy import func, cast, Date
from datetime import datetime
import pytz

from models import (
    SessionLocal,
    ParkingLot,
    ParkingSpot,
    Reservation,
    User,
    SpotStatus,
)

from redis_cache import pull_cache, store_cache, reset_lot_cache

dubai_tz = pytz.timezone("Asia/Dubai")

admin_bp = Blueprint("admin_bp", __name__)



def require_admin():
    claims = get_jwt()
    if not claims or not claims.get("is_admin"):
        return None
    return claims



@admin_bp.route("/lots", methods=["GET"])
@jwt_required()
def list_lots():
    if not require_admin():
        return jsonify({"msg": "Admin access required"}), 403

    page = request.args.get("page", 1, type=int)
    search = request.args.get("search", "", type=str).strip()
    per_page = 10

    cache_key = f"admin:lots:{page}:{search.lower()}"
    cached = pull_cache(cache_key)
    if cached is not None:
        return jsonify(cached)

    session = SessionLocal()
    try:
        query = session.query(ParkingLot)

        if search:
            pattern = f"%{search}%"
            query = query.filter(func.lower(ParkingLot.prime_location_name).like(func.lower(pattern)))

        total_items = query.count()
        total_pages = (total_items + per_page - 1) // per_page

        lots = (
            query.order_by(ParkingLot.id.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        items = []
        for lot in lots:
            available_count = (
                session.query(ParkingSpot)
                .filter(
                    ParkingSpot.lot_id == lot.id,
                    ParkingSpot.status == SpotStatus.AVAILABLE,
                )
                .count()
            )
            items.append({
                "id": lot.id,
                "name": lot.prime_location_name,
                "location": lot.address,
                "price": lot.price,
                "maximum_number_of_spots": lot.maximum_number_of_spots,
                "available_spots": available_count,
            })

        payload = {
            "items": items,
            "total_items": total_items,
            "total_pages": total_pages,
            "page": page,
        }

        store_cache(cache_key, payload, ttl=60)
        return jsonify(payload)

    finally:
        session.close()



@admin_bp.route("/lots", methods=["POST"])
@jwt_required()
def create_lot():
    if not require_admin():
        return jsonify({"msg": "Admin access required"}), 403

    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    location = (data.get("location") or "").strip()
    price = data.get("price")
    capacity = data.get("capacity")
    pin_code = (data.get("pin_code") or "000000")

    if not name or not location or price is None or capacity is None:
        return jsonify({"msg": "Missing required fields"}), 400

    try:
        price_val = float(price)
        capacity_val = int(capacity)
    except:
        return jsonify({"msg": "Invalid price or capacity"}), 400

    session = SessionLocal()
    try:
        lot = ParkingLot(
            prime_location_name=name,
            price=price_val,
            address=location,
            maximum_number_of_spots=capacity_val,
            pin_code=pin_code,
        )

        session.add(lot)
        session.flush()

        for _ in range(capacity_val):
            session.add(ParkingSpot(lot_id=lot.id, status=SpotStatus.AVAILABLE))

        session.commit()
        reset_lot_cache()

        return jsonify({"msg": "Parking lot created", "id": lot.id}), 201

    except Exception as e:
        session.rollback()
        return jsonify({"msg": "Failed to create parking lot"}), 500

    finally:
        session.close()



@admin_bp.route("/lots/<int:lot_id>", methods=["DELETE"])
@jwt_required()
def delete_lot(lot_id):
    if not require_admin():
        return jsonify({"msg": "Admin access required"}), 403

    session = SessionLocal()
    try:
        lot = session.query(ParkingLot).get(lot_id)
        if not lot:
            return jsonify({"msg": "Parking lot not found"}), 404

        active_reservations = (
            session.query(Reservation)
            .filter(
                Reservation.spot_id.in_([s.id for s in lot.spots]),
                Reservation.leaving_timestamp == None,
            )
            .count()
        )

        if active_reservations > 0:
            return jsonify({"msg": "Cannot delete. Spots are occupied."}), 400

        for s in lot.spots:
            session.delete(s)

        session.delete(lot)
        session.commit()

        reset_lot_cache()
        return jsonify({"msg": "Lot deleted successfully"}), 200

    finally:
        session.close()



@admin_bp.route("/lots/<int:lot_id>", methods=["PUT"])
@jwt_required()
def update_lot(lot_id):
    if not require_admin():
        return jsonify({"msg": "Admin access required"}), 403

    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    location = (data.get("location") or "").strip()
    price = data.get("price")
    capacity = data.get("capacity")

    if not name or not location or price is None or capacity is None:
        return jsonify({"msg": "Missing required fields"}), 400

    try:
        price_val = float(price)
        capacity_val = int(capacity)
    except:
        return jsonify({"msg": "Invalid price or capacity"}), 400

    session = SessionLocal()
    try:
        lot = session.query(ParkingLot).get(lot_id)
        if not lot:
            return jsonify({"msg": "Parking lot not found"}), 404

        lot.prime_location_name = name
        lot.address = location
        lot.price = price_val

        current = session.query(ParkingSpot).filter(ParkingSpot.lot_id == lot.id).count()

        if capacity_val > current:
            for _ in range(capacity_val - current):
                session.add(ParkingSpot(lot_id=lot.id, status=SpotStatus.AVAILABLE))

        elif capacity_val < current:
            to_remove = (
                session.query(ParkingSpot)
                .filter(
                    ParkingSpot.lot_id == lot.id,
                    ParkingSpot.status == SpotStatus.AVAILABLE,
                )
                .order_by(ParkingSpot.id.desc())
                .limit(current - capacity_val)
                .all()
            )

            if len(to_remove) < current - capacity_val:
                return jsonify({"msg": "Cannot reduce below active spots"}), 400

            for s in to_remove:
                session.delete(s)

        lot.maximum_number_of_spots = capacity_val

        session.commit()
        reset_lot_cache()

        return jsonify({"msg": "Parking lot updated"}), 200

    finally:
        session.close()


@admin_bp.route("/users", methods=["GET"])
@jwt_required()
def list_users():
    if not require_admin():
        return jsonify({"msg": "Admin access required"}), 403

    session = SessionLocal()
    try:
        users = session.query(User).filter_by(is_admin=False).order_by(User.id.asc()).all()
        data = []

        for u in users:
            active_res = (
                session.query(Reservation)
                .filter(
                    Reservation.user_id == u.id,
                    Reservation.leaving_timestamp == None,
                )
                .first()
            )

            lot_name = None
            spot_id = None

            if active_res:
                spot = session.query(ParkingSpot).get(active_res.spot_id)
                if spot:
                    lot = session.query(ParkingLot).get(spot.lot_id)
                    lot_name = lot.prime_location_name
                    spot_id = spot.id

            data.append({
                "id": u.id,
                "name": u.name,
                "email": u.email,
                "spot_number": spot_id,
                "lot_name": lot_name,
            })

        return jsonify({"users": data}), 200

    finally:
        session.close()


@admin_bp.route("/lots/<int:lot_id>/spots", methods=["GET"])
@jwt_required()
def lot_spots(lot_id):
    session = SessionLocal()
    try:
        spots = session.query(ParkingSpot).filter(ParkingSpot.lot_id == lot_id).all()
        data = []
        for spot in spots:
            user = (
                session.query(User)
                .filter(User.spot_id == spot.id)
                .first()
            )

            active_res = (
                session.query(Reservation)
                .filter(
                    Reservation.spot_id == spot.id,
                    Reservation.leaving_timestamp.is_(None),
                )
                .order_by(Reservation.parking_timestamp.desc())
                .first()
            )

            if active_res and active_res.parking_timestamp:
                dt_utc = active_res.parking_timestamp
                dt_local = dt_utc.replace(tzinfo=pytz.utc).astimezone(dubai_tz)
                since_str = dt_local.strftime("%d %b %Y, %I:%M %p")
            else:
                since_str = None

            data.append({
                "id": spot.id,
                "spot_number": spot.id,
                "status": spot.status.name if hasattr(spot.status, "name") else str(spot.status),
                "user_id": user.id if user else None,
                "user_name": user.name if user else None,
                "user_email": user.email if user else None,
                "start_time": since_str,
            })
        return jsonify({"spots": data})
    finally:
        session.close()



@admin_bp.route("/reservations", methods=["GET"])
@jwt_required()
def list_reservations():
    if not require_admin():
        return jsonify({"msg": "Admin access required"}), 403

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    session = SessionLocal()
    try:
        query = session.query(Reservation).order_by(Reservation.id.desc())
        total_items = query.count()
        total_pages = (total_items + per_page - 1) // per_page

        reservations = query.offset((page - 1) * per_page).limit(per_page).all()

        def fmt(dt):
            if not dt:
                return None
            return dt.replace(tzinfo=pytz.utc).astimezone(dubai_tz).strftime("%d %b %Y, %I:%M %p")

        items = []
        for r in reservations:
            user = session.query(User).get(r.user_id)
            spot = session.query(ParkingSpot).get(r.spot_id)
            lot = session.query(ParkingLot).get(spot.lot_id) if spot else None

            if r.leaving_timestamp and r.parking_timestamp:
                delta = r.leaving_timestamp - r.parking_timestamp
                minutes = int(delta.total_seconds() // 60)
                duration = f"{minutes // 60}h {minutes % 60}m" if minutes else "0m"
            else:
                duration = None

            items.append({
                "id": r.id,
                "user_email": user.email if user else None,
                "user_name": user.name if user else None,
                "lot_name": lot.prime_location_name if lot else None,
                "spot_id": r.spot_id,
                "parking_timestamp": fmt(r.parking_timestamp),
                "leaving_timestamp": fmt(r.leaving_timestamp),
                "duration": duration,
                "parking_cost": r.parking_cost,
                "status": "Active" if r.leaving_timestamp is None else "Completed",
            })

        return jsonify({
            "items": items,
            "page": page,
            "per_page": per_page,
            "total_items": total_items,
            "total_pages": total_pages,
        })

    finally:
        session.close()



@admin_bp.route("/analytics/overview", methods=["GET"])
@jwt_required()
def analytics_overview():
    if not require_admin():
        return jsonify({"msg": "Admin access required"}), 403

    session = SessionLocal()
    try:
        total = session.query(ParkingSpot).count()
        occupied = session.query(ParkingSpot).filter_by(status=SpotStatus.OCCUPIED).count()
        available = total - occupied

        return jsonify({
            "total_spots": total,
            "occupied_spots": occupied,
            "available_spots": available,
        })

    finally:
        session.close()


@admin_bp.route("/analytics/revenue", methods=["GET"])
@jwt_required()
def analytics_revenue():
    if not require_admin():
        return jsonify({"msg": "Admin access required"}), 403

    session = SessionLocal()
    try:
        rows = (
            session.query(
                func.date(Reservation.leaving_timestamp),
                func.sum(Reservation.parking_cost).label("revenue"),
            )
            .filter(Reservation.leaving_timestamp.isnot(None))
            .group_by(func.date(Reservation.leaving_timestamp))
            .order_by(func.date(Reservation.leaving_timestamp))
            .all()
        )

        data = [
            {"date": str(d), "revenue": float(rv or 0)}
            for d, rv in rows
        ]

        return jsonify(data)

    finally:
        session.close()



@admin_bp.route("/analytics/parking-trends", methods=["GET"])
@jwt_required()
def analytics_parking_trends():
    if not require_admin():
        return jsonify({"msg": "Admin access required"}), 403

    session = SessionLocal()
    try:
        rows = (
            session.query(
                func.date(Reservation.parking_timestamp),
                func.count(Reservation.id),
            )
            .filter(Reservation.parking_timestamp.isnot(None))
            .group_by(func.date(Reservation.parking_timestamp))
            .order_by(func.date(Reservation.parking_timestamp))
            .all()
        )

        data = [
            {"date": str(d), "count": int(c)}
            for d, c in rows
        ]

        return jsonify(data)

    finally:
        session.close()
