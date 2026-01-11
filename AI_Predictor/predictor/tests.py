"""
Unit tests for AI Disease Prediction System

Tests cover:
- Model loading
- Input preprocessing
- Prediction service
- API endpoints
"""

from django.test import TestCase, Client
from django.urls import reverse
import json
import numpy as np

from predictor.utils import preprocess_inputs, get_model, FEATURE_ORDER
from predictor.services import predict_disease
from predictor.models import PredictionRecord


class UtilsTestCase(TestCase):
    """Test utility functions for model loading and preprocessing"""
    
    def test_preprocess_diabetes_inputs(self):
        """Test preprocessing of diabetes inputs"""
        sample_input = {
            'Pregnancies': 2,
            'Glucose': 120,
            'BloodPressure': 70,
            'SkinThickness': 20,
            'Insulin': 80,
            'BMI': 25.5,
            'DiabetesPedigreeFunction': 0.5,
            'Age': 33
        }
        
        result = preprocess_inputs(sample_input, 'diabetes')
        
        # Check shape
        self.assertEqual(result.shape, (1, 8))
        
        # Check data type
        self.assertEqual(result.dtype, np.float64)
        
        # Check feature order
        expected_order = [2, 120, 70, 20, 80, 25.5, 0.5, 33]
        np.testing.assert_array_almost_equal(result[0], expected_order)
    
    def test_preprocess_heart_inputs(self):
        """Test preprocessing of heart disease inputs"""
        sample_input = {
            'age': 55,
            'sex': 1,
            'cp': 0,
            'trestbps': 120,
            'chol': 200,
            'fbs': 0,
            'restecg': 0,
            'thalach': 150,
            'exang': 0,
            'oldpeak': 1.0,
            'slope': 1,
            'ca': 0,
            'thal': 2
        }
        
        result = preprocess_inputs(sample_input, 'heart')
        
        # Check shape
        self.assertEqual(result.shape, (1, 13))
        
        # Check first value
        self.assertEqual(result[0][0], 55)
    
    def test_preprocess_missing_features(self):
        """Test that missing features raise ValueError"""
        incomplete_input = {
            'Pregnancies': 2,
            'Glucose': 120,
            # Missing other required features
        }
        
        with self.assertRaises(ValueError) as context:
            preprocess_inputs(incomplete_input, 'diabetes')
        
        self.assertIn('Missing required features', str(context.exception))
    
    def test_invalid_model_name(self):
        """Test that invalid model name raises ValueError"""
        sample_input = {'test': 1}
        
        with self.assertRaises(ValueError):
            preprocess_inputs(sample_input, 'invalid_model')


class ServicesTestCase(TestCase):
    """Test prediction service functions"""
    
    def test_predict_diabetes_structure(self):
        """Test that prediction returns correctly structured JSON"""
        sample_input = {
            'Pregnancies': 2,
            'Glucose': 120,
            'BloodPressure': 70,
            'SkinThickness': 20,
            'Insulin': 80,
            'BMI': 25.5,
            'DiabetesPedigreeFunction': 0.5,
            'Age': 33
        }
        
        result = predict_disease('diabetes', sample_input)
        
        # Check required keys
        self.assertIn('disease', result)
        self.assertIn('prediction_label', result)
        self.assertIn('probability', result)
        self.assertIn('probabilities', result)
        self.assertIn('record_id', result)
        self.assertIn('created_at', result)
        
        # Check types
        self.assertEqual(result['disease'], 'diabetes')
        self.assertIsInstance(result['prediction_label'], str)
        self.assertIsInstance(result['probability'], float)
        self.assertIsInstance(result['probabilities'], dict)
        self.assertIsInstance(result['record_id'], int)
        
        # Check probability range
        self.assertGreaterEqual(result['probability'], 0.0)
        self.assertLessEqual(result['probability'], 1.0)
        
        # Check database record was created
        record = PredictionRecord.objects.get(id=result['record_id'])
        self.assertEqual(record.disease, 'diabetes')


class ViewsTestCase(TestCase):
    """Test views and endpoints"""
    
    def setUp(self):
        self.client = Client()
    
    def test_home_view(self):
        """Test home page loads"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI-Based Disease Prediction System')
    
    def test_diabetes_form_view_get(self):
        """Test diabetes form page loads"""
        response = self.client.get(reverse('diabetes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Diabetes')
    
    def test_heart_form_view_get(self):
        """Test heart disease form page loads"""
        response = self.client.get(reverse('heart'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Heart')
    
    def test_breast_form_view_get(self):
        """Test breast cancer form page loads"""
        response = self.client.get(reverse('breast'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Breast')
    
    def test_api_predict_diabetes(self):
        """Test API prediction endpoint for diabetes"""
        payload = {
            'disease': 'diabetes',
            'inputs': {
                'Pregnancies': 2,
                'Glucose': 120,
                'BloodPressure': 70,
                'SkinThickness': 20,
                'Insulin': 80,
                'BMI': 25.5,
                'DiabetesPedigreeFunction': 0.5,
                'Age': 33
            }
        }
        
        response = self.client.post(
            reverse('api_predict'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        
        # Verify response structure
        self.assertIn('disease', data)
        self.assertIn('prediction_label', data)
        self.assertIn('probability', data)
        self.assertIn('record_id', data)
        
        self.assertEqual(data['disease'], 'diabetes')
    
    def test_api_predict_missing_disease(self):
        """Test API returns 400 for missing disease field"""
        payload = {
            'inputs': {'test': 1}
        }
        
        response = self.client.post(
            reverse('api_predict'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
    
    def test_api_predict_invalid_disease(self):
        """Test API returns 400 for invalid disease type"""
        payload = {
            'disease': 'invalid',
            'inputs': {'test': 1}
        }
        
        response = self.client.post(
            reverse('api_predict'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_result_view(self):
        """Test result page displays prediction"""
        # Create a prediction first
        sample_input = {
            'Pregnancies': 2,
            'Glucose': 120,
            'BloodPressure': 70,
            'SkinThickness': 20,
            'Insulin': 80,
            'BMI': 25.5,
            'DiabetesPedigreeFunction': 0.5,
            'Age': 33
        }
        
        result = predict_disease('diabetes', sample_input)
        record_id = result['record_id']
        
        # Access result page
        response = self.client.get(reverse('result', args=[record_id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Prediction Results')
        self.assertContains(response, result['prediction_label'])


class ModelsTestCase(TestCase):
    """Test database models"""
    
    def test_prediction_record_creation(self):
        """Test creating a PredictionRecord"""
        record = PredictionRecord.objects.create(
            disease='diabetes',
            inputs={'Glucose': 120, 'Age': 33},
            prediction_label='Non-Diabetic',
            probability=0.65,
            probabilities={'Non-Diabetic': 0.65, 'Diabetic': 0.35}
        )
        
        self.assertEqual(record.disease, 'diabetes')
        self.assertEqual(record.prediction_label, 'Non-Diabetic')
        self.assertAlmostEqual(record.probability, 0.65)
        
        # Test string representation
        str_repr = str(record)
        self.assertIn('Diabetes', str_repr)
        self.assertIn('Non-Diabetic', str_repr)
