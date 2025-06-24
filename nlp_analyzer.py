import re
import logging
from typing import Dict, List, Tuple
import hashlib
import PyPDF2
from io import BytesIO
from ml_analyzer import LegalMLAnalyzer
from power_analysis import PowerStructureAnalyzer

class TOSAnalyzer:
    def __init__(self):
        # Initialize ML analyzer and power structure analyzer
        self.ml_analyzer = LegalMLAnalyzer()
        self.power_analyzer = PowerStructureAnalyzer()
        # Risk patterns with weights
        self.risk_patterns = {
            'data_sharing': {
                'patterns': [
                    r'(?i)we may share.*?information.*?with.*?third parties',
                    r'(?i)your data.*?may be.*?disclosed.*?to.*?partners',
                    r'(?i)information.*?shared.*?with.*?affiliates',
                    r'(?i)sell.*?personal.*?information',
                    r'(?i)transfer.*?data.*?to.*?other.*?companies',
                    r'(?i)provide.*?information.*?to.*?advertisers',
                ],
                'weight': 25,
                'description': 'Data sharing with third parties'
            },
            'arbitration_waiver': {
                'patterns': [
                    r'(?i)binding.*?arbitration',
                    r'(?i)waive.*?right.*?to.*?jury.*?trial',
                    r'(?i)class.*?action.*?waiver',
                    r'(?i)individual.*?arbitration.*?only',
                    r'(?i)resolve.*?disputes.*?through.*?arbitration',
                    r'(?i)mandatory.*?arbitration',
                ],
                'weight': 20,
                'description': 'Arbitration clauses that limit legal rights'
            },
            'unilateral_changes': {
                'patterns': [
                    r'(?i)we.*?reserve.*?the.*?right.*?to.*?modify',
                    r'(?i)may.*?change.*?these.*?terms.*?at.*?any.*?time',
                    r'(?i)update.*?terms.*?without.*?notice',
                    r'(?i)sole.*?discretion.*?to.*?change',
                    r'(?i)modify.*?agreement.*?unilaterally',
                ],
                'weight': 15,
                'description': 'Unilateral right to change terms'
            },
            'account_suspension': {
                'patterns': [
                    r'(?i)suspend.*?terminate.*?account.*?at.*?any.*?time',
                    r'(?i)discontinue.*?service.*?without.*?notice',
                    r'(?i)sole.*?discretion.*?to.*?terminate',
                    r'(?i)ban.*?user.*?without.*?cause',
                    r'(?i)immediate.*?termination.*?without.*?warning',
                ],
                'weight': 15,
                'description': 'Unfair account termination clauses'
            },
            'broad_liability_waiver': {
                'patterns': [
                    r'(?i)not.*?liable.*?for.*?any.*?damages',
                    r'(?i)disclaim.*?all.*?warranties',
                    r'(?i)use.*?at.*?your.*?own.*?risk',
                    r'(?i)no.*?responsibility.*?for.*?content',
                    r'(?i)maximum.*?liability.*?limited.*?to',
                ],
                'weight': 12,
                'description': 'Broad liability limitations'
            },
            'consent_by_default': {
                'patterns': [
                    r'(?i)by.*?using.*?this.*?service.*?you.*?agree',
                    r'(?i)continued.*?use.*?constitutes.*?acceptance',
                    r'(?i)accessing.*?implies.*?consent',
                    r'(?i)deemed.*?to.*?have.*?accepted',
                ],
                'weight': 10,
                'description': 'Implied consent through usage'
            }
        }
        
        # Dark patterns for manipulative language
        self.dark_patterns = {
            'forced_consent': [
                # Consent through passive actions
                r'(?i)(?:by|through).*?(?:using|accessing|browsing|scrolling|clicking|visiting).*?(?:you|user).*?(?:consent|agree|accept)',
                r'(?i)(?:continued|ongoing|further).*?(?:use|access|browsing).*?(?:constitutes|means|implies|indicates).*?(?:consent|agreement|acceptance)',
                r'(?i)(?:accessing|using|browsing).*?(?:this|our).*?(?:site|service|platform).*?(?:means|implies|constitutes).*?(?:you|user).*?(?:agree|consent|accept)',
                r'(?i)(?:deemed|considered|assumed).*?(?:to|as).*?(?:have|having).*?(?:consented|agreed|accepted)',
                r'(?i)(?:consent|agreement).*?(?:automatic|automatically|implied|passive|default)',
                r'(?i)(?:no.*?action.*?required|automatic.*?consent|passive.*?acceptance)',
                r'(?i)(?:silence|inaction|failure.*?to.*?object).*?(?:constitutes|means|implies).*?(?:consent|agreement)',
            ],
            'non_negotiable_terms': [
                # Unilateral control over terms
                r'(?i)(?:we|company|service).*?(?:may|can|will|shall|reserve.*?right).*?(?:change|modify|update|alter|amend).*?(?:these.*?terms|this.*?agreement|any.*?provision).*?(?:at.*?any.*?time|anytime|without.*?notice|sole.*?discretion)',
                r'(?i)(?:terms|agreement|conditions).*?(?:may.*?be|can.*?be|will.*?be|are.*?subject.*?to).*?(?:changed|modified|updated|revised).*?(?:unilaterally|at.*?will|without.*?consent|sole.*?discretion)',
                r'(?i)(?:modifications|changes|updates).*?(?:effective|binding).*?(?:immediately|upon.*?posting|when.*?posted|without.*?notice)',
                r'(?i)(?:you|user).*?(?:may.*?not|cannot|are.*?not.*?permitted|have.*?no.*?right).*?(?:modify|change|negotiate|alter).*?(?:these.*?terms|this.*?agreement)',
                r'(?i)(?:take.*?it.*?or.*?leave.*?it|non-negotiable|no.*?negotiation|final.*?terms)',
            ],
            'irrevocable_arbitration': [
                # Forced arbitration with no escape
                r'(?i)(?:binding|mandatory|required|irrevocable).*?arbitration.*?(?:waive|waiver|give.*?up|forfeit|surrender).*?(?:right|rights).*?(?:to|for).*?(?:jury.*?trial|court.*?proceedings|class.*?action)',
                r'(?i)(?:all|any).*?(?:disputes|claims|controversies).*?(?:must|shall|will|are.*?required.*?to).*?(?:be.*?resolved|go.*?to|submit.*?to).*?(?:binding|mandatory|individual).*?arbitration',
                r'(?i)(?:no.*?opt.*?out|cannot.*?opt.*?out|irrevocable.*?waiver).*?(?:arbitration|dispute.*?resolution)',
                r'(?i)(?:waive|waiver|give.*?up|forfeit).*?(?:permanently|forever|irrevocably).*?(?:right|rights).*?(?:to|for).*?(?:sue|court|trial|legal.*?action)',
                r'(?i)(?:class.*?action|collective.*?action|representative.*?action).*?(?:waiver|waive|prohibited|forbidden|not.*?permitted)',
                r'(?i)(?:individual.*?basis.*?only|one.*?on.*?one.*?arbitration|private.*?arbitration.*?only)',
            ],
            'hidden_consequences': [
                # Vague termination and punishment clauses
                r'(?i)(?:we|company|service).*?(?:may|can|will|reserve.*?right).*?(?:terminate|suspend|ban|disable|revoke|cancel).*?(?:your|user).*?(?:account|access|service).*?(?:for.*?any.*?reason|at.*?any.*?time|without.*?cause|sole.*?discretion|immediately)',
                r'(?i)(?:immediate|instant|without.*?warning|without.*?notice).*?(?:termination|suspension|cancellation|account.*?closure)',
                r'(?i)(?:violation|breach).*?(?:may.*?result|will.*?result|results).*?(?:in|to).*?(?:immediate|instant|automatic).*?(?:termination|suspension|ban)',
                r'(?i)(?:consequences|penalties|sanctions).*?(?:may.*?include|can.*?include|include.*?but.*?not.*?limited.*?to).*?(?:termination|suspension|legal.*?action|prosecution)',
                r'(?i)(?:any.*?reason|sole.*?discretion|without.*?cause|without.*?explanation|without.*?notice).*?(?:terminate|suspend|ban|revoke)',
                r'(?i)(?:forfeit|lose|surrender).*?(?:all|any).*?(?:data|content|credits|payments|rights).*?(?:upon|after|following).*?(?:termination|suspension)',
            ],
            'urgency_pressure': [
                r'(?i)limited.*?time.*?offer',
                r'(?i)act.*?now.*?or',
                r'(?i)expires.*?soon',
                r'(?i)last.*?chance',
                r'(?i)must.*?act.*?immediately',
                r'(?i)offer.*?expires.*?midnight',
            ],
            'hidden_costs': [
                r'(?i)additional.*?fees.*?may.*?apply',
                r'(?i)subject.*?to.*?additional.*?charges',
                r'(?i)plus.*?applicable.*?taxes',
                r'(?i)excluding.*?processing.*?fees',
                r'(?i)may.*?incur.*?additional.*?costs',
                r'(?i)supplemental.*?charges.*?may.*?apply',
            ],
            'confusing_language': [
                r'(?i)notwithstanding.*?the.*?foregoing',
                r'(?i)subject.*?to.*?the.*?provisions.*?herein',
                r'(?i)without.*?prejudice.*?to',
                r'(?i)save.*?as.*?otherwise.*?provided',
                r'(?i)pursuant.*?to.*?the.*?aforementioned',
                r'(?i)heretofore.*?and.*?hereafter',
            ],
            'opt_out_difficulty': [
                r'(?i)to.*?opt.*?out.*?you.*?must.*?contact',
                r'(?i)unsubscribe.*?by.*?writing.*?to',
                r'(?i)cancellation.*?requires.*?30.*?days',
                r'(?i)written.*?notice.*?required.*?for',
                r'(?i)must.*?provide.*?90.*?days.*?notice',
                r'(?i)cancellation.*?must.*?be.*?in.*?writing',
            ],
            'auto_renewal': [
                r'(?i)automatically.*?renew',
                r'(?i)auto.*?renewal',
                r'(?i)subscription.*?will.*?continue',
                r'(?i)recurring.*?billing',
                r'(?i)charged.*?automatically',
            ],
            'data_harvesting': [
                r'(?i)collect.*?device.*?information',
                r'(?i)track.*?your.*?browsing',
                r'(?i)analytics.*?and.*?tracking',
                r'(?i)behavioral.*?data',
                r'(?i)usage.*?patterns.*?and.*?preferences',
            ]
        }
        
        # Positive indicators (good practices)
        self.positive_patterns = {
            'user_rights': [
                r'(?i)you.*?have.*?the.*?right.*?to',
                r'(?i)users.*?may.*?request.*?deletion',
                r'(?i)data.*?portability',
                r'(?i)right.*?to.*?access.*?your.*?data',
                r'(?i)opt.*?out.*?at.*?any.*?time',
            ],
            'transparency': [
                r'(?i)we.*?will.*?notify.*?you',
                r'(?i)advance.*?notice',
                r'(?i)clear.*?and.*?conspicuous',
                r'(?i)plain.*?language',
                r'(?i)easy.*?to.*?understand',
            ],
            'data_protection': [
                r'(?i)encrypt.*?your.*?data',
                r'(?i)secure.*?transmission',
                r'(?i)gdpr.*?compliant',
                r'(?i)data.*?protection.*?measures',
                r'(?i)privacy.*?by.*?design',
            ]
        }
    
    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_file = BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
            
            return text
        except Exception as e:
            logging.error(f"Error extracting text from PDF: {e}")
            return ""
    
    def chunk_text(self, text: str) -> List[Dict]:
        """Chunk text into sections for analysis with enhanced section detection"""
        # Enhanced section patterns for better document structure detection
        section_patterns = [
            r'(?i)^\s*\d+\.\s+',  # Numbered sections (1. 2. 3.)
            r'(?i)^\s*[A-Z][A-Z\s]+\s*$',  # ALL CAPS headers
            r'(?i)^\s*(privacy|data|terms|conditions|liability|arbitration|termination|dispute|account|service|user|content|intellectual|payment|billing)',
            r'(?i)^\s*\d+\.\d+\s+',  # Subsections (1.1, 1.2)
            r'(?i)^\s*[a-z]\)\s+',  # Lettered subsections (a) b) c))
            r'(?i)^\s*\([a-z]\)\s+',  # Parenthetical subsections (a) (b) (c))
        ]
        
        chunks = []
        current_chunk = ""
        current_section_title = "Introduction"
        section_number = 0
        lines = text.split('\n')
        
        for line_idx, line in enumerate(lines):
            is_header = any(re.match(pattern, line.strip()) for pattern in section_patterns)
            
            if is_header and current_chunk.strip():
                section_number += 1
                chunks.append({
                    'text': current_chunk.strip(),
                    'section_title': current_section_title,
                    'section_number': section_number,
                    'start_pos': sum(len(c['text']) for c in chunks) if chunks else 0,
                    'line_start': line_idx - current_chunk.count('\n'),
                    'line_end': line_idx
                })
                current_chunk = line + '\n'
                current_section_title = self._extract_section_title(line.strip())
            else:
                current_chunk += line + '\n'
        
        # Add the last chunk
        if current_chunk.strip():
            section_number += 1
            chunks.append({
                'text': current_chunk.strip(),
                'section_title': current_section_title,
                'section_number': section_number,
                'start_pos': sum(len(c['text']) for c in chunks) if chunks else 0,
                'line_start': len(lines) - current_chunk.count('\n'),
                'line_end': len(lines)
            })
        
        return chunks if chunks else [{'text': text, 'section_title': 'Full Document', 'section_number': 1, 'start_pos': 0, 'line_start': 0, 'line_end': len(text.split('\n'))}]
    
    def _extract_section_title(self, header_line: str) -> str:
        """Extract meaningful section title from header line"""
        # Remove common prefixes and clean up
        title = re.sub(r'^\s*\d+\.\s*', '', header_line)  # Remove "1. "
        title = re.sub(r'^\s*\d+\.\d+\s*', '', title)     # Remove "1.1 "
        title = re.sub(r'^\s*[a-z]\)\s*', '', title)      # Remove "a) "
        title = re.sub(r'^\s*\([a-z]\)\s*', '', title)    # Remove "(a) "
        
        # If it's too long, take first meaningful part
        if len(title) > 50:
            words = title.split()[:6]  # First 6 words
            title = ' '.join(words) + ('...' if len(title.split()) > 6 else '')
        
        return title.strip() or "Untitled Section"
    
    def analyze_text(self, text: str) -> Dict:
        """Analyze text for risks and dark patterns"""
        if not text.strip():
            return {
                'risk_score': 0,
                'risk_breakdown': {},
                'dark_patterns': {},
                'positive_indicators': {},
                'flagged_sections': [],
                'transparency_score': 100,
                'total_flags': 0,
                'readability_score': 100,
                'word_count': 0,
                'avg_sentence_length': 0,
                'complex_words_ratio': 0
            }
        
        chunks = self.chunk_text(text)
        risk_breakdown = {}
        dark_patterns_found = {}
        positive_indicators = {}
        flagged_sections = []
        total_flags = 0
        
        # Calculate readability metrics
        readability_metrics = self._calculate_readability(text)
        
        # Perform ML-based analysis
        ml_results = self.ml_analyzer.analyze_text_ml(text)
        
        # Import and use enhanced pattern analyzer
        try:
            from enhanced_patterns import EnhancedPatternAnalyzer
            enhanced_analyzer = EnhancedPatternAnalyzer()
            enhanced_results = enhanced_analyzer.analyze_with_enhanced_patterns(text)
            
            # Merge enhanced dark patterns with basic detection
            enhanced_dark_patterns = self._detect_enhanced_dark_patterns(text, enhanced_analyzer.dark_pattern_enhanced)
            
            # Merge with existing dark patterns
            for pattern_type, data in enhanced_dark_patterns.items():
                if pattern_type in dark_patterns_found:
                    # Merge counts and add enhanced detection info
                    dark_patterns_found[pattern_type]['count'] += data['count']
                    dark_patterns_found[pattern_type]['enhanced_detection'] = True
                    dark_patterns_found[pattern_type]['severity'] = data.get('severity', 'moderate')
                    dark_patterns_found[pattern_type]['description'] = data.get('description', '')
                    dark_patterns_found[pattern_type]['matches'].extend(data['matches'])
                else:
                    dark_patterns_found[pattern_type] = data
                    dark_patterns_found[pattern_type]['enhanced_detection'] = True
                    
        except ImportError:
            logging.warning("Enhanced pattern analyzer not available")
        
        # Analyze each chunk for risk patterns with section-level context
        section_analyses = []
        for chunk_idx, chunk in enumerate(chunks):
            chunk_text = chunk['text']
            chunk_flags = []
            section_risk_score = 0
            critical_issues_in_section = []
            
            # Check risk patterns
            for category, data in self.risk_patterns.items():
                matches = []
                for pattern in data['patterns']:
                    pattern_matches = list(re.finditer(pattern, chunk_text))
                    matches.extend(pattern_matches)
                
                if matches:
                    if category not in risk_breakdown:
                        risk_breakdown[category] = {
                            'count': 0,
                            'weight': data['weight'],
                            'description': data['description'],
                            'matches': [],
                            'sections_found': []
                        }
                    
                    risk_breakdown[category]['count'] += len(matches)
                    risk_breakdown[category]['sections_found'].append({
                        'section_number': chunk.get('section_number', chunk_idx + 1),
                        'section_title': chunk.get('section_title', f'Section {chunk_idx + 1}'),
                        'match_count': len(matches)
                    })
                    
                    for match in matches:
                        risk_breakdown[category]['matches'].append({
                            'text': match.group(),
                            'start': match.start(),
                            'end': match.end(),
                            'chunk_index': chunk_idx,
                            'section_title': chunk.get('section_title', f'Section {chunk_idx + 1}')
                        })
                        chunk_flags.append({
                            'type': 'risk',
                            'category': category,
                            'text': match.group(),
                            'description': data['description'],
                            'severity': self._get_risk_severity(category),
                            'weight': data['weight']
                        })
                        section_risk_score += data['weight']
                        
                        # Track critical issues per section
                        if data['weight'] >= 20:  # Critical threshold
                            critical_issues_in_section.append(category)
            
            # Check dark patterns
            for pattern_type, patterns in self.dark_patterns.items():
                matches = []
                for pattern in patterns:
                    pattern_matches = list(re.finditer(pattern, chunk_text))
                    matches.extend(pattern_matches)
                
                if matches:
                    if pattern_type not in dark_patterns_found:
                        dark_patterns_found[pattern_type] = {
                            'count': 0,
                            'matches': [],
                            'sections_found': []
                        }
                    
                    dark_patterns_found[pattern_type]['count'] += len(matches)
                    dark_patterns_found[pattern_type]['sections_found'].append({
                        'section_number': chunk.get('section_number', chunk_idx + 1),
                        'section_title': chunk.get('section_title', f'Section {chunk_idx + 1}'),
                        'match_count': len(matches)
                    })
                    
                    for match in matches:
                        dark_patterns_found[pattern_type]['matches'].append({
                            'text': match.group(),
                            'start': match.start(),
                            'end': match.end(),
                            'chunk_index': chunk_idx,
                            'section_title': chunk.get('section_title', f'Section {chunk_idx + 1}')
                        })
                        chunk_flags.append({
                            'type': 'dark_pattern',
                            'category': pattern_type,
                            'text': match.group(),
                            'description': f"Potentially manipulative: {pattern_type.replace('_', ' ')}",
                            'severity': 'high',
                            'weight': 15
                        })
                        section_risk_score += 15
            
            # Check positive indicators
            for pattern_type, patterns in self.positive_patterns.items():
                matches = []
                for pattern in patterns:
                    pattern_matches = list(re.finditer(pattern, chunk_text))
                    matches.extend(pattern_matches)
                
                if matches:
                    if pattern_type not in positive_indicators:
                        positive_indicators[pattern_type] = {
                            'count': 0,
                            'matches': [],
                            'sections_found': []
                        }
                    
                    positive_indicators[pattern_type]['count'] += len(matches)
                    positive_indicators[pattern_type]['sections_found'].append({
                        'section_number': chunk.get('section_number', chunk_idx + 1),
                        'section_title': chunk.get('section_title', f'Section {chunk_idx + 1}'),
                        'match_count': len(matches)
                    })
                    
                    for match in matches:
                        positive_indicators[pattern_type]['matches'].append({
                            'text': match.group(),
                            'start': match.start(),
                            'end': match.end(),
                            'chunk_index': chunk_idx,
                            'section_title': chunk.get('section_title', f'Section {chunk_idx + 1}')
                        })
                        section_risk_score -= 5  # Positive indicators reduce section risk
            
            # Calculate section-level severity
            section_severity = self._calculate_section_severity(section_risk_score, critical_issues_in_section, chunk_flags)
            
            # Store section analysis
            section_analysis = {
                'section_number': chunk.get('section_number', chunk_idx + 1),
                'section_title': chunk.get('section_title', f'Section {chunk_idx + 1}'),
                'section_risk_score': section_risk_score,
                'section_severity': section_severity,
                'critical_issues': critical_issues_in_section,
                'total_flags': len(chunk_flags),
                'flag_breakdown': self._categorize_section_flags(chunk_flags)
            }
            section_analyses.append(section_analysis)
            
            if chunk_flags:
                flagged_sections.append({
                    'chunk_index': chunk_idx,
                    'section_number': chunk.get('section_number', chunk_idx + 1),
                    'section_title': chunk.get('section_title', f'Section {chunk_idx + 1}'),
                    'section_severity': section_severity,
                    'section_risk_score': section_risk_score,
                    'text': chunk_text[:500] + ('...' if len(chunk_text) > 500 else ''),
                    'flags': chunk_flags,
                    'flag_count': len(chunk_flags),
                    'critical_issues': critical_issues_in_section,
                    'danger_summary': self._generate_section_danger_summary(section_severity, critical_issues_in_section)
                })
                total_flags += len(chunk_flags)
        
        # Merge ML results with pattern-based results
        merged_risk_breakdown = self._merge_risk_results(risk_breakdown, ml_results.get('risk_breakdown', {}))
        merged_positive_indicators = self._merge_positive_results(positive_indicators, ml_results.get('positive_indicators', {}))
        
        # Calculate risk score using merged results
        risk_score = self._calculate_risk_score(merged_risk_breakdown)
        
        # Calculate transparency score with positive indicators boost
        base_transparency = 100 - (len(dark_patterns_found) * 8) - (risk_score * 0.25)
        positive_boost = min(20, len(merged_positive_indicators) * 5)
        transparency_score = max(0, min(100, base_transparency + positive_boost))
        
        # Perform power structure analysis
        power_analysis = self.power_analyzer.analyze_power_structure(text, user_persona='individual_user')
        
        # Generate executive summary using merged results and power analysis
        try:
            executive_summary = self._generate_executive_summary(
                risk_score, merged_risk_breakdown, dark_patterns_found, 
                merged_positive_indicators or {}, transparency_score, readability_metrics
            )
        except Exception as e:
            logging.error(f"Error generating executive summary: {e}")
            executive_summary = {
                'overall_assessment': 'Analysis completed with limited summary due to processing error',
                'critical_issues': [],
                'moderate_concerns': [],
                'immediate_actions': ['Review the flagged sections manually'],
                'next_steps': ['Consider getting legal advice for complex terms'],
                'risk_level': 'medium',
                'bottom_line': 'Manual review recommended due to analysis error'
            }
        
        return {
            'risk_score': risk_score,
            'risk_breakdown': merged_risk_breakdown,
            'dark_patterns': dark_patterns_found,
            'positive_indicators': merged_positive_indicators,
            'flagged_sections': flagged_sections,
            'section_analyses': section_analyses,
            'most_dangerous_sections': self._identify_most_dangerous_sections(section_analyses),
            'transparency_score': int(transparency_score),
            'total_flags': total_flags,
            'text_length': len(text),
            'chunk_count': len(chunks),
            'executive_summary': executive_summary,
            'power_analysis': power_analysis,
            'ml_analysis_info': {
                'ml_enabled': ml_results.get('ml_analysis', False),
                'classification_method': ml_results.get('classification_method', 'pattern_only'),
                'confidence_scores': ml_results.get('ml_confidence_scores', {}),
                'sentences_processed': ml_results.get('sentences_processed', 0),
                'model_info': self.ml_analyzer.get_model_info()
            },
            **readability_metrics
        }
    
    def _get_risk_severity(self, category: str) -> str:
        """Map risk categories to severity levels"""
        severity_map = {
            'data_sharing': 'critical',
            'arbitration_waiver': 'critical', 
            'unilateral_changes': 'high',
            'account_suspension': 'high',
            'broad_liability_waiver': 'medium',
            'consent_by_default': 'medium'
        }
        return severity_map.get(category, 'medium')
    
    def _calculate_section_severity(self, risk_score: int, critical_issues: List[str], flags: List[Dict]) -> str:
        """Calculate overall severity for a section based on cumulative risk"""
        critical_count = len(critical_issues)
        high_risk_flags = len([f for f in flags if f.get('severity') in ['critical', 'high']])
        
        # Critical section criteria
        if critical_count >= 2:  # Multiple critical issues
            return 'critical'
        elif risk_score >= 50:  # High cumulative risk
            return 'critical'
        elif critical_count >= 1 or high_risk_flags >= 3:
            return 'high'
        elif risk_score >= 25 or high_risk_flags >= 1:
            return 'medium'
        else:
            return 'low'
    
    def _categorize_section_flags(self, flags: List[Dict]) -> Dict:
        """Categorize flags within a section by severity"""
        categorized = {'critical': [], 'high': [], 'medium': [], 'low': []}
        for flag in flags:
            severity = flag.get('severity', 'medium')
            categorized[severity].append(flag)
        return categorized
    
    def _generate_section_danger_summary(self, severity: str, critical_issues: List[str]) -> str:
        """Generate human-readable danger summary for sections"""
        if severity == 'critical':
            if len(critical_issues) >= 2:
                issue_names = [issue.replace('_', ' ').title() for issue in critical_issues[:2]]
                return f"🔴 CRITICAL: {' + '.join(issue_names)} - All legal rights eliminated"
            else:
                return "🔴 CRITICAL: Multiple high-risk clauses present"
        elif severity == 'high':
            return "🟠 HIGH RISK: Significant user rights restrictions"
        elif severity == 'medium':
            return "🟡 MODERATE: Some concerning clauses present"
        else:
            return "🟢 LOW RISK: Minor issues detected"
    
    def _identify_most_dangerous_sections(self, section_analyses: List[Dict]) -> List[Dict]:
        """Identify the most dangerous sections for executive summary"""
        # Sort by risk score and return top 3 most dangerous
        dangerous_sections = sorted(section_analyses, key=lambda s: s['section_risk_score'], reverse=True)
        return dangerous_sections[:3]
    
    def _calculate_risk_score(self, risk_breakdown: Dict) -> int:
        """Calculate overall risk score with severity-weighted critical issue enforcement"""
        total_score = 0
        critical_issues_count = 0
        high_risk_issues_count = 0
        
        # Severity-based scoring with much higher weights for critical issues
        severity_weights = {
            'critical': 35,    # Critical issues get massive weight
            'high': 20,        # High risk issues get substantial weight  
            'medium': 10,      # Medium issues get moderate weight
            'low': 5           # Low issues get minimal weight
        }
        
        # Category to severity mapping (enhanced)
        category_severity = {
            'data_sharing': 'critical',
            'arbitration_waiver': 'critical',
            'unilateral_changes': 'high',
            'account_suspension': 'high', 
            'account_termination': 'high',
            'broad_liability_waiver': 'medium',
            'liability_limitation': 'medium',
            'consent_by_default': 'medium',
            'auto_renewal': 'medium',
            'hidden_costs': 'medium'
        }
        
        # Count issues by severity and calculate weighted score
        for category, data in risk_breakdown.items():
            issue_count = data['count']
            if issue_count == 0:
                continue
                
            severity = category_severity.get(category, 'medium')
            severity_weight = severity_weights[severity]
            
            # Count issues by severity
            if severity == 'critical':
                critical_issues_count += issue_count
            elif severity == 'high':
                high_risk_issues_count += issue_count
            
            # Exponential scaling for multiple instances of same issue
            if issue_count > 1:
                category_score = severity_weight * (1 + (issue_count - 1) * 0.5)  # 50% additional for each extra
            else:
                category_score = severity_weight
            
            total_score += category_score
        
        # Critical issue enforcement - if you have critical issues, minimum score applies
        if critical_issues_count >= 3:
            # 3+ critical issues = extreme danger
            total_score = max(total_score, 85)
        elif critical_issues_count >= 2:
            # 2 critical issues = high danger
            total_score = max(total_score, 75)
        elif critical_issues_count >= 1:
            # 1 critical issue = significant danger
            total_score = max(total_score, 65)
        elif high_risk_issues_count >= 4:
            # 4+ high risk issues = accumulated danger
            total_score = max(total_score, 60)
        elif high_risk_issues_count >= 2:
            # 2+ high risk issues = moderate danger
            total_score = max(total_score, 45)
        
        # Specific critical combinations that should force very high scores
        has_arbitration = any(cat in ['arbitration_waiver'] for cat in risk_breakdown.keys() if risk_breakdown[cat]['count'] > 0)
        has_data_sharing = any(cat in ['data_sharing'] for cat in risk_breakdown.keys() if risk_breakdown[cat]['count'] > 0)
        
        if has_arbitration and has_data_sharing:
            # Arbitration + Data Sharing = Digital dictatorship
            total_score = max(total_score, 90)
        elif has_arbitration:
            # Arbitration alone = You lose legal rights
            total_score = max(total_score, 75)
        elif has_data_sharing:
            # Data sharing alone = Privacy obliterated
            total_score = max(total_score, 70)
        
        # Cap at 100 but ensure critical issues never result in low scores
        final_score = min(int(total_score), 100)
        
        # Final safety check: If we detected critical issues but somehow scored low, force correction
        if critical_issues_count > 0 and final_score < 60:
            final_score = 60 + (critical_issues_count * 10)  # 60 base + 10 per critical issue
            final_score = min(final_score, 100)
        
        return final_score
    
    def _calculate_readability(self, text: str) -> Dict:
        """Calculate readability metrics"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        words = re.findall(r'\b\w+\b', text.lower())
        word_count = len(words)
        sentence_count = len(sentences)
        
        # Average sentence length
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        # Complex words (3+ syllables or legal jargon)
        complex_words = []
        legal_jargon = [
            'notwithstanding', 'aforementioned', 'heretofore', 'hereafter', 
            'pursuant', 'thereto', 'whereas', 'indemnify', 'arbitration',
            'jurisdiction', 'covenant', 'warranty', 'liability', 'statutory'
        ]
        
        for word in words:
            if len(word) > 10 or word in legal_jargon:
                complex_words.append(word)
        
        complex_words_ratio = (len(complex_words) / word_count * 100) if word_count > 0 else 0
        
        # Simple readability score (inverse of complexity)
        readability_score = max(0, 100 - (avg_sentence_length * 2) - complex_words_ratio)
        
        return {
            'readability_score': int(readability_score),
            'word_count': word_count,
            'avg_sentence_length': round(avg_sentence_length, 1),
            'complex_words_ratio': round(complex_words_ratio, 1)
        }
    
    def _detect_enhanced_dark_patterns(self, text: str, enhanced_patterns: Dict) -> Dict:
        """Detect enhanced dark patterns with contextual analysis"""
        detected_patterns = {}
        
        for pattern_type, pattern_data in enhanced_patterns.items():
            matches = []
            for pattern in pattern_data['patterns']:
                pattern_matches = list(re.finditer(pattern, text))
                matches.extend(pattern_matches)
            
            if matches:
                detected_patterns[pattern_type] = {
                    'count': len(matches),
                    'severity': pattern_data['severity'],
                    'description': pattern_data.get('description', f"Enhanced detection: {pattern_type.replace('_', ' ')}"),
                    'confidence_base': pattern_data.get('confidence_base', 0.7),
                    'matches': []
                }
                
                for match in matches:
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 50)
                    context = text[start:end].strip()
                    
                    detected_patterns[pattern_type]['matches'].append({
                        'text': match.group(),
                        'context': context,
                        'start': match.start(),
                        'end': match.end()
                    })
        
        return detected_patterns
    
    def _generate_executive_summary(self, risk_score, risk_breakdown, dark_patterns, 
                                   positive_indicators, transparency_score, readability_metrics):
        """Generate an executive summary of the analysis"""
        # Ensure all inputs are properly initialized
        risk_breakdown = risk_breakdown or {}
        dark_patterns = dark_patterns or {}
        positive_indicators = positive_indicators or {}
        
        summary = {
            'overall_assessment': '',
            'critical_issues': [],
            'moderate_concerns': [],
            'immediate_actions': [],
            'next_steps': [],
            'risk_level': 'low' if risk_score < 30 else 'medium' if risk_score < 70 else 'high',
            'bottom_line': ''
        }
        
        # Risk severity mapping with user impact
        risk_impacts = {
            'data_sharing': {
                'severity': 'critical',
                'impact': 'Your personal data will be sold or shared with unknown third parties',
                'action': 'DO NOT PROCEED unless you accept permanent loss of data privacy'
            },
            'arbitration_waiver': {
                'severity': 'critical', 
                'impact': 'You cannot sue this company in court, even for serious harm',
                'action': 'STOP - You lose all legal recourse if something goes wrong'
            },
            'unilateral_changes': {
                'severity': 'moderate',
                'impact': 'Company can change rules anytime without asking your permission',
                'action': 'Monitor for changes or set up alerts'
            },
            'account_suspension': {
                'severity': 'moderate',
                'impact': 'Company can ban you instantly without explanation or appeal',
                'action': 'Ensure you have data backups before proceeding'
            },
            'broad_liability_waiver': {
                'severity': 'moderate',
                'impact': 'Company takes no responsibility if their service harms you',
                'action': 'Consider if the risk is worth the service benefits'
            }
        }
        
        # Categorize issues by severity
        for risk_type, data in risk_breakdown.items():
            if not isinstance(data, dict):
                continue
                
            risk_info = risk_impacts.get(risk_type, {
                'severity': 'moderate',
                'impact': data.get('description', f'Risk detected: {risk_type}'),
                'action': 'Review this clause carefully'
            })
            
            issue = {
                'type': risk_type.replace('_', ' ').title(),
                'count': data.get('count', 0),
                'impact': risk_info['impact'],
                'action': risk_info['action']
            }
            
            if risk_info['severity'] == 'critical':
                summary['critical_issues'].append(issue)
            else:
                summary['moderate_concerns'].append(issue)
        
        # Dark pattern severity with new critical patterns
        critical_patterns = [
            'forced_consent', 'forced_consent_coercion', 'non_negotiable_terms', 
            'unilateral_term_control', 'irrevocable_arbitration', 'irrevocable_legal_waiver',
            'auto_renewal', 'hidden_costs'
        ]
        high_risk_patterns = [
            'hidden_consequences', 'consequence_obfuscation', 'auto_renewal_hidden'
        ]
        
        for pattern_type, data in dark_patterns.items():
            if not isinstance(data, dict) or data.get('count', 0) == 0:
                continue
                
            pattern_name = pattern_type.replace('_', ' ').title()
            
            # Get specific impact messages for new patterns
            impact_messages = {
                    'forced_consent': "You 'agree' just by using the service - no real choice given",
                    'forced_consent_coercion': "Your consent is assumed through passive actions like scrolling",
                    'non_negotiable_terms': "Company can change rules anytime - you have no say",
                    'unilateral_term_control': "Terms can be changed unilaterally without your consent",
                    'irrevocable_arbitration': "You permanently lose the right to sue in court",
                    'irrevocable_legal_waiver': "Fundamental legal rights are permanently waived",
                    'hidden_consequences': "Severe punishments hidden in vague language",
                    'consequence_obfuscation': "Consequences for violations are deliberately unclear",
                    'auto_renewal': "Designed to trick you into recurring charges",
                    'hidden_costs': "Additional fees hidden until it's too late"
                }
                
                action_messages = {
                'forced_consent': "STOP - This is predatory consent manipulation",
                'forced_consent_coercion': "RED FLAG - Consent should be explicit, not assumed",
                'non_negotiable_terms': "DANGER - You have no protection from rule changes",
                'unilateral_term_control': "WARNING - Company has absolute control over terms",
                'irrevocable_arbitration': "CRITICAL - You lose fundamental legal rights forever",
                'irrevocable_legal_waiver': "EMERGENCY - Seek legal advice before proceeding",
                'hidden_consequences': "HIGH RISK - Punishments are deliberately obscured",
                'consequence_obfuscation': "CAUTION - Understand penalties before agreeing"
            }
                
                issue = {
                'type': pattern_name,
                'count': data['count'],
                'impact': impact_messages.get(pattern_type, f"Designed to manipulate users through {pattern_type.replace('_', ' ')}"),
                'action': action_messages.get(pattern_type, 'Be extra cautious - this is intentionally deceptive'),
                'severity': data.get('severity', 'moderate'),
                'enhanced_detection': data.get('enhanced_detection', False)
            }
                
                if pattern_type in critical_patterns:
                summary['critical_issues'].append(issue)
            elif pattern_type in high_risk_patterns:
                summary['critical_issues'].append(issue)  # Treat high-risk as critical
            else:
                summary['moderate_concerns'].append(issue)
        
        # Generate overall assessment based on actual findings AND risk score alignment
        critical_count = len(summary['critical_issues'])
        moderate_count = len(summary['moderate_concerns'])
        
        # Check for specific critical combinations
        has_arbitration = any('arbitration' in issue['type'].lower() for issue in summary['critical_issues'])
        has_data_sharing = any('data' in issue['type'].lower() for issue in summary['critical_issues'])
        
        # Generate assessment based on BOTH critical count AND risk score (they must align)
        if critical_count >= 3 or risk_score >= 85:
            summary['overall_assessment'] = f"EXTREME DANGER: {critical_count} critical issues detected - this is predatory. You lose fundamental rights."
            summary['bottom_line'] = "🚨 AVOID AT ALL COSTS - This agreement is designed to exploit users"
        elif critical_count >= 2 or risk_score >= 75:
            if has_arbitration and has_data_sharing:
                summary['overall_assessment'] = f"DIGITAL DICTATORSHIP: {critical_count} critical issues including arbitration + data sharing. All user power eliminated."
                summary['bottom_line'] = "🚨 EXTREME DANGER - You lose legal rights AND data control permanently"
            else:
                summary['overall_assessment'] = f"DANGER: {critical_count} critical issue{'s' if critical_count != 1 else ''} that eliminate fundamental user rights."
                summary['bottom_line'] = "❌ DO NOT AGREE - Critical user rights are being stripped away"
        elif critical_count >= 1 or risk_score >= 65:
            if has_arbitration:
                summary['overall_assessment'] = f"CRITICAL: Arbitration waiver detected - you lose the right to sue in court for any reason."
                summary['bottom_line'] = "🔴 HIGH DANGER - You surrender fundamental legal protections"
            elif has_data_sharing:
                summary['overall_assessment'] = f"CRITICAL: Data sharing detected - your personal information will be sold/shared without meaningful consent."
                summary['bottom_line'] = "🔴 PRIVACY RISK - Your data becomes a commodity for profit"
            else:
                summary['overall_assessment'] = f"HIGH RISK: {critical_count} critical issue detected that seriously undermines user rights."
                summary['bottom_line'] = "⚠️ MAJOR CAUTION - Only proceed if absolutely necessary and no alternatives exist"
        elif risk_score >= 45 or moderate_count > 2:
            summary['overall_assessment'] = f"MODERATE RISK: {moderate_count} concerning clauses that favor the company over users."
            summary['bottom_line'] = "⚠️ PROCEED WITH CAUTION - Review flagged sections carefully before agreeing"
        elif risk_score >= 30 or moderate_count > 0:
            summary['overall_assessment'] = f"MIXED: {moderate_count} issue{'s' if moderate_count != 1 else ''} found but within acceptable range for this service type."
            summary['bottom_line'] = "✓ ACCEPTABLE - Standard business terms with minor concerns"
        else:
            summary['overall_assessment'] = "GOOD: No major red flags detected. This appears to be a user-friendly agreement."
            summary['bottom_line'] = "✅ SAFE TO PROCEED - This company respects user rights"
        
        # Immediate actions (what to do right now)
        if critical_count > 0:
            summary['immediate_actions'] = [
                "STOP - Do not sign this agreement yet",
                "Get legal advice if the service is essential to you", 
                "Look for alternative services with better terms",
                "Document what data you'll lose access to"
            ]
        elif moderate_count > 2:
            summary['immediate_actions'] = [
                "Read every flagged section in detail",
                "Understand exactly what rights you're giving up",
                "Set up data export/backup before agreeing",
                "Check if you can negotiate better terms"
            ]
        else:
            summary['immediate_actions'] = [
                "Save a copy of these terms for your records",
                "Review the flagged sections once more",
                "Set calendar reminders to check for term changes"
            ]
        
        # Next steps (ongoing protection)
        if 'arbitration_waiver' in risk_breakdown:
            summary['next_steps'].append("Remember: You cannot sue in court if problems arise")
        if 'data_sharing' in risk_breakdown:
            summary['next_steps'].append("Check privacy settings immediately after signing up")
        if 'unilateral_changes' in risk_breakdown:
            summary['next_steps'].append("Set up Google Alerts for this company's policy changes")
        if any('auto_renewal' in p for p in dark_patterns):
            summary['next_steps'].append("Cancel subscription immediately if you ever want to stop")
            
        # Default next steps
        summary['next_steps'].extend([
            "Keep screenshots of the current terms",
            "Monitor your account for unexpected changes",
            "Know your cancellation process before you need it"
        ])
        
        return summary
    
    def _merge_risk_results(self, pattern_results: Dict, ml_results: Dict) -> Dict:
        """Merge pattern-based and ML-based risk results"""
        merged = pattern_results.copy() if pattern_results else {}
        
        if not ml_results:
            return merged
            
        for category, ml_data in ml_results.items():
            if not isinstance(ml_data, dict):
                continue
                
            if category in merged:
                # Merge counts and matches
                merged[category]['count'] += ml_data.get('count', 0)
                merged[category]['matches'].extend(ml_data.get('matches', []))
                # Add ML confidence if available
                if 'confidence_scores' in ml_data:
                    confidence_scores = ml_data['confidence_scores']
                    if confidence_scores:
                        merged[category]['ml_confidence'] = sum(confidence_scores) / len(confidence_scores)
            else:
                # Add new ML-detected category
                merged[category] = ml_data.copy()
                merged[category]['source'] = 'ml_detected'
        
        return merged
    
    def _merge_positive_results(self, pattern_results: Dict, ml_results: Dict) -> Dict:
        """Merge pattern-based and ML-based positive indicator results"""
        merged = pattern_results.copy() if pattern_results else {}
        
        if not ml_results:
            return merged
            
        for category, ml_data in ml_results.items():
            if not isinstance(ml_data, dict):
                continue
                
            if category in merged:
                merged[category]['count'] += ml_data.get('count', 0)
                merged[category]['matches'].extend(ml_data.get('matches', []))
                if 'confidence_scores' in ml_data:
                    confidence_scores = ml_data['confidence_scores']
                    if confidence_scores:
                        merged[category]['ml_confidence'] = sum(confidence_scores) / len(confidence_scores)
            else:
                merged[category] = ml_data.copy()
                merged[category]['source'] = 'ml_detected'
        
        return merged
    
    def generate_file_hash(self, content: bytes) -> str:
        """Generate hash for file content"""
        return hashlib.sha256(content).hexdigest()
