"""
Views and API Endpoints for Disease Prediction

Implements:
- Home page view
- Form views for each disease
- Result display view
- PDF report generation
- JSON API endpoint for predictions
"""

import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
import json

from .forms import DiabetesForm, HeartForm, BreastForm
from .models import PredictionRecord
from .services import predict_disease
from .utils import load_models

logger = logging.getLogger('predictor')

# Load models at module initialization
# Non-blocking: server will start even if models fail to load
try:
    load_models()
    logger.info("Models loaded successfully at startup")
except Exception as e:
    logger.error(f"Failed to load models at startup: {e}", exc_info=True)
    logger.warning("Server starting without pre-loaded models. Models will be loaded on first prediction attempt.")


def home_view(request):
    """
    Render the home page with disease prediction options.
    - Non-authenticated users: Landing page with features
    - Authenticated users: Personal dashboard with stats
    """
    context = {}
    
    if request.user.is_authenticated:
        # Get user's prediction statistics
        user_predictions = PredictionRecord.objects.filter(user=request.user).order_by('-created_at')
        
        context = {
            'predictions_count': user_predictions.count(),
            'low_risk_count': user_predictions.filter(risk_level='LOW').count(),
            'medium_risk_count': user_predictions.filter(risk_level='MEDIUM').count(),
            'high_risk_count': user_predictions.filter(risk_level='HIGH').count(),
            'recent_predictions': user_predictions[:5]  # Latest 5 predictions
        }
    
    return render(request, 'predictor/home.html', context)


@login_required
def disease_form_view(request, disease):
    """
    Display and process disease prediction forms.
    Requires user to be logged in.
    
    Args:
        request: HTTP request
        disease: Disease type ('diabetes', 'heart', 'breast')
        
    Returns:
        GET: Render form page
        POST: Process form and redirect to results
    """
    # Map disease to form class
    form_mapping = {
        'diabetes': DiabetesForm,
        'heart': HeartForm,
        'breast': BreastForm,
    }
    
    template_mapping = {
        'diabetes': 'predictor/diabetes.html',
        'heart': 'predictor/heart.html',
        'breast': 'predictor/breast.html',
    }
    
    if disease not in form_mapping:
        return render(request, 'predictor/error.html', {
            'error': f'Invalid disease type: {disease}'
        })
    
    FormClass = form_mapping[disease]
    template_name = template_mapping[disease]
    
    if request.method == 'POST':
        form = FormClass(request.POST)
        if form.is_valid():
            try:
                # Get cleaned data
                inputs = form.cleaned_data
                
                # Perform prediction with user and request for audit logging
                result = predict_disease(disease, inputs, user=request.user, request=request)
                record_id = result['record_id']
                
                # Redirect to result page
                return redirect('result', record_id=record_id)
                
            except Exception as e:
                logger.error(f"Prediction error: {e}", exc_info=True)
                return render(request, template_name, {
                    'form': form,
                    'error': f'Prediction failed: {str(e)}'
                })
        else:
            return render(request, template_name, {
                'form': form,
                'error': 'Please correct the errors below.'
            })
    else:
        form = FormClass()
    
    return render(request, template_name, {'form': form, 'disease': disease})



def result_view(request, record_id):
    """
    Display enhanced prediction results with AI explainability.
    
    Args:
        request: HTTP request
        record_id: ID of the PredictionRecord
        
    Returns:
        Rendered result page with full XAI features
    """
    from .risk_stratification import get_risk_description
    
    record = get_object_or_404(PredictionRecord, id=record_id)
    
    # Determine color class for prediction label
    color_mapping = {
        'Diabetic': 'danger',
        'Non-Diabetic': 'success',
        'Heart Disease Present': 'danger',
        'No Heart Disease': 'success',
        'Malignant': 'danger',
        'Benign': 'success',
    }
    
    color_class = color_mapping.get(record.prediction_label, 'info')
    
    # Get risk description if available
    risk_description = None
    if record.risk_level:
        risk_description = get_risk_description(
            record.disease,
            record.risk_level,
            record.probability
        )
    
    context = {
        'record': record,
        'color_class': color_class,
        'probability_percent': round(record.probability * 100, 2),
        'risk_description': risk_description,
    }
    
    # Use enhanced template if XAI features are present
    if record.top_features or record.risk_level or record.recommendations:
        template_name = 'predictor/result_enhanced.html'
    else:
        template_name = 'predictor/result.html'
    
    return render(request, template_name, context)


