import re
import difflib
from typing import List, Dict, Tuple

class TextProcessor:
    def __init__(self):
        self.common_contractions = {
            "won't": "will not",
            "can't": "cannot",
            "n't": " not",
            "'re": " are",
            "'ve": " have",
            "'ll": " will",
            "'d": " would",
            "'m": " am"
        }
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for correction"""
        # Remove extra whitespaces
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Fix common spacing issues
        text = re.sub(r'\s+([,.!?;:])', r'\1', text)
        text = re.sub(r'([,.!?;:])\s*', r'\1 ', text)
        
        return text
    
    def expand_contractions(self, text: str) -> str:
        """Expand contractions in text"""
        for contraction, expansion in self.common_contractions.items():
            text = text.replace(contraction, expansion)
        return text
    
    def find_differences(self, original: str, corrected: str) -> List[Dict]:
        """Find differences between original and corrected text"""
        differences = []
        
        # Use difflib to find differences
        differ = difflib.unified_diff(
            original.split(), 
            corrected.split(), 
            lineterm=''
        )
        
        diff_list = list(differ)
        
        # Parse differences
        for i, line in enumerate(diff_list):
            if line.startswith('-') and not line.startswith('---'):
                original_word = line[1:].strip()
                if i + 1 < len(diff_list) and diff_list[i + 1].startswith('+'):
                    corrected_word = diff_list[i + 1][1:].strip()
                    
                    differences.append({
                        'original': original_word,
                        'corrected': corrected_word,
                        'type': self._classify_correction(original_word, corrected_word),
                        'reason': self._get_correction_reason(original_word, corrected_word),
                        'confidence': self._calculate_confidence(original_word, corrected_word)
                    })
        
        return differences
    
    def _classify_correction(self, original: str, corrected: str) -> str:
        """Classify the type of correction"""
        if len(original) != len(corrected):
            return "Spelling"
        elif original.lower() == corrected.lower():
            return "Capitalization"
        elif self._is_grammar_correction(original, corrected):
            return "Grammar"
        else:
            return "Fluency"
    
    def _is_grammar_correction(self, original: str, corrected: str) -> bool:
        """Check if correction is grammar-related"""
        grammar_indicators = ['was', 'were', 'is', 'are', 'have', 'has', 'had']
        return any(word in [original.lower(), corrected.lower()] for word in grammar_indicators)
    
    def _get_correction_reason(self, original: str, corrected: str) -> str:
        """Get reason for correction"""
        if original.lower() != corrected.lower():
            if len(original) > len(corrected):
                return "Removed unnecessary characters"
            elif len(original) < len(corrected):
                return "Added missing characters"
            else:
                return "Fixed spelling error"
        elif original != corrected:
            return "Fixed capitalization"
        else:
            return "Improved fluency"
    
    def _calculate_confidence(self, original: str, corrected: str) -> float:
        """Calculate confidence score for correction"""
        # Simple confidence calculation based on edit distance
        edit_distance = self._edit_distance(original, corrected)
        max_length = max(len(original), len(corrected))
        
        if max_length == 0:
            return 1.0
        
        confidence = 1.0 - (edit_distance / max_length)
        return max(0.5, confidence)  # Minimum confidence of 0.5
    
    def _edit_distance(self, s1: str, s2: str) -> int:
        """Calculate edit distance between two strings"""
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i-1] == s2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
        
        return dp[m][n]
    
    def extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def count_words(self, text: str) -> int:
        """Count words in text"""
        return len(text.split())
    
    def count_characters(self, text: str) -> int:
        """Count characters in text"""
        return len(text)
    
    def calculate_typing_errors(self, original: str, corrected: str) -> Dict:
        """Calculate various typing error metrics"""
        original_words = original.split()
        corrected_words = corrected.split()
        
        total_words = len(original_words)
        corrected_count = sum(1 for orig, corr in zip(original_words, corrected_words) if orig != corr)
        
        return {
            'total_words': total_words,
            'errors_corrected': corrected_count,
            'error_rate': (corrected_count / total_words * 100) if total_words > 0 else 0,
            'accuracy': ((total_words - corrected_count) / total_words * 100) if total_words > 0 else 100
        }