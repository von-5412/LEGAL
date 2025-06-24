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
        """
        Analyze text using ML approach with fallback to enhanced patterns
        """
        if not self.ml_available:
            logging.info("ML libraries not available, using enhanced pattern-based analysis")
            try:
                from enhanced_patterns import EnhancedPatternAnalyzer
                enhanced_analyzer = EnhancedPatternAnalyzer()
                result = enhanced_analyzer.analyze_with_enhanced_patterns(text)
                # Ensure result is properly structured
                if isinstance(result, dict):
                    return result
                else:
                    return self._fallback_analysis()
            except ImportError:
                logging.warning("Enhanced pattern analyzer not available either")
                return self._fallback_analysis()

        try:
            if not self.model_loaded:
                success = self.load_model()
                if not success:
                    return self._fallback_analysis()

            return self._perform_ml_analysis(text)

        except Exception as e:
            logging.error(f"ML analysis failed: {e}")
            return self._fallback_analysis()

    def _fallback_analysis(self):
        """Return basic analysis structure when ML fails"""
        return {
            'risk_breakdown': {},
            'positive_indicators': {},
            'ml_analysis': False,
            'classification_method': 'fallback',
            'ml_confidence_scores': {},
            'sentences_processed': 0
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