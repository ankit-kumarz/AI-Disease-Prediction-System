"""
Django Forms for Disease Prediction

Each form validates inputs for a specific disease model and ensures
data is clean before being passed to the prediction service.
"""

from django import forms


class DiabetesForm(forms.Form):
    """
    Form for diabetes prediction inputs.
    
    All fields correspond to the Pima Indians Diabetes Dataset features.
    """
    Pregnancies = forms.IntegerField(
        min_value=0,
        max_value=20,
        label='Number of Pregnancies',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 2'
        })
    )
    
    Glucose = forms.FloatField(
        min_value=0,
        max_value=300,
        label='Glucose Level (mg/dL)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 120',
            'step': '0.1'
        })
    )
    
    BloodPressure = forms.FloatField(
        min_value=0,
        max_value=200,
        label='Blood Pressure (mm Hg)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 70',
            'step': '0.1'
        })
    )
    
    SkinThickness = forms.FloatField(
        min_value=0,
        max_value=100,
        label='Skin Thickness (mm)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 20',
            'step': '0.1'
        })
    )
    
    Insulin = forms.FloatField(
        min_value=0,
        max_value=900,
        label='Insulin Level (μU/mL)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 80',
            'step': '0.1'
        })
    )
    
    BMI = forms.FloatField(
        min_value=0,
        max_value=70,
        label='Body Mass Index (BMI)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 25.5',
            'step': '0.1'
        })
    )
    
    DiabetesPedigreeFunction = forms.FloatField(
        min_value=0,
        max_value=3,
        label='Diabetes Pedigree Function',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 0.5',
            'step': '0.01'
        })
    )
    
    Age = forms.IntegerField(
        min_value=0,
        max_value=120,
        label='Age (years)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 33'
        })
    )


