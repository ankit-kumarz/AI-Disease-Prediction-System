"""
Personalized Health Recommendation Engine

Generates evidence-based, personalized health recommendations based on:
- Disease type
- Risk level
- Dominant contributing features
- Patient demographics (if available)
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger('predictor')


def generate_recommendations(
    disease: str,
    risk_level: str,
    top_features: List[Dict],
    feature_values: Dict[str, Any],
    patient_profile: Any = None
) -> Dict[str, List[str]]:
    """
    Generate comprehensive personalized health recommendations.
    
    Args:
        disease: Disease type (diabetes, heart, breast)
        risk_level: Risk stratification level (LOW, MEDIUM, HIGH)
        top_features: List of top contributing features
        feature_values: Dictionary of all feature values
        patient_profile: PatientProfile object (optional)
        
    Returns:
        Dictionary with categorized recommendations:
        - lifestyle: Lifestyle modifications
        - diet: Dietary recommendations
        - medical: Medical follow-up actions
        - monitoring: Metrics to monitor
    """
    logger.info(f"Generating recommendations for {disease} at {risk_level} risk")
    
    recommendations = {
        'lifestyle': [],
        'diet': [],
        'medical': [],
        'monitoring': []
    }
    
    if disease == 'diabetes':
        recommendations = generate_diabetes_recommendations(
            risk_level, top_features, feature_values, patient_profile
        )
    elif disease == 'heart':
        recommendations = generate_heart_recommendations(
            risk_level, top_features, feature_values, patient_profile
        )
    elif disease == 'breast':
        recommendations = generate_breast_recommendations(
            risk_level, top_features, feature_values, patient_profile
        )
    
    # Add general recommendations based on risk level
    add_risk_based_recommendations(recommendations, risk_level, disease)
    
    return recommendations


def generate_diabetes_recommendations(
    risk_level: str,
    top_features: List[Dict],
    feature_values: Dict[str, Any],
    patient_profile: Any
) -> Dict[str, List[str]]:
    """Generate diabetes-specific recommendations"""
    recommendations = {
        'lifestyle': [],
        'diet': [],
        'medical': [],
        'monitoring': []
    }
    
    glucose = feature_values.get('Glucose', 0)
    bmi = feature_values.get('BMI', 0)
    age = feature_values.get('Age', 0)
    
    # Lifestyle recommendations
    if bmi > 25:
        recommendations['lifestyle'].append(
            f'Weight management is crucial. Your BMI ({bmi:.1f}) indicates overweight/obesity. '
            'Aim for 5-10% weight loss through diet and exercise.'
        )
    
    recommendations['lifestyle'].extend([
        'Engage in at least 150 minutes of moderate aerobic activity per week (brisk walking, cycling, swimming)',
        'Include resistance training 2-3 times per week to improve insulin sensitivity',
        'Maintain 7-9 hours of quality sleep per night',
        'Practice stress management techniques (meditation, yoga, deep breathing)',
    ])
    
    # Diet recommendations
    if glucose > 100:
        recommendations['diet'].append(
            f'Your glucose level ({glucose} mg/dL) is elevated. Focus on blood sugar control through diet.'
        )
    
    recommendations['diet'].extend([
        'Follow a low glycemic index (GI) diet: whole grains, legumes, non-starchy vegetables',
        'Avoid refined carbohydrates: white bread, sugary drinks, pastries, candy',
        'Include healthy fats: avocados, nuts, olive oil, fatty fish',
        'Practice portion control and eat smaller, frequent meals',
        'Stay hydrated with water; limit fruit juices and sodas',
        'Increase fiber intake to 25-30g daily through vegetables, fruits, and whole grains',
    ])
    
    # Medical follow-up
    if risk_level == 'HIGH':
        recommendations['medical'].append(
            'URGENT: Schedule immediate appointment with endocrinologist or primary care physician'
        )
    
    recommendations['medical'].extend([
        'Annual comprehensive diabetes screening (HbA1c, fasting glucose)',
        'Annual eye examination to screen for diabetic retinopathy',
        'Regular foot examinations to prevent diabetic neuropathy',
        'Blood pressure monitoring (target <140/90 mmHg)',
        'Discuss metformin or other preventive medications with your doctor',
    ])
    
    if age > 45:
        recommendations['medical'].append(
            f'Age {age} increases diabetes risk. Consider more frequent screening.'
        )
    
    # Monitoring recommendations
    recommendations['monitoring'].extend([
        'Track fasting blood glucose weekly (target: 70-100 mg/dL)',
        'Monitor HbA1c every 3-6 months (target: <5.7% for prevention)',
        'Weekly weight monitoring and BMI calculation',
        'Use diabetes tracking app to log meals, exercise, and glucose levels',
        'Home blood pressure monitoring if hypertensive',
    ])
    
    return recommendations


def generate_heart_recommendations(
    risk_level: str,
    top_features: List[Dict],
    feature_values: Dict[str, Any],
    patient_profile: Any
) -> Dict[str, List[str]]:
    """Generate heart disease-specific recommendations"""
    recommendations = {
        'lifestyle': [],
        'diet': [],
        'medical': [],
        'monitoring': []
    }
    
    chol = feature_values.get('chol', 0)
    trestbps = feature_values.get('trestbps', 0)
    age = feature_values.get('age', 0)
    exang = feature_values.get('exang', 0)
    
    # Lifestyle recommendations
    recommendations['lifestyle'].extend([
        'Aerobic exercise 150 minutes/week: walking, jogging, swimming, cycling',
        'Strength training 2 days/week to improve cardiovascular health',
        'Quit smoking immediately - single most important intervention for heart health',
        'Limit alcohol: ≤1 drink/day (women), ≤2 drinks/day (men)',
        'Prioritize 7-8 hours of quality sleep nightly',
        'Stress reduction: yoga, meditation, mindfulness practices',
    ])
    
    if exang == 1:
        recommendations['lifestyle'].append(
            'Exercise-induced angina detected. Consult cardiologist before starting exercise program.'
        )
    
    # Diet recommendations
    if chol > 200:
        recommendations['diet'].append(
            f'Cholesterol level ({chol} mg/dL) is elevated. Focus on heart-healthy diet.'
        )
    
    recommendations['diet'].extend([
        'Eat fatty fish 2-3x/week (salmon, mackerel, sardines) - rich in omega-3',
        'Mediterranean diet: olive oil, nuts, vegetables, whole grains, legumes',
        'Limit saturated fats: red meat, butter, full-fat dairy, fried foods',
        'Reduce sodium intake to <2,300 mg/day (ideally <1,500 mg)',
        'Increase fruits and vegetables to 5-9 servings daily',
        'Choose whole grains over refined grains',
        'Include nuts, seeds, and plant-based proteins',
    ])
    
    if trestbps > 130:
        recommendations['diet'].append(
            f'Blood pressure ({trestbps} mmHg) elevated. Follow DASH diet principles.'
        )
    
    # Medical follow-up
    if risk_level == 'HIGH':
        recommendations['medical'].append(
            'URGENT: Immediate cardiology consultation required'
        )
    
    recommendations['medical'].extend([
        'Discuss statin therapy if cholesterol >200 mg/dL',
        'Annual lipid panel (total cholesterol, LDL, HDL, triglycerides)',
        'Resting ECG and stress test as recommended by cardiologist',
        'Consider echocardiogram to assess heart function',
        'Annual flu vaccine - important for heart disease prevention',
        'Low-dose aspirin therapy (81mg) - discuss with doctor',
    ])
    
    if age > 55:
        recommendations['medical'].append(
            f'Age {age} significantly increases cardiovascular risk. Intensify preventive measures.'
        )
    
    # Monitoring recommendations
    recommendations['monitoring'].extend([
        'Daily blood pressure monitoring (target: <120/80 mmHg)',
        'Cholesterol check every 3-6 months until stabilized',
        'Weekly weight monitoring',
        'Track resting heart rate (target: 60-100 bpm)',
        'Use heart health tracking app for symptoms and metrics',
        'Monitor for warning signs: chest pain, shortness of breath, palpitations',
    ])
    
    return recommendations


def generate_breast_recommendations(
    risk_level: str,
    top_features: List[Dict],
    feature_values: Dict[str, Any],
    patient_profile: Any
) -> Dict[str, List[str]]:
    """Generate breast cancer-specific recommendations"""
    recommendations = {
        'lifestyle': [],
        'diet': [],
        'medical': [],
        'monitoring': []
    }
    
    # Lifestyle recommendations
    recommendations['lifestyle'].extend([
        'Regular physical activity: 150-300 min/week moderate intensity exercise',
        'Maintain healthy weight (BMI 18.5-24.9) - obesity increases risk',
        'Limit alcohol to ≤1 drink per day or avoid completely',
        'Avoid tobacco in all forms',
        'Maintain healthy sleep patterns (7-9 hours)',
        'Consider breastfeeding (if planning children) - protective effect',
    ])
    
    # Diet recommendations
    recommendations['diet'].extend([
        'Plant-based diet rich in fruits, vegetables, whole grains, legumes',
        'Include healthy fats: olive oil, avocados, nuts, omega-3 fatty fish',
        'Limit red meat and processed meats',
        'Choose low-fat dairy options',
        'Cruciferous vegetables: broccoli, cauliflower, Brussels sprouts (cancer-protective)',
        'Antioxidant-rich berries: blueberries, strawberries, raspberries',
        'Green tea consumption (contains protective polyphenols)',
    ])
    
    # Medical follow-up
    if risk_level == 'HIGH':
        recommendations['medical'].append(
            'URGENT: Immediate consultation with breast specialist/oncologist required'
        )
        recommendations['medical'].append(
            'Discuss genetic testing (BRCA1/BRCA2) with healthcare provider'
        )
    
    recommendations['medical'].extend([
        'Annual mammogram screening (age 40+, or earlier if high risk)',
        'Clinical breast exam every 1-3 years (age 25-39), annually (40+)',
        'Consider additional imaging: breast ultrasound or MRI if dense breasts',
        'Discuss chemoprevention options (tamoxifen, raloxifene) if high risk',
        'Consider consultation with genetic counselor if family history present',
    ])
    
    if risk_level in ['MEDIUM', 'HIGH']:
        recommendations['medical'].extend([
            'Referral to high-risk breast cancer clinic',
            'Comprehensive risk assessment using Gail Model or Tyrer-Cuzick model',
        ])
    
    # Monitoring recommendations
    recommendations['monitoring'].extend([
        'Monthly breast self-examination (one week after period)',
        'Keep diary of breast changes, lumps, or abnormalities',
        'Be aware of warning signs: lump, skin changes, nipple discharge, pain',
        'Use breast health tracking app',
        'Visual inspection for asymmetry, skin dimpling, or nipple changes',
        'Report any changes immediately to healthcare provider',
    ])
    
    return recommendations


def add_risk_based_recommendations(
    recommendations: Dict[str, List[str]],
    risk_level: str,
    disease: str
) -> None:
    """Add general recommendations based on risk level"""
    
    if risk_level == 'HIGH':
        recommendations['medical'].insert(0,
            'HIGH RISK ALERT: Immediate medical consultation is strongly recommended. '
            'Do not delay seeking professional medical advice.'
        )
        recommendations['monitoring'].insert(0,
            'Frequent monitoring required. Follow healthcare provider instructions closely.'
        )
    
    elif risk_level == 'MEDIUM':
        recommendations['medical'].insert(0,
            'Moderate risk detected. Schedule consultation with healthcare provider '
            'within 1-2 weeks to discuss preventive strategies.'
        )
    
    else:  # LOW
        recommendations['medical'].append(
            'Continue routine health screenings as per age-appropriate guidelines.'
        )
        recommendations['monitoring'].append(
            'Maintain current healthy habits and monitor key health metrics annually.'
        )


def format_recommendations_for_display(recommendations: Dict[str, List[str]]) -> str:
    """Format recommendations as HTML for display"""
    html = '<div class="recommendations-container">'
    
    categories = {
        'lifestyle': ('Lifestyle Modifications', 'primary'),
        'diet': ('Dietary Recommendations', 'success'),
        'medical': ('Medical Follow-Up', 'danger'),
        'monitoring': ('Health Monitoring', 'info')
    }
    
    for key, (title, color) in categories.items():
        if recommendations[key]:
            html += f'<div class="card mb-3 border-{color}">'
            html += f'<div class="card-header bg-{color} text-white"><strong>{title}</strong></div>'
            html += '<ul class="list-group list-group-flush">'
            
            for rec in recommendations[key]:
                html += f'<li class="list-group-item">{rec}</li>'
            
            html += '</ul></div>'
    
    html += '</div>'
    return html
