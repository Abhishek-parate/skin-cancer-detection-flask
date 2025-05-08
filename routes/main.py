# routes/main.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from utils.email_service import send_contact_email
from utils.validators import validate_contact_form

# Create a Blueprint for the main routes
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')

@main_bp.route('/about')
def about():
    """Render the about page."""
    # Team member information for the about page
    team_members = [
        {
            'name': 'Dr. Sarah Johnson',
            'role': 'Medical Director',
            'bio': 'Board-certified dermatologist with over 15 years of experience in skin cancer detection and treatment.',
            'image': 'team/doctor1.jpg'
        },
        {
            'name': 'Dr. Michael Chen',
            'role': 'AI Research Lead',
            'bio': 'PhD in Machine Learning with a focus on medical imaging analysis and deep learning applications in healthcare.',
            'image': 'team/researcher.jpg'
        },
        {
            'name': 'Dr. Emily Rodriguez',
            'role': 'Clinical Advisor',
            'bio': 'Oncology specialist with expertise in melanoma treatment and early detection protocols.',
            'image': 'team/doctor2.jpg'
        }
    ]
    
    # Research papers and publications
    publications = [
        {
            'title': 'Deep Learning for Automated Detection of Melanoma in Dermoscopic Images',
            'journal': 'Journal of Medical Imaging',
            'year': 2023,
            'url': '#'
        },
        {
            'title': 'Comparison of Machine Learning Algorithms for Skin Lesion Classification',
            'journal': 'JAMA Dermatology',
            'year': 2022,
            'url': '#'
        },
        {
            'title': 'Improving Early Detection of Skin Cancer through AI-Assisted Diagnosis',
            'journal': 'Nature Medicine',
            'year': 2021,
            'url': '#'
        }
    ]
    
    return render_template('about.html', team_members=team_members, publications=publications)

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Handle the contact page and form submission."""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Validate form data
        errors = validate_contact_form(name, email, subject, message)
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('contact.html', 
                                  name=name, 
                                  email=email, 
                                  subject=subject, 
                                  message=message)
        
        # Send email
        try:
            send_contact_email(name, email, subject, message)
            flash('Your message has been sent. We will get back to you soon!', 'success')
            return redirect(url_for('main.contact'))
        except Exception as e:
            current_app.logger.error(f"Error sending email: {str(e)}")
            flash('There was a problem sending your message. Please try again later.', 'error')
            
    return render_template('contact.html')

@main_bp.route('/find-doctor')
def find_doctor():
    """Render the find a doctor page."""
    google_maps_api_key = current_app.config['GOOGLE_MAPS_API_KEY']
    return render_template('find_doctor.html', google_maps_api_key=google_maps_api_key)

@main_bp.route('/privacy-policy')
def privacy_policy():
    """Render the privacy policy page."""
    return render_template('privacy_policy.html')

@main_bp.route('/terms-of-service')
def terms_of_service():
    """Render the terms of service page."""
    return render_template('terms_of_service.html')