# routes/education.py
from flask import Blueprint, render_template, request, abort, current_app

# Create a Blueprint for education routes
education_bp = Blueprint('education', __name__)

@education_bp.route('/')
def index():
    """Render the education home page."""
    return render_template('education/index.html')

@education_bp.route('/conditions')
def conditions():
    """Render the page listing all skin conditions."""
    # Get query parameters for filtering and sorting
    search_query = request.args.get('search', '').lower()
    sort_by = request.args.get('sort', 'name')  # Default sort by name
    
    # Get all conditions data
    all_conditions = get_all_conditions()
    
    # Filter conditions based on search query
    if search_query:
        filtered_conditions = [c for c in all_conditions if search_query in c['name'].lower()]
    else:
        filtered_conditions = all_conditions
    
    # Sort conditions
    if sort_by == 'severity':
        # Define severity order for sorting
        severity_order = {'low': 1, 'moderate': 2, 'high': 3, 'very high': 4}
        filtered_conditions.sort(key=lambda x: severity_order.get(x['severity'].lower(), 0), reverse=True)
    elif sort_by == 'prevalence':
        # Define prevalence order for sorting
        prevalence_order = {'rare': 1, 'less common': 2, 'common': 3, 'very common': 4}
        filtered_conditions.sort(key=lambda x: prevalence_order.get(x['prevalence'].lower(), 0), reverse=True)
    else:  # Default to sorting by name
        filtered_conditions.sort(key=lambda x: x['name'])
    
    return render_template('education/conditions.html', 
                          conditions=filtered_conditions,
                          search_query=search_query,
                          sort_by=sort_by)

@education_bp.route('/conditions/<condition_id>')
def condition_detail(condition_id):
    """Render detailed information for a specific condition."""
    # Get condition data by ID or slug
    condition = get_condition_by_id(condition_id)
    
    if not condition:
        abort(404)
    
    # Get related conditions
    related_conditions = get_related_conditions(condition_id)
    
    return render_template('education/condition_detail.html', 
                          condition=condition,
                          related_conditions=related_conditions)

@education_bp.route('/prevention')
def prevention():
    """Render information about skin cancer prevention."""
    prevention_tips = [
        {
            'category': 'Sun Protection',
            'tips': [
                'Seek shade between 10 AM and 4 PM when the sun is strongest',
                'Wear protective clothing, including wide-brimmed hats and UV-blocking sunglasses',
                'Apply broad-spectrum sunscreen with SPF 30+ to all exposed skin, even on cloudy days',
                'Reapply sunscreen every 2 hours, or more frequently if swimming or sweating',
                'Avoid tanning beds and sun lamps, which emit harmful UV radiation'
            ]
        },
        {
            'category': 'Regular Skin Checks',
            'tips': [
                'Perform monthly self-examinations to notice any changes in your skin',
                'Use the ABCDE rule to check moles: Asymmetry, Border, Color, Diameter, and Evolving',
                'Have a yearly skin examination by a dermatologist',
                'Track changes in existing moles and the appearance of new spots',
                'Create a body map to document the location of moles and spots'
            ]
        },
        {
            'category': 'Lifestyle Factors',
            'tips': [
                'Stay hydrated and maintain a balanced diet rich in antioxidants',
                'Avoid smoking, which can increase skin cancer risk',
                'Be extra cautious near water, snow, and sand, which reflect and intensify UV rays',
                'Teach children good sun protection habits from an early age',
                'Consider taking vitamin D supplements instead of sun exposure if you have low levels'
            ]
        }
    ]
    
    return render_template('education/prevention.html', prevention_tips=prevention_tips)

@education_bp.route('/self-examination')
def self_examination():
    """Render guide for skin self-examination."""
    examination_steps = [
        {
            'title': 'Examine your body front and back',
            'description': 'Stand in front of a full-length mirror and examine your front, back, and sides with arms raised.',
            'image': 'self-exam-1.jpg'
        },
        {
            'title': 'Check your arms and hands',
            'description': 'Look at your arms, underarms, both sides of your hands, between fingers, and under fingernails.',
            'image': 'self-exam-2.jpg'
        },
        {
            'title': 'Examine your legs and feet',
            'description': 'Sit down and carefully check your legs, feet, between toes, and under toenails.',
            'image': 'self-exam-3.jpg'
        },
        {
            'title': 'Use a hand mirror for difficult areas',
            'description': 'Use a hand mirror to check your neck, scalp, back, and buttocks. Part your hair to examine your scalp.',
            'image': 'self-exam-4.jpg'
        }
    ]
    
    abcde_rule = {
        'A': {'title': 'Asymmetry', 'description': 'One half of the mole doesn\'t match the other half.'},
        'B': {'title': 'Border', 'description': 'The edges are irregular, ragged, notched, or blurred.'},
        'C': {'title': 'Color', 'description': 'The color is not uniform and may include different shades of brown, black, or patches of red, white, or blue.'},
        'D': {'title': 'Diameter', 'description': 'The spot is larger than 6 millimeters across (about the size of a pencil eraser), although melanomas can sometimes be smaller.'},
        'E': {'title': 'Evolving', 'description': 'The mole is changing in size, shape, color, or elevation, or is causing new symptoms like bleeding, itching, or crusting.'}
    }
    
    return render_template('education/self_examination.html', 
                          examination_steps=examination_steps,
                          abcde_rule=abcde_rule)

