"""
Model Loader and Preprocessing Utilities

This module handles:
- Loading pre-trained .pkl models from disk (cached at module level)
- Preprocessing raw form inputs into the exact feature format expected by each model
- Feature ordering and validation

Expected input keys for each disease:

DIABETES:
  - Pregnancies: int
  - Glucose: float
  - BloodPressure: float
  - SkinThickness: float
  - Insulin: float
  - BMI: float
  - DiabetesPedigreeFunction: float
  - Age: int

HEART:
  - age: int
  - sex: int (1=male, 0=female)
  - cp: int (chest pain type 0-3)
  - trestbps: float (resting blood pressure)
  - chol: float (serum cholesterol)
  - fbs: int (fasting blood sugar > 120 mg/dl, 1=true, 0=false)
  - restecg: int (resting ECG results 0-2)
  - thalach: float (max heart rate achieved)
  - exang: int (exercise induced angina, 1=yes, 0=no)
  - oldpeak: float (ST depression)
  - slope: int (slope of peak exercise ST segment 0-2)
  - ca: int (number of major vessels colored by fluoroscopy 0-4)
  - thal: int (thalassemia 0-3)

BREAST:
  - radius_mean: float
  - texture_mean: float
  - perimeter_mean: float
  - area_mean: float
  - smoothness_mean: float
  - compactness_mean: float
  - concavity_mean: float
  - concave_points_mean: float
  - symmetry_mean: float
  - fractal_dimension_mean: float
  - radius_se: float
  - texture_se: float
  - perimeter_se: float
  - area_se: float
  - smoothness_se: float
  - compactness_se: float
  - concavity_se: float
  - concave_points_se: float
  - symmetry_se: float
  - fractal_dimension_se: float
  - radius_worst: float
  - texture_worst: float
  - perimeter_worst: float
  - area_worst: float
  - smoothness_worst: float
  - compactness_worst: float
  - concavity_worst: float
  - concave_points_worst: float
  - symmetry_worst: float
  - fractal_dimension_worst: float
"""

import os
import joblib
import numpy as np
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger('predictor')

# Module-level cache for loaded models
_MODELS_CACHE = {}

# Feature order mapping - MUST match training data column order
FEATURE_ORDER = {
    'diabetes': [
        'Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
        'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age'
    ],
    'heart': [
        'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg',
        'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal'
    ],
    'breast': [
        'mean radius', 'mean texture', 'mean perimeter', 'mean area',
        'mean smoothness', 'mean compactness', 'mean concavity',
        'mean concave points', 'mean symmetry', 'mean fractal dimension',
        'radius error', 'texture error', 'perimeter error', 'area error',
        'smoothness error', 'compactness error', 'concavity error',
        'concave points error', 'symmetry error', 'fractal dimension error',
        'worst radius', 'worst texture', 'worst perimeter', 'worst area',
        'worst smoothness', 'worst compactness', 'worst concavity',
        'worst concave points', 'worst symmetry', 'worst fractal dimension'
    ]
}

# Mapping from form field names to model feature names for breast cancer
BREAST_FEATURE_MAPPING = {
    'radius_mean': 'mean radius',
    'texture_mean': 'mean texture',
    'perimeter_mean': 'mean perimeter',
    'area_mean': 'mean area',
    'smoothness_mean': 'mean smoothness',
    'compactness_mean': 'mean compactness',
    'concavity_mean': 'mean concavity',
    'concave_points_mean': 'mean concave points',
    'symmetry_mean': 'mean symmetry',
    'fractal_dimension_mean': 'mean fractal dimension',
    'radius_se': 'radius error',
    'texture_se': 'texture error',
    'perimeter_se': 'perimeter error',
    'area_se': 'area error',
    'smoothness_se': 'smoothness error',
    'compactness_se': 'compactness error',
    'concavity_se': 'concavity error',
    'concave_points_se': 'concave points error',
    'symmetry_se': 'symmetry error',
    'fractal_dimension_se': 'fractal dimension error',
    'radius_worst': 'worst radius',
    'texture_worst': 'worst texture',
    'perimeter_worst': 'worst perimeter',
    'area_worst': 'worst area',
    'smoothness_worst': 'worst smoothness',
    'compactness_worst': 'worst compactness',
    'concavity_worst': 'worst concavity',
    'concave_points_worst': 'worst concave points',
    'symmetry_worst': 'worst symmetry',
    'fractal_dimension_worst': 'worst fractal dimension'
}


