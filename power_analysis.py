"""
Power Structure Analysis for Legal Documents
Advanced analysis focusing on power dynamics, rights erosion, and user empowerment
"""

import re
import logging
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass

@dataclass
class PowerClause:
    """Represents a clause with power dynamics analysis"""
    text: str
    power_holder: str  # 'company', 'user', 'shared', 'unclear'
    reversible: bool
    negotiable: bool
    user_can_exit: bool
    impact_level: str  # 'low', 'medium', 'high', 'critical'
    confidence: float

class PowerStructureAnalyzer:
    def __init__(self):
        """Initialize power structure analyzer with sophisticated patterns"""
        
        # PILLAR 1: Power Imbalance Detector - Who controls what
        self.power_control_patterns = {
            'rule_modification_power': {
                'patterns': [
                    r'(?i)(?:we|company|service provider).*?(?:may|can|will|shall|reserve|retain).*?(?:modify|change|update|alter|amend).*?(?:terms|agreement|policy|rules).*?(?:at.*?(?:our|sole|absolute|complete).*?discretion|without.*?(?:notice|consent)|any.*?time|anytime)',
                    r'(?i)(?:terms|agreement|policy).*?(?:may.*?be|can.*?be|are|will.*?be).*?(?:changed|modified|updated|revised).*?(?:at.*?(?:our|sole|complete).*?discretion|without.*?(?:notice|consent)|any.*?time)'
                ],
                'power_holder': 'company',
                'impact': 'high',
                'weight': 30
            },
            'data_ownership_control': {
                'patterns': [
                    r'(?i)(?:we|company|service provider).*?(?:own|retain|control|possess).*?(?:all|any|your|user).*?(?:data|information|content|intellectual.*?property)',
                    r'(?i)(?:you|user).*?(?:grant|give|assign|transfer|provide).*?(?:us|company|service provider).*?(?:unlimited|perpetual|irrevocable|worldwide|exclusive).*?(?:license|right|permission)'
                ],
                'power_holder': 'company',
                'impact': 'critical',
                'weight': 35
            },
            'termination_power': {
                'patterns': [
                    r'(?i)(?:we|company|service provider).*?(?:may|can|will|shall|reserve|retain).*?(?:terminate|suspend|end|discontinue|cancel).*?(?:your|user).*?(?:account|access|service).*?(?:at.*?(?:our|sole|absolute|complete).*?discretion|without.*?(?:notice|cause|reason)|any.*?time|immediately)',
                    r'(?i)(?:immediate|instant|without.*?notice).*?(?:termination|suspension|cancellation).*?(?:of|for).*?(?:account|service|access)'
                ],
                'power_holder': 'company', 
                'impact': 'high',
                'weight': 25
            },
            'dispute_resolution_power': {
                'patterns': [
                    r'(?i)(?:all|any).*?(?:disputes?|claims?|controversies?).*?(?:shall|must|will|are.*?required.*?to).*?(?:be.*?(?:resolved|settled|decided|handled)|go.*?to).*?(?:binding.*?arbitration|arbitration|specific.*?court|designated.*?jurisdiction)',
                    r'(?i)(?:you|user).*?(?:waive|give.*?up|surrender|forfeit).*?(?:right|claim).*?(?:to|for).*?(?:jury.*?trial|class.*?action|court.*?proceedings|legal.*?action)'
                ],
                'power_holder': 'company',
                'impact': 'critical',
                'weight': 40
            },
            'user_empowerment': {
                'patterns': [
                    r'(?i)(?:you|user).*?(?:may|can|have.*?the.*?right|are.*?entitled).*?(?:to|for).*?(?:opt.*?out|withdraw|cancel|modify|delete|access|control|refuse|object)',
                    r'(?i)(?:with.*?(?:your|user).*?(?:explicit|express|written|prior|informed).*?consent|only.*?with.*?(?:your|user).*?permission)',
                    r'(?i)(?:you|user).*?(?:retain|keep|maintain).*?(?:full|complete|absolute).*?(?:control|ownership|rights).*?(?:over|to|of).*?(?:your|user).*?(?:data|content|information)'
                ],
                'power_holder': 'user',
                'impact': 'positive',
                'weight': -15
            }
        }
        
        # PILLAR 2: Structural Dark Pattern Scanner - Beyond language manipulation
        self.structural_dark_patterns = {
            'exit_friction': {
                'patterns': [
                    r'(?i)(?:cancel|terminate|close|delete).*?(?:account|subscription|service).*?(?:must|shall|require|need).*?(?:contact|call|write|email|submit.*?request)',
                    r'(?i)(?:deletion|removal|cancellation).*?(?:request|application).*?(?:processed|completed|take|require).*?(?:up.*?to|within|may.*?take).*?(?:\d+.*?(?:business.*?)?days?|\d+.*?weeks?|\d+.*?months?)',
                    r'(?i)(?:verification|authentication|confirmation).*?(?:process|procedure|steps?).*?(?:required|necessary|mandatory).*?(?:before|prior.*?to).*?(?:deletion|cancellation|termination)'
                ],
                'manipulation_type': 'exit_barriers',
                'damage_level': 'high',
                'weight': 25
            },
            'data_retention_trap': {
                'patterns': [
                    r'(?i)(?:data|information|records?).*?(?:may.*?be.*?retained|retained|kept|stored).*?(?:indefinitely|permanently|for.*?legitimate.*?business.*?purposes|after.*?(?:termination|cancellation|deletion))',
                    r'(?i)(?:anonymized?|aggregated?|de-identified).*?(?:data|information).*?(?:may.*?be.*?retained|kept|used).*?(?:indefinitely|permanently|without.*?limitation)',
                    r'(?i)(?:we|company).*?(?:may|will).*?(?:retain|keep).*?(?:backup|archived|historical).*?(?:copies|versions).*?(?:of|containing).*?(?:your|user).*?(?:data|information)'
                ],
                'manipulation_type': 'data_hoarding',
                'damage_level': 'critical',
                'weight': 30
            },
            'asymmetric_obligations': {
                'patterns': [
                    r'(?i)(?:you|user).*?(?:must|shall|are.*?required.*?to|have.*?obligation.*?to).*?(?:provide|give|maintain|ensure).*?(?:accurate|current|complete|truthful).*?(?:information|data)',
                    r'(?i)(?:failure|inability).*?(?:to|of).*?(?:you|user).*?(?:to|for).*?(?:comply|meet|satisfy|fulfill).*?(?:may.*?result.*?in|will.*?result.*?in|results.*?in).*?(?:immediate.*?)?(?:termination|suspension|cancellation)',
                    r'(?i)(?:you|user).*?(?:agree|consent|acknowledge).*?(?:to|that).*?(?:indemnify|hold.*?harmless|defend).*?(?:us|company|provider)'
                ],
                'manipulation_type': 'power_asymmetry',
                'damage_level': 'high',
                'weight': 20
            },
            'modification_asymmetry': {
                'patterns': [
                    r'(?i)(?:we|company).*?(?:may|can|reserve.*?right).*?(?:modify|change|update|alter).*?(?:at.*?any.*?time|without.*?(?:notice|consent)|with.*?(?:little|minimal|brief).*?notice)',
                    r'(?i)(?:continued.*?use|use.*?after.*?changes|accessing.*?after.*?modification).*?(?:constitutes|means|indicates|represents).*?(?:acceptance|agreement|consent)',
                    r'(?i)(?:you|user).*?(?:may.*?not|cannot|are.*?not.*?permitted.*?to).*?(?:modify|change|alter|negotiate).*?(?:these.*?terms|this.*?agreement|any.*?part)'
                ],
                'manipulation_type': 'unilateral_control',
                'damage_level': 'high',
                'weight': 25
            }
        }
        
        # PILLAR 3: AI/Data Commodification Scanner - Hidden data monetization
        self.data_commodification_patterns = {
            'ai_training_extraction': {
                'patterns': [
                    r'(?i)(?:anonymized?|aggregated?|de-identified).*?(?:data|information|content).*?(?:may.*?be.*?used|used.*?to|for|can.*?be.*?used).*?(?:train|improve|enhance|develop|create|build).*?(?:machine.*?learning|artificial.*?intelligence|ai|ml|algorithms?|models?)',
                    r'(?i)(?:your|user).*?(?:interactions?|behavior|usage|activity|content).*?(?:may.*?be.*?used|used.*?to|for|can.*?be.*?used).*?(?:improve|enhance|develop|train|create).*?(?:our|the).*?(?:services?|products?|algorithms?|ai|ml)',
                    r'(?i)(?:machine.*?learning|artificial.*?intelligence|ai|ml|algorithms?).*?(?:training|development|improvement|enhancement).*?(?:using|with|from|based.*?on).*?(?:your|user|customer).*?(?:data|information|content|inputs?)'
                ],
                'commodification_type': 'ai_training',
                'opt_out_available': False,
                'transparency_level': 'hidden',
                'weight': 35
            },
            'behavioral_profiling': {
                'patterns': [
                    r'(?i)(?:behavioral|usage|interaction|activity).*?(?:data|information|patterns?|profiles?).*?(?:collect|gather|analyze|process|use|create|build|develop)',
                    r'(?i)(?:analytics?|metrics|insights?|profiles?).*?(?:derive|extract|generate|create|build).*?(?:from|using|based.*?on).*?(?:your|user).*?(?:data|behavior|activity|usage)',
                    r'(?i)(?:personalization|targeted|customized).*?(?:advertising|marketing|recommendations|content).*?(?:based.*?on|using|from).*?(?:your|user).*?(?:data|behavior|preferences)'
                ],
                'commodification_type': 'behavioral_profiling',
                'opt_out_available': False,
                'transparency_level': 'vague',
                'weight': 25
            },
            'data_resale_licensing': {
                'patterns': [
                    r'(?i)(?:share|provide|disclose|sell|license|transfer).*?(?:your|user|anonymized|aggregated).*?(?:data|information).*?(?:with|to).*?(?:third.*?parties|partners|affiliates|advertisers|business.*?partners).*?(?:for.*?their.*?(?:business.*?purposes|commercial.*?use)|for.*?marketing)',
                    r'(?i)(?:third.*?parties|partners|affiliates).*?(?:may|can|will).*?(?:receive|access|use|process).*?(?:your|user).*?(?:data|information).*?(?:for.*?their.*?(?:own|business|commercial).*?purposes)',
                    r'(?i)(?:monetize|commercial.*?use|business.*?purposes).*?(?:of|using|from).*?(?:your|user|customer).*?(?:data|information|content)'
                ],
                'commodification_type': 'data_resale',
                'opt_out_available': False,
                'transparency_level': 'buried',
                'weight': 40
            },
            'perpetual_licensing': {
                'patterns': [
                    r'(?i)(?:you|user).*?(?:grant|give|provide|assign).*?(?:us|company|service.*?provider).*?(?:perpetual|irrevocable|worldwide|unlimited|unrestricted|royalty-free).*?(?:license|right|permission).*?(?:to|for).*?(?:use|exploit|monetize|commercialize)',
                    r'(?i)(?:perpetual|irrevocable|unlimited|worldwide).*?(?:license|right|permission).*?(?:to|for).*?(?:use|modify|distribute|display|perform|create.*?derivative.*?works)',
                    r'(?i)(?:rights?|license).*?(?:survive|continue|remain.*?in.*?effect|persist).*?(?:termination|cancellation|end.*?of.*?service|account.*?closure)'
                ],
                'commodification_type': 'perpetual_rights',
                'opt_out_available': False,
                'transparency_level': 'legal_jargon',
                'weight': 30
            }
        }
        
        # Rights stripping detection
        self.rights_erosion_patterns = {
            'privacy_rights': {
                'patterns': [
                    r'(?i)(?:share|sell|transfer|disclose).*?(?:personal|private).*?(?:information|data).*?(?:third.*?parties|partners|affiliates|anyone)',
                    r'(?i)(?:no.*?privacy|waive.*?privacy|give.*?up.*?privacy|forfeit.*?privacy)',
                    r'(?i)(?:monitor|track|record|log).*?(?:all|any|your).*?(?:activity|actions|communications|behavior)'
                ],
                'severity': 25,
                'description': 'Privacy rights compromised'
            },
            'due_process': {
                'patterns': [
                    r'(?i)(?:waive|give.*?up|forfeit|surrender).*?(?:right.*?to|rights.*?of).*?(?:trial|jury|court|appeal|hearing)',
                    r'(?i)(?:binding|mandatory|required).*?arbitration.*?(?:individual|private).*?basis',
                    r'(?i)(?:no.*?class.*?action|waive.*?class.*?action|individual.*?claims.*?only)'
                ],
                'severity': 20,
                'description': 'Legal rights and due process removed'
            },
            'data_control': {
                'patterns': [
                    r'(?i)(?:cannot|unable|not.*?possible|refuse|deny).*?(?:delete|remove|access|download|export).*?(?:data|information|account)',
                    r'(?i)(?:retain|keep|maintain).*?(?:data|information).*?(?:indefinitely|permanently|as.*?long.*?as)',
                    r'(?i)(?:no.*?data.*?portability|cannot.*?export|not.*?transferable)'
                ],
                'severity': 15,
                'description': 'Data ownership and control stripped'
            },
            'unilateral_changes': {
                'patterns': [
                    r'(?i)(?:modify|change|update|alter).*?(?:terms|agreement|policy).*?(?:without.*?notice|any.*?time|sole.*?discretion)',
                    r'(?i)(?:continued.*?use|ongoing.*?use).*?(?:constitutes|means|deemed).*?(?:acceptance|agreement)',
                    r'(?i)(?:effective.*?immediately|immediate.*?effect).*?(?:upon.*?posting|when.*?posted)'
                ],
                'severity': 15,
                'description': 'Unilateral modification rights'
            },
            'irreversible_consequences': {
                'patterns': [
                    r'(?i)(?:permanent|permanently|irreversible|irreversibly|final|irrevocable).*?(?:deletion|removal|termination|suspension|ban)',
                    r'(?i)(?:no.*?refund|non-refundable).*?(?:under.*?any|in.*?any|regardless)',
                    r'(?i)(?:auto.*?renew|automatic.*?renewal).*?(?:unless|until).*?(?:cancel|opt.*?out).*?(?:before|prior)'
                ],
                'severity': 18,
                'description': 'Irreversible consequences imposed'
            }
        }
        
        # Multi-clause trap detection
        self.compound_traps = {
            'digital_dictatorship': [
                'unilateral_changes',
                'due_process',
                'irreversible_consequences'
            ],
            'data_hostage': [
                'data_control',
                'privacy_rights',
                'irreversible_consequences'
            ],
            'legal_immunity': [
                'due_process',
                'liability_limitation',
                'unilateral_changes'
            ]
        }
        
        # User risk personas
        self.risk_personas = {
            'healthcare_provider': {
                'high_risk_categories': ['privacy_rights', 'data_control'],
                'multiplier': 2.0,
                'description': 'Patient data protection required'
            },
            'small_business': {
                'high_risk_categories': ['due_process', 'irreversible_consequences'],
                'multiplier': 1.5,
                'description': 'Limited legal resources for disputes'
            },
            'developer': {
                'high_risk_categories': ['data_control', 'unilateral_changes'],
                'multiplier': 1.3,
                'description': 'API dependencies and code integration'
            },
            'individual_user': {
                'high_risk_categories': ['privacy_rights', 'due_process'],
                'multiplier': 1.0,
                'description': 'Personal data and consumer protection'
            }
        }
        
        # Structural dark patterns
        self.structural_patterns = {
            'cancellation_friction': {
                'patterns': [
                    r'(?i)(?:cancel|unsubscribe|opt.*?out).*?(?:must|required|need.*?to).*?(?:call|phone|write|mail|contact.*?customer.*?service)',
                    r'(?i)(?:cancellation|termination).*?(?:requires|needs).*?(?:\d+).*?(?:days|weeks|months).*?(?:notice|advance.*?notice)',
                    r'(?i)(?:online|website|digital).*?(?:cancellation|termination).*?(?:not.*?available|not.*?permitted|unavailable)'
                ],
                'friction_score': 8,
                'description': 'High friction cancellation process'
            },
            'auto_renewal_trap': {
                'patterns': [
                    r'(?i)(?:automatic|auto).*?(?:renewal|billing).*?(?:unless|until).*?(?:cancel|opt.*?out).*?(?:before|prior.*?to).*?(?:renewal|billing).*?(?:date|period)',
                    r'(?i)(?:trial|promotional).*?(?:ends|expires).*?(?:automatic|auto).*?(?:billing|subscription|renewal)',
                    r'(?i)(?:difficult|complex|complicated).*?(?:to|process.*?to).*?(?:cancel|unsubscribe|opt.*?out)'
                ],
                'friction_score': 7,
                'description': 'Auto-renewal with difficult opt-out'
            },
            'hidden_cost_structure': {
                'patterns': [
                    r'(?i)(?:additional|extra|hidden|other).*?(?:fees|charges|costs).*?(?:may|might|could|will).*?(?:apply|be.*?charged)',
                    r'(?i)(?:excluding|not.*?including|separate|plus).*?(?:taxes|fees|shipping|handling|processing)',
                    r'(?i)(?:fees|charges).*?(?:subject.*?to.*?change|may.*?vary|at.*?current.*?rates)'
                ],
                'friction_score': 6,
                'description': 'Hidden or variable cost structure'
            }
        }

    def analyze_power_structure(self, text: str, user_persona: str = 'individual_user') -> Dict[str, Any]:
        """Comprehensive power structure analysis implementing the 5 pillars"""
        
        # Split into sentences for analysis
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        
        # PILLAR 1: Power Imbalance Detection
        power_analysis = self._analyze_power_imbalance(sentences, text)
        
        # PILLAR 2: Structural Dark Pattern Scanning  
        structural_analysis = self._scan_structural_dark_patterns(text)
        
        # PILLAR 3: AI/Data Commodification Scanning
        commodification_analysis = self._scan_data_commodification(text)
        
        # PILLAR 4: Weighted Risk Scoring
        risk_analysis = self._calculate_weighted_risk_score(power_analysis, structural_analysis, commodification_analysis, user_persona)
        
        # PILLAR 5: Explanatory Flag Reporting
        flag_reports = self._generate_explanatory_flags(text, sentences, power_analysis, structural_analysis, commodification_analysis)
        
        # Legacy compatibility fields
        rights_analysis = self._calculate_rights_stripping_index(sentences, user_persona)
        transparency_analysis = self._analyze_real_transparency(text)
        power_flow = self._generate_power_flow_map(sentences)
        
        return {
            # New 5-pillar structure
            'power_imbalance_analysis': power_analysis,
            'structural_dark_patterns': structural_analysis,
            'data_commodification': commodification_analysis,
            'weighted_risk_assessment': risk_analysis,
            'explanatory_flags': flag_reports,
            
            # Legacy compatibility
            'power_distribution': power_analysis,
            'rights_stripping_index': rights_analysis,
            'transparency_empowerment': transparency_analysis,
            'power_flow_map': power_flow,
            'overall_assessment': risk_analysis,
            'user_persona': user_persona,
            'sentences_analyzed': len(sentences)
        }
    
    def _analyze_power_imbalance(self, sentences: List[str], full_text: str) -> Dict[str, Any]:
        """PILLAR 1: Detect who holds control over rules, data, rights"""
        power_control_analysis = {}
        total_company_power = 0
        total_user_power = 0
        control_mechanisms = []
        
        for control_type, pattern_data in self.power_control_patterns.items():
            detected_clauses = []
            power_score = 0
            
            for sentence in sentences:
                for pattern in pattern_data['patterns']:
                    if re.search(pattern, sentence):
                        clause_info = {
                            'text': sentence.strip(),
                            'pattern_matched': pattern,
                            'power_holder': pattern_data['power_holder'],
                            'impact_level': pattern_data['impact'],
                            'weight': pattern_data['weight']
                        }
                        detected_clauses.append(clause_info)
                        power_score += pattern_data['weight']
                        
                        if pattern_data['power_holder'] == 'company':
                            total_company_power += pattern_data['weight']
                        else:
                            total_user_power += pattern_data['weight']
            
            if detected_clauses:
                power_control_analysis[control_type] = {
                    'detected': True,
                    'clause_count': len(detected_clauses),
                    'power_score': power_score,
                    'clauses': detected_clauses,
                    'primary_holder': pattern_data['power_holder'],
                    'impact_assessment': pattern_data['impact']
                }
                control_mechanisms.extend(detected_clauses)
        
        # Calculate realistic power distribution
        base_company_power = 60  # Companies inherently control the contract
        company_power_percentage = min(95, base_company_power + (total_company_power / 4))
        user_power_percentage = max(5, 100 - company_power_percentage + (total_user_power / 3))
        
        # Cap user power realistically
        if user_power_percentage > 25:
            user_power_percentage = 25
            company_power_percentage = 75
        
        digital_dictatorship = company_power_percentage > 85 and total_user_power < 10
        
        return {
            'company_power_percentage': round(company_power_percentage, 1),
            'user_power_percentage': round(user_power_percentage, 1),
            'power_imbalance_score': round(abs(company_power_percentage - user_power_percentage), 1),
            'digital_dictatorship': digital_dictatorship,
            'control_mechanisms_detected': len(control_mechanisms),
            'power_control_breakdown': power_control_analysis,
            'total_company_power_points': total_company_power,
            'total_user_power_points': total_user_power,
            'power_assessment': self._get_power_assessment(company_power_percentage, digital_dictatorship)
        }
    
    def _analyze_power_distribution(self, sentences: List[str]) -> Dict[str, Any]:
        """Analyze who holds power in each clause"""
        power_scores = {'company': 0, 'user': 0, 'shared': 0}
        clause_analysis = []
        
        for sentence in sentences:
            company_power = 0
            user_power = 0
            
            # Check company power patterns
            for pattern in self.power_patterns['company_absolute']['patterns']:
                if re.search(pattern, sentence):
                    company_power += self.power_patterns['company_absolute']['weight']
            
            # Check user empowerment patterns
            for pattern in self.power_patterns['user_empowerment']['patterns']:
                if re.search(pattern, sentence):
                    user_power += abs(self.power_patterns['user_empowerment']['weight'])
            
            # Determine power holder for this clause
            if company_power > user_power * 1.5:
                power_holder = 'company'
                power_scores['company'] += 1
            elif user_power > company_power:
                power_holder = 'user'
                power_scores['user'] += 1
            else:
                power_holder = 'shared'
                power_scores['shared'] += 1
            
            if company_power > 0 or user_power > 0:
                clause_analysis.append({
                    'text': sentence[:100] + '...' if len(sentence) > 100 else sentence,
                    'power_holder': power_holder,
                    'company_power_score': company_power,
                    'user_power_score': user_power
                })
        
        total_clauses = sum(power_scores.values())
        if total_clauses > 0:
            company_percentage = (power_scores['company'] / total_clauses) * 100
        else:
            company_percentage = 0
        
        # More realistic power calculation - start with base company advantage
        base_company_power = 70  # Companies always have structural advantage
        
        # Adjust based on detected patterns
        if total_clauses > 0:
            power_adjustment = (power_scores['company'] / total_clauses) * 25  # Max 25 point increase
            company_percentage = min(95, base_company_power + power_adjustment)
        else:
            company_percentage = base_company_power
        
        user_percentage = max(5, 100 - company_percentage)
        
        # Ensure realistic caps - users rarely get >30% power in ToS
        if user_percentage > 30:
            user_percentage = 30
            company_percentage = 70
        
        # Digital dictatorship detection (company has >85% power)
        is_dictatorship = company_percentage > 85
        is_dictatorship = company_percentage > 75 and power_scores['user'] < 2
        
        return {
            'company_power_percentage': round(company_percentage, 1),
            'user_power_percentage': round(user_percentage, 1),
            'power_imbalance_score': round(abs(company_percentage - user_percentage), 1),
            'digital_dictatorship': is_dictatorship,
            'clause_breakdown': clause_analysis,
            'power_assessment': self._get_power_assessment(company_percentage, is_dictatorship)
        }
    
    def _calculate_rights_stripping_index(self, sentences: List[str], user_persona: str) -> Dict[str, Any]:
        """Calculate how many user rights are being stripped away"""
        rights_violations = {}
        total_severity = 0
        categories_detected = set()
        
        for sentence in sentences:
            for category, pattern_data in self.rights_erosion_patterns.items():
                for pattern in pattern_data['patterns']:
                    if re.search(pattern, sentence):
                        if category not in rights_violations:
                            rights_violations[category] = {
                                'count': 0,
                                'severity': pattern_data['severity'],
                                'description': pattern_data['description'],
                                'examples': []
                            }
                        
                        rights_violations[category]['count'] += 1
                        rights_violations[category]['examples'].append(
                            sentence[:100] + '...' if len(sentence) > 100 else sentence
                        )
                        categories_detected.add(category)
                        
                        # Apply persona multiplier
                        persona_data = self.risk_personas.get(user_persona, self.risk_personas['individual_user'])
                        if category in persona_data.get('high_risk_categories', []):
                            total_severity += pattern_data['severity'] * persona_data['multiplier']
                        else:
                            total_severity += pattern_data['severity']
        
        # Calculate rights vs control balance (1-10 scale)
        max_possible_severity = sum(data['severity'] for data in self.rights_erosion_patterns.values()) * 3
        if max_possible_severity > 0:
            rights_score = max(1, 10 - (total_severity / max_possible_severity * 9))
        else:
            rights_score = 10
        
        return {
            'rights_violations': rights_violations,
            'total_severity_score': total_severity,
            'rights_vs_control_balance': rights_score,
            'categories_detected': list(categories_detected),
            'red_flag_triggered': rights_score < 4,
            'persona_risk_assessment': self._get_persona_risk_assessment(user_persona, rights_violations)
        }
    
    def _detect_compound_traps(self, categories_detected: set) -> Dict[str, Any]:
        """Detect dangerous combinations of clauses that form legal traps"""
        detected_traps = {}
        
        for trap_name, required_categories in self.compound_traps.items():
            detected_categories = [cat for cat in required_categories if cat in categories_detected]
            
            if len(detected_categories) >= len(required_categories) * 0.67:  # 67% threshold
                trap_severity = len(detected_categories) / len(required_categories)
                detected_traps[trap_name] = {
                    'detected_categories': detected_categories,
                    'completion_percentage': trap_severity * 100,
                    'severity': 'critical' if trap_severity > 0.8 else 'high',
                    'description': self._get_trap_description(trap_name)
                }
        
        return {
            'detected_traps': detected_traps,
            'trap_count': len(detected_traps),
            'highest_severity_trap': max(detected_traps.items(), key=lambda x: x[1]['completion_percentage']) if detected_traps else None
        }
    
    def _analyze_structural_patterns(self, text: str) -> Dict[str, Any]:
        """Analyze structural dark patterns beyond just language"""
        
        structural_issues = {
            'power_loops': 0,
            'friction_gradients': 0, 
            'reflexive_clauses': 0,
            'ml_data_extraction': 0
        }
        
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        
        # Check for structural patterns
        for category, pattern_data in self.structural_patterns.items():
            for pattern in pattern_data['patterns']:
                matches = re.findall(pattern, text)
                if matches:
                    structural_issues[category] += len(matches)
        
        # Check for ML data extraction patterns specifically
        ml_patterns = self.power_patterns.get('ml_data_extraction', {}).get('patterns', [])
        for pattern in ml_patterns:
            matches = re.findall(pattern, text)
            if matches:
                structural_issues['ml_data_extraction'] += len(matches)
        
        # Calculate friction score (0-100, higher = more friction)
        total_issues = sum(structural_issues.values())
        friction_score = min(100, total_issues * 20)  # Each issue adds 20 points
        
        return {
            'structural_issues': structural_issues,
            'friction_score': friction_score,
            'dark_patterns_detected': total_issues,
            'structural_assessment': self._get_structural_assessment(friction_score)
        }
    
    def _analyze_real_transparency(self, text: str) -> Dict[str, Any]:
        """Analyze real transparency = informed control, not just clarity"""
        transparency_factors = {
            'meaningful_notice': {
                'patterns': [
                    r'(?i)(?:advance|prior|reasonable).*?(?:notice|notification).*?(?:before|prior.*?to).*?(?:changes|modifications)',
                    r'(?i)(?:notify|inform|alert).*?(?:you|users).*?(?:before|in.*?advance).*?(?:important|significant).*?(?:changes|updates)'
                ],
                'score': 25
            },
            'meaningful_opt_out': {
                'patterns': [
                    r'(?i)(?:easy|simple|straightforward).*?(?:to|process.*?to).*?(?:cancel|unsubscribe|opt.*?out)',
                    r'(?i)(?:one.*?click|single.*?click|online).*?(?:cancellation|unsubscribe|opt.*?out)',
                    r'(?i)(?:no.*?questions.*?asked|immediate|instant).*?(?:cancellation|termination)'
                ],
                'score': 25
            },
            'data_deletion_possible': {
                'patterns': [
                    r'(?i)(?:you.*?can|users.*?may|right.*?to).*?(?:delete|remove|erase).*?(?:all|your|personal).*?(?:data|information)',
                    r'(?i)(?:complete|full|permanent).*?(?:data|account).*?(?:deletion|removal).*?(?:available|possible)'
                ],
                'score': 25
            },
            'comparison_enabled': {
                'patterns': [
                    r'(?i)(?:compare|comparison).*?(?:plans|options|alternatives).*?(?:available|provided)',
                    r'(?i)(?:clear|transparent).*?(?:pricing|costs|fees).*?(?:structure|breakdown|comparison)'
                ],
                'score': 25
            }
        }
        
        transparency_score = 0
        detected_factors = {}
        
        for factor, data in transparency_factors.items():
            factor_detected = False
            for pattern in data['patterns']:
                if re.search(pattern, text):
                    factor_detected = True
                    break
            
            if factor_detected:
                transparency_score += data['score']
                detected_factors[factor] = True
            else:
                detected_factors[factor] = False
        
        return {
            'transparency_score': round(transparency_score, 1),
            'empowerment_factors': detected_factors,
            'real_transparency': transparency_score > 60,
            'transparency_assessment': self._get_transparency_assessment(transparency_score)
        }
    
    def _generate_power_flow_map(self, sentences: List[str]) -> Dict[str, str]:
        """Generate a power flow map showing who controls key decisions"""
        power_map = {
            'rule_changes': 'unclear',
            'service_termination': 'unclear',
            'data_ownership': 'unclear',
            'dispute_resolution': 'unclear'
        }
        
        rule_change_patterns = [
            r'(?i)(?:we|company).*?(?:may|can|will).*?(?:modify|change|update).*?(?:terms|rules|policy)',
            r'(?i)(?:you|user).*?(?:can|may).*?(?:modify|negotiate|change).*?(?:terms|agreement)'
        ]
        
        termination_patterns = [
            r'(?i)(?:we|company).*?(?:may|can|will).*?(?:terminate|suspend|end).*?(?:service|account)',
            r'(?i)(?:you|user).*?(?:can|may).*?(?:terminate|cancel|end).*?(?:service|account)'
        ]
        
        data_patterns = [
            r'(?i)(?:we|company).*?(?:own|control|retain).*?(?:data|information)',
            r'(?i)(?:you|user).*?(?:own|control|retain).*?(?:data|information)'
        ]
        
        dispute_patterns = [
            r'(?i)(?:arbitration|company.*?decides|binding.*?arbitration)',
            r'(?i)(?:court|legal.*?system|jury.*?trial|user.*?choice)'
        ]
        
        # Analyze each category - fix dispute resolution logic
        for sentence in sentences:
            # Rule changes
            if any(re.search(p, sentence) for p in rule_change_patterns[:1]):
                power_map['rule_changes'] = 'company'
            elif any(re.search(p, sentence) for p in rule_change_patterns[1:]):
                power_map['rule_changes'] = 'user'
            
            # Service termination
            if any(re.search(p, sentence) for p in termination_patterns[:1]):
                power_map['service_termination'] = 'company'
            elif any(re.search(p, sentence) for p in termination_patterns[1:]):
                power_map['service_termination'] = 'shared'
            
            # Data ownership
            if any(re.search(p, sentence) for p in data_patterns[:1]):
                power_map['data_ownership'] = 'company'
            elif any(re.search(p, sentence) for p in data_patterns[1:]):
                power_map['data_ownership'] = 'user'
            
            # Dispute resolution - fix the logic (Ontario courts = company power)
            if re.search(r'(?i)(?:arbitration|company.*?decides|binding.*?arbitration)', sentence):
                power_map['dispute_resolution'] = 'company'
            elif re.search(r'(?i)(?:disputes?|claims?).*?(?:shall|must|will).*?(?:be.*?governed|resolved|subject).*?(?:by|in|under).*?(?:laws?.*?of|courts?.*?of|jurisdiction.*?of)', sentence):
                power_map['dispute_resolution'] = 'company'  # Courts chosen by company = company power
            elif re.search(r'(?i)(?:you.*?may.*?choose|user.*?choice|multiple.*?options).*?(?:court|arbitration|dispute)', sentence):
                power_map['dispute_resolution'] = 'user'
        
        return power_map
    
    def _calculate_overall_power_score(self, power_analysis, rights_analysis, structural_analysis, transparency_analysis) -> Dict[str, Any]:
        """Calculate overall power score and assessment"""
        
        # Extract key metrics
        company_power = power_analysis['company_power_percentage']
        rights_score = rights_analysis['rights_vs_control_balance']
        friction_score = structural_analysis['friction_score']
        transparency_score = transparency_analysis['transparency_score']
        
        # Calculate overall score - realistic risk assessment
        # Start with base risk of 50 (terms of service are inherently risky)
        base_risk = 50
        
        # Add risk based on company power (0-40 points)
        power_risk = (company_power - 60) * 0.8 if company_power > 60 else 0
        
        # Add risk based on rights erosion (0-30 points)
        rights_risk = (10 - rights_score) * 3
        
        # Add risk based on friction (0-20 points)
        friction_risk = friction_score * 0.2
        
        # Reduce risk based on transparency (0-15 points reduction)
        transparency_benefit = (transparency_score - 30) * 0.3 if transparency_score > 30 else 0
        
        # Calculate final score
        overall_score = max(15, min(90, base_risk + power_risk + rights_risk + friction_risk - transparency_benefit))
        
        # Determine assessment level with realistic thresholds
        if overall_score <= 30:
            assessment = "User-Friendly"
            risk_level = "low"
        elif overall_score <= 60:
            assessment = "Moderate Risk"
            risk_level = "medium"
        else:
            assessment = "High Risk"
            risk_level = "high"
        
        return {
            'overall_score': round(overall_score, 1),
            'assessment': assessment,
            'risk_level': risk_level,
            'component_scores': {
                'company_power': round(company_power, 1),
                'rights_protection': round(rights_score, 1),
                'friction_score': round(friction_score, 1),
                'transparency': round(transparency_score, 1)
            },
            'critical_issues': self._identify_critical_issues(power_analysis, rights_analysis, structural_analysis)
        }
    
    def _get_power_assessment(self, company_percentage: float, is_dictatorship: bool) -> str:
        """Get human-readable power assessment"""
        if is_dictatorship:
            return "Digital Dictatorship: Company has absolute control"
        elif company_percentage > 85:
            return "Heavily Company-Favored: Significant power imbalance"
        elif company_percentage > 75:
            return "Company-Favored: Notable power imbalance" 
        elif company_percentage > 65:
            return "Moderately Company-Favored: Some imbalance"
        else:
            return "Reasonably Balanced: Acceptable power distribution"
    
    def _get_persona_risk_assessment(self, persona: str, rights_violations: Dict) -> str:
        """Get persona-specific risk assessment"""
        persona_data = self.risk_personas.get(persona, self.risk_personas['individual_user'])
        high_risk_detected = any(cat in rights_violations for cat in persona_data.get('high_risk_categories', []))
        
        if high_risk_detected:
            return f"HIGH RISK: As a {persona.replace('_', ' ')}, {persona_data['description']} - critical violations detected"
        else:
            return f"Moderate risk for {persona.replace('_', ' ')} use case"
    
    def _get_trap_description(self, trap_name: str) -> str:
        """Get description for compound traps"""
        descriptions = {
            'digital_dictatorship': 'Complete erosion of user rights and legal recourse',
            'data_hostage': 'User data held hostage with no meaningful control or deletion',
            'legal_immunity': 'Company shields itself from all legal accountability'
        }
        return descriptions.get(trap_name, 'Compound legal trap detected')
    
    def _get_structural_assessment(self, friction_score: int) -> str:
        """Get structural assessment"""
        if friction_score > 20:
            return "Extreme friction - users are structurally trapped"
        elif friction_score > 15:
            return "High friction - difficult for users to exercise rights"
        elif friction_score > 8:
            return "Moderate friction in user processes"
        else:
            return "Low friction - reasonable user experience"
    
    def _get_transparency_assessment(self, score: int) -> str:
        """Get transparency assessment"""
        if score > 75:
            return "High transparency with meaningful user control"
        elif score > 50:
            return "Moderate transparency with some user empowerment"
        elif score > 25:
            return "Limited transparency - minimal user control"
        else:
            return "Low transparency - users lack meaningful choices"
    
    def _identify_critical_issues(self, power_analysis, rights_analysis, structural_analysis) -> List[str]:
        """Identify the most critical issues"""
        issues = []
        
        if power_analysis['digital_dictatorship']:
            issues.append("Digital dictatorship detected")
        
        if rights_analysis['red_flag_triggered']:
            issues.append("Rights vs control balance critically low")
        
        if structural_analysis.get('dark_patterns_detected', 0) > 3:
            issues.append("Multiple structural dark patterns detected")
        
        if power_analysis['company_power_percentage'] > 80:
            issues.append("Extreme power asymmetry favoring company")
        
        return issues
    
    def _scan_structural_dark_patterns(self, text: str) -> Dict[str, Any]:
        """PILLAR 2: Go beyond language — find manipulative structure"""
        detected_patterns = {}
        total_manipulation_score = 0
        manipulation_mechanisms = []
        
        for pattern_type, pattern_data in self.structural_dark_patterns.items():
            pattern_detected = False
            clause_matches = []
            
            for pattern in pattern_data['patterns']:
                matches = re.finditer(pattern, text)
                for match in matches:
                    pattern_detected = True
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 50)
                    context = text[start:end].strip()
                    
                    clause_info = {
                        'matched_text': match.group(),
                        'context': context,
                        'manipulation_type': pattern_data['manipulation_type'],
                        'damage_level': pattern_data['damage_level'],
                        'weight': pattern_data['weight']
                    }
                    clause_matches.append(clause_info)
                    total_manipulation_score += pattern_data['weight']
            
            if pattern_detected:
                detected_patterns[pattern_type] = {
                    'detected': True,
                    'clause_count': len(clause_matches),
                    'manipulation_type': pattern_data['manipulation_type'],
                    'damage_level': pattern_data['damage_level'],
                    'total_weight': len(clause_matches) * pattern_data['weight'],
                    'clauses': clause_matches
                }
                manipulation_mechanisms.extend(clause_matches)
        
        # Calculate structural manipulation score
        friction_score = min(100, total_manipulation_score)
        manipulation_severity = self._assess_manipulation_severity(total_manipulation_score)
        
        return {
            'structural_patterns_detected': detected_patterns,
            'total_patterns_found': len(detected_patterns),
            'friction_score': friction_score,
            'manipulation_score': total_manipulation_score,
            'manipulation_severity': manipulation_severity,
            'dark_patterns_detected': len(manipulation_mechanisms),
            'structural_assessment': self._get_structural_assessment(friction_score),
            'manipulation_mechanisms': manipulation_mechanisms
        }
    
    def _scan_data_commodification(self, text: str) -> Dict[str, Any]:
        """PILLAR 3: Flag hidden data training, resale, behavioral profiling"""
        commodification_detected = {}
        total_commodification_score = 0
        hidden_monetization = []
        
        for commodity_type, pattern_data in self.data_commodification_patterns.items():
            commodity_detected = False
            clause_matches = []
            
            for pattern in pattern_data['patterns']:
                matches = re.finditer(pattern, text)
                for match in matches:
                    commodity_detected = True
                    start = max(0, match.start() - 75)
                    end = min(len(text), match.end() + 75)
                    context = text[start:end].strip()
                    
                    clause_info = {
                        'matched_text': match.group(),
                        'context': context,
                        'commodification_type': pattern_data['commodification_type'],
                        'opt_out_available': pattern_data['opt_out_available'],
                        'transparency_level': pattern_data['transparency_level'],
                        'weight': pattern_data['weight'],
                        'explanation': self._explain_commodification_risk(pattern_data['commodification_type'])
                    }
                    clause_matches.append(clause_info)
                    total_commodification_score += pattern_data['weight']
            
            if commodity_detected:
                commodification_detected[commodity_type] = {
                    'detected': True,
                    'clause_count': len(clause_matches),
                    'commodification_type': pattern_data['commodification_type'],
                    'transparency_level': pattern_data['transparency_level'],
                    'opt_out_available': pattern_data['opt_out_available'],
                    'total_weight': len(clause_matches) * pattern_data['weight'],
                    'clauses': clause_matches,
                    'risk_explanation': self._explain_commodification_risk(pattern_data['commodification_type'])
                }
                hidden_monetization.extend(clause_matches)
        
        # Calculate data commodification risk
        commodification_risk = min(100, total_commodification_score)
        data_safety_score = max(0, 100 - commodification_risk)
        
        return {
            'commodification_patterns': commodification_detected,
            'total_commodification_types': len(commodification_detected),
            'commodification_risk_score': commodification_risk,
            'data_safety_score': data_safety_score,
            'hidden_monetization_count': len(hidden_monetization),
            'ai_training_detected': 'ai_training_extraction' in commodification_detected,
            'behavioral_profiling_detected': 'behavioral_profiling' in commodification_detected,
            'data_resale_detected': 'data_resale_licensing' in commodification_detected,
            'perpetual_licensing_detected': 'perpetual_licensing' in commodification_detected,
            'commodification_assessment': self._assess_commodification_level(commodification_risk),
            'hidden_monetization_mechanisms': hidden_monetization
        }
    
    def _calculate_weighted_risk_score(self, power_analysis: Dict, structural_analysis: Dict, 
                                     commodification_analysis: Dict, user_persona: str) -> Dict[str, Any]:
        """PILLAR 4: Prioritize high-damage clauses, not just clause count"""
        
        # Calculate weighted risk components based on actual damage potential
        power_risk = self._calculate_power_risk_weighted(power_analysis)
        structural_risk = self._calculate_structural_risk_weighted(structural_analysis)
        commodification_risk = commodification_analysis.get('commodification_risk_score', 0)
        
        # Check for critical combinations that should trigger high scores
        is_digital_dictatorship = power_analysis.get('digital_dictatorship', False)
        has_dispute_resolution_control = 'dispute_resolution_power' in power_analysis.get('power_control_breakdown', {})
        has_data_ownership_control = 'data_ownership_control' in power_analysis.get('power_control_breakdown', {})
        has_critical_commodification = commodification_risk > 60
        
        # Base weighted combination
        total_weighted_risk = (
            power_risk * 0.35 +           # Power imbalance is critical
            commodification_risk * 0.30 + # Data commodification is very serious
            structural_risk * 0.25 +      # Structural manipulation matters
            self._get_persona_risk_modifier(user_persona) * 0.10  # Persona-specific adjustments
        )
        
        # Critical escalation logic - if digital dictatorship detected, force high score
        if is_digital_dictatorship:
            total_weighted_risk = max(total_weighted_risk, 85)  # Digital dictatorship = critical risk
        elif has_dispute_resolution_control and (has_data_ownership_control or has_critical_commodification):
            total_weighted_risk = max(total_weighted_risk, 75)  # Arbitration + data control = high risk
        elif has_dispute_resolution_control:
            total_weighted_risk = max(total_weighted_risk, 65)  # Arbitration alone = medium-high risk
        elif has_critical_commodification:
            total_weighted_risk = max(total_weighted_risk, 60)  # Critical data issues = medium risk floor
        
        # Overall risk assessment
        risk_level = self._determine_risk_level(total_weighted_risk)
        
        return {
            'overall_score': round(total_weighted_risk, 1),
            'risk_level': risk_level,
            'assessment': self._get_risk_assessment(total_weighted_risk),
            'component_scores': {
                'power_risk': round(power_risk, 1),
                'structural_risk': round(structural_risk, 1), 
                'commodification_risk': round(commodification_risk, 1)
            },
            'high_damage_clauses': self._identify_high_damage_clauses(power_analysis, structural_analysis, commodification_analysis),
            'critical_issues': self._identify_critical_issues_weighted(power_analysis, structural_analysis, commodification_analysis),
            'escalation_triggered': is_digital_dictatorship or (has_dispute_resolution_control and has_data_ownership_control)
        }
    
    def _generate_explanatory_flags(self, text: str, sentences: List[str], power_analysis: Dict,
                                  structural_analysis: Dict, commodification_analysis: Dict) -> Dict[str, Any]:
        """PILLAR 5: Quote, explain, and rate every red flag clearly"""
        
        all_flags = []
        flag_categories = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        # Extract flags from power analysis
        for control_type, control_data in power_analysis.get('power_control_breakdown', {}).items():
            if control_data.get('detected'):
                for clause in control_data['clauses']:
                    flag = {
                        'flag_id': f"power_{control_type}_{len(all_flags)}",
                        'category': 'power_imbalance',
                        'severity': control_data['impact_assessment'],
                        'quoted_text': clause['text'],
                        'explanation': self._explain_power_flag(control_type, clause),
                        'risk_rating': self._rate_flag_risk(control_data['impact_assessment']),
                        'user_impact': self._describe_user_impact(control_type, clause),
                        'mitigation_advice': self._suggest_mitigation(control_type)
                    }
                    all_flags.append(flag)
                    flag_categories[control_data['impact_assessment']].append(flag)
        
        # Extract flags from structural analysis
        for pattern_type, pattern_data in structural_analysis.get('structural_patterns_detected', {}).items():
            if pattern_data.get('detected'):
                for clause in pattern_data['clauses']:
                    flag = {
                        'flag_id': f"structural_{pattern_type}_{len(all_flags)}",
                        'category': 'structural_manipulation',
                        'severity': pattern_data['damage_level'],
                        'quoted_text': clause['context'],
                        'explanation': self._explain_structural_flag(pattern_type, clause),
                        'risk_rating': self._rate_flag_risk(pattern_data['damage_level']),
                        'user_impact': self._describe_structural_impact(pattern_type, clause),
                        'mitigation_advice': self._suggest_structural_mitigation(pattern_type)
                    }
                    all_flags.append(flag)
                    flag_categories[pattern_data['damage_level']].append(flag)
        
        # Extract flags from commodification analysis
        for commodity_type, commodity_data in commodification_analysis.get('commodification_patterns', {}).items():
            if commodity_data.get('detected'):
                for clause in commodity_data['clauses']:
                    severity = self._determine_commodification_severity(commodity_data['commodification_type'])
                    flag = {
                        'flag_id': f"commodity_{commodity_type}_{len(all_flags)}",
                        'category': 'data_commodification',
                        'severity': severity,
                        'quoted_text': clause['context'],
                        'explanation': clause['explanation'],
                        'risk_rating': self._rate_flag_risk(severity),
                        'user_impact': self._describe_commodification_impact(commodity_type, clause),
                        'mitigation_advice': self._suggest_commodification_mitigation(commodity_type)
                    }
                    all_flags.append(flag)
                    flag_categories[severity].append(flag)
        
        return {
            'total_flags': len(all_flags),
            'all_flags': all_flags,
            'flags_by_severity': flag_categories,
            'critical_flag_count': len(flag_categories['critical']),
            'high_flag_count': len(flag_categories['high']),
            'medium_flag_count': len(flag_categories['medium']),
            'low_flag_count': len(flag_categories['low']),
            'flag_summary': self._generate_flag_summary(flag_categories),
            'recommended_action': self._recommend_action_based_on_flags(flag_categories)
        }
    
    # Helper methods for the 5 pillars
    def _explain_commodification_risk(self, commodification_type: str) -> str:
        explanations = {
            'ai_training': "Your data is being used to train AI models without clear consent or compensation.",
            'behavioral_profiling': "Your behavior patterns are being analyzed to create detailed profiles for targeting.",
            'data_resale': "Your personal information may be sold or licensed to third parties for profit.",
            'perpetual_rights': "The company claims permanent, irrevocable rights to your content and data."
        }
        return explanations.get(commodification_type, "Unknown data commodification detected.")
    
    def _assess_manipulation_severity(self, score: int) -> str:
        if score >= 80: return "Extreme manipulation detected"
        elif score >= 60: return "High manipulation risk"
        elif score >= 40: return "Moderate manipulation present"
        elif score >= 20: return "Some manipulative elements"
        else: return "Minimal manipulation detected"
    
    def _assess_commodification_level(self, risk_score: int) -> str:
        if risk_score >= 80: return "Extensive data commodification"
        elif risk_score >= 60: return "Significant monetization of user data"
        elif risk_score >= 40: return "Moderate data commercialization"
        elif risk_score >= 20: return "Limited data monetization"
        else: return "Minimal data commodification"
    
    def _calculate_power_risk_weighted(self, power_analysis: Dict) -> float:
        """Calculate power risk with weighted damage assessment"""
        company_power = power_analysis.get('company_power_percentage', 70)
        control_mechanisms = power_analysis.get('control_mechanisms_detected', 0)
        
        # Higher company power = higher risk
        power_risk = (company_power - 50) * 1.2 if company_power > 50 else 0
        
        # Multiple control mechanisms compound the risk
        mechanism_risk = control_mechanisms * 5
        
        return min(100, power_risk + mechanism_risk)
    
    def _calculate_structural_risk_weighted(self, structural_analysis: Dict) -> float:
        """Calculate structural risk with weighted damage assessment"""
        return structural_analysis.get('friction_score', 0)
    
    def _get_persona_risk_modifier(self, persona: str) -> float:
        """Get persona-specific risk modifiers"""
        modifiers = {
            'individual_user': 10,    # Higher vulnerability
            'business_user': 5,       # Some protection
            'developer': 8,           # Technical awareness but still vulnerable
            'healthcare': 15          # Highest sensitivity
        }
        return modifiers.get(persona, 10)
    
    def _determine_risk_level(self, score: float) -> str:
        if score >= 75: return "critical"  # Lowered threshold for critical
        elif score >= 60: return "high"
        elif score >= 40: return "medium"
        else: return "low"
    
    def _get_risk_assessment(self, score: float) -> str:
        if score >= 75: return "Critical Risk - Avoid if possible"
        elif score >= 60: return "High Risk - Proceed with extreme caution" 
        elif score >= 40: return "Moderate Risk - Review carefully"
        else: return "Acceptable Risk - Standard precautions apply"
    
    def _identify_high_damage_clauses(self, power_analysis: Dict, structural_analysis: Dict, commodification_analysis: Dict) -> List[str]:
        """Identify the most damaging clauses"""
        high_damage = []
        
        # Check for critical power imbalances
        power_breakdown = power_analysis.get('power_control_breakdown', {})
        for control_type, data in power_breakdown.items():
            if data.get('impact_assessment') == 'critical':
                high_damage.append(f"Critical power imbalance: {control_type}")
        
        # Check for high-damage structural patterns
        structural_patterns = structural_analysis.get('structural_patterns_detected', {})
        for pattern_type, data in structural_patterns.items():
            if data.get('damage_level') == 'critical':
                high_damage.append(f"Critical structural manipulation: {pattern_type}")
        
        # Check for data commodification
        commodity_patterns = commodification_analysis.get('commodification_patterns', {})
        for commodity_type, data in commodity_patterns.items():
            if data.get('commodification_type') in ['ai_training', 'data_resale']:
                high_damage.append(f"Data commodification: {commodity_type}")
        
        return high_damage
    
    def _identify_critical_issues_weighted(self, power_analysis: Dict, structural_analysis: Dict, commodification_analysis: Dict) -> List[str]:
        """Identify critical issues using weighted assessment"""
        issues = []
        
        if power_analysis.get('digital_dictatorship'):
            issues.append("Digital dictatorship detected - extreme power imbalance")
        
        if commodification_analysis.get('ai_training_detected'):
            issues.append("AI training on user data without clear consent")
        
        if structural_analysis.get('manipulation_score', 0) > 60:
            issues.append("High structural manipulation score")
        
        return issues
    
    # Placeholder methods for flag explanations (can be expanded)
    def _explain_power_flag(self, control_type: str, clause: Dict) -> str:
        return f"Power imbalance detected in {control_type}: {clause.get('power_holder', 'unknown')} holds control"
    
    def _rate_flag_risk(self, severity: str) -> int:
        ratings = {'critical': 10, 'high': 8, 'medium': 5, 'low': 2}
        return ratings.get(severity, 5)
    
    def _describe_user_impact(self, control_type: str, clause: Dict) -> str:
        return f"This clause affects user {control_type} rights and control"
    
    def _suggest_mitigation(self, control_type: str) -> str:
        return f"Consider negotiating {control_type} terms or seeking alternatives"
    
    def _explain_structural_flag(self, pattern_type: str, clause: Dict) -> str:
        return f"Structural dark pattern detected: {pattern_type}"
    
    def _describe_structural_impact(self, pattern_type: str, clause: Dict) -> str:
        return f"This creates {pattern_type} barriers for users"
    
    def _suggest_structural_mitigation(self, pattern_type: str) -> str:
        return f"Be aware of {pattern_type} when using the service"
    
    def _determine_commodification_severity(self, commodity_type: str) -> str:
        severity_map = {
            'ai_training': 'critical',
            'data_resale': 'critical', 
            'behavioral_profiling': 'high',
            'perpetual_rights': 'high'
        }
        return severity_map.get(commodity_type, 'medium')
    
    def _describe_commodification_impact(self, commodity_type: str, clause: Dict) -> str:
        return f"Your data may be used for {commodity_type} without your control"
    
    def _suggest_commodification_mitigation(self, commodity_type: str) -> str:
        return f"Seek services that don't engage in {commodity_type} of user data"
    
    def _generate_flag_summary(self, flag_categories: Dict) -> str:
        critical_count = len(flag_categories['critical'])
        high_count = len(flag_categories['high'])
        
        if critical_count > 0:
            return f"{critical_count} critical and {high_count} high-risk flags detected"
        elif high_count > 0:
            return f"{high_count} high-risk flags detected"
        else:
            return "No critical issues detected"
    
    def _recommend_action_based_on_flags(self, flag_categories: Dict) -> str:
        critical_count = len(flag_categories['critical'])
        high_count = len(flag_categories['high'])
        
        if critical_count > 2:
            return "Strong recommendation: Avoid this service due to multiple critical issues"
        elif critical_count > 0:
            return "Caution: Critical issues detected, proceed with extreme care"
        elif high_count > 3:
            return "Warning: Multiple high-risk issues, consider alternatives"
        else:
            return "Acceptable with standard precautions"