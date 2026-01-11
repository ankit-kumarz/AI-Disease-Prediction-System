"""
Risk Stratification Service

Converts prediction probabilities into clinically meaningful risk levels:
- LOW: Low probability of disease
- MEDIUM: Moderate risk, monitoring recommended
- HIGH: High risk, immediate medical consultation recommended
"""

import logging
from typing import Dict, Tuple

logger = logging.getLogger('predictor')

# Risk thresholds by disease
RISK_THRESHOLDS = {
    'diabetes': {
        'LOW': (0.0, 0.30),      # 0-30% probability = Low Risk
        'MEDIUM': (0.30, 0.60),  # 30-60% = Medium Risk
        'HIGH': (0.60, 1.0),     # 60-100% = High Risk
    },
    'heart': {
        'LOW': (0.0, 0.35),
        'MEDIUM': (0.35, 0.65),
        'HIGH': (0.65, 1.0),
    },
    'breast': {
        'LOW': (0.0, 0.40),
        'MEDIUM': (0.40, 0.70),
        'HIGH': (0.70, 1.0),
    },
}


def calculate_risk_level(disease: str, probability: float) -> str:
    """
    Calculate risk stratification level based on disease type and probability.
    
    Args:
        disease: Disease type (diabetes, heart, breast)
        probability: Prediction probability (0.0 to 1.0)
        
    Returns:
        Risk level: 'LOW', 'MEDIUM', or 'HIGH'
    """
    thresholds = RISK_THRESHOLDS.get(disease, RISK_THRESHOLDS['diabetes'])
    
    if thresholds['LOW'][0] <= probability < thresholds['LOW'][1]:
        return 'LOW'
    elif thresholds['MEDIUM'][0] <= probability < thresholds['MEDIUM'][1]:
        return 'MEDIUM'
    else:
        return 'HIGH'


def get_risk_description(disease: str, risk_level: str, probability: float) -> Dict[str, str]:
    """
    Get detailed risk description and clinical interpretation.
    
    Args:
        disease: Disease type
        risk_level: Risk stratification level
        probability: Prediction probability
        
    Returns:
        Dictionary with title, description, and action items
    """
    disease_name = {
        'diabetes': 'Type 2 Diabetes',
        'heart': 'Heart Disease',
        'breast': 'Breast Cancer'
    }.get(disease, disease.title())
    
    prob_percent = round(probability * 100, 1)
    
    if risk_level == 'LOW':
        return {
            'title': f'Low Risk of {disease_name}',
            'description': f'Based on the provided health parameters, your risk of {disease_name.lower()} is low ({prob_percent}%). The predictive model indicates that your current health markers are within acceptable ranges.',
            'action': '✓ Continue maintaining healthy lifestyle habits\n✓ Schedule routine check-ups as recommended\n✓ Monitor key health metrics regularly',
            'color': 'success',
            'icon': 'check-circle'
        }
    
    elif risk_level == 'MEDIUM':
        return {
            'title': f'Moderate Risk of {disease_name}',
            'description': f'The analysis indicates a moderate risk ({prob_percent}%) for {disease_name.lower()}. Some health parameters may benefit from lifestyle modifications or medical attention.',
            'action': '⚠️ Schedule a consultation with your healthcare provider\n⚠️ Discuss preventive measures and lifestyle changes\n⚠️ Consider additional diagnostic tests\n⚠️ Monitor symptoms closely',
            'color': 'warning',
            'icon': 'exclamation-triangle'
        }
    
    else:  # HIGH
        return {
            'title': f'High Risk of {disease_name}',
            'description': f'The predictive analysis shows a high risk ({prob_percent}%) for {disease_name.lower()}. Multiple health parameters indicate significant concern requiring immediate medical evaluation.',
            'action': '🚨 URGENT: Consult a healthcare professional immediately\n🚨 Bring this report to your doctor\n🚨 Do not delay seeking medical advice\n🚨 Follow all medical recommendations closely',
            'color': 'danger',
            'icon': 'exclamation-circle'
        }


def get_preventive_measures(disease: str, risk_level: str) -> list:
    """
    Get disease-specific preventive measures based on risk level.
    
    Args:
        disease: Disease type
        risk_level: Risk level
        
    Returns:
        List of preventive measure strings
    """
    measures = []
    
    if disease == 'diabetes':
        measures = [
            '🥗 Adopt a balanced diet low in refined sugars and carbohydrates',
            '🏃 Engage in regular physical activity (150 min/week minimum)',
            '⚖️ Maintain healthy body weight (BMI 18.5-24.9)',
            '🩺 Monitor blood glucose levels regularly',
            '💊 Take prescribed medications as directed',
        ]
        if risk_level == 'HIGH':
            measures.extend([
                '📅 Schedule HbA1c test every 3 months',
                '👨‍⚕️ Consult with endocrinologist',
                '🚭 Cease smoking immediately',
            ])
    
    elif disease == 'heart':
        measures = [
            '❤️ Follow a heart-healthy diet (Mediterranean or DASH diet)',
            '🚶 Exercise regularly: cardio and strength training',
            '🩺 Monitor blood pressure and cholesterol regularly',
            '🚭 Avoid tobacco and limit alcohol consumption',
            '😌 Manage stress through relaxation techniques',
        ]
        if risk_level == 'HIGH':
            measures.extend([
                '💊 Take prescribed cardiac medications consistently',
                '📊 Regular ECG and echocardiogram monitoring',
                '👨‍⚕️ Cardiology consultation recommended',
            ])
    
    elif disease == 'breast':
        measures = [
            '🩺 Perform monthly breast self-examinations',
            '📅 Schedule annual mammograms (age 40+)',
            '👨‍⚕️ Regular clinical breast exams',
            '🏃 Maintain healthy weight through exercise',
            '🍷 Limit alcohol consumption',
            '🤱 Consider breastfeeding (if applicable)',
        ]
        if risk_level in ['MEDIUM', 'HIGH']:
            measures.extend([
                '🧬 Discuss genetic testing with your doctor',
                '📊 Consider additional imaging (ultrasound/MRI)',
                '🏥 Consultation with breast specialist recommended',
            ])
    
    return measures