def load_models(base_dir: Path = None) -> Dict[str, Any]:
    """
    Load all three pre-trained models from the models/ directory.
    
    Models are cached at module level to avoid repeated disk I/O.
    
    Args:
        base_dir: Base directory of the Django project (default: auto-detect)
        
    Returns:
        Dictionary with keys 'diabetes', 'heart', 'breast' mapping to loaded model objects
        
    Raises:
        FileNotFoundError: If model files are missing
        Exception: If model loading fails
    """
    global _MODELS_CACHE
    
    if _MODELS_CACHE:
        logger.info("Returning cached models")
        return _MODELS_CACHE
    
    if base_dir is None:
        # Auto-detect: navigate up from this file to project root
        base_dir = Path(__file__).resolve().parent.parent.parent
    
    models_dir = base_dir / 'Model'
    logger.info(f"Loading models from: {models_dir}")
    
    model_files = {
        'diabetes': models_dir / 'diabetes_model.pkl',
        'heart': models_dir / 'heart_model.pkl',
        'breast': models_dir / 'breast_model.pkl',
    }
    
    for name, path in model_files.items():
        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")
        
        try:
            logger.info(f"Loading {name} model from {path}")
            _MODELS_CACHE[name] = joblib.load(path)
            logger.info(f"Successfully loaded {name} model")
        except Exception as e:
            logger.error(f"Failed to load {name} model: {e}", exc_info=True)
            raise Exception(f"Error loading {name} model: {str(e)}")
    
    return _MODELS_CACHE


def get_model(name: str):
    """
    Retrieve a loaded model by name.
    
    Args:
        name: Model name ('diabetes', 'heart', or 'breast')
        
    Returns:
        Loaded sklearn model/pipeline
        
    Raises:
        ValueError: If model name is invalid
        RuntimeError: If models haven't been loaded yet
    """
    if not _MODELS_CACHE:
        load_models()
    
    if name not in _MODELS_CACHE:
        raise ValueError(f"Invalid model name: {name}. Must be one of: {list(_MODELS_CACHE.keys())}")
    
    return _MODELS_CACHE[name]


def preprocess_inputs(data: Dict[str, Any], model_name: str) -> np.ndarray:
    """
    Convert raw form inputs into a 2D numpy array suitable for model prediction.
    
    This function:
    1. Maps form field names to model feature names (for breast cancer)
    2. Validates all required features are present
    3. Orders features according to FEATURE_ORDER mapping
    4. Converts values to appropriate numeric types
    5. Handles missing values (uses 0 for missing numeric values as fallback)
    6. Returns shaped array (1, n_features)
    
    Args:
        data: Dictionary of input features (keys from Django forms)
        model_name: Name of the model ('diabetes', 'heart', 'breast')
        
    Returns:
        2D numpy array of shape (1, n_features) ready for model.predict()
        
    Raises:
        ValueError: If required features are missing or model_name is invalid
    """
    if model_name not in FEATURE_ORDER:
        raise ValueError(f"Invalid model name: {model_name}. Must be one of: {list(FEATURE_ORDER.keys())}")
    
    # For breast cancer, map form field names to model feature names
    if model_name == 'breast':
        mapped_data = {}
        for form_key, form_value in data.items():
            model_key = BREAST_FEATURE_MAPPING.get(form_key, form_key)
            mapped_data[model_key] = form_value
        data = mapped_data
    
    expected_features = FEATURE_ORDER[model_name]
    
    # Validate all required features are present
    missing_features = [f for f in expected_features if f not in data]
    if missing_features:
        raise ValueError(
            f"Missing required features for {model_name}: {missing_features}. "
            f"Expected features: {expected_features}"
        )
    
    # Extract and order features
    feature_values = []
    for feature_name in expected_features:
        value = data[feature_name]
        
        # Convert to numeric, handling strings and empty values
        if value == '' or value is None:
            numeric_value = 0.0  # Fallback for missing values
            logger.warning(f"Missing value for {feature_name}, using 0.0")
        else:
            try:
                numeric_value = float(value)
            except (ValueError, TypeError) as e:
                logger.error(f"Invalid value for {feature_name}: {value}")
                raise ValueError(f"Feature '{feature_name}' must be numeric, got: {value}")
        
        feature_values.append(numeric_value)
    
    # Convert to 2D numpy array (1 sample, n features)
    input_array = np.array([feature_values], dtype=np.float64)
    
    logger.debug(f"Preprocessed {model_name} inputs: shape={input_array.shape}")
    return input_array
