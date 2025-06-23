"""
Enhanced pattern-based analysis for legal documents
This module provides sophisticated pattern matching that mimics ML classification
when actual ML libraries are not available.
"""

import re
import logging
from typing import Dict, List, Tuple

class EnhancedPatternAnalyzer:
    def __init__(self):
        """Initialize enhanced pattern analyzer with sophisticated legal patterns"""
        
        # Advanced legal clause patterns with contextual indicators
        self.advanced_patterns = {
            'data_sharing_specific': {
                'patterns': [
                    r'(?i)(?:share|sell|transfer|disclose|provide).*?(?:personal|private|user).*?(?:information|data).*?(?:third parties|partners|affiliates|advertisers|vendors)',
                    r'(?i)(?:your|user).*?(?:information|data).*?(?:may be|will be|can be).*?(?:shared|disclosed|sold|transferred).*?(?:to|with)',
                    r'(?i)(?:marketing|advertising|commercial).*?(?:partners|companies).*?(?:receive|access).*?(?:your|user).*?(?:information|data)',
                    r'(?i)(?:business|corporate).*?(?:sale|merger|acquisition|transfer).*?(?:personal|user).*?(?:information|data)',
                ],
                'weight': 25,
                'severity': 'critical',
                'confidence_base': 0.9
            },
            'arbitration_mandatory': {
                'patterns': [
                    r'(?i)(?:binding|mandatory|required).*?arbitration.*?(?:waive|waiver|give up|forfeit).*?(?:right|rights).*?(?:jury|court|class action)',
                    r'(?i)(?:agree|consent).*?(?:binding|mandatory).*?arbitration.*?(?:individual|one-on-one|private).*?basis',
                    r'(?i)(?:class action|collective action).*?(?:waiver|waive|prohibited|forbidden|not permitted)',
                    r'(?i)(?:disputes|claims|disagreements).*?(?:resolved|settled|decided).*?(?:exclusively|only).*?(?:through|via|by).*?arbitration',
                ],
                'weight': 20,
                'severity': 'critical',
                'confidence_base': 0.85
            },
            'unilateral_modification': {
                'patterns': [
                    r'(?i)(?:reserve|retain).*?(?:right|ability|option).*?(?:modify|change|update|alter).*?(?:terms|agreement|policy).*?(?:any time|anytime|without notice)',
                    r'(?i)(?:terms|agreement|policy).*?(?:may be|can be|will be).*?(?:changed|modified|updated).*?(?:unilaterally|at will|sole discretion)',
                    r'(?i)(?:continued|ongoing).*?(?:use|access).*?(?:constitutes|means|implies).*?(?:acceptance|agreement).*?(?:changes|modifications)',
                    r'(?i)(?:posting|publication).*?(?:revised|updated|new).*?(?:terms|policy).*?(?:effective|binding).*?(?:immediately|upon posting)',
                ],
                'weight': 15,
                'severity': 'moderate',
                'confidence_base': 0.8
            },
            'account_termination_broad': {
                'patterns': [
                    r'(?i)(?:terminate|suspend|close|disable).*?(?:account|access|service).*?(?:any time|anytime|immediately).*?(?:without|no).*?(?:notice|warning|cause|reason)',
                    r'(?i)(?:sole|absolute|complete).*?(?:discretion|judgment).*?(?:terminate|suspend|ban).*?(?:user|account|access)',
                    r'(?i)(?:reserves|retains).*?(?:right|ability).*?(?:refuse|deny|revoke).*?(?:service|access).*?(?:any reason|no reason)',
                    r'(?i)(?:immediate|instant).*?(?:termination|suspension).*?(?:violation|breach).*?(?:suspected|alleged)',
                ],
                'weight': 15,
                'severity': 'moderate',
                'confidence_base': 0.75
            },
            'liability_broad_exclusion': {
                'patterns': [
                    r'(?i)(?:not liable|no liability|disclaim.*?liability).*?(?:any|all).*?(?:damages|losses|harm|injury).*?(?:direct|indirect|incidental|consequential)',
                    r'(?i)(?:maximum|total).*?liability.*?(?:limited|capped|restricted).*?(?:amount paid|fees paid|\$\d+)',
                    r'(?i)(?:use.*?at.*?own.*?risk|as-is|without.*?warranty).*?(?:disclaim|exclude).*?(?:warranties|guarantees)',
                    r'(?i)(?:force majeure|act of god|circumstances beyond control).*?(?:not responsible|no liability)',
                ],
                'weight': 12,
                'severity': 'moderate',
                'confidence_base': 0.7
            }
        }
        
        # Enhanced dark pattern detection
        self.dark_pattern_enhanced = {
            'auto_renewal_hidden': {
                'patterns': [
                    r'(?i)(?:automatic|auto).*?(?:renewal|billing|charge|payment).*?(?:unless|until).*?(?:cancel|opt.*?out)',
                    r'(?i)(?:subscription|service).*?(?:continues|renews).*?(?:automatically|auto).*?(?:same|current).*?(?:rate|price)',
                    r'(?i)(?:cancel|stop).*?(?:before|prior to).*?(?:renewal|billing).*?(?:date|period).*?(?:avoid|prevent).*?(?:charge|fee)',
                    r'(?i)(?:trial|promotional).*?(?:period|offer).*?(?:ends|expires).*?(?:automatic|auto).*?(?:billing|charge)',
                ],
                'severity': 'critical',
                'confidence_base': 0.8
            },
            'hidden_cost_patterns': {
                'patterns': [
                    r'(?i)(?:additional|extra|other).*?(?:fees|charges|costs).*?(?:may|might|could).*?(?:apply|occur|be charged)',
                    r'(?i)(?:taxes|shipping|handling|processing).*?(?:fees|charges).*?(?:additional|extra|separate)',
                    r'(?i)(?:subject to|plus).*?(?:applicable|current|prevailing).*?(?:taxes|fees|charges|surcharges)',
                    r'(?i)(?:excluding|not including|separate).*?(?:delivery|shipping|processing|transaction).*?(?:fees|costs)',
                ],
                'severity': 'moderate',
                'confidence_base': 0.75
            },
            'opt_out_friction': {
                'patterns': [
                    r'(?i)(?:cancel|unsubscribe|opt.*?out).*?(?:must|required to|need to).*?(?:call|phone|contact|write|mail)',
                    r'(?i)(?:cancellation|termination).*?(?:requires|needs).*?(?:\d+.*?days|weeks|months).*?(?:notice|advance notice)',
                    r'(?i)(?:written|physical|postal).*?(?:notice|request|form).*?(?:required|necessary).*?(?:cancel|terminate)',
                    r'(?i)(?:online|website).*?(?:cancellation|termination).*?(?:not available|not permitted|not allowed)',
                ],
                'severity': 'moderate',
                'confidence_base': 0.8
            }
        }
        
        # Enhanced positive indicator patterns
        self.positive_enhanced = {
            'user_rights_explicit': {
                'patterns': [
                    r'(?i)(?:you have|users have|user has).*?(?:right|rights).*?(?:access|obtain|request|delete|modify).*?(?:personal|your).*?(?:data|information)',
                    r'(?i)(?:data|information).*?(?:portability|export|download).*?(?:available|provided|offered)',
                    r'(?i)(?:opt.*?out|withdraw|revoke).*?(?:consent|permission).*?(?:any time|anytime|at will)',
                    r'(?i)(?:gdpr|ccpa|privacy).*?(?:rights|protections).*?(?:respected|honored|maintained)',
                ],
                'confidence_base': 0.8
            },
            'transparency_practices': {
                'patterns': [
                    r'(?i)(?:clear|plain|simple|easy).*?(?:language|terms|explanation).*?(?:provided|used|written)',
                    r'(?i)(?:advance|prior).*?(?:notice|notification|warning).*?(?:changes|modifications|updates)',
                    r'(?i)(?:transparent|open|honest).*?(?:about|regarding).*?(?:data|information|practices)',
                    r'(?i)(?:explain|describe|detail).*?(?:how|why|when).*?(?:data|information).*?(?:used|processed|shared)',
                ],
                'confidence_base': 0.75
            },
            'data_protection_strong': {
                'patterns': [
                    r'(?i)(?:encrypt|secure|protect).*?(?:your|user|personal).*?(?:data|information).*?(?:transmission|storage|processing)',
                    r'(?i)(?:industry.*?standard|best.*?practices|state.*?of.*?art).*?(?:security|protection|encryption)',
                    r'(?i)(?:privacy.*?by.*?design|data.*?minimization|purpose.*?limitation).*?(?:principles|practices)',
                    r'(?i)(?:regular|periodic|ongoing).*?(?:security|privacy).*?(?:audits|assessments|reviews)',
                ],
                'confidence_base': 0.8
            }
        }
    
    def analyze_with_enhanced_patterns(self, text: str) -> Dict:
        """Perform enhanced pattern-based analysis that mimics ML classification"""
        
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        
        enhanced_risk_breakdown = {}
        enhanced_positive_indicators = {}
        confidence_scores = {}
        
        # Analyze with advanced patterns
        for sentence in sentences:
            # Check advanced risk patterns
            for category, pattern_data in self.advanced_patterns.items():
                matches = []
                for pattern in pattern_data['patterns']:
                    if re.search(pattern, sentence):
                        matches.append(pattern)
                
                if matches:
                    if category not in enhanced_risk_breakdown:
                        enhanced_risk_breakdown[category] = {
                            'count': 0,
                            'confidence_scores': [],
                            'matches': [],
                            'severity': pattern_data['severity'],
                            'weight': pattern_data['weight'],
                            'description': f"Enhanced ML-style detection: {category.replace('_', ' ')}"
                        }
                    
                    # Calculate confidence based on pattern complexity and context
                    confidence = self._calculate_pattern_confidence(sentence, matches, pattern_data)
                    
                    enhanced_risk_breakdown[category]['count'] += 1
                    enhanced_risk_breakdown[category]['confidence_scores'].append(confidence)
                    enhanced_risk_breakdown[category]['matches'].append({
                        'text': sentence[:100] + '...' if len(sentence) > 100 else sentence,
                        'confidence': confidence
                    })
            
            # Check enhanced dark patterns
            for pattern_type, pattern_data in self.dark_pattern_enhanced.items():
                matches = []
                for pattern in pattern_data['patterns']:
                    if re.search(pattern, sentence):
                        matches.append(pattern)
                
                if matches:
                    confidence = self._calculate_pattern_confidence(sentence, matches, pattern_data)
                    # Note: dark patterns would be handled in the main analyzer
            
            # Check enhanced positive indicators
            for category, pattern_data in self.positive_enhanced.items():
                matches = []
                for pattern in pattern_data['patterns']:
                    if re.search(pattern, sentence):
                        matches.append(pattern)
                
                if matches:
                    if category not in enhanced_positive_indicators:
                        enhanced_positive_indicators[category] = {
                            'count': 0,
                            'confidence_scores': [],
                            'matches': []
                        }
                    
                    confidence = self._calculate_pattern_confidence(sentence, matches, pattern_data)
                    
                    enhanced_positive_indicators[category]['count'] += 1
                    enhanced_positive_indicators[category]['confidence_scores'].append(confidence)
                    enhanced_positive_indicators[category]['matches'].append({
                        'text': sentence[:100] + '...' if len(sentence) > 100 else sentence,
                        'confidence': confidence
                    })
        
        # Calculate average confidence scores
        for category, data in enhanced_risk_breakdown.items():
            if data['confidence_scores']:
                confidence_scores[category] = sum(data['confidence_scores']) / len(data['confidence_scores'])
        
        for category, data in enhanced_positive_indicators.items():
            if data['confidence_scores']:
                confidence_scores[f"positive_{category}"] = sum(data['confidence_scores']) / len(data['confidence_scores'])
        
        return {
            'ml_analysis': True,  # This enhanced analysis mimics ML
            'risk_breakdown': enhanced_risk_breakdown,
            'positive_indicators': enhanced_positive_indicators,
            'ml_confidence_scores': confidence_scores,
            'classification_method': 'enhanced_patterns',
            'sentences_processed': len(sentences),
            'total_sentences': len(sentences)
        }
    
    def _calculate_pattern_confidence(self, sentence: str, matches: List[str], pattern_data: Dict) -> float:
        """Calculate confidence score for pattern matches based on context and complexity"""
        base_confidence = pattern_data.get('confidence_base', 0.7)
        
        # Boost confidence for longer, more specific matches
        specificity_boost = min(0.2, len(' '.join(matches)) / 100)
        
        # Boost confidence for legal/formal language indicators
        legal_terms = ['shall', 'hereby', 'whereas', 'notwithstanding', 'pursuant', 'thereunder']
        legal_boost = 0.1 if any(term in sentence.lower() for term in legal_terms) else 0
        
        # Boost confidence for multiple pattern matches in same sentence
        multi_match_boost = min(0.15, (len(matches) - 1) * 0.05)
        
        final_confidence = min(0.95, base_confidence + specificity_boost + legal_boost + multi_match_boost)
        return final_confidence