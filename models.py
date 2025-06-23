from app import db
from datetime import datetime
import json

class AnalysisResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_hash = db.Column(db.String(64), nullable=False)
    risk_score = db.Column(db.Integer, nullable=False)
    analysis_data = db.Column(db.Text, nullable=False)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_analysis_data(self):
        """Convert JSON string back to Python dict"""
        return json.loads(self.analysis_data)
    
    def set_analysis_data(self, data):
        """Convert Python dict to JSON string"""
        self.analysis_data = json.dumps(data)
