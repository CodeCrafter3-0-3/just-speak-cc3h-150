from flask import Blueprint, request, jsonify
from models import db, Appointment, Payment, User
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime

appointment_bp = Blueprint('appointment_bp', __name__)

@appointment_bp.route('/book', methods=['POST'])
@jwt_required()
def book_appointment():
    current_user_id = get_jwt_identity()
    claims = get_jwt()
    if claims.get('role') != 'patient':
        return jsonify({"message": "Only patients can book appointments"}), 403
        
    data = request.get_json()
    therapist_id = data.get('therapist_id')
    start_time_str = data.get('start_time')
    end_time_str = data.get('end_time')
    
    try:
        start_time = datetime.fromisoformat(start_time_str)
        end_time = datetime.fromisoformat(end_time_str)
    except ValueError:
        return jsonify({"message": "Invalid date format. Use ISO format."}), 400
        
    # Verify therapist exists
    therapist = User.query.filter_by(id=therapist_id, role='therapist').first()
    if not therapist or not therapist.therapist_profile:
        return jsonify({"message": "Therapist not found"}), 404
        
    # Calculate price based on duration
    duration_hours = (end_time - start_time).total_seconds() / 3600
    total_price = duration_hours * therapist.therapist_profile.hourly_rate
    
    appointment = Appointment(
        patient_id=current_user_id,
        therapist_id=therapist_id,
        start_time=start_time,
        end_time=end_time,
        total_price=total_price,
        status='pending'
    )
    
    db.session.add(appointment)
    db.session.commit()
    
    # Create initial payment record
    payment = Payment(
        appointment_id=appointment.id,
        amount=total_price,
        status='pending'
    )
    db.session.add(payment)
    db.session.commit()
    
    return jsonify({
        "message": "Appointment booked successfully",
        "appointment_id": appointment.id,
        "total_price": total_price
    }), 201

@appointment_bp.route('/', methods=['GET'])
@jwt_required()
def get_appointments():
    user_id = get_jwt_identity()
    claims = get_jwt()
    role = claims.get('role')
    
    if role == 'patient':
        appointments = Appointment.query.filter_by(patient_id=user_id).all()
    else:  # therapist
        appointments = Appointment.query.filter_by(therapist_id=user_id).all()
        
    result = []
    for appt in appointments:
        therapist = User.query.get(appt.therapist_id)
        patient   = User.query.get(appt.patient_id)
        result.append({
            "id": appt.id,
            "patient_id": appt.patient_id,
            "patient_name": patient.full_name if patient else "Unknown",
            "therapist_id": appt.therapist_id,
            "therapist_name": therapist.full_name if therapist else "Unknown",
            "start_time": appt.start_time.isoformat(),
            "end_time": appt.end_time.isoformat(),
            "status": appt.status,
            "total_price": appt.total_price
        })
        
    return jsonify(result), 200
