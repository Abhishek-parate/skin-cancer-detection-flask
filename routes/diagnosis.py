# routes/diagnosis.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify, session
import os
from werkzeug.utils import secure_filename
import uuid
import time
from datetime import datetime

# Import model related functions
from models.model import predict_image
from models.preprocessing import preprocess_image
from utils.helpers import allowed_file

# Create a Blueprint for diagnosis routes
diagnosis_bp = Blueprint('diagnosis', __name__)

@diagnosis_bp.route('/')
def index():
    """Render the diagnosis upload page."""
    # Get sample images for the diagnosis page
    sample_conditions = [
        {
            'name': 'Melanoma',
            'image': 'conditions/melanoma.jpg',
            'description': 'The most serious type of skin cancer'
        },
        {
            'name': 'Nevus',
            'image': 'conditions/nevus.jpg',
            'description': 'Common moles that are usually harmless'
        },
        {
            'name': 'Actinic Keratosis',
            'image': 'conditions/actinic-keratosis.jpg',
            'description': 'Pre-cancerous skin growths caused by sun damage'
        }
    ]
    
    return render_template('diagnose.html', sample_conditions=sample_conditions)

@diagnosis_bp.route('/upload', methods=['POST'])
def upload():
    """Handle image upload and processing."""
    # Check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('diagnosis.index'))
    
    file = request.files['file']
    
    # If user does not select file, browser might submit an empty file
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('diagnosis.index'))
    
    if file and allowed_file(file.filename):
        # Generate a unique filename
        original_filename = secure_filename(file.filename)
        file_extension = os.path.splitext(original_filename)[1]
        unique_filename = f"{str(uuid.uuid4())}{file_extension}"
        
        # Save the file
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        try:
            # Preprocess the image
            preprocessed_image = preprocess_image(file_path)
            
            # Make prediction
            prediction_result = predict_image(preprocessed_image)
            
            # Store results in session for the results page
            session['diagnosis_result'] = {
                'filename': unique_filename,
                'original_filename': original_filename,
                'prediction': prediction_result['prediction'],
                'confidence': prediction_result['confidence'],
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Redirect to results page
            return redirect(url_for('diagnosis.results'))
            
        except Exception as e:
            current_app.logger.error(f"Error during prediction: {str(e)}")
            flash('An error occurred during processing. Please try again.', 'error')
            return redirect(url_for('diagnosis.index'))
    else:
        flash('File type not allowed. Please upload a JPG, JPEG, or PNG image.', 'error')
        return redirect(url_for('diagnosis.index'))

@diagnosis_bp.route('/results')
def results():
    """Display diagnosis results."""
    # Check if results exist in session
    if 'diagnosis_result' not in session:
        flash('No diagnosis results found. Please upload an image first.', 'error')
        return redirect(url_for('diagnosis.index'))
    
    # Get result from session
    result = session['diagnosis_result']
    
    # Get details about the predicted condition
    condition_info = get_condition_info(result['prediction'])
    
    # Generate recommendations based on the condition
    recommendations = generate_recommendations(result['prediction'])
    
    return render_template('results.html', 
                          result=result, 
                          condition_info=condition_info,
                          recommendations=recommendations)

@diagnosis_bp.route('/api/upload', methods=['POST'])
def api_upload():
    """API endpoint for image upload and processing (for AJAX requests)."""
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # If user does not select file, browser might submit an empty file
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        # Generate a unique filename
        original_filename = secure_filename(file.filename)
        file_extension = os.path.splitext(original_filename)[1]
        unique_filename = f"{str(uuid.uuid4())}{file_extension}"
        
        # Save the file
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        try:
            # Preprocess the image
            preprocessed_image = preprocess_image(file_path)
            
            # Make prediction
            prediction_result = predict_image(preprocessed_image)
            
            # Add filename to result
            prediction_result['filename'] = unique_filename
            prediction_result['original_filename'] = original_filename
            
            return jsonify({
                'success': True, 
                'result': prediction_result
            })
            
        except Exception as e:
            current_app.logger.error(f"Error during prediction: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    else:
        return jsonify({
            'success': False, 
            'error': 'File type not allowed. Please upload a JPG, JPEG, or PNG image.'
        }), 400

# Helper functions
def get_condition_info(condition_name):
    """Get detailed information about a skin condition."""
    # This would typically come from a database, but for simplicity we're hardcoding it
    conditions = {
        'actinic keratosis': {
            'name': 'Actinic Keratosis',
            'description': 'Actinic keratoses are dry scaly patches of skin that have been damaged by the sun. The patches are not usually serious, but there\'s a small chance they could become skin cancer.',
            'severity': 'Moderate',
            'treatments': [
                'Prescription creams and gels',
                'Freezing the patches (cryotherapy)',
                'Surgery to cut out or scrape away the patches',
                'Photodynamic therapy (PDT)'
            ],
            'learn_more_url': 'https://www.nhs.uk/conditions/actinic-keratoses'
        },
        'basal cell carcinoma': {
            'name': 'Basal Cell Carcinoma',
            'description': 'Basal cell carcinoma is a type of skin cancer that begins in the basal cells — a type of cell within the skin that produces new skin cells as old ones die off.',
            'severity': 'High',
            'symptoms': [
                'A shiny, skin-colored bump that\'s translucent',
                'A brown, black or blue lesion with a raised border',
                'A flat, scaly patch with a raised edge',
                'A white, waxy, scar-like lesion'
            ],
            'learn_more_url': 'https://www.mayoclinic.org/diseases-conditions/basal-cell-carcinoma/symptoms-causes/syc-20354187'
        },
        'melanoma': {
            'name': 'Melanoma',
            'description': 'Melanoma, the most serious type of skin cancer, develops in the cells that produce melanin — the pigment that gives your skin its color.',
            'severity': 'Very High',
            'warning_signs': [
                'A change in an existing mole',
                'The development of a new pigmented growth on your skin'
            ],
            'learn_more_url': 'https://www.mayoclinic.org/diseases-conditions/melanoma/symptoms-causes/syc-20374884'
        },
        # Add other conditions here...
    }
    
    # Default information if condition not found
    default_info = {
        'name': condition_name.title(),
        'description': 'A skin condition that requires professional evaluation.',
        'severity': 'Unknown',
        'learn_more_url': url_for('education.conditions')
    }
    
    # Return condition info or default if not found
    return conditions.get(condition_name.lower(), default_info)

def generate_recommendations(condition_name):
    """Generate recommendations based on the diagnosed condition."""
    # Common recommendations for all conditions
    common_recommendations = [
        'Schedule an appointment with a dermatologist for a professional evaluation',
        'Take clear photos of the affected area to show your doctor',
        'Protect your skin from sun exposure and use SPF 30+ sunscreen daily',
        'Perform regular skin self-examinations'
    ]
    
    # Condition-specific recommendations
    condition_specific = {
        'actinic keratosis': [
            'Avoid direct sun exposure, especially during peak hours (10 AM to 4 PM)',
            'Use skin moisturizers regularly to reduce dryness'
        ],
        'basal cell carcinoma': [
            'Seek medical attention within the next 2-3 weeks',
            'Avoid picking at or irritating the lesion'
        ],
        'melanoma': [
            'Seek medical attention as soon as possible (within 1 week)',
            'Check for any other suspicious spots on your skin'
        ],
        # Add other conditions here...
    }
    
    # Get specific recommendations or empty list if not found
    specific_recs = condition_specific.get(condition_name.lower(), [])
    
    # Combine and return all recommendations
    return common_recommendations + specific_recs