def report_view(request, record_id):
    """
    Generate and download PDF report for a prediction.
    
    Args:
        request: HTTP request
        record_id: ID of the PredictionRecord
        
    Returns:
        PDF file as HTTP response
    """
    record = get_object_or_404(PredictionRecord, id=record_id)
    
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        from io import BytesIO
        from datetime import datetime
        
        # Create PDF buffer
        buffer = BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        # Container for PDF elements
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#3A1C71'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#D76D77'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        normal_style = styles['Normal']
        
        # Title
        title = Paragraph("Disease Prediction Report", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Report Info
        report_data = [
            ['Report ID:', f'#{record.id}'],
            ['Disease Type:', record.disease.title()],
            ['Prediction:', record.prediction_label],
            ['Probability:', f'{record.probability:.2%}'],
            ['Date:', record.created_at.strftime('%B %d, %Y at %I:%M %p')]
        ]
        
        report_table = Table(report_data, colWidths=[2*inch, 4*inch])
        report_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F0F0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        elements.append(report_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Probability Distribution
        prob_heading = Paragraph("Probability Distribution", heading_style)
        elements.append(prob_heading)
        
        prob_data = [['Class', 'Probability']]
        for label, prob in record.probabilities.items():
            prob_data.append([label, f'{prob:.2%}'])
        
        prob_table = Table(prob_data, colWidths=[3*inch, 3*inch])
        prob_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3A1C71')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(prob_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Input Features
        input_heading = Paragraph("Input Features", heading_style)
        elements.append(input_heading)
        
        # Convert inputs to table format
        input_data = [['Feature', 'Value']]
        for key, value in record.inputs.items():
            # Format the key nicely
            formatted_key = key.replace('_', ' ').title()
            input_data.append([formatted_key, str(value)])
        
        input_table = Table(input_data, colWidths=[3*inch, 3*inch])
        input_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D76D77')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FFF8F0')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(input_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # AI Explainability - Risk Level and Top Features
        if record.risk_level or record.top_features:
            xai_heading = Paragraph("AI Analysis & Risk Assessment", heading_style)
            elements.append(xai_heading)
            
            if record.risk_level:
                risk_text = f"<b>Risk Level:</b> {record.get_risk_level_display()}"
                risk_para = Paragraph(risk_text, normal_style)
                elements.append(risk_para)
                elements.append(Spacer(1, 0.1*inch))
            
            if record.top_features:
                features_text = "<b>Top Contributing Factors:</b><br/>"
                for feature in record.top_features[:5]:
                    features_text += f"• {feature['name'].title()}: {feature['value']} (Importance: {feature['importance']}%)<br/>"
                features_para = Paragraph(features_text, normal_style)
                elements.append(features_para)
                elements.append(Spacer(1, 0.3*inch))
        
        # Personalized Medical Recommendations
        if record.recommendations:
            rec_heading = Paragraph("Personalized Medical Recommendations", heading_style)
            elements.append(rec_heading)
            elements.append(Spacer(1, 0.1*inch))
            
            categories = {
                'lifestyle': ('Lifestyle Modifications', colors.HexColor('#0d6efd')),
                'diet': ('Dietary Recommendations', colors.HexColor('#198754')),
                'medical': ('Medical Follow-up', colors.HexColor('#dc3545')),
                'monitoring': ('Health Monitoring', colors.HexColor('#0dcaf0'))
            }
            
            for key, (title, color) in categories.items():
                if record.recommendations.get(key):
                    # Category title
                    category_style = ParagraphStyle(
                        f'{key}_style',
                        parent=normal_style,
                        fontSize=12,
                        textColor=color,
                        fontName='Helvetica-Bold',
                        spaceAfter=6,
                        spaceBefore=12
                    )
                    cat_title = Paragraph(title, category_style)
                    elements.append(cat_title)
                    
                    # Recommendations as bullet points
                    bullet_style = ParagraphStyle(
                        f'{key}_bullet',
                        parent=normal_style,
                        fontSize=10,
                        leftIndent=20,
                        bulletIndent=10,
                        spaceAfter=4
                    )
                    
                    for rec in record.recommendations[key]:
                        # Clean text for PDF (remove any HTML tags if present)
                        clean_rec = rec.replace('<b>', '').replace('</b>', '').replace('<strong>', '').replace('</strong>', '')
                        bullet_text = f"• {clean_rec}"
                        bullet_para = Paragraph(bullet_text, bullet_style)
                        elements.append(bullet_para)
                    
                    elements.append(Spacer(1, 0.1*inch))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Medical Disclaimer
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=normal_style,
            fontSize=9,
            textColor=colors.HexColor('#856404'),
            alignment=TA_CENTER,
            spaceBefore=12,
            spaceAfter=12
        )
        disclaimer_text = (
            "<b>MEDICAL DISCLAIMER:</b> This prediction is generated by a machine learning model "
            "and is for informational purposes only. It should NOT replace professional medical diagnosis. "
            "Always consult with qualified healthcare providers for medical advice, diagnosis, and treatment."
        )
        disclaimer = Paragraph(disclaimer_text, disclaimer_style)
        elements.append(disclaimer)
        elements.append(Spacer(1, 0.2*inch))
        
        # Footer
        footer_text = f"<i>Generated by AI Disease Prediction System on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</i>"
        footer = Paragraph(footer_text, normal_style)
        elements.append(footer)
        
        # Build PDF
        doc.build(elements)
        
        # Return PDF response
        buffer.seek(0)
        response = HttpResponse(buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="prediction_report_{record_id}.pdf"'
        
        return response
        
    except ImportError as e:
        logger.error(f"ReportLab import failed: {e}", exc_info=True)
        return HttpResponse("PDF library not available. Please install reportlab.", status=500)
    except Exception as e:
        logger.error(f"PDF generation failed: {e}", exc_info=True)
        return HttpResponse(f"Error generating PDF: {str(e)}", status=500)


@csrf_exempt  # API endpoint - using CSRF exemption for simplicity; use token auth in production
@require_http_methods(["POST"])
def api_predict(request):
    """
    JSON API endpoint for disease predictions.
    
    Security Note: This endpoint is CSRF exempt for easier API integration.
    In production, implement proper API authentication (JWT, API keys, etc.)
    and remove csrf_exempt decorator.
    
    Request Body (JSON):
        {
            "disease": "diabetes" | "heart" | "breast",
            "inputs": {
                // Feature dict matching the disease's expected inputs
            }
        }
    
    Response (JSON):
        {
            "disease": "diabetes",
            "prediction_label": "Diabetic",
            "probability": 0.8312,
            "probabilities": {...},
            "raw_scores": [...],
            "record_id": 17,
            "created_at": "2025-11-14T12:34:56Z"
        }
    
    Errors:
        400: Invalid request (missing fields, invalid disease)
        500: Prediction failure
    """
    try:
        # Parse JSON body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON in request body'
            }, status=400)
        
        # Validate required fields
        if 'disease' not in data:
            return JsonResponse({
                'error': 'Missing required field: disease'
            }, status=400)
        
        if 'inputs' not in data:
            return JsonResponse({
                'error': 'Missing required field: inputs'
            }, status=400)
        
        disease = data['disease']
        inputs = data['inputs']
        
        # Validate disease type
        valid_diseases = ['diabetes', 'heart', 'breast']
        if disease not in valid_diseases:
            return JsonResponse({
                'error': f'Invalid disease type. Must be one of: {valid_diseases}'
            }, status=400)
        
        # Perform prediction
        result = predict_disease(disease, inputs)
        
        return JsonResponse(result, status=200)
        
    except ValueError as e:
        # Validation errors (missing features, invalid values)
        logger.warning(f"Validation error in API: {e}")
        return JsonResponse({
            'error': str(e)
        }, status=400)
        
    except Exception as e:
        # Unexpected errors
        logger.error(f"API prediction failed: {e}", exc_info=True)
        return JsonResponse({
            'error': f'Prediction failed: {str(e)}'
        }, status=500)


@login_required
def history_view(request):
    """
    Show prediction history for logged-in user.
    Users can only see their own predictions.
    """
    predictions = PredictionRecord.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'predictor/history.html', {
        'predictions': predictions
    })


@login_required
def api_user_history(request):
    """
    API endpoint to get logged-in user's prediction history.
    Returns JSON array of predictions.
    """
    predictions = PredictionRecord.objects.filter(user=request.user).order_by('-created_at')
    
    data = [{
        'id': p.id,
        'disease': p.disease,
        'prediction_label': p.prediction_label,
        'probability': p.probability,
        'probabilities': p.probabilities,
        'created_at': p.created_at.isoformat(),
    } for p in predictions]
    
    return JsonResponse({'predictions': data}, status=200)
