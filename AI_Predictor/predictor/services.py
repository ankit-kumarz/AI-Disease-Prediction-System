"""
Prediction Business Logic and Service Layer

This module contains the core prediction logic that:
- Accepts raw inputs
- Preprocesses them using utils.preprocess_inputs
- Runs model inference with XAI explanations
- Calculates risk stratification
- Generates personalized recommendations
- Persists results to database with audit logging
- Returns structured JSON responses
"""

import logging
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime
from django.utils import timezone

from .utils import get_model, preprocess_inputs, FEATURE_ORDER
from .models import PredictionRecord, AuditLog
from .explainability import explain_prediction
from .risk_stratification import calculate_risk_level, get_risk_description
from .recommendations import generate_recommendations

logger = logging.getLogger('predictor')

# Class label mappings for each disease
# Maps class indices (0, 1) to human-readable labels
CLASS_LABELS = {
    'diabetes': {
        0: 'Non-Diabetic',
        1: 'Diabetic'
    },
    'heart': {
        0: 'No Heart Disease',
        1: 'Heart Disease Present'
    },
    'breast': {
        0: 'Benign',
        1: 'Malignant'
    }
}


def predict_disease(
    model_name: str,
    raw_inputs: Dict[str, Any],
    user=None,
    request=None
) -> Dict[str, Any]:
    """
    Perform disease prediction with full explainability and recommendations.
    
    This function:
    1. Preprocesses inputs
    2. Loads the appropriate model
    3. Runs prediction and probability estimation
    4. Generates AI explanations (feature importance)
    5. Calculates risk stratification
    6. Generates personalized recommendations
    7. Saves prediction to database with all metadata
    8. Creates audit log entry
    9. Returns comprehensive JSON response
    
    Args:
        model_name: Name of disease model ('diabetes', 'heart', 'breast')
        raw_inputs: Dictionary of input features
        user: Django User object (optional)
        request: HTTP request object for IP/user-agent logging (optional)
        
    Returns:
        Dictionary containing:
        - disease: str (model name)
        - prediction_label: str (human-readable prediction)
        - probability: float (confidence for predicted class, 0-1)
        - probabilities: dict (all class probabilities with labels)
        - risk_level: str (LOW, MEDIUM, HIGH)
        - risk_description: dict (detailed risk interpretation)
        - feature_importance: dict (XAI feature importance scores)
        - top_features: list (top 5 contributing features)
        - explanations: list (human-readable feature explanations)
        - risk_factors: list (identified risk factors)
        - recommendations: dict (categorized health recommendations)
        - record_id: int (database record ID)
        - created_at: str (ISO timestamp)
        
    Raises:
        ValueError: If inputs are invalid or model_name is unknown
        Exception: If model prediction fails
    """
    logger.info(f"Starting enhanced prediction for {model_name}")
    
    try:
        # Step 1: Preprocess inputs
        input_array = preprocess_inputs(raw_inputs, model_name)
        logger.debug(f"Preprocessed input array shape: {input_array.shape}")
        
        # Step 2: Load model
        model = get_model(model_name)
        
        # Step 3: Run prediction
        prediction = model.predict(input_array)
        predicted_class = int(prediction[0])
        logger.info(f"Raw prediction: {predicted_class}")
        
        # Step 4: Get probability estimates
        raw_scores = None
        probability = None
        probabilities_dict = {}
        
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(input_array)
            raw_scores = proba[0].tolist()
            probability = float(proba[0][predicted_class])
            
            # Map probabilities to human labels
            class_labels = CLASS_LABELS.get(model_name, {})
            for class_idx, prob in enumerate(proba[0]):
                label = class_labels.get(class_idx, f"Class {class_idx}")
                probabilities_dict[label] = float(prob)
            
            logger.debug(f"Probabilities: {probabilities_dict}")
        else:
            # Fallback if predict_proba not available
            probability = 1.0
            raw_scores = [1.0]
            probabilities_dict = {CLASS_LABELS[model_name][predicted_class]: 1.0}
        
        # Step 5: Map prediction to human label
        prediction_label = CLASS_LABELS.get(model_name, {}).get(
            predicted_class, 
            f"Unknown Class {predicted_class}"
        )
        
        # Step 6: Generate AI Explanations
        feature_names = FEATURE_ORDER[model_name]
        explanation_data = explain_prediction(
            model=model,
            input_array=input_array,
            feature_names=feature_names,
            feature_values=raw_inputs,
            disease=model_name
        )
        
        # Step 7: Calculate risk stratification
        risk_level = calculate_risk_level(model_name, probability)
        risk_description = get_risk_description(model_name, risk_level, probability)
        logger.info(f"Risk level: {risk_level}")
        
        # Step 8: Generate personalized recommendations
        patient_profile = None
        if user and hasattr(user, 'patient_profile'):
            patient_profile = user.patient_profile
        
        recommendations = generate_recommendations(
            disease=model_name,
            risk_level=risk_level,
            top_features=explanation_data.get('top_features', []),
            feature_values=raw_inputs,
            patient_profile=patient_profile
        )
        
        # Step 9: Persist to database with all advanced features
        record = PredictionRecord.objects.create(
            user=user,
            disease=model_name,
            inputs=raw_inputs,
            prediction_label=prediction_label,
            probability=probability,
            probabilities=probabilities_dict,
            risk_level=risk_level,
            feature_importance=explanation_data.get('feature_importance', {}),
            top_features=explanation_data.get('top_features', []),
            risk_factors=explanation_data.get('risk_factors', []),
            recommendations=recommendations
        )
        
        logger.info(f"Saved enhanced prediction record ID: {record.id}")
        
        # Step 10: Create audit log entry
        if user:
            create_audit_log(
                user=user,
                action_type='PREDICTION',
                description=f"Prediction made for {model_name}: {prediction_label} ({risk_level} risk)",
                request=request,
                metadata={
                    'disease': model_name,
                    'prediction': prediction_label,
                    'risk_level': risk_level,
                    'probability': probability,
                    'record_id': record.id
                }
            )
        
        # Step 11: Build comprehensive response
        response = {
            'disease': model_name,
            'prediction_label': prediction_label,
            'probability': round(probability, 4),
            'probabilities': probabilities_dict,
            'risk_level': risk_level,
            'risk_description': risk_description,
            'feature_importance': explanation_data.get('feature_importance', {}),
            'top_features': explanation_data.get('top_features', []),
            'explanations': explanation_data.get('explanations', []),
            'risk_factors': explanation_data.get('risk_factors', []),
            'recommendations': recommendations,
            'record_id': record.id,
            'created_at': record.created_at.isoformat(),
        }
        
        return response
        
    except ValueError as e:
        logger.error(f"Validation error in predict_disease: {e}")
        raise
    except Exception as e:
        logger.error(f"Prediction failed for {model_name}: {e}", exc_info=True)
        raise Exception(f"Prediction failed: {str(e)}")


def create_audit_log(
    user,
    action_type: str,
    description: str,
    request=None,
    metadata: Optional[Dict] = None
) -> None:
    """
    Create an audit log entry for security and compliance.
    
    Args:
        user: Django User object
        action_type: Type of action (from AuditLog.ACTION_TYPES)
        description: Human-readable description
        request: HTTP request object (optional)
        metadata: Additional JSON metadata (optional)
    """
    try:
        ip_address = None
        user_agent = None
        
        if request:
            # Get IP address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            
            # Get user agent
            user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        AuditLog.objects.create(
            user=user,
            action_type=action_type,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {}
        )
        
        logger.debug(f"Audit log created: {action_type} by {user.username if user else 'System'}")
    
    except Exception as e:
        logger.error(f"Failed to create audit log: {e}", exc_info=True)
        # Don't raise - audit logging failure shouldn't break main flow

