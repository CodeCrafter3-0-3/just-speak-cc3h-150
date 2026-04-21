from flask import Blueprint, request, jsonify
from models import db, User, TherapistProfile
from flask_jwt_extended import create_access_token

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    role = data.get('role') # 'patient' or 'therapist'
    
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400
        
    new_user = User(email=email, full_name=full_name, role=role)
    new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()
    
    # If the user is a therapist, create a profile
    if role == 'therapist':
        license_number = data.get('license_number')
        hourly_rate = data.get('hourly_rate')
        
        if not license_number or not hourly_rate:
            # Revert creation if missing fields
            db.session.delete(new_user)
            db.session.commit()
            return jsonify({"message": "License number and hourly rate are required for therapists"}), 400
            
        profile = TherapistProfile(
            user_id=new_user.id,
            license_number=license_number,
            hourly_rate=hourly_rate,
            bio=data.get('bio', '')
        )
        db.session.add(profile)
        db.session.commit()
        
    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    
    if user and user.check_password(password):
        # Create token with user id and role
        access_token = create_access_token(
            identity=str(user.id), 
            additional_claims={'role': user.role}
        )
        return jsonify({
            "access_token": access_token, 
            "user": {
                "id": user.id, 
                "email": user.email, 
                "full_name": user.full_name, 
                "role": user.role
            }
        }), 200
        
    return jsonify({"message": "Invalid email or password"}), 401