@education_bp.route('/resources')
def resources():
    """Render educational resources and links."""
    resource_categories = [
        {
            'name': 'Medical Organizations',
            'resources': [
                {
                    'name': 'Skin Cancer Foundation',
                    'url': 'https://www.skincancer.org',
                    'description': 'Comprehensive information on skin cancer prevention, treatment, and research'
                },
                {
                    'name': 'American Academy of Dermatology',
                    'url': 'https://www.aad.org',
                    'description': 'Educational resources on skin conditions from the national association of dermatologists'
                },
                {
                    'name': 'American Cancer Society',
                    'url': 'https://www.cancer.org',
                    'description': 'Information on all types of cancer including skin cancer'
                },
                {
                    'name': 'World Health Organization (WHO)',
                    'url': 'https://www.who.int/news-room/fact-sheets/detail/skin-cancers',
                    'description': 'Global perspective and statistics on skin cancer'
                }
            ]
        },
        {
            'name': 'Support Groups',
            'resources': [
                {
                    'name': 'Melanoma Research Foundation',
                    'url': 'https://www.melanoma.org',
                    'description': 'Support and resources specifically for melanoma patients'
                },
                {
                    'name': 'Cancer Support Community',
                    'url': 'https://www.cancersupportcommunity.org',
                    'description': 'Support network and resources for cancer patients and families'
                },
                {
                    'name': 'CancerCare',
                    'url': 'https://www.cancercare.org',
                    'description': 'Professional support services for anyone affected by cancer'
                }
            ]
        },
        {
            'name': 'Mobile Apps',
            'resources': [
                {
                    'name': 'UMSkinCheck',
                    'url': 'https://www.uofmhealth.org/patient-visitor-guide/um-skin-check-app',
                    'description': 'App for melanoma detection and self-examination tracking developed by University of Michigan'
                },
                {
                    'name': 'SkinVision',
                    'url': 'https://www.skinvision.com',
                    'description': 'App that assesses skin cancer risk and helps track skin changes over time'
                },
                {
                    'name': 'MoleMapper',
                    'url': 'https://www.ohsu.edu/xd/health/services/dermatology/war-on-melanoma/mole-mapper.cfm',
                    'description': 'App to help track and document moles for early detection of changes'
                }
            ]
        }
    ]
    
    return render_template('education/resources.html', resource_categories=resource_categories)

