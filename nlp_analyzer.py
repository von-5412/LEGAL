import re
import logging
from typing import Dict, List, Tuple
import hashlib
import PyPDF2
from io import BytesIO

class TOSAnalyzer:
    def __init__(self):
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
        """Chunk text into sections for analysis"""
        # Split by common section headers
        section_patterns = [
            r'(?i)^\s*\d+\.\s+',  # Numbered sections
            r'(?i)^\s*[A-Z][A-Z\s]+\s*$',  # ALL CAPS headers
            r'(?i)^\s*(privacy|data|terms|conditions|liability|arbitration|termination)',
        ]
        
        chunks = []
        current_chunk = ""
        lines = text.split('\n')
        
        for line in lines:
            is_header = any(re.match(pattern, line.strip()) for pattern in section_patterns)
            
            if is_header and current_chunk.strip():
                chunks.append({
                    'text': current_chunk.strip(),
                    'start_pos': sum(len(c['text']) for c in chunks) if chunks else 0
                })
                current_chunk = line + '\n'
            else:
                current_chunk += line + '\n'
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'start_pos': sum(len(c['text']) for c in chunks) if chunks else 0
            })
        
        return chunks if chunks else [{'text': text, 'start_pos': 0}]
    
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
        
        # Analyze each chunk for risk patterns
        for chunk_idx, chunk in enumerate(chunks):
            chunk_text = chunk['text']
            chunk_flags = []
            
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
                            'matches': []
                        }
                    
                    risk_breakdown[category]['count'] += len(matches)
                    for match in matches:
                        risk_breakdown[category]['matches'].append({
                            'text': match.group(),
                            'start': match.start(),
                            'end': match.end(),
                            'chunk_index': chunk_idx
                        })
                        chunk_flags.append({
                            'type': 'risk',
                            'category': category,
                            'text': match.group(),
                            'description': data['description']
                        })
            
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
                            'matches': []
                        }
                    
                    dark_patterns_found[pattern_type]['count'] += len(matches)
                    for match in matches:
                        dark_patterns_found[pattern_type]['matches'].append({
                            'text': match.group(),
                            'start': match.start(),
                            'end': match.end(),
                            'chunk_index': chunk_idx
                        })
                        chunk_flags.append({
                            'type': 'dark_pattern',
                            'category': pattern_type,
                            'text': match.group(),
                            'description': f"Potentially manipulative: {pattern_type.replace('_', ' ')}"
                        })
            
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
                            'matches': []
                        }
                    
                    positive_indicators[pattern_type]['count'] += len(matches)
                    for match in matches:
                        positive_indicators[pattern_type]['matches'].append({
                            'text': match.group(),
                            'start': match.start(),
                            'end': match.end(),
                            'chunk_index': chunk_idx
                        })
            
            if chunk_flags:
                flagged_sections.append({
                    'chunk_index': chunk_idx,
                    'text': chunk_text[:500] + ('...' if len(chunk_text) > 500 else ''),
                    'flags': chunk_flags,
                    'flag_count': len(chunk_flags)
                })
                total_flags += len(chunk_flags)
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(risk_breakdown)
        
        # Calculate transparency score with positive indicators boost
        base_transparency = 100 - (len(dark_patterns_found) * 8) - (risk_score * 0.25)
        positive_boost = min(20, len(positive_indicators) * 5)
        transparency_score = max(0, min(100, base_transparency + positive_boost))
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(
            risk_score, risk_breakdown, dark_patterns_found, 
            positive_indicators, transparency_score, readability_metrics
        )
        
        return {
            'risk_score': risk_score,
            'risk_breakdown': risk_breakdown,
            'dark_patterns': dark_patterns_found,
            'positive_indicators': positive_indicators,
            'flagged_sections': flagged_sections,
            'transparency_score': int(transparency_score),
            'total_flags': total_flags,
            'text_length': len(text),
            'chunk_count': len(chunks),
            'executive_summary': executive_summary,
            **readability_metrics
        }
    
    def _calculate_risk_score(self, risk_breakdown: Dict) -> int:
        """Calculate overall risk score based on weighted categories"""
        total_score = 0
        
        for category, data in risk_breakdown.items():
            # Score based on count and weight
            category_score = min(data['count'] * data['weight'], data['weight'])
            total_score += category_score
        
        # Cap at 100
        return min(total_score, 100)
    
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
    
    def _generate_executive_summary(self, risk_score, risk_breakdown, dark_patterns, 
                                   positive_indicators, transparency_score, readability_metrics):
        """Generate an executive summary of the analysis"""
        summary = {
            'overall_assessment': '',
            'key_concerns': [],
            'positive_aspects': [],
            'recommendations': [],
            'risk_level': 'low' if risk_score < 30 else 'medium' if risk_score < 70 else 'high'
        }
        
        # Overall assessment
        if risk_score >= 70:
            summary['overall_assessment'] = "This document contains significant risks that could substantially limit your rights and expose you to potential harm. Exercise extreme caution before agreeing."
        elif risk_score >= 40:
            summary['overall_assessment'] = "This document has moderate risk levels with some concerning clauses. Review carefully and consider if the service value justifies the risks."
        else:
            summary['overall_assessment'] = "This document appears to have reasonable terms with minimal concerning elements. Risk levels are within acceptable ranges for most users."
        
        # Key concerns
        high_priority_risks = ['data_sharing', 'arbitration_waiver', 'unilateral_changes']
        for risk_type, data in risk_breakdown.items():
            if risk_type in high_priority_risks:
                summary['key_concerns'].append(f"{data['description']} ({data['count']} instances)")
        
        for pattern_type, data in dark_patterns.items():
            if data['count'] > 2:  # Only flag patterns that appear frequently
                summary['key_concerns'].append(f"Frequent use of {pattern_type.replace('_', ' ')} tactics ({data['count']} instances)")
        
        # Positive aspects
        for indicator_type, data in positive_indicators.items():
            summary['positive_aspects'].append(f"{indicator_type.replace('_', ' ').title()} mentioned {data['count']} times")
        
        if transparency_score > 70:
            summary['positive_aspects'].append("Document demonstrates good transparency practices")
        
        if readability_metrics['readability_score'] > 60:
            summary['positive_aspects'].append("Document uses relatively clear language")
        
        # Recommendations
        if risk_score >= 70:
            summary['recommendations'].extend([
                "Seek legal advice before agreeing to these terms",
                "Consider alternative services with more user-friendly terms",
                "Document any existing data you want to protect"
            ])
        elif risk_score >= 40:
            summary['recommendations'].extend([
                "Carefully review all flagged sections before agreeing",
                "Understand what rights you're waiving",
                "Consider setting up data export/backup procedures"
            ])
        else:
            summary['recommendations'].extend([
                "Standard precautions apply - review key sections",
                "Keep records of the terms you've agreed to"
            ])
        
        if 'arbitration_waiver' in risk_breakdown:
            summary['recommendations'].append("Understand that you're waiving your right to sue in court")
        
        if 'data_sharing' in risk_breakdown:
            summary['recommendations'].append("Review privacy settings and opt-out options for data sharing")
        
        return summary
    
    def generate_file_hash(self, content: bytes) -> str:
        """Generate hash for file content"""
        return hashlib.sha256(content).hexdigest()
