# models/model.py
import os
import numpy as np
import tensorflow as tf
from flask import current_app
import logging
from models.groq_integration import get_groq_analysis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to hold the loaded model
_model = None

def load_model():
    """Load and return the TensorFlow model."""
    global _model
    
    # If model is already loaded, return it
    if _model is not None:
        return _model
    
    try:
        # Define custom objects to handle the 'auto' reduction parameter
        custom_objects = {
            'loss': 'categorical_crossentropy'
        }
        
        # First try to load with custom objects and without compiling
        try:
            model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'models', 'model.h5')
            _model = tf.keras.models.load_model(
                model_path,
                custom_objects=custom_objects,
                compile=False
            )
            
            # Recompile the model with compatible parameters
            _model.compile(
                optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )
            
            logger.info("Model loaded successfully from .h5 file")
            
        except Exception as e:
            logger.error(f"Error loading .h5 model: {str(e)}")
            
            # Try loading from SavedModel format as fallback
            try:
                model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'models', 'converted_model')
                if os.path.exists(model_dir):
                    _model = tf.keras.models.load_model(model_dir)
                    logger.info("Model loaded successfully from SavedModel directory")
                else:
                    # If all else fails, create a dummy model for development
                    logger.warning("No model found. Creating a dummy model for development.")
                    _model = create_dummy_model()
            except Exception as e2:
                logger.error(f"Error loading SavedModel: {str(e2)}")
                # Create a dummy model for development
                logger.warning("Creating a dummy model for development after all load attempts failed.")
                _model = create_dummy_model()
        
        return _model
        
    except Exception as e:
        logger.error(f"Error in load_model: {str(e)}")
        return create_dummy_model()

def create_dummy_model():
    """Create a dummy model for development purposes."""
    logger.info("Creating dummy model for development")
    
    # Simple sequential model
    model = tf.keras.Sequential([
        tf.keras.layers.InputLayer(input_shape=(180, 180, 3)),
        tf.keras.layers.Conv2D(16, 3, activation='relu'),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(9, activation='softmax')
    ])
    
    # Compile the model
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

def predict_image(image_array):
    """Predict the skin condition from the image array."""
    try:
        # Load the model if not already loaded
        model = load_model()
        
        # Make prediction
        predictions = model.predict(image_array)
        
        # Get the class with highest probability
        predicted_class_index = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_index])
        
        # Get the class labels
        class_labels = [
            'actinic keratosis',
            'basal cell carcinoma',
            'dermatofibroma',
            'melanoma',
            'nevus',
            'pigmented benign keratosis',
            'seborrheic keratosis',
            'squamous cell carcinoma',
            'vascular lesion'
        ]
        
        # Get the predicted class name
        predicted_class = class_labels[predicted_class_index]
        
        # Use Groq for additional analysis if API key is available
        groq_api_key = current_app.config.get('GROQ_API_KEY', '')
        additional_analysis = None
        
        if groq_api_key:
            try:
                additional_analysis = get_groq_analysis(predicted_class, confidence)
            except Exception as e:
                logger.error(f"Error getting Groq analysis: {str(e)}")
                additional_analysis = None
        
        # Return prediction result
        return {
            'prediction': predicted_class,
            'confidence': round(confidence * 100, 2),
            'class_index': int(predicted_class_index),
            'all_probabilities': {class_labels[i]: float(predictions[0][i]) for i in range(len(class_labels))},
            'additional_analysis': additional_analysis
        }
        
    except Exception as e:
        logger.error(f"Error in predict_image: {str(e)}")
        
        # Return fallback prediction
        return {
            'prediction': 'unknown',
            'confidence': 0.0,
            'class_index': -1,
            'all_probabilities': {},
            'error': str(e)
        }