class HeartForm(forms.Form):
    """
    Form for heart disease prediction inputs.
    
    Based on the Cleveland Heart Disease dataset.
    """
    age = forms.IntegerField(
        min_value=0,
        max_value=120,
        label='Age (years)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 55'
        })
    )
    
    sex = forms.ChoiceField(
        choices=[(1, 'Male'), (0, 'Female')],
        label='Sex',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    cp = forms.ChoiceField(
        choices=[
            (0, 'Typical Angina'),
            (1, 'Atypical Angina'),
            (2, 'Non-anginal Pain'),
            (3, 'Asymptomatic')
        ],
        label='Chest Pain Type',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    trestbps = forms.FloatField(
        min_value=50,
        max_value=250,
        label='Resting Blood Pressure (mm Hg)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 120',
            'step': '0.1'
        })
    )
    
    chol = forms.FloatField(
        min_value=100,
        max_value=600,
        label='Serum Cholesterol (mg/dl)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 200',
            'step': '0.1'
        })
    )
    
    fbs = forms.ChoiceField(
        choices=[(1, 'True (> 120 mg/dl)'), (0, 'False (<= 120 mg/dl)')],
        label='Fasting Blood Sugar > 120 mg/dl',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    restecg = forms.ChoiceField(
        choices=[
            (0, 'Normal'),
            (1, 'ST-T Wave Abnormality'),
            (2, 'Left Ventricular Hypertrophy')
        ],
        label='Resting ECG Results',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    thalach = forms.FloatField(
        min_value=60,
        max_value=250,
        label='Maximum Heart Rate Achieved',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 150',
            'step': '0.1'
        })
    )
    
    exang = forms.ChoiceField(
        choices=[(1, 'Yes'), (0, 'No')],
        label='Exercise Induced Angina',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    oldpeak = forms.FloatField(
        min_value=0,
        max_value=10,
        label='ST Depression (oldpeak)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 1.0',
            'step': '0.1'
        })
    )
    
    slope = forms.ChoiceField(
        choices=[
            (0, 'Upsloping'),
            (1, 'Flat'),
            (2, 'Downsloping')
        ],
        label='Slope of Peak Exercise ST Segment',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    ca = forms.ChoiceField(
        choices=[(0, '0'), (1, '1'), (2, '2'), (3, '3'), (4, '4')],
        label='Number of Major Vessels (0-4)',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    thal = forms.ChoiceField(
        choices=[
            (0, 'Normal'),
            (1, 'Fixed Defect'),
            (2, 'Reversible Defect'),
            (3, 'Not Described')
        ],
        label='Thalassemia',
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class BreastForm(forms.Form):
    """
    Form for breast cancer prediction inputs.
    
    Based on the Wisconsin Breast Cancer dataset - 30 numeric features
    derived from cell nuclei measurements.
    """
    
    # Mean features
    radius_mean = forms.FloatField(
        min_value=0,
        label='Radius Mean',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 14.5',
            'step': '0.01'
        })
    )
    
    texture_mean = forms.FloatField(
        min_value=0,
        label='Texture Mean',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 19.5',
            'step': '0.01'
        })
    )
    
    perimeter_mean = forms.FloatField(
        min_value=0,
        label='Perimeter Mean',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 92.0',
            'step': '0.01'
        })
    )
    
    area_mean = forms.FloatField(
        min_value=0,
        label='Area Mean',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 655.0',
            'step': '0.01'
        })
    )
    
    smoothness_mean = forms.FloatField(
        min_value=0,
        max_value=1,
        label='Smoothness Mean',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 0.096',
            'step': '0.001'
        })
    )
    
    compactness_mean = forms.FloatField(
        min_value=0,
        label='Compactness Mean',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 0.104',
            'step': '0.001'
        })
    )
    
    concavity_mean = forms.FloatField(
        min_value=0,
        label='Concavity Mean',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 0.089',
            'step': '0.001'
        })
    )
    
    concave_points_mean = forms.FloatField(
        min_value=0,
        label='Concave Points Mean',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 0.048',
            'step': '0.001'
        })
    )
    
    symmetry_mean = forms.FloatField(
        min_value=0,
        max_value=1,
        label='Symmetry Mean',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 0.181',
            'step': '0.001'
        })
    )
    
    fractal_dimension_mean = forms.FloatField(
        min_value=0,
        label='Fractal Dimension Mean',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 0.063',
            'step': '0.001'
        })
    )
    
    # Standard error features
    radius_se = forms.FloatField(
        min_value=0,
        label='Radius SE',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 0.4',
            'step': '0.01'
        })
    )
    
    texture_se = forms.FloatField(
        min_value=0,
        label='Texture SE',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 1.2',
            'step': '0.01'
        })
    )
    
    perimeter_se = forms.FloatField(
        min_value=0,
        label='Perimeter SE',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 2.9',
            'step': '0.01'
        })
    )
    
    area_se = forms.FloatField(
        min_value=0,
        label='Area SE',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 40.0',
            'step': '0.01'
        })
    )
    
    smoothness_se = forms.FloatField(
        min_value=0,
        label='Smoothness SE',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 0.007',
            'step': '0.0001'
        })
    )
    
    compactness_se = forms.FloatField(
        min_value=0,
        label='Compactness SE',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 0.025',
            'step': '0.001'
        })
    )
    
    concavity_se = forms.FloatField(
        min_value=0,
        label='Concavity SE',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 0.032',
            'step': '0.001'
        })
    )
    
    concave_points_se = forms.FloatField(
        min_value=0,
        label='Concave Points SE',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 0.011',
            'step': '0.001'
        })
    )
    
    symmetry_se = forms.FloatField(
        min_value=0,
        label='Symmetry SE',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 0.020',
            'step': '0.001'
        })
    )
    
    fractal_dimension_se = forms.FloatField(
        min_value=0,
        label='Fractal Dimension SE',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 0.003',
            'step': '0.0001'
        })
    )
    
    # Worst features
    radius_worst = forms.FloatField(
        min_value=0,
        label='Radius Worst',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 16.3',
            'step': '0.01'
        })
    )
    
    texture_worst = forms.FloatField(
        min_value=0,
        label='Texture Worst',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 25.7',
            'step': '0.01'
        })
    )
    
    perimeter_worst = forms.FloatField(
        min_value=0,
        label='Perimeter Worst',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 107.0',
            'step': '0.01'
        })
    )
    
    area_worst = forms.FloatField(
        min_value=0,
        label='Area Worst',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 830.0',
            'step': '0.01'
        })
    )
    
    smoothness_worst = forms.FloatField(
        min_value=0,
        max_value=1,
        label='Smoothness Worst',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 0.132',
            'step': '0.001'
        })
    )
    
    compactness_worst = forms.FloatField(
        min_value=0,
        label='Compactness Worst',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 0.254',
            'step': '0.001'
        })
    )
    
    concavity_worst = forms.FloatField(
        min_value=0,
        label='Concavity Worst',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 0.272',
            'step': '0.001'
        })
    )
    
    concave_points_worst = forms.FloatField(
        min_value=0,
        label='Concave Points Worst',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 0.114',
            'step': '0.001'
        })
    )
    
    symmetry_worst = forms.FloatField(
        min_value=0,
        max_value=1,
        label='Symmetry Worst',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 0.290',
            'step': '0.001'
        })
    )
    
    fractal_dimension_worst = forms.FloatField(
        min_value=0,
        label='Fractal Dimension Worst',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 0.084',
            'step': '0.001'
        })
    )
