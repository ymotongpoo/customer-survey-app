"""
Main routes for the application.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from src.models.survey import Survey, SurveyOption, SurveyResponse
from src.extensions import db

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Landing page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page."""
    surveys = Survey.query.filter_by(user_id=current_user.user_id).all()
    return render_template('dashboard.html', surveys=surveys)


@main_bp.route('/surveys/create', methods=['GET', 'POST'])
@login_required
def create_survey():
    """Create a new survey."""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        options = request.form.getlist('options[]')
        
        if not title:
            flash('Survey title is required', 'error')
            return render_template('create_survey.html')
        
        if len(options) < 2 or len(options) > 5:
            flash('Survey must have between 2 and 5 options', 'error')
            return render_template('create_survey.html')
        
        # Filter out empty options
        options = [opt for opt in options if opt.strip()]
        
        try:
            # Create survey
            survey = Survey(
                user_id=current_user.user_id,
                title=title,
                description=description
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
            flash('Survey created successfully', 'success')
            return redirect(url_for('main.view_survey', survey_id=survey.survey_id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating survey: {str(e)}")
            flash('An error occurred while creating the survey', 'error')
    
    return render_template('create_survey.html')


@main_bp.route('/surveys/<int:survey_id>')
@login_required
def view_survey(survey_id):
    """View a specific survey."""
    survey = Survey.query.filter_by(survey_id=survey_id, user_id=current_user.user_id).first_or_404()
    options = SurveyOption.query.filter_by(survey_id=survey_id).order_by(SurveyOption.option_order).all()
    
    # Get results
    results = {}
    total_responses = 0
    
    for option in options:
        count = SurveyResponse.query.filter_by(option_id=option.option_id).count()
        results[option.option_text] = count
        total_responses += count
    
    # Generate share link
    host = request.host_url.rstrip('/')
    share_link = f"{host}/respond/{survey_id}"
    
    return render_template(
        'view_survey.html',
        survey=survey,
        options=options,
        results=results,
        total_responses=total_responses,
        share_link=share_link
    )


@main_bp.route('/surveys/<int:survey_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_survey(survey_id):
    """Edit a survey."""
    survey = Survey.query.filter_by(survey_id=survey_id, user_id=current_user.user_id).first_or_404()
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        is_active = request.form.get('is_active') == '1'
        
        if not title:
            flash('Survey title is required', 'error')
            return render_template('edit_survey.html', survey=survey)
        
        try:
            survey.title = title
            survey.description = description
            survey.is_active = is_active
            
            db.session.commit()
            flash('Survey updated successfully', 'success')
            return redirect(url_for('main.view_survey', survey_id=survey_id))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating survey: {str(e)}")
            flash('An error occurred while updating the survey', 'error')
    
    return render_template('edit_survey.html', survey=survey)


@main_bp.route('/surveys/<int:survey_id>/toggle', methods=['POST'])
@login_required
def toggle_survey_status(survey_id):
    """Toggle survey active status."""
    survey = Survey.query.filter_by(survey_id=survey_id, user_id=current_user.user_id).first_or_404()
    
    try:
        survey.is_active = not survey.is_active
        db.session.commit()
        
        status = "activated" if survey.is_active else "deactivated"
        flash(f'Survey {status} successfully', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error toggling survey status: {str(e)}")
        flash('An error occurred', 'error')
    
    return redirect(url_for('main.view_survey', survey_id=survey_id))


@main_bp.route('/surveys/<int:survey_id>/delete', methods=['POST'])
@login_required
def delete_survey(survey_id):
    """Delete a survey."""
    survey = Survey.query.filter_by(survey_id=survey_id, user_id=current_user.user_id).first_or_404()
    
    try:
        db.session.delete(survey)
        db.session.commit()
        flash('Survey deleted successfully', 'success')
        return redirect(url_for('main.dashboard'))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting survey: {str(e)}")
        flash('An error occurred while deleting the survey', 'error')
        return redirect(url_for('main.view_survey', survey_id=survey_id))


@main_bp.route('/respond/<int:survey_id>', methods=['GET', 'POST'])
def respond_survey(survey_id):
    """Public page to respond to a survey."""
    survey = Survey.query.filter_by(survey_id=survey_id, is_active=True).first_or_404()
    options = SurveyOption.query.filter_by(survey_id=survey_id).order_by(SurveyOption.option_order).all()
    
    if request.method == 'POST':
        option_id = request.form.get('option_id')
        email = request.form.get('email', '')
        
        if not option_id:
            flash('Please select an option', 'error')
            return render_template('respond_survey.html', survey=survey, options=options)
        
        try:
            response = SurveyResponse(
                survey_id=survey_id,
                option_id=option_id,
                respondent_email=email
            )
            db.session.add(response)
            db.session.commit()
            flash('Thank you for your feedback!', 'success')
            return render_template('response_thank_you.html', survey=survey)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error submitting response: {str(e)}")
            flash('An error occurred. Please try again.', 'error')
    
    return render_template('respond_survey.html', survey=survey, options=options)