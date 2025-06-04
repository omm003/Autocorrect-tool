import re
import nltk
from textblob import TextBlob
from typing import List, Tuple, Dict
import spellchecker

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('wordnet', quiet=True)
except:
    pass

class CorrectionEngine:
    def __init__(self):
        self.spell_checker = spellchecker.SpellChecker()
        self.grammar_rules = self._load_grammar_rules()
        self.fluency_patterns = self._load_fluency_patterns()
    
    def correct_text(self, text: str, correction_types: List[str], confidence_threshold: float = 0.7) -> Tuple[str, List[Dict]]:
        """Main correction function"""
        corrected_text = text
        suggestions = []
        
        # Apply corrections based on selected types
        if "Spelling" in correction_types:
            corrected_text, spell_suggestions = self._correct_spelling(corrected_text, confidence_threshold)
            suggestions.extend(spell_suggestions)
        
        if "Grammar" in correction_types:
            corrected_text, grammar_suggestions = self._correct_grammar(corrected_text, confidence_threshold)
            suggestions.extend(grammar_suggestions)
        
        if "Punctuation" in correction_types:
            corrected_text, punct_suggestions = self._correct_punctuation(corrected_text, confidence_threshold)
            suggestions.extend(punct_suggestions)
        
        if "Fluency" in correction_types:
            corrected_text, fluency_suggestions = self._improve_fluency(corrected_text, confidence_threshold)
            suggestions.extend(fluency_suggestions)
        
        return corrected_text, suggestions
    
    def _correct_spelling(self, text: str, threshold: float) -> Tuple[str, List[Dict]]:
        """Correct spelling errors"""
        words = text.split()
        corrected_words = []
        suggestions = []
        
        for word in words:
            # Clean word for checking
            clean_word = re.sub(r'[^\w]', '', word.lower())
            
            if clean_word and clean_word not in self.spell_checker:
                # Get correction
                correction = self.spell_checker.correction(clean_word)
                
                if correction and correction != clean_word:
                    # Preserve original case and punctuation
                    corrected_word = self._preserve_case_and_punct(word, correction)
                    corrected_words.append(corrected_word)
                    
                    suggestions.append({
                        'original': word,
                        'corrected': corrected_word,
                        'type': 'spelling',
                        'confidence': 0.8  # Default confidence for spelling
                    })
                else:
                    corrected_words.append(word)
            else:
                corrected_words.append(word)
        
        return ' '.join(corrected_words), suggestions
    
    def _correct_grammar(self, text: str, threshold: float) -> Tuple[str, List[Dict]]:
        """Correct grammar errors"""
        blob = TextBlob(text)
        suggestions = []
        
        # Use TextBlob's correction
        corrected_blob = blob.correct()
        corrected_text = str(corrected_blob)
        
        # Find differences for suggestions
        if corrected_text != text:
            suggestions.append({
                'original': text,
                'corrected': corrected_text,
                'type': 'grammar',
                'confidence': 0.75
            })
        
        # Apply custom grammar rules
        for rule in self.grammar_rules:
            if rule['pattern'].search(corrected_text):
                old_text = corrected_text
                corrected_text = rule['pattern'].sub(rule['replacement'], corrected_text)
                
                if corrected_text != old_text:
                    suggestions.append({
                        'original': old_text,
                        'corrected': corrected_text,
                        'type': 'grammar',
                        'confidence': rule['confidence']
                    })
        
        return corrected_text, suggestions
    
    def _correct_punctuation(self, text: str, threshold: float) -> Tuple[str, List[Dict]]:
        """Correct punctuation errors"""
        corrected_text = text
        suggestions = []
        
        # Fix missing spaces after punctuation
        pattern = r'([.!?,:;])([A-Za-z])'
        if re.search(pattern, corrected_text):
            old_text = corrected_text
            corrected_text = re.sub(pattern, r'\1 \2', corrected_text)
            suggestions.append({
                'original': old_text,
                'corrected': corrected_text,
                'type': 'punctuation',
                'confidence': 0.9
            })
        
        # Fix multiple spaces
        pattern = r'\s{2,}'
        if re.search(pattern, corrected_text):
            old_text = corrected_text
            corrected_text = re.sub(pattern, ' ', corrected_text)
            suggestions.append({
                'original': old_text,
                'corrected': corrected_text,
                'type': 'punctuation',
                'confidence': 0.95
            })
        
        # Fix missing periods at end of sentences
        if corrected_text and not corrected_text.strip().endswith(('.', '!', '?')):
            old_text = corrected_text
            corrected_text = corrected_text.strip() + '.'
            suggestions.append({
                'original': old_text,
                'corrected': corrected_text,
                'type': 'punctuation',
                'confidence': 0.8
            })
        
        return corrected_text, suggestions
    
    def _improve_fluency(self, text: str, threshold: float) -> Tuple[str, List[Dict]]:
        """Improve text fluency"""
        corrected_text = text
        suggestions = []
        
        # Apply fluency patterns
        for pattern in self.fluency_patterns:
            if pattern['pattern'].search(corrected_text):
                old_text = corrected_text
                corrected_text = pattern['pattern'].sub(pattern['replacement'], corrected_text)
                
                if corrected_text != old_text and pattern['confidence'] >= threshold:
                    suggestions.append({
                        'original': old_text,
                        'corrected': corrected_text,
                        'type': 'fluency',
                        'confidence': pattern['confidence']
                    })
        
        return corrected_text, suggestions
    
    def _preserve_case_and_punct(self, original: str, corrected: str) -> str:
        """Preserve original case and punctuation"""
        if not original or not corrected:
            return corrected
        
        result = ""
        corrected_lower = corrected.lower()
        
        i = 0
        for char in original:
            if char.isalpha() and i < len(corrected_lower):
                if char.isupper():
                    result += corrected_lower[i].upper()
                else:
                    result += corrected_lower[i]
                i += 1
            elif not char.isalpha():
                result += char
        
        # Add remaining characters from corrected word
        if i < len(corrected_lower):
            result += corrected_lower[i:]
        
        return result
    
    def _load_grammar_rules(self) -> List[Dict]:
        """Load grammar correction rules"""
        return [
            {
                'pattern': re.compile(r'\bi\b', re.IGNORECASE),
                'replacement': 'I',
                'confidence': 0.95
            },
            {
                'pattern': re.compile(r'\bteh\b', re.IGNORECASE),
                'replacement': 'the',
                'confidence': 0.9
            },
            {
                'pattern': re.compile(r'\band\s+and\b', re.IGNORECASE),
                'replacement': 'and',
                'confidence': 0.9
            },
            {
                'pattern': re.compile(r'\bthe\s+the\b', re.IGNORECASE),
                'replacement': 'the',
                'confidence': 0.9
            },
            {
                'pattern': re.compile(r'\bis\s+are\b', re.IGNORECASE),
                'replacement': 'are',
                'confidence': 0.8
            }
        ]
    
    def _load_fluency_patterns(self) -> List[Dict]:
        """Load fluency improvement patterns"""
        return [
            {
                'pattern': re.compile(r'\bvery\s+very\b', re.IGNORECASE),
                'replacement': 'extremely',
                'confidence': 0.8
            },
            {
                'pattern': re.compile(r'\bgood\s+good\b', re.IGNORECASE),
                'replacement': 'excellent',
                'confidence': 0.7
            },
            {
                'pattern': re.compile(r'\bbig\s+big\b', re.IGNORECASE),
                'replacement': 'enormous',
                'confidence': 0.7
            },
            {
                'pattern': re.compile(r'\bsmall\s+small\b', re.IGNORECASE),
                'replacement': 'tiny',
                'confidence': 0.7
            },
            {
                'pattern': re.compile(r'\ba\s+lot\s+of\b', re.IGNORECASE),
                'replacement': 'many',
                'confidence': 0.75
            }
        ]
    
    def get_word_suggestions(self, word: str, limit: int = 5) -> List[str]:
        """Get spelling suggestions for a word"""
        clean_word = re.sub(r'[^\w]', '', word.lower())
        candidates = self.spell_checker.candidates(clean_word)
        
        if candidates:
            return list(candidates)[:limit]
        return []
    
    def is_word_correct(self, word: str) -> bool:
        """Check if a word is spelled correctly"""
        clean_word = re.sub(r'[^\w]', '', word.lower())
        return clean_word in self.spell_checker