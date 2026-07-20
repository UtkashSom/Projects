from flask import Blueprint, render_template, redirect, session, request, url_for, flash
from datetime import datetime
from models.base import SessionLocal
from models.user import User
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot, SpotStatus
from models.reservation import Reservation
from sqlalchemy.orm import joinedload

user_bp = Blueprint('user', __name__)

@user_bp.route('/user/dashboard')
def user_dashboard():
    if session.get('user_type') != 'user':
        return redirect(url_for('auth.login'))

    db = SessionLocal()
    user_id = session.get('user_id')
    user = db.query(User).get(user_id)
    lots = db.query(ParkingLot).all()

    current_reservation = db.query(Reservation).options(
        joinedload(Reservation.spot).joinedload(ParkingSpot.lot)
    ).filter(
        Reservation.user_id == user_id,
        Reservation.leaving_timestamp == None
    ).first()

    history = db.query(Reservation).options(
        joinedload(Reservation.spot).joinedload(ParkingSpot.lot)
    ).filter(
        Reservation.user_id == user_id,
        Reservation.leaving_timestamp != None
    ).order_by(Reservation.parking_timestamp.desc()).all()

    db.close()

    return render_template('user_dashboard.html', user=user, lots=lots, reservation=current_reservation, history=history)

@user_bp.route('/user/reserve/<int:lot_id>', methods=['POST'])
def reserve_spot(lot_id):
    if session.get('user_type') != 'user':
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')
    db = SessionLocal()

    active = db.query(Reservation).filter_by(
    user_id=user_id,
    leaving_timestamp=None
    ).first()

    if active:
        db.close()
        flash('You already have an active reservation. Please release it before booking another.', 'error')
        return redirect(url_for('user.user_dashboard'))

    spot = db.query(ParkingSpot).filter_by(lot_id=lot_id, status=SpotStatus.AVAILABLE).first()

    if not spot:
        db.close()
        flash('No available spots in this lot.', 'error')
        return redirect(url_for('user.user_dashboard'))

    spot.status = SpotStatus.OCCUPIED
    db.add(spot)

    reservation = Reservation(
        user_id=user_id,
        spot_id=spot.id,
        parking_timestamp=datetime.utcnow(),
        leaving_timestamp=None,
        parking_cost=0.0
    )
    db.add(reservation)

    user = db.query(User).get(user_id)
    user.spot_id = spot.id
    db.add(user)

    db.commit()
    flash(f'Spot {spot.id} reserved successfully.', 'success')
    db.close()

    return redirect(url_for('user.user_dashboard'))


@user_bp.route('/user/release', methods=['POST'])
def release_spot():
    if session.get('user_type') != 'user':
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')
    db = SessionLocal()

    reservation = db.query(Reservation).filter_by(
        user_id=user_id,
        leaving_timestamp=None
    ).first()

    if not reservation:
        db.close()
        flash('No active reservation found.', 'error')
        return redirect(url_for('user.user_dashboard'))

    reservation.leaving_timestamp = datetime.utcnow()
    duration_seconds = (reservation.leaving_timestamp - reservation.parking_timestamp).total_seconds()
    duration_hours = duration_seconds / 3600
    price_per_hour = reservation.spot.lot.price
    reservation.parking_cost = round(duration_hours * price_per_hour, 2)

    spot = db.query(ParkingSpot).get(reservation.spot_id)
    spot.status = SpotStatus.AVAILABLE

    user = db.query(User).get(user_id)
    user.spot_id = None
    db.add(user)
    db.add(reservation)
    db.commit()
    flash('Spot released successfully.', 'success')
    db.close()

    return redirect(url_for('user.user_dashboard'))


