"""
Explainable AI (XAI) Service for Medical Predictions

This module provides AI explainability features using:
- Feature importance from tree-based models
- SHAP values (optional, requires shap library)
- Human-readable explanations of predictions
"""

import logging
import numpy as np
from typing import Dict, List, Tuple, Any

logger = logging.getLogger('predictor')

# Feature importance thresholds
HIGH_IMPORTANCE = 0.1  # Features contributing >10% to prediction
MODERATE_IMPORTANCE = 0.05  # Features contributing 5-10%


def get_feature_importance(model, feature_names: List[str]) -> Dict[str, float]:
    """
    Extract feature importance from trained model.
    
    Args:
        model: Trained sklearn model
        feature_names: List of feature names in order
        
    Returns:
        Dictionary mapping feature names to importance scores
    """
    try:
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        elif hasattr(model, 'coef_'):
            importances = np.abs(model.coef_[0])
        else:
            logger.warning("Model does not support feature importance extraction")
            return {}
        
        # Normalize to sum to 1
        importances = importances / importances.sum()
        
        return dict(zip(feature_names, importances.tolist()))
    
    except Exception as e:
        logger.error(f"Error extracting feature importance: {e}")
        return {}


def explain_prediction(
    model,
    input_array: np.ndarray,
    feature_names: List[str],
    feature_values: Dict[str, Any],
    disease: str
) -> Dict[str, Any]:
    """
    Generate comprehensive explanation for a prediction.
    
    Args:
        model: Trained model
        input_array: Preprocessed input features (2D array)
        feature_names: List of feature names
        feature_values: Dictionary of raw feature values
        disease: Disease type (diabetes, heart, breast)
        
    Returns:
        Dictionary containing:
        - feature_importance: Dict of feature -> importance score
        - top_features: List of top 5 contributing features
        - explanations: Human-readable explanations
        - risk_factors: Identified risk factors
    """
    logger.info(f"Generating explanation for {disease} prediction")
    
    # Get feature importance
    importance_dict = get_feature_importance(model, feature_names)
    
    if not importance_dict:
        return {
            'feature_importance': {},
            'top_features': [],
            'explanations': [],
            'risk_factors': []
        }
    
    # Sort by importance
    sorted_features = sorted(
        importance_dict.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    # Get top 5 features
    top_features = [
        {
            'name': feature,
            'importance': round(importance * 100, 2),
            'value': feature_values.get(feature, 'N/A')
        }
        for feature, importance in sorted_features[:5]
    ]
    
    # Generate human-readable explanations
    explanations = generate_feature_explanations(
        top_features,
        disease,
        feature_values
    )
    
    # Identify risk factors
    risk_factors = identify_risk_factors(
        feature_values,
        disease
    )
    
    return {
        'feature_importance': importance_dict,
        'top_features': top_features,
        'explanations': explanations,
        'risk_factors': risk_factors
    }


def generate_feature_explanations(
    top_features: List[Dict],
    disease: str,
    feature_values: Dict[str, Any]
) -> List[str]:
    """
    Generate human-readable explanations for top contributing features.
    
    Args:
        top_features: List of top feature dictionaries
        disease: Disease type
        feature_values: Raw feature values
        
    Returns:
        List of explanation strings
    """
    explanations = []
    
    for feature in top_features:
        name = feature['name']
        value = feature['value']
        importance = feature['importance']
        
        explanation = f"**{name}** (importance: {importance}%): "
        
        # Disease-specific explanations
        if disease == 'diabetes':
            explanation += explain_diabetes_feature(name, value)
        elif disease == 'heart':
            explanation += explain_heart_feature(name, value)
        elif disease == 'breast':
            explanation += explain_breast_feature(name, value)
        
        explanations.append(explanation)
    
    return explanations


def explain_diabetes_feature(feature: str, value: Any) -> str:
    """Generate explanation for diabetes features."""
    explanations = {
        'Glucose': f"Blood glucose level of {value} mg/dL. Normal fasting glucose is <100 mg/dL.",
        'BMI': f"BMI of {value}. Normal BMI range is 18.5-24.9.",
        'Age': f"Age {value} years. Diabetes risk increases with age.",
        'Pregnancies': f"{value} pregnancies. Gestational diabetes history increases risk.",
        'DiabetesPedigreeFunction': f"Family history score: {value}. Higher values indicate stronger genetic predisposition.",
        'Insulin': f"Insulin level: {value} μU/mL. Abnormal levels may indicate insulin resistance.",
        'BloodPressure': f"Blood pressure: {value} mm Hg. High BP is a diabetes risk factor.",
        'SkinThickness': f"Skin thickness: {value} mm. May correlate with body fat percentage."
    }
    return explanations.get(feature, f"Value: {value}")


def explain_heart_feature(feature: str, value: Any) -> str:
    """Generate explanation for heart disease features."""
    explanations = {
        'age': f"Age {value} years. Heart disease risk increases significantly after 45 (men) or 55 (women).",
        'chol': f"Cholesterol: {value} mg/dL. Desirable level is <200 mg/dL.",
        'trestbps': f"Resting blood pressure: {value} mm Hg. Normal is <120/80 mm Hg.",
        'thalach': f"Maximum heart rate: {value} bpm. Lower max heart rate may indicate cardiovascular issues.",
        'oldpeak': f"ST depression: {value}. Indicates exercise-induced cardiac stress.",
        'ca': f"Number of major vessels: {value}. More vessels with blockage increases risk.",
        'cp': f"Chest pain type: {value}. Different types indicate varying risk levels.",
        'sex': "Gender: " + ("Male" if value == 1 else "Female") + ". Men have higher heart disease risk.",
        'exang': "Exercise-induced angina: " + ("Yes" if value == 1 else "No") + ".",
        'fbs': "Fasting blood sugar >120 mg/dL: " + ("Yes" if value == 1 else "No") + "."
    }
    return explanations.get(feature, f"Value: {value}")


def explain_breast_feature(feature: str, value: Any) -> str:
    """Generate explanation for breast cancer features."""
    if 'radius' in feature.lower():
        return f"Cell radius measurement: {value}. Larger cells may indicate malignancy."
    elif 'texture' in feature.lower():
        return f"Cell texture variation: {value}. Higher variation correlates with cancer."
    elif 'perimeter' in feature.lower():
        return f"Cell perimeter: {value}. Irregular perimeters suggest malignant cells."
    elif 'area' in feature.lower():
        return f"Cell area: {value}. Larger cell areas may indicate cancer."
    elif 'smoothness' in feature.lower():
        return f"Cell smoothness: {value}. Irregular surfaces suggest malignancy."
    elif 'compactness' in feature.lower():
        return f"Cell compactness: {value}. Higher values indicate irregular cell shape."
    elif 'concavity' in feature.lower():
        return f"Cell concavity: {value}. Indentations in cell boundary suggest cancer."
    elif 'symmetry' in feature.lower():
        return f"Cell symmetry: {value}. Asymmetric cells are more likely malignant."
    elif 'fractal' in feature.lower():
        return f"Fractal dimension: {value}. Measures complexity of cell boundary."
    else:
        return f"Cellular measurement: {value}"


def identify_risk_factors(feature_values: Dict[str, Any], disease: str) -> List[str]:
    """
    Identify specific risk factors based on feature values.
    
    Args:
        feature_values: Dictionary of feature values
        disease: Disease type
        
    Returns:
        List of identified risk factor messages
    """
    risk_factors = []
    
    if disease == 'diabetes':
        if feature_values.get('Glucose', 0) > 125:
            risk_factors.append("⚠️ Elevated glucose level (>125 mg/dL) indicates prediabetes or diabetes")
        if feature_values.get('BMI', 0) > 30:
            risk_factors.append("⚠️ Obesity (BMI >30) significantly increases diabetes risk")
        if feature_values.get('Age', 0) > 45:
            risk_factors.append("⚠️ Age >45 years increases diabetes risk")
        if feature_values.get('DiabetesPedigreeFunction', 0) > 0.5:
            risk_factors.append("⚠️ Strong family history of diabetes")
    
    elif disease == 'heart':
        if feature_values.get('chol', 0) > 240:
            risk_factors.append("⚠️ High cholesterol (>240 mg/dL) is a major risk factor")
        if feature_values.get('trestbps', 0) > 140:
            risk_factors.append("⚠️ High blood pressure (>140 mm Hg) indicates hypertension")
        if feature_values.get('age', 0) > 55:
            risk_factors.append("⚠️ Age >55 years significantly increases heart disease risk")
        if feature_values.get('exang', 0) == 1:
            risk_factors.append("⚠️ Exercise-induced angina is a concerning symptom")
        if feature_values.get('ca', 0) >= 2:
            risk_factors.append("⚠️ Multiple major vessels with blockage detected")
    
    elif disease == 'breast':
        # Breast cancer risk factors are based on cellular measurements
        # These are already reflected in the model's prediction
        risk_factors.append("ℹ️ Risk assessment based on cellular morphology analysis")
    
    if not risk_factors:
        risk_factors.append("✓ No major risk factors identified in the analyzed parameters")
    
    return risk_factors
