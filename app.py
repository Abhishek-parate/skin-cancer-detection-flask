# app.py
from flask import Flask, render_template, flash, redirect, url_for, request, jsonify, session
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid

# Import configuration
from config import Config

# Import route modules
from routes.main import main_bp
from routes.diagnosis import diagnosis_bp
from routes.education import education_bp

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(diagnosis_bp, url_prefix='/diagnose')
app.register_blueprint(education_bp, url_prefix='/education')

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Custom error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500

# Context processor for common template variables
@app.context_processor
def inject_globals():
    return {
        'current_year': datetime.now().year,
        'app_name': 'Skin Cancer Detection'
    }

# Custom Jinja2 filters
@app.template_filter('capitalize_all')
def capitalize_all(text):
    """Capitalize each word in a string"""
    return ' '.join(word.capitalize() for word in text.split())

# Main entry point
if __name__ == '__main__':
    # Run the Flask application
    app.run(debug=app.config['DEBUG'], host=app.config['HOST'], port=app.config['PORT'])