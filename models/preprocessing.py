# Image preprocessing# models/preprocessing.py
import cv2
import numpy as np
from PIL import Image
import tensorflow as tf
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def preprocess_image(image_path, target_size=(180, 180)):
    """
    Preprocess an image for prediction.
    
    Args:
        image_path (str): Path to the image file.
        target_size (tuple): Target size for the image (height, width).
        
    Returns:
        numpy.ndarray: Preprocessed image array suitable for model input.
    """
    try:
        # Load the image using PIL
        img = Image.open(image_path)
        
        # Resize the image
        img = img.resize(target_size)
        
        # Convert to numpy array
        img_array = np.array(img)
        
        # Ensure the image has 3 channels (RGB)
        if len(img_array.shape) == 2:  # Grayscale
            img_array = np.stack([img_array, img_array, img_array], axis=-1)
        elif img_array.shape[2] == 4:  # RGBA
            img_array = img_array[:, :, :3]  # Drop alpha channel
        
        # Expand dimensions to create a batch of size 1
        img_array = np.expand_dims(img_array, axis=0)
        
        # Normalize pixel values to [0, 1]
        img_array = img_array.astype('float32') / 255.0
        
        logger.info(f"Image preprocessed successfully: {image_path}")
        return img_array
        
    except Exception as e:
        logger.error(f"Error preprocessing image: {str(e)}")
        raise

def enhance_image(image_path, output_path):
    """
    Enhance an image for better visualization and analysis.
    
    Args:
        image_path (str): Path to the input image file.
        output_path (str): Path to save the enhanced image.
        
    Returns:
        bool: True if enhancement was successful, False otherwise.
    """
    try:
        # Read the image
        img = cv2.imread(image_path)
        
        if img is None:
            logger.error(f"Failed to read image: {image_path}")
            return False
        
        # Convert to float32 for processing
        img_float = img.astype(np.float32) / 255.0
        
        # Apply contrast enhancement (CLAHE)
        lab = cv2.cvtColor(img_float, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)
        
        # Apply CLAHE to L-channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(np.uint8(l_channel * 255)) / 255.0
        
        # Merge channels
        enhanced_lab = cv2.merge([cl, a_channel, b_channel])
        
        # Convert back to BGR
        enhanced_img = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        
        # Normalize
        enhanced_img = np.clip(enhanced_img * 255, 0, 255).astype(np.uint8)
        
        # Save the enhanced image
        cv2.imwrite(output_path, enhanced_img)
        
        logger.info(f"Image enhanced successfully: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error enhancing image: {str(e)}")
        return False

def extract_features(img_array):
    """
    Extract features from an image that might be relevant for skin condition analysis.
    
    Args:
        img_array (numpy.ndarray): Image array.
        
    Returns:
        dict: Dictionary of extracted features.
    """
    try:
        # Convert to BGR if needed and create a copy for processing
        if len(img_array.shape) == 4:  # If batch dimension is present
            img = img_array[0].copy()
        else:
            img = img_array.copy()
        
        # Convert to uint8 if in float format
        if img.dtype == np.float32 or img.dtype == np.float64:
            img = (img * 255).astype(np.uint8)
        
        # Convert to BGR if in RGB
        if img.shape[2] == 3:  # If RGB
            img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        else:
            img_bgr = img
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        
        # Extract color features (average color values in HSV space)
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        hue_avg = np.mean(img_hsv[:, :, 0])
        saturation_avg = np.mean(img_hsv[:, :, 1])
        value_avg = np.mean(img_hsv[:, :, 2])
        
        # Calculate color variance (standard deviation)
        hue_std = np.std(img_hsv[:, :, 0])
        saturation_std = np.std(img_hsv[:, :, 1])
        value_std = np.std(img_hsv[:, :, 2])
        
        # Calculate texture features using GLCM (Gray-Level Co-occurrence Matrix)
        # Simplified version - just calculate some basic statistics
        # Real implementation would use a proper GLCM calculation
        texture_contrast = np.std(gray)
        texture_energy = np.sum(gray**2) / (gray.shape[0] * gray.shape[1])
        
        # Calculate shape features
        # Threshold the image (Otsu's method)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # If contours are found, calculate shape features
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            perimeter = cv2.arcLength(largest_contour, True)
            
            # Calculate circularity: 4*pi*area/perimeter^2
            circularity = 0
            if perimeter > 0:
                circularity = 4 * np.pi * area / (perimeter**2)
                
            # Calculate aspect ratio using bounding rectangle
            x, y, w, h = cv2.boundingRect(largest_contour)
            aspect_ratio = w / h if h > 0 else 0
            
            # Calculate solidity: area/convex hull area
            hull = cv2.convexHull(largest_contour)
            hull_area = cv2.contourArea(hull)
            solidity = area / hull_area if hull_area > 0 else 0
        else:
            area = 0
            perimeter = 0
            circularity = 0
            aspect_ratio = 0
            solidity = 0
        
        # Return all features
        features = {
            'color': {
                'hue_avg': float(hue_avg),
                'saturation_avg': float(saturation_avg),
                'value_avg': float(value_avg),
                'hue_std': float(hue_std),
                'saturation_std': float(saturation_std),
                'value_std': float(value_std)
            },
            'texture': {
                'contrast': float(texture_contrast),
                'energy': float(texture_energy)
            },
            'shape': {
                'area': float(area),
                'perimeter': float(perimeter),
                'circularity': float(circularity),
                'aspect_ratio': float(aspect_ratio),
                'solidity': float(solidity)
            }
        }
        
        logger.info("Features extracted successfully")
        return features
        
    except Exception as e:
        logger.error(f"Error extracting features: {str(e)}")
        return {
            'color': {},
            'texture': {},
            'shape': {},
            'error': str(e)
        }