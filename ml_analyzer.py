import re
import logging
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings("ignore")

# Try to import ML libraries, fall back gracefully if not available
try:
    import numpy as np
    import torch
    from transformers import AutoTokenizer, AutoModel
    from sklearn.metrics.pairwise import cosine_similarity
    ML_AVAILABLE = True
except ImportError as e:
    logging.warning(f"ML libraries not available: {e}")
    ML_AVAILABLE = False
    # Create dummy classes to prevent import errors
    class DummyModel:
        def eval(self): pass
        def to(self, device): return self
    
    class DummyTokenizer:
        def from_pretrained(self, name): return self
        def __call__(self, *args, **kwargs): return {'input_ids': None}

class LegalMLAnalyzer:
    def __init__(self):
        self.ml_available = ML_AVAILABLE
        if self.ml_available:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = 'cpu'
        self.tokenizer = None
        self.model = None
        self.model_loaded = False
        
        # Pre-defined legal clause embeddings for classification
        self.clause_categories = {
            'data_sharing': {
                'templates': [
                    "We may share your personal information with third parties for marketing purposes",
                    "Your data may be disclosed to our partners and affiliates",
                    "We sell personal information to advertising companies",
                    "Information shared with business partners for commercial use"
                ],
                'weight': 25,
                'severity': 'critical'
            },
            'arbitration_waiver': {
                'templates': [
                    "All disputes must be resolved through binding arbitration",
                    "You waive your right to a jury trial",
                    "Class action waiver and individual arbitration requirement",
                    "Mandatory arbitration clause limiting legal rights"
                ],
                'weight': 20,
                'severity': 'critical'
            },
            'unilateral_changes': {
                'templates': [
                    "We reserve the right to modify these terms at any time",
                    "Terms may be updated without prior notice to users",
                    "Company may change agreement unilaterally at sole discretion",
                    "Modifications effective immediately upon posting"
                ],
                'weight': 15,
                'severity': 'moderate'
            },
            'account_termination': {
                'templates': [
                    "We may suspend or terminate your account at any time",
                    "Service termination without cause or notice",
                    "Immediate account closure at company discretion",
                    "User access may be revoked without explanation"
                ],
                'weight': 15,
                'severity': 'moderate'
            },
            'liability_limitation': {
                'templates': [
                    "Company is not liable for any damages arising from service use",
                    "We disclaim all warranties and limit maximum liability",
                    "User assumes all risks of service usage",
                    "No responsibility for indirect or consequential damages"
                ],
                'weight': 12,
                'severity': 'moderate'
            }
        }
        
        self.positive_indicators = {
            'user_rights': {
                'templates': [
                    "You have the right to access your personal data",
                    "Users may request deletion of their information",
                    "Data portability rights are provided to users",
                    "Right to opt out of data processing"
                ]
            },
            'transparency': {
                'templates': [
                    "We will provide clear notice of any changes",
                    "Users will be informed of policy updates",
                    "Transparent communication about data usage",
                    "Clear explanation of terms in plain language"
                ]
            },
            'data_protection': {
                'templates': [
                    "Your data is encrypted and securely stored",
                    "Strong security measures protect user information",
                    "GDPR compliant data processing practices",
                    "Privacy by design principles are followed"
                ]
            }
        }
        
        self.category_embeddings = {}
        self.positive_embeddings = {}
        
    def load_model(self):
        """Load LegalBERT model for legal text analysis"""
        if not self.ml_available:
            logging.info("ML libraries not available, using enhanced pattern-based analysis")
            self.model_loaded = False
            return
            
        try:
            model_name = "nlpaueb/legal-bert-base-uncased"
            logging.info(f"Loading {model_name}...")
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()
            
            # Pre-compute embeddings for clause categories
            self._compute_category_embeddings()
            self.model_loaded = True
            logging.info("LegalBERT model loaded successfully")
            
        except Exception as e:
            logging.warning(f"Failed to load LegalBERT model: {e}")
            logging.info("Falling back to enhanced pattern-based analysis")
            self.model_loaded = False
    
    def _compute_category_embeddings(self):
        """Pre-compute embeddings for all clause categories"""
        if not self.model_loaded:
            return
            
        # Compute embeddings for risk categories
        for category, data in self.clause_categories.items():
            embeddings = []
            for template in data['templates']:
                embedding = self._get_text_embedding(template)
                if embedding is not None:
                    embeddings.append(embedding)
            
            if embeddings:
                # Average embeddings for this category
                self.category_embeddings[category] = np.mean(embeddings, axis=0)
        
        # Compute embeddings for positive indicators
        for category, data in self.positive_indicators.items():
            embeddings = []
            for template in data['templates']:
                embedding = self._get_text_embedding(template)
                if embedding is not None:
                    embeddings.append(embedding)
            
            if embeddings:
                self.positive_embeddings[category] = np.mean(embeddings, axis=0)
    
    def _get_text_embedding(self, text: str):
        """Get embedding for a piece of text using LegalBERT"""
        if not self.model_loaded:
            return None
            
        try:
            # Tokenize and encode text
            inputs = self.tokenizer(text, return_tensors="pt", 
                                  truncation=True, padding=True, 
                                  max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Use CLS token embedding
                embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()
                return embedding.flatten()
                
        except Exception as e:
            logging.error(f"Error getting embedding for text: {e}")
            return None
    
    def _classify_sentence_ml(self, sentence: str) -> Dict:
        """Classify a sentence using ML-based approach"""
        if not self.model_loaded:
            return {}
        
        sentence_embedding = self._get_text_embedding(sentence)
        if sentence_embedding is None:
            return {}
        
        classifications = {}
        
        # Check against risk categories
        for category, category_embedding in self.category_embeddings.items():
            if not self.ml_available:
                continue
            similarity = cosine_similarity(
                sentence_embedding.reshape(1, -1),
                category_embedding.reshape(1, -1)
            )[0][0]
            
            # Threshold for classification (adjustable)
            if similarity > 0.7:
                classifications[category] = {
                    'confidence': float(similarity),
                    'type': 'risk',
                    'severity': self.clause_categories[category]['severity'],
                    'weight': self.clause_categories[category]['weight']
                }
        
        # Check against positive indicators
        for category, category_embedding in self.positive_embeddings.items():
            if not self.ml_available:
                continue
            similarity = cosine_similarity(
                sentence_embedding.reshape(1, -1),
                category_embedding.reshape(1, -1)
            )[0][0]
            
            if similarity > 0.7:
                classifications[f"positive_{category}"] = {
                    'confidence': float(similarity),
                    'type': 'positive',
                    'severity': 'good'
                }
        
        return classifications
    
    def analyze_text_ml(self, text: str) -> Dict:
        """Analyze text using machine learning approach"""
        # Load model if not already loaded
        if not self.model_loaded:
            self.load_model()
        
        # If model still not loaded, use enhanced patterns
        if not self.model_loaded:
            try:
                from enhanced_patterns import EnhancedPatternAnalyzer
                enhanced_analyzer = EnhancedPatternAnalyzer()
                return enhanced_analyzer.analyze_with_enhanced_patterns(text)
            except ImportError:
                logging.warning("Enhanced patterns not available, using basic analysis")
                return {'error': 'ML and enhanced pattern analysis unavailable'}
        
        # Split text into sentences for analysis
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        
        ml_risk_breakdown = {}
        ml_positive_indicators = {}
        confidence_scores = {}
        total_sentences = len(sentences)
        processed_sentences = 0
        
        logging.info(f"Analyzing {total_sentences} sentences with LegalBERT...")
        
        for sentence in sentences:
            try:
                classifications = self._classify_sentence_ml(sentence)
                processed_sentences += 1
                
                for category, data in classifications.items():
                    if data['type'] == 'risk':
                        if category not in ml_risk_breakdown:
                            ml_risk_breakdown[category] = {
                                'count': 0,
                                'confidence_scores': [],
                                'matches': [],
                                'severity': data['severity'],
                                'weight': data['weight'],
                                'description': f"ML-detected {category.replace('_', ' ')}"
                            }
                        
                        ml_risk_breakdown[category]['count'] += 1
                        ml_risk_breakdown[category]['confidence_scores'].append(data['confidence'])
                        ml_risk_breakdown[category]['matches'].append({
                            'text': sentence[:100] + '...' if len(sentence) > 100 else sentence,
                            'confidence': data['confidence']
                        })
                    
                    elif data['type'] == 'positive':
                        clean_category = category.replace('positive_', '')
                        if clean_category not in ml_positive_indicators:
                            ml_positive_indicators[clean_category] = {
                                'count': 0,
                                'confidence_scores': [],
                                'matches': []
                            }
                        
                        ml_positive_indicators[clean_category]['count'] += 1
                        ml_positive_indicators[clean_category]['confidence_scores'].append(data['confidence'])
                        ml_positive_indicators[clean_category]['matches'].append({
                            'text': sentence[:100] + '...' if len(sentence) > 100 else sentence,
                            'confidence': data['confidence']
                        })
                
            except Exception as e:
                logging.error(f"Error processing sentence with ML: {e}")
                continue
        
        # Calculate average confidence scores
        for category, data in ml_risk_breakdown.items():
            if data['confidence_scores']:
                if self.ml_available:
                    confidence_scores[category] = np.mean(data['confidence_scores'])
                else:
                    confidence_scores[category] = sum(data['confidence_scores']) / len(data['confidence_scores'])
        
        for category, data in ml_positive_indicators.items():
            if data['confidence_scores']:
                if self.ml_available:
                    confidence_scores[f"positive_{category}"] = np.mean(data['confidence_scores'])
                else:
                    confidence_scores[f"positive_{category}"] = sum(data['confidence_scores']) / len(data['confidence_scores'])
        
        logging.info(f"ML analysis completed: {processed_sentences}/{total_sentences} sentences processed")
        
        return {
            'ml_analysis': self.ml_available and self.model_loaded,
            'risk_breakdown': ml_risk_breakdown,
            'positive_indicators': ml_positive_indicators,
            'ml_confidence_scores': confidence_scores,
            'classification_method': 'legalbert' if (self.ml_available and self.model_loaded) else 'enhanced_patterns',
            'sentences_processed': processed_sentences,
            'total_sentences': total_sentences
        }
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model"""
        return {
            'ml_libraries_available': self.ml_available,
            'model_loaded': self.model_loaded,
            'device': str(self.device),
            'model_name': 'nlpaueb/legal-bert-base-uncased' if self.model_loaded else 'enhanced_patterns',
            'categories_available': len(self.clause_categories),
            'positive_indicators_available': len(self.positive_indicators),
            'analysis_method': 'machine_learning' if self.model_loaded else 'advanced_patterns'
        }