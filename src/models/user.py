"""
User model.
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from src.extensions import db, login_manager


class User(UserMixin, db.Model):
    """User model for storing user account information."""
    __tablename__ = 'Users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    alias = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    surveys = db.relationship('Survey', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, email, alias, password):
        self.email = email
        self.alias = alias
        self.set_password(password)
    
    def set_password(self, password):
        """Create hashed password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Return the user ID as a unicode string."""
        return str(self.user_id)
    
    def __repr__(self):
        return f'<User {self.email}>'


@login_manager.user_loader
def load_user(user_id):
    """User loader for Flask-Login."""
    return User.query.get(int(user_id))