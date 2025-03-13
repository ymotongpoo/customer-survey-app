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
Survey routes.
"""
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError

from src.extensions import db
from src.models.survey import Survey, SurveyOption, SurveyResponse

survey_bp = Blueprint('survey', __name__, url_prefix='/api/surveys')


@survey_bp.route('/', methods=['GET'])
@login_required
def get_surveys():
    """Get all surveys for the current user."""
    try:
        surveys = Survey.query.filter_by(user_id=current_user.user_id).all()
        return jsonify({
            'surveys': [survey.to_dict() for survey in surveys]
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error retrieving surveys: {str(e)}")
        return jsonify({'error': 'Failed to retrieve surveys'}), 500


@survey_bp.route('/<int:survey_id>', methods=['GET'])
@login_required
def get_survey(survey_id):
    """Get a specific survey."""
    try:
        survey = Survey.query.filter_by(survey_id=survey_id, user_id=current_user.user_id).first()
        if not survey:
            return jsonify({'error': 'Survey not found'}), 404
        
        return jsonify(survey.to_dict()), 200
    except Exception as e:
        current_app.logger.error(f"Error retrieving survey: {str(e)}")
        return jsonify({'error': 'Failed to retrieve survey'}), 500


@survey_bp.route('/', methods=['POST'])
@login_required
def create_survey():
    """Create a new survey."""
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('title'):
        return jsonify({'error': 'Survey title is required'}), 400
    
    options = data.get('options', [])
    if len(options) < 2 or len(options) > 5:
        return jsonify({'error': 'Survey must have between 2 and 5 options'}), 400
    
    try:
        # Create survey
        survey = Survey(
            user_id=current_user.user_id,
            title=data['title'],
            description=data.get('description')
        )
        db.session.add(survey)
        db.session.flush()  # Get survey_id without committing
        
        # Add options
        for i, option_text in enumerate(options, 1):
            option = SurveyOption(
                survey_id=survey.survey_id,
                option_text=option_text,
                option_order=i
            )
            db.session.add(option)
        
        db.session.commit()
        return jsonify({
            'message': 'Survey created successfully',
            'survey': survey.to_dict()
        }), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error creating survey: {str(e)}")
        return jsonify({'error': 'Failed to create survey'}), 500
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating survey: {str(e)}")
        return jsonify({'error': 'Failed to create survey'}), 500


@survey_bp.route('/<int:survey_id>', methods=['PUT'])
@login_required
def update_survey(survey_id):
    """Update a survey."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        survey = Survey.query.filter_by(survey_id=survey_id, user_id=current_user.user_id).first()
        if not survey:
            return jsonify({'error': 'Survey not found'}), 404
        
        # Update survey fields
        if 'title' in data:
            survey.title = data['title']
        if 'description' in data:
            survey.description = data['description']
        if 'is_active' in data:
            survey.is_active = data['is_active']
        
        db.session.commit()
        return jsonify({
            'message': 'Survey updated successfully',
            'survey': survey.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating survey: {str(e)}")
        return jsonify({'error': 'Failed to update survey'}), 500


@survey_bp.route('/<int:survey_id>', methods=['DELETE'])
@login_required
def delete_survey(survey_id):
    """Delete a survey."""
    try:
        survey = Survey.query.filter_by(survey_id=survey_id, user_id=current_user.user_id).first()
        if not survey:
            return jsonify({'error': 'Survey not found'}), 404
        
        db.session.delete(survey)
        db.session.commit()
        return jsonify({'message': 'Survey deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting survey: {str(e)}")
        return jsonify({'error': 'Failed to delete survey'}), 500


@survey_bp.route('/<int:survey_id>/respond', methods=['POST'])
def submit_response(survey_id):
    """Submit a response to a survey."""
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('option_id'):
        return jsonify({'error': 'Option ID is required'}), 400
    
    try:
        # Check if survey exists and is active
        survey = Survey.query.filter_by(survey_id=survey_id, is_active=True).first()
        if not survey:
            return jsonify({'error': 'Survey not found or inactive'}), 404
        
        # Check if option belongs to the survey
        option = SurveyOption.query.filter_by(
            option_id=data['option_id'],
            survey_id=survey_id
        ).first()
        if not option:
            return jsonify({'error': 'Invalid option for this survey'}), 400
        
        # Create response
        response = SurveyResponse(
            survey_id=survey_id,
            option_id=data['option_id'],
            respondent_email=data.get('email')
        )
        db.session.add(response)
        db.session.commit()
        
        return jsonify({
            'message': 'Response submitted successfully',
            'response_id': response.response_id
        }), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error submitting response: {str(e)}")
        return jsonify({'error': 'Failed to submit response'}), 500


@survey_bp.route('/<int:survey_id>/results', methods=['GET'])
@login_required
def get_results(survey_id):
    """Get results for a survey."""
    try:
        # Check if survey belongs to current user
        survey = Survey.query.filter_by(survey_id=survey_id, user_id=current_user.user_id).first()
        if not survey:
            return jsonify({'error': 'Survey not found'}), 404
        
        # Get all options for this survey
        options = SurveyOption.query.filter_by(survey_id=survey_id).all()
        
        # Count responses for each option
        results = {}
        total_responses = 0
        
        for option in options:
            count = SurveyResponse.query.filter_by(option_id=option.option_id).count()
            results[option.option_text] = count
            total_responses += count
        
        return jsonify({
            'survey_title': survey.title,
            'total_responses': total_responses,
            'results': results
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error retrieving results: {str(e)}")
        return jsonify({'error': 'Failed to retrieve results'}), 500