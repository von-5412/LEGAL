import os
import logging
from flask import render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from app import app, db
from models import AnalysisResult
from nlp_analyzer import TOSAnalyzer

# Initialize analyzer
analyzer = TOSAnalyzer()

ALLOWED_EXTENSIONS = {'txt', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page with upload form"""
    recent_analyses = AnalysisResult.query.order_by(AnalysisResult.created_at.desc()).limit(5).all()
    return render_template('index.html', recent_analyses=recent_analyses)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and analysis"""
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            file_content = file.read()
            
            # Generate file hash for deduplication
            file_hash = analyzer.generate_file_hash(file_content)
            
            # Check if we've already analyzed this file
            existing_analysis = AnalysisResult.query.filter_by(file_hash=file_hash).first()
            if existing_analysis:
                flash('This file has already been analyzed. Showing previous results.', 'info')
                return redirect(url_for('results', analysis_id=existing_analysis.id))
            
            # Extract text based on file type
            if filename.lower().endswith('.pdf'):
                text = analyzer.extract_text_from_pdf(file_content)
            else:
                text = file_content.decode('utf-8', errors='ignore')
            
            if not text.strip():
                flash('Could not extract text from the file. Please check the file format.', 'error')
                return redirect(url_for('index'))
            
            # Analyze the text
            analysis_data = analyzer.analyze_text(text)
            
            # Save analysis to database
            analysis_result = AnalysisResult(
                filename=filename,
                file_hash=file_hash,
                risk_score=analysis_data['risk_score']
            )
            analysis_result.set_analysis_data(analysis_data)
            
            db.session.add(analysis_result)
            db.session.commit()
            
            flash('Analysis completed successfully!', 'success')
            return redirect(url_for('results', analysis_id=analysis_result.id))
            
        except Exception as e:
            logging.error(f"Error processing file: {e}")
            flash('Error processing file. Please try again.', 'error')
            return redirect(url_for('index'))
    else:
        flash('Invalid file type. Please upload a PDF or text file.', 'error')
        return redirect(url_for('index'))

@app.route('/results/<int:analysis_id>')
def results(analysis_id):
    """Display analysis results"""
    analysis = AnalysisResult.query.get_or_404(analysis_id)
    analysis_data = analysis.get_analysis_data()
    
    return render_template('results.html', 
                         analysis=analysis, 
                         analysis_data=analysis_data)

@app.route('/api/analysis/<int:analysis_id>')
def api_analysis(analysis_id):
    """API endpoint for analysis data"""
    analysis = AnalysisResult.query.get_or_404(analysis_id)
    analysis_data = analysis.get_analysis_data()
    
    return jsonify({
        'id': analysis.id,
        'filename': analysis.filename,
        'risk_score': analysis.risk_score,
        'created_at': analysis.created_at.isoformat(),
        'analysis_data': analysis_data
    })

@app.route('/history')
def history():
    """View analysis history"""
    analyses = AnalysisResult.query.order_by(AnalysisResult.created_at.desc()).all()
    return render_template('history.html', analyses=analyses)

@app.errorhandler(413)
def too_large(e):
    flash('File too large. Maximum size is 16MB.', 'error')
    return redirect(url_for('index'))
