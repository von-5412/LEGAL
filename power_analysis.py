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
        
        # Power holder detection patterns
        self.power_patterns = {
            'company_absolute': {
                'patterns': [
                    r'(?i)(?:we|company|service provider).*?(?:may|can|will|shall|reserve|retain).*?(?:at.*?(?:our|sole|absolute|complete).*?discretion|without.*?notice|any.*?time|anytime)',
                    r'(?i)(?:sole|absolute|complete|unlimited|unrestricted).*?(?:discretion|right|authority|power).*?(?:to|for)',
                    r'(?i)(?:without.*?(?:notice|warning|cause|reason|liability|obligation)|immediately|instantly).*?(?:terminate|suspend|modify|change|remove)',
                    r'(?i)(?:final|binding|conclusive|irrevocable|non-negotiable).*?(?:decision|determination|judgment)'
                ],
                'weight': 30
            },
            'user_empowerment': {
                'patterns': [
                    r'(?i)(?:you|user).*?(?:may|can|have.*?right|entitled).*?(?:opt.*?out|withdraw|cancel|modify|delete|access|control)',
                    r'(?i)(?:with.*?(?:your|user).*?consent|permission|approval|authorization)',
                    r'(?i)(?:you.*?can.*?(?:object|refuse|decline|opt.*?out)|right.*?to.*?(?:object|refuse|decline))',
                    r'(?i)(?:user.*?choice|user.*?control|your.*?decision|at.*?your.*?option)'
                ],
                'weight': -15  # Negative weight reduces company power score
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
        """Comprehensive power structure analysis"""
        
        # Split into sentences for analysis
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        
        # Analyze power distribution
        power_analysis = self._analyze_power_distribution(sentences)
        
        # Calculate rights stripping index
        rights_analysis = self._calculate_rights_stripping_index(sentences, user_persona)
        
        # Detect compound traps
        compound_traps = self._detect_compound_traps(rights_analysis['categories_detected'])
        
        # Analyze structural dark patterns
        structural_analysis = self._analyze_structural_patterns(text)
        
        # Calculate transparency score (redefined)
        transparency_analysis = self._analyze_real_transparency(text)
        
        # Generate power flow map
        power_flow = self._generate_power_flow_map(sentences)
        
        # Overall assessment
        overall_score = self._calculate_overall_power_score(
            power_analysis, rights_analysis, structural_analysis, transparency_analysis
        )
        
        return {
            'power_distribution': power_analysis,
            'rights_stripping_index': rights_analysis,
            'compound_traps': compound_traps,
            'structural_dark_patterns': structural_analysis,
            'transparency_empowerment': transparency_analysis,
            'power_flow_map': power_flow,
            'overall_assessment': overall_score,
            'user_persona': user_persona,
            'sentences_analyzed': len(sentences)
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
        
        # Determine if it's a "digital dictatorship"
        is_dictatorship = company_percentage > 75 and power_scores['user'] < 2
        
        return {
            'power_distribution': power_scores,
            'company_control_percentage': company_percentage,
            'is_digital_dictatorship': is_dictatorship,
            'clause_breakdown': clause_analysis,
            'assessment': self._get_power_assessment(company_percentage, is_dictatorship)
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
        structural_issues = {}
        total_friction_score = 0
        
        for pattern_name, pattern_data in self.structural_patterns.items():
            for pattern in pattern_data['patterns']:
                if re.search(pattern, text):
                    if pattern_name not in structural_issues:
                        structural_issues[pattern_name] = {
                            'detected': True,
                            'friction_score': pattern_data['friction_score'],
                            'description': pattern_data['description']
                        }
                    total_friction_score += pattern_data['friction_score']
        
        return {
            'structural_issues': structural_issues,
            'total_friction_score': total_friction_score,
            'user_trapped': total_friction_score > 15,
            'structural_assessment': self._get_structural_assessment(total_friction_score)
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
            'transparency_score': transparency_score,
            'empowerment_factors': detected_factors,
            'real_transparency': transparency_score > 75,
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
        
        # Analyze each category
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
            
            # Dispute resolution
            if any(re.search(p, sentence) for p in dispute_patterns[:1]):
                power_map['dispute_resolution'] = 'company'
            elif any(re.search(p, sentence) for p in dispute_patterns[1:]):
                power_map['dispute_resolution'] = 'user'
        
        return power_map
    
    def _calculate_overall_power_score(self, power_analysis, rights_analysis, structural_analysis, transparency_analysis) -> Dict[str, Any]:
        """Calculate overall power score and assessment"""
        
        # Weight the different factors
        power_weight = 0.3
        rights_weight = 0.4
        structural_weight = 0.2
        transparency_weight = 0.1
        
        # Convert scores to 0-100 scale
        power_score = max(0, 100 - power_analysis['company_control_percentage'])
        rights_score = rights_analysis['rights_vs_control_balance'] * 10
        structural_score = max(0, 100 - structural_analysis['total_friction_score'] * 5)
        transparency_score = transparency_analysis['transparency_score']
        
        overall_score = (
            power_score * power_weight +
            rights_score * rights_weight +
            structural_score * structural_weight +
            transparency_score * transparency_weight
        )
        
        # Determine assessment level
        if overall_score >= 70:
            assessment = "User-Friendly"
            risk_level = "low"
        elif overall_score >= 50:
            assessment = "Moderately Balanced"
            risk_level = "medium"
        elif overall_score >= 30:
            assessment = "Company-Favored"
            risk_level = "high"
        else:
            assessment = "Digital Dictatorship"
            risk_level = "critical"
        
        return {
            'overall_score': round(overall_score, 1),
            'assessment': assessment,
            'risk_level': risk_level,
            'component_scores': {
                'power_balance': round(power_score, 1),
                'rights_protection': round(rights_score, 1),
                'structural_fairness': round(structural_score, 1),
                'transparency': round(transparency_score, 1)
            },
            'critical_issues': self._identify_critical_issues(power_analysis, rights_analysis, structural_analysis)
        }
    
    def _get_power_assessment(self, company_percentage: float, is_dictatorship: bool) -> str:
        """Get human-readable power assessment"""
        if is_dictatorship:
            return "You're signing a digital dictatorship - company has absolute control"
        elif company_percentage > 60:
            return "Heavily skewed toward company control"
        elif company_percentage > 40:
            return "Moderately company-favored"
        else:
            return "Reasonably balanced power distribution"
    
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
        
        if power_analysis['is_digital_dictatorship']:
            issues.append("Digital dictatorship detected")
        
        if rights_analysis['red_flag_triggered']:
            issues.append("Rights vs control balance critically low")
        
        if structural_analysis['user_trapped']:
            issues.append("High structural friction traps users")
        
        if power_analysis['company_control_percentage'] > 80:
            issues.append("Extreme power asymmetry favoring company")
        
        return issues