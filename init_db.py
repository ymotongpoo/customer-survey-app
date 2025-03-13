# Copyright 2025 Amazon Q Developer for CLI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Database initialization script.
"""
import os
import sqlite3
from pathlib import Path
from flask import Flask
from src.extensions import db
from src.models.user import User
from src.models.survey import Survey, SurveyOption, SurveyResponse


def init_db():
    """Initialize the database with schema and sample data."""
    app = Flask(__name__)
    
    # Configure the app
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL', 
        f"sqlite:///{os.path.join(app.instance_path, 'customer_feedback.db')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)
    
    # Initialize SQLAlchemy
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if we already have users
        if User.query.count() == 0:
            print("Adding sample data...")
            
            # Add a sample user
            user = User(
                email="demo@example.com",
                alias="Demo User",
                password="password123"
            )
            db.session.add(user)
            db.session.flush()  # Get user_id without committing
            
            # Add a sample survey
            survey = Survey(
                user_id=user.user_id,
                title="Customer Satisfaction Survey",
                description="Please rate your experience with our service."
            )
            db.session.add(survey)
            db.session.flush()  # Get survey_id without committing
            
            # Add survey options
            options = [
                ("Very Satisfied", 1),
                ("Satisfied", 2),
                ("Neutral", 3),
                ("Dissatisfied", 4),
                ("Very Dissatisfied", 5)
            ]
            
            for text, order in options:
                option = SurveyOption(
                    survey_id=survey.survey_id,
                    option_text=text,
                    option_order=order
                )
                db.session.add(option)
            
            # Commit all changes
            db.session.commit()
            print("Sample data added successfully!")
        else:
            print("Database already contains data. Skipping sample data creation.")


if __name__ == "__main__":
    init_db()