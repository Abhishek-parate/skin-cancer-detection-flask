# models/groq_integration.py
import os
import json
import requests
from flask import current_app
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_groq_analysis(predicted_class, confidence):
    """
    Get additional analysis from Groq LLM API for the predicted skin condition.
    
    Args:
        predicted_class (str): The predicted skin condition class.
        confidence (float): The confidence score of the prediction.
        
    Returns:
        dict: Additional analysis information from Groq.
    """
    try:
        # Get API key from config
        api_key = current_app.config.get('GROQ_API_KEY', '')
        model_name = current_app.config.get('GROQ_MODEL', 'llama2-70b-4096')
        
        if not api_key:
            logger.warning("No Groq API key provided")
            return None
        
        # Define the prompt
        prompt = f"""
        You are a dermatology assistant. Based on an AI image analysis, a skin lesion has been classified as '{predicted_class}' with {confidence:.2f}% confidence.

        Please provide:
        1. A brief description of this condition (2-3 sentences)
        2. Three key characteristics to look for
        3. Whether this condition generally requires urgent medical attention (Yes/No, with brief explanation)
        4. Two follow-up questions a doctor might ask the patient about this condition
        
        Format your response as structured JSON with the following keys:
        - description
        - key_characteristics (as an array)
        - urgency_level (string: "High", "Medium", or "Low")
        - requires_urgent_attention (boolean)
        - urgency_explanation
        - followup_questions (as an array)
        
        Ensure your response is valid JSON format.
        """
        
        # Prepare the API request
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": "You are a helpful dermatology assistant that provides information in JSON format."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,  # Low temperature for more consistent, factual responses
            "max_tokens": 2048,
            "response_format": {"type": "json_object"}
        }
        
        # Make the API request
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            response_data = response.json()
            content = response_data['choices'][0]['message']['content']
            
            # Parse the JSON response
            try:
                analysis = json.loads(content)
                return analysis
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response from Groq: {e}")
                # If parsing fails, try to extract JSON using simple string operations
                try:
                    # Find the starting and ending curly braces
                    start_idx = content.find('{')
                    end_idx = content.rfind('}') + 1
                    if start_idx >= 0 and end_idx > start_idx:
                        json_str = content[start_idx:end_idx]
                        analysis = json.loads(json_str)
                        return analysis
                except Exception:
                    return {"error": "Failed to parse JSON from Groq response"}
        else:
            logger.error(f"Groq API request failed with status code {response.status_code}: {response.text}")
            return {"error": f"API request failed with status code {response.status_code}"}
            
    except Exception as e:
        logger.error(f"Error in get_groq_analysis: {str(e)}")
        return {"error": str(e)}