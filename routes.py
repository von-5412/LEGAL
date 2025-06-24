from flask import render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import os
import hashlib
from datetime import datetime
from app import app, db
from models import AnalysisResult
from nlp_analyzer import TOSAnalyzer

# Initialize analyzer
analyzer = TOSAnalyzer()

ALLOWED_EXTENSIONS = {'txt', 'pdf'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main upload page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and analysis"""
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    user_persona = request.form.get('user_persona', 'individual_user')
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    if not allowed_file(file.filename):
        flash('Please upload a PDF or TXT file only', 'error')
        return redirect(url_for('index'))
    
    try:
        # Read file content
        file_content = file.read()
        
        # Generate hash for deduplication
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        # Check if we've already analyzed this file
        existing_analysis = AnalysisResult.query.filter_by(file_hash=file_hash).first()
        if existing_analysis:
            flash('This file has already been analyzed. Showing previous results.', 'info')
            return redirect(url_for('results', result_id=existing_analysis.id))
        
        # Extract text based on file type
        filename = secure_filename(file.filename)
        if filename.lower().endswith('.pdf'):
            text = analyzer.extract_text_from_pdf(file_content)
        else:
            text = file_content.decode('utf-8')
        
        if not text.strip():
            flash('No text could be extracted from the file', 'error')
            return redirect(url_for('index'))
        
        # Analyze text with user persona
        analysis_results = analyzer.analyze_text(text)
        
        # Update power analysis with selected persona
        if 'power_analysis' in analysis_results:
            power_analysis = analyzer.power_analyzer.analyze_power_structure(text, user_persona=user_persona)
            analysis_results['power_analysis'] = power_analysis
        
        # Save results to database
        result = AnalysisResult(
            filename=filename,
            file_hash=file_hash,
            risk_score=analysis_results.get('risk_score', 0),
            transparency_score=analysis_results.get('transparency_score', 0)
        )
        result.set_analysis_data(analysis_results)
        
        db.session.add(result)
        db.session.commit()
        
        flash('Analysis completed successfully!', 'success')
        return redirect(url_for('results', result_id=result.id))
        
    except Exception as e:
        app.logger.error(f"Analysis error: {str(e)}")
        flash(f'Error analyzing file: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/results/<int:result_id>')
def results(result_id):
    """Display analysis results"""
    analysis = AnalysisResult.query.get_or_404(result_id)
    return render_template('results.html', analysis=analysis, analysis_data=analysis.get_analysis_data())

@app.route('/history')
def history():
    """Show analysis history"""
    analyses = AnalysisResult.query.order_by(AnalysisResult.created_at.desc()).limit(50).all()
    return render_template('history.html', analyses=analyses)

@app.route('/compare')
def compare():
    """Compare multiple analyses"""
    analyses = AnalysisResult.query.order_by(AnalysisResult.created_at.desc()).limit(20).all()
    return render_template('compare.html', analyses=analyses)

@app.route('/export/<int:result_id>')
def export_results(result_id):
    """Export analysis results as JSON"""
    analysis = AnalysisResult.query.get_or_404(result_id)
    
    export_data = {
        'filename': analysis.filename,
        'analysis_date': analysis.created_at.isoformat(),
        'risk_score': analysis.risk_score,
        'transparency_score': analysis.transparency_score,
        'analysis_results': analysis.get_analysis_data()
    }
    
    return jsonify(export_data)

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for text analysis"""
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    data = request.get_json()
    text = data.get('text', '')
    user_persona = data.get('user_persona', 'individual_user')
    
    if not text.strip():
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        # Analyze the text
        results = analyzer.analyze_text(text)
        
        # Add power analysis with persona
        power_analysis = analyzer.power_analyzer.analyze_power_structure(text, user_persona=user_persona)
        results['power_analysis'] = power_analysis
        
        return jsonify({
            'status': 'success',
            'results': results
        })
        
    except Exception as e:
        app.logger.error(f"API analysis error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500