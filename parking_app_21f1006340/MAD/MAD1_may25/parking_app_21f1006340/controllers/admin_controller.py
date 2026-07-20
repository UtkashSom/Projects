from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from sqlalchemy.orm import sessionmaker
from models.base import SessionLocal
from models.base import engine
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot, SpotStatus
from models.user import User
from models.reservation import Reservation
from sqlalchemy.orm import joinedload

Session = sessionmaker(bind=engine)

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/dashboard')
def dashboard():
    if session.get('user_type') != 'admin':
        return redirect(url_for('auth.login'))

    db_session = Session()
    parking_lots = db_session.query(ParkingLot).all()
    db_session.close()

    return render_template('admin_dashboard.html', admin=session.get('username'), lots=parking_lots)


@admin_bp.route('/admin/create-lot', methods=['GET', 'POST'])
def create_lot():
    if session.get('user_type') != 'admin':
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        location_name = request.form['prime_location_name']
        lot_price = float(request.form['price'])
        lot_address = request.form['address']
        lot_pin_code = request.form['pin_code']
        max_spot_count = int(request.form['maximum_number_of_spots'])

        db_session = Session()
        new_parking_lot = ParkingLot(
            prime_location_name=location_name,
            price=lot_price,
            address=lot_address,
            pin_code=lot_pin_code,
            maximum_number_of_spots=max_spot_count
        )
        db_session.add(new_parking_lot)
        db_session.commit()

        for _ in range(max_spot_count):
            spot = ParkingSpot(lot_id=new_parking_lot.id, status=SpotStatus.AVAILABLE)
            db_session.add(spot)

        db_session.commit()
        db_session.close()

        flash("Parking lot successfully created with spots generated!", "success")
        return redirect(url_for('admin.dashboard'))

    return render_template('create_lot.html')


@admin_bp.route('/admin/view-lots')
def view_lots():
    if session.get('user_type') != 'admin':
        return redirect(url_for('auth.login'))

    db_session = Session()
    parking_lots = db_session.query(ParkingLot).options(joinedload(ParkingLot.spots)).all()
    lots_summary = []

    for lot in parking_lots:
        for spot in lot.spots:
            spot.status = spot.status.name 

        total = len(lot.spots)
        available = sum(1 for spot in lot.spots if spot.status == 'AVAILABLE')
        occupied = total - available

        lots_summary.append({
            'lot': lot,
            'total_spots': total,
            'available_spots': available,
            'occupied_spots': occupied
        })

    db_session.close()
    return render_template('view_lots.html', lots_data=lots_summary)


@admin_bp.route('/admin/edit-lot/<int:lot_id>', methods=['GET', 'POST'])
def edit_lot(lot_id):
    if session.get('user_type') != 'admin':
        return redirect(url_for('auth.login'))

    db_session = Session()
    lot = db_session.query(ParkingLot).get(lot_id)
    if not lot:
        flash("Parking lot could not be found.", "error")
        db_session.close()
        return redirect(url_for('admin.view_lots'))

    if request.method == 'POST':
        lot.prime_location_name = request.form['prime_location_name']
        lot.address = request.form['address']
        lot.pin_code = request.form['pin_code']
        lot.price = float(request.form['price'])

        db_session.commit()
        db_session.close()

        flash("Parking lot details updated successfully.", "success")
        return redirect(url_for('admin.dashboard'))

    db_session.close()
    return render_template('edit_lot.html', lot=lot)


@admin_bp.route('/admin/delete-lot/<int:lot_id>', methods=['POST', 'GET'])
def delete_lot(lot_id):
    if session.get('user_type') != 'admin':
        return redirect(url_for('auth.login'))

    db_session = Session()
    lot = db_session.query(ParkingLot).get(lot_id)

    if not lot:
        flash("Unable to find parking lot.", "error")
        db_session.close()
        return redirect(url_for('admin.dashboard'))

    db_session.delete(lot)
    db_session.commit()
    db_session.close()

    flash("Parking lot deleted successfully.", "success")
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/admin/view-spots/<int:lot_id>')
def view_spots(lot_id):
    if session.get('user_type') != 'admin':
        return redirect(url_for('auth.login'))

    db_session = Session()
    lot = db_session.query(ParkingLot).get(lot_id)
    if not lot:
        flash("Parking lot not found.", "error")
        db_session.close()
        return redirect(url_for('admin.view_lots'))

    spots = db_session.query(ParkingSpot).filter_by(lot_id=lot_id).all()

    for spot in spots:
        spot.status = spot.status.name

    db_session.close()

    return render_template('view_spots.html', lot=lot, spots=spots)

@admin_bp.route('/admin/parking_history')
def view_all_parking_history():
    db = SessionLocal()
    reservations = db.query(Reservation).options(
        joinedload(Reservation.spot).joinedload(ParkingSpot.lot),
        joinedload(Reservation.user)
    ).filter(
        Reservation.leaving_timestamp.isnot(None)
    ).order_by(
        Reservation.parking_timestamp.desc()
    ).all()
    db.close()

    return render_template('admin_parking_history.html', history=reservations)


@admin_bp.route('/admin/view-users')
def view_users():
    if session.get('user_type') != 'admin':
        return redirect(url_for('auth.login'))

    db_session = Session()
    users = db_session.query(User).all()

    users_with_spots = []
    for user in users:
        assigned_spot = db_session.query(ParkingSpot).get(user.spot_id) if user.spot_id else None
        if assigned_spot and assigned_spot.status:
            assigned_spot.status = assigned_spot.status.name 
        users_with_spots.append({'user': user, 'spot': assigned_spot})

    db_session.close()
    return render_template('view_users.html', user_spot_data=users_with_spots)