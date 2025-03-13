"""
Survey models.
"""
from datetime import datetime
from src.extensions import db


class Survey(db.Model):
    """Survey model for storing survey information."""
    __tablename__ = 'Surveys'
    
    survey_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    options = db.relationship('SurveyOption', backref='survey', lazy=True, cascade='all, delete-orphan')
    responses = db.relationship('SurveyResponse', backref='survey', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, user_id, title, description=None):
        self.user_id = user_id
        self.title = title
        self.description = description
    
    def __repr__(self):
        return f'<Survey {self.title}>'
    
    def to_dict(self):
        """Convert survey to dictionary."""
        return {
            'survey_id': self.survey_id,
            'title': self.title,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'options': [option.to_dict() for option in self.options]
        }


class SurveyOption(db.Model):
    """Survey option model for storing survey choices."""
    __tablename__ = 'Survey_Options'
    
    option_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('Surveys.survey_id', ondelete='CASCADE'), nullable=False)
    option_text = db.Column(db.Text, nullable=False)
    option_order = db.Column(db.Integer, nullable=False)
    
    # Constraints
    __table_args__ = (
        db.CheckConstraint('option_order BETWEEN 1 AND 5', name='check_option_order'),
    )
    
    # Relationships
    responses = db.relationship('SurveyResponse', backref='option', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, survey_id, option_text, option_order):
        self.survey_id = survey_id
        self.option_text = option_text
        self.option_order = option_order
    
    def __repr__(self):
        return f'<SurveyOption {self.option_text}>'
    
    def to_dict(self):
        """Convert option to dictionary."""
        return {
            'option_id': self.option_id,
            'option_text': self.option_text,
            'option_order': self.option_order
        }


class SurveyResponse(db.Model):
    """Survey response model for storing end user feedback."""
    __tablename__ = 'Survey_Responses'
    
    response_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('Surveys.survey_id', ondelete='CASCADE'), nullable=False)
    option_id = db.Column(db.Integer, db.ForeignKey('Survey_Options.option_id', ondelete='CASCADE'), nullable=False)
    respondent_email = db.Column(db.String(120))
    response_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, survey_id, option_id, respondent_email=None):
        self.survey_id = survey_id
        self.option_id = option_id
        self.respondent_email = respondent_email
    
    def __repr__(self):
        return f'<SurveyResponse {self.response_id}>'
    
    def to_dict(self):
        """Convert response to dictionary."""
        return {
            'response_id': self.response_id,
            'survey_id': self.survey_id,
            'option_id': self.option_id,
            'respondent_email': self.respondent_email,
            'response_date': self.response_date.isoformat()
        }