from flask import Flask
from models import db
from flask_jwt_extended import JWTManager
from routes.auth_routes import auth_bp
from routes.therapist_routes import therapist_bp
from routes.appointment_routes import appointment_bp
from signaling import socketio
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_cors import CORS
from models import User, TherapistProfile, Appointment, Payment
import os

def create_app():
    # Use the absolute path to your frontend folder
    frontend_folder = r"c:\Users\Dell\OneDrive\Documents\frontend"
    app = Flask(__name__, static_folder=frontend_folder, static_url_path='/')
    
    # Configure the SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///therapy.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configure JWT
    app.config['JWT_SECRET_KEY'] = 'super-secret-key-change-in-production' # Change in production
    
    # Initialize extensions
    db.init_app(app)
    JWTManager(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Initialize Admin Dashboard
    admin = Admin(app, name='Platform Admin', url='/admin')
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(TherapistProfile, db.session))
    admin.add_view(ModelView(Appointment, db.session))
    admin.add_view(ModelView(Payment, db.session))
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(therapist_bp, url_prefix='/api/therapists')
    app.register_blueprint(appointment_bp, url_prefix='/api/appointments')
    
    # Serve the frontend files
    @app.route('/')
    def serve_index():
        return app.send_static_file('signin2.html')

    @app.route('/<path:path>')
    def serve_static_files(path):
        return app.send_static_file(path)
        
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # Create database tables if they don't exist
        db.create_all()
    socketio.run(app, debug=True, port=5000)