# Helper functions
def get_all_conditions():
    """Get information about all skin conditions."""
    return [
        {
            'id': 'actinic-keratosis',
            'name': 'Actinic Keratosis',
            'image': 'conditions/actinic-keratosis.jpg',
            'description': 'Actinic keratoses are dry scaly patches of skin that have been damaged by the sun.',
            'severity': 'Moderate',
            'prevalence': 'Common',
            'related': ['squamous-cell-carcinoma', 'basal-cell-carcinoma']
        },
        {
            'id': 'basal-cell-carcinoma',
            'name': 'Basal Cell Carcinoma',
            'image': 'conditions/basal-cell-carcinoma.jpg',
            'description': 'Basal cell carcinoma is a type of skin cancer that begins in the basal cells — a type of cell within the skin that produces new skin cells as old ones die off.',
            'severity': 'High',
            'prevalence': 'Very common',
            'related': ['squamous-cell-carcinoma', 'actinic-keratosis']
        },
        {
            'id': 'dermatofibroma',
            'name': 'Dermatofibroma',
            'image': 'conditions/dermatofibroma.jpg',
            'description': 'Dermatofibromas are harmless growths within the skin that usually have a small diameter.',
            'severity': 'Low',
            'prevalence': 'Common',
            'related': ['nevus']
        },
        {
            'id': 'melanoma',
            'name': 'Melanoma',
            'image': 'conditions/melanoma.jpg',
            'description': 'Melanoma, the most serious type of skin cancer, develops in the cells that produce melanin — the pigment that gives your skin its color.',
            'severity': 'Very high',
            'prevalence': 'Less common',
            'related': ['nevus', 'basal-cell-carcinoma']
        },
        {
            'id': 'nevus',
            'name': 'Nevus',
            'image': 'conditions/nevus.jpg',
            'description': 'Nevus (plural: nevi) is the medical term for a mole. Nevi are very common. Most people have between 10 and 40.',
            'severity': 'Low',
            'prevalence': 'Very common',
            'related': ['melanoma', 'dermatofibroma']
        },
        {
            'id': 'pigmented-benign-keratosis',
            'name': 'Pigmented Benign Keratosis',
            'image': 'conditions/pigmented-benign-keratosis.jpg',
            'description': 'Pigmented benign keratosis refers to a group of non-cancerous skin growths that appear as thickened, wartlike lesions on the skin.',
            'severity': 'Low',
            'prevalence': 'Common',
            'related': ['seborrheic-keratosis', 'actinic-keratosis']
        },
        {
            'id': 'seborrheic-keratosis',
            'name': 'Seborrheic Keratosis',
            'image': 'conditions/seborrheic-keratosis.jpg',
            'description': 'A seborrheic keratosis is a common noncancerous skin growth. People tend to get more of them as they get older.',
            'severity': 'Low',
            'prevalence': 'Very common',
            'related': ['pigmented-benign-keratosis']
        },
        {
            'id': 'squamous-cell-carcinoma',
            'name': 'Squamous Cell Carcinoma',
            'image': 'conditions/squamous-cell-carcinoma.jpg',
            'description': 'Squamous cell carcinoma of the skin is a common form of skin cancer that develops in the squamous cells that make up the middle and outer layers of the skin.',
            'severity': 'High',
            'prevalence': 'Common',
            'related': ['basal-cell-carcinoma', 'actinic-keratosis']
        },
        {
            'id': 'vascular-lesion',
            'name': 'Vascular Lesion',
            'image': 'conditions/vascular-lesion.jpg',
            'description': 'Vascular lesions are relatively common abnormalities of the skin and underlying tissues, more commonly known as birthmarks.',
            'severity': 'Varies',
            'prevalence': 'Less common',
            'related': []
        }
    ]

def get_condition_by_id(condition_id):
    """Get detailed information about a specific condition by ID."""
    all_conditions = get_all_conditions()
    
    # Find the condition by ID
    for condition in all_conditions:
        if condition['id'] == condition_id:
            # Add additional detailed information
            if condition_id == 'actinic-keratosis':
                condition['detailed_description'] = """
                Actinic keratoses (also called solar keratoses) are dry scaly patches of skin that have been damaged by the sun.
                The patches are not usually serious. But there's a small chance they could become skin cancer, so it's important to avoid further damage to your skin.
                """
                condition['treatments'] = [
                    'Prescription creams and gels',
                    'Freezing the patches (cryotherapy)',
                    'Surgery to cut out or scrape away the patches',
                    'Photodynamic therapy (PDT)'
                ]
            elif condition_id == 'melanoma':
                condition['detailed_description'] = """
                Melanoma, the most serious type of skin cancer, develops in the cells (melanocytes) that produce melanin — the pigment that gives your skin its color.
                Melanoma can also form in your eyes and, rarely, inside your body, such as in your nose or throat. The exact cause of all melanomas isn't clear,
                but exposure to ultraviolet (UV) radiation from sunlight or tanning lamps and beds increases your risk of developing melanoma.
                """
                condition['warning_signs'] = [
                    'A change in an existing mole',
                    'The development of a new pigmented or unusual-looking growth on your skin'
                ]
                condition['hidden_melanomas'] = [
                    'Melanoma under a nail',
                    'Melanoma in the mouth, digestive tract, urinary tract or vagina',
                    'Melanoma in the eye'
                ]
            # Add more condition-specific information for other conditions...
            
            return condition
    
    # Return None if condition not found
    return None

def get_related_conditions(condition_id):
    """Get related conditions for a specific condition."""
    # Get all conditions
    all_conditions = get_all_conditions()
    
    # Find the condition by ID
    current_condition = None
    for condition in all_conditions:
        if condition['id'] == condition_id:
            current_condition = condition
            break
    
    if not current_condition:
        return []
    
    # Get related conditions
    related_ids = current_condition.get('related', [])
    related_conditions = []
    
    for related_id in related_ids:
        for condition in all_conditions:
            if condition['id'] == related_id:
                related_conditions.append(condition)
                break
    
    return related_conditions