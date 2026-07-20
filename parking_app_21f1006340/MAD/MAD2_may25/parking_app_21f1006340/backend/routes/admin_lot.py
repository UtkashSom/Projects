from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
import logging
from models.base import SessionLocal
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot, SpotStatus
from models.user import User
from models.reservation import Reservation
from sqlalchemy.orm import joinedload
from sqlalchemy import and_

logger = logging.getLogger(__name__)

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user = get_jwt_identity()
        if not current_user or current_user.get('role') != 'admin':
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)
    return wrapper

admin_lot_bp = Blueprint('admin_lot', __name__)

@admin_lot_bp.route('/lots', methods=['POST'])
def create_lot():
    session = SessionLocal()
    try:
        data = request.json
        lot = ParkingLot(
            name=data['name'],
            price=data['price'],
            capacity=data['capacity']
        )
        session.add(lot)
        session.commit()

        for i in range(1, lot.maximum_number_of_spots + 1):
            spot = ParkingSpot(lot_id=lot.id, number=i, status=SpotStatus.AVAILABLE)
            session.add(spot)
        session.commit()

        return jsonify({'message': 'Lot and spots created'})
    except Exception as e:
        session.rollback()
        return jsonify({'error': 'Failed to create lot', 'details': str(e)}), 500
    finally:
        session.close()

@admin_lot_bp.route('/lots/<int:lot_id>', methods=['PUT'])
def update_lot(lot_id):
    session = SessionLocal()
    try:
        data = request.json
        lot = session.query(ParkingLot).options(joinedload(ParkingLot.spots)).filter_by(id=lot_id).first()
        if not lot:
            return jsonify({'error': 'Lot not found'}), 404

        lot.price = data['price']

        new_capacity = data['capacity']
        if new_capacity != lot.maximum_number_of_spots:
            current_spots = lot.spots
            current_spot_count = len(current_spots)

            if new_capacity > current_spot_count:
                for i in range(current_spot_count + 1, new_capacity + 1):
                    new_spot = ParkingSpot(lot_id=lot.id, number=i, status=SpotStatus.AVAILABLE)
                    session.add(new_spot)
            elif new_capacity < current_spot_count:
                spots_to_remove = current_spot_count - new_capacity
                free_spots = [spot for spot in current_spots if spot.status == SpotStatus.AVAILABLE]

                if len(free_spots) < spots_to_remove:
                    return jsonify({"error": "Cannot reduce capacity below occupied or reserved spots"}), 400

                free_spots_sorted = sorted(free_spots, key=lambda x: x.number, reverse=True)
                for spot in free_spots_sorted[:spots_to_remove]:
                    session.delete(spot)

            lot.maximum_number_of_spots = new_capacity

        session.commit()
        return jsonify({'message': 'Lot updated'})
    except Exception as e:
        session.rollback()
        return jsonify({'error': 'Failed to update lot', 'details': str(e)}), 500
    finally:
        session.close()

@admin_lot_bp.route('/lots/<int:lot_id>', methods=['DELETE'])
def delete_lot(lot_id):
    session = SessionLocal()
    try:
        lot = session.query(ParkingLot).filter_by(id=lot_id).first()
        if not lot:
            return jsonify({'error': 'Lot not found'}), 404
        session.query(ParkingSpot).filter_by(lot_id=lot_id).delete()
        session.delete(lot)
        session.commit()
        return jsonify({'message': 'Lot and spots deleted'})
    except Exception as e:
        session.rollback()
        return jsonify({'error': 'Failed to delete lot', 'details': str(e)}), 500
    finally:
        session.close()

@admin_lot_bp.route('/lots', methods=['GET'])
def get_lots():
    session = SessionLocal()
    try:
        lots = session.query(ParkingLot).all()
        result = []
        for lot in lots:
            total_spots = session.query(ParkingSpot).filter_by(lot_id=lot.id).count()
            available_spots = session.query(ParkingSpot).filter_by(lot_id=lot.id, status=SpotStatus.AVAILABLE).count()
            result.append({
                'id': lot.id,
                'name': lot.prime_location_name,
                'price': lot.price,
                'capacity': lot.maximum_number_of_spots
            })
        return jsonify(result)
    finally:
        session.close()

@admin_lot_bp.route('/lots/<int:lot_id>/spots', methods=['GET'])
def get_spots(lot_id):
    session = SessionLocal()
    try:
        spots = session.query(ParkingSpot).filter_by(lot_id=lot_id).all()
        return jsonify([{'id': s.id, 'number': s.number, 'status': s.status.value} for s in spots])
    finally:
        session.close()

@admin_lot_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    session = SessionLocal()
    try:
        users = session.query(User).options(joinedload(User.reservations)).all()
        result = []
        for user in users:
            active_res = session.query(Reservation).filter(
                and_(
                    Reservation.user_id == user.id,
                    Reservation.leaving_timestamp == None
                )
            ).first()
            
            user_data = {
                'id': user.id,
                'email': user.email,
                'spot_number': None,
                'lot_name': None
            }
            
            if active_res and hasattr(active_res, 'spot') and active_res.spot:
                user_data['spot_number'] = active_res.spot.id
                if hasattr(active_res.spot, 'lot') and active_res.spot.lot:
                    user_data['lot_name'] = active_res.spot.lot.name
            
            result.append(user_data)
            
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in get_users: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        session.close()
