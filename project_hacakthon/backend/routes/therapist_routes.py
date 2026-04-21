from flask import Blueprint, jsonify
from models import User, TherapistProfile

therapist_bp = Blueprint('therapist_bp', __name__)

@therapist_bp.route('/', methods=['GET'])
def get_therapists():
    therapists = User.query.filter_by(role='therapist').all()
    result = []
    for therapist in therapists:
        profile = therapist.therapist_profile
        if profile:
            result.append({
                "id": therapist.id,
                "full_name": therapist.full_name,
                "license_number": profile.license_number,
                "hourly_rate": profile.hourly_rate,
                "bio": profile.bio,
                "is_verified": profile.is_verified
            })
    return jsonify(result), 200

@therapist_bp.route('/<int:id>', methods=['GET'])
def get_therapist(id):
    therapist = User.query.filter_by(id=id, role='therapist').first()
    if not therapist or not therapist.therapist_profile:
        return jsonify({"message": "Therapist not found"}), 404
        
    profile = therapist.therapist_profile
    return jsonify({
        "id": therapist.id,
        "full_name": therapist.full_name,
        "email": therapist.email,
        "license_number": profile.license_number,
        "hourly_rate": profile.hourly_rate,
        "bio": profile.bio,
        "is_verified": profile.is_verified
    }), 200
