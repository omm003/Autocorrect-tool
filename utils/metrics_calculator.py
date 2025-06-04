import re
import math
from typing import Dict, List
from textblob import TextBlob

class MetricsCalculator:
    def __init__(self):
        self.syllable_patterns = [
            re.compile(r'[aeiouy]+', re.IGNORECASE),
            re.compile(r'[^aeiouy\s]+', re.IGNORECASE)
        ]
    
    def calculate_accuracy(self, original: str, corrected: str) -> float:
        """Calculate accuracy improvement percentage"""
        if not original:
            return 100.0
        
        original_words = original.split()
        corrected_words = corrected.split()
        
        if len(original_words) != len(corrected_words):
            # Handle different word counts
            min_length = min(len(original_words), len(corrected_words))
            original_words = original_words[:min_length]
            corrected_words = corrected_words[:min_length]
        
        if not original_words:
            return 100.0
        
        corrections_made = sum(1 for orig, corr in zip(original_words, corrected_words) if orig != corr)
        improvement = (corrections_made / len(original_words)) * 100
        
        return min(improvement, 100.0)
    
    def calculate_readability(self, text: str) -> float:
        """Calculate readability score (Flesch Reading Ease)"""
        if not text.strip():
            return 0.0
        
        sentences = self._count_sentences(text)
        words = self._count_words(text)
        syllables = self._count_syllables(text)
        
        if sentences == 0 or words == 0:
            return 0.0
        
        # Flesch Reading Ease formula
        score = 206.835 - (1.015 * (words / sentences)) - (84.6 * (syllables / words))
        return max(0.0, min(100.0, score))
    
    def calculate_fluency(self, text: str) -> float:
        """Calculate fluency score based on various factors"""
        if not text.strip():
            return 0.0
        
        # Factors for fluency calculation
        word_variety = self._calculate_word_variety(text)
        sentence_variety = self._calculate_sentence_variety(text)
        grammar_score = self._calculate_grammar_score(text)
        coherence_score = self._calculate_coherence_score(text)
        
        # Weighted average
        fluency = (
            word_variety * 0.25 +
            sentence_variety * 0.25 +
            grammar_score * 0.3 +
            coherence_score * 0.2
        )
        
        return min(100.0, max(0.0, fluency))
    
    def calculate_typing_speed(self, text: str, time_taken: float) -> Dict:
        """Calculate typing speed metrics"""
        if time_taken <= 0:
            return {'wpm': 0, 'cpm': 0}
        
        words = len(text.split())
        characters = len(text)
        
        # Words per minute
        wpm = (words / time_taken) * 60
        
        # Characters per minute
        cpm = (characters / time_taken) * 60
        
        return {
            'wpm': round(wpm, 1),
            'cpm': round(cpm, 1)
        }
    
    def calculate_error_rate(self, original: str, corrected: str) -> Dict:
        """Calculate error rate metrics"""
        original_words = original.split()
        corrected_words = corrected.split()
        
        total_words = len(original_words)
        if total_words == 0:
            return {'error_rate': 0.0, 'accuracy_rate': 100.0, 'errors_corrected': 0}
        
        # Count differences
        min_length = min(len(original_words), len(corrected_words))
        errors = sum(1 for i in range(min_length) if original_words[i] != corrected_words[i])
        
        # Add length difference as errors
        errors += abs(len(original_words) - len(corrected_words))
        
        error_rate = (errors / total_words) * 100
        accuracy_rate = 100 - error_rate
        
        return {
            'error_rate': round(error_rate, 2),
            'accuracy_rate': round(accuracy_rate, 2),
            'errors_corrected': errors
        }
    
    def _count_sentences(self, text: str) -> int:
        """Count sentences in text"""
        sentences = re.split(r'[.!?]+', text)
        return len([s for s in sentences if s.strip()])
    
    def _count_words(self, text: str) -> int:
        """Count words in text"""
        return len(text.split())
    
    def _count_syllables(self, text: str) -> int:
        """Count syllables in text"""
        words = text.lower().split()
        total_syllables = 0
        
        for word in words:
            # Remove punctuation
            word = re.sub(r'[^a-z]', '', word)
            if not word:
                continue
            
            # Count vowel groups
            vowel_groups = len(re.findall(r'[aeiouy]+', word))
            
            # Adjust for silent e
            if word.endswith('e') and vowel_groups > 1:
                vowel_groups -= 1
            
            # At least one syllable per word
            total_syllables += max(1, vowel_groups)
        
        return total_syllables
    
    def _calculate_word_variety(self, text: str) -> float:
        """Calculate word variety score"""
        words = [word.lower() for word in text.split()]
        if not words:
            return 0.0
        
        unique_words = len(set(words))
        total_words = len(words)
        
        # Type-Token Ratio (TTR)
        ttr = (unique_words / total_words) * 100
        return min(100.0, ttr)
    
    def _calculate_sentence_variety(self, text: str) -> float:
        """Calculate sentence length variety"""
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        if len(sentences) < 2:
            return 50.0  # Default score for single sentence
        
        lengths = [len(s.split()) for s in sentences]
        avg_length = sum(lengths) / len(lengths)
        
        # Calculate variance
        variance = sum((length - avg_length) ** 2 for length in lengths) / len(lengths)
        std_dev = math.sqrt(variance)
        
        # Normalize to 0-100 scale
        variety_score = min(100.0, (std_dev / avg_length) * 100)
        return variety_score
    
    def _calculate_grammar_score(self, text: str) -> float:
        """Calculate grammar score using basic heuristics"""
        if not text.strip():
            return 0.0
        
        score = 100.0
        
        # Check for basic grammar issues
        blob = TextBlob(text)
        
        # Check sentence structure
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        for sentence in sentences:
            words = sentence.split()
            
            # Penalize very short sentences (less than 3 words)
            if len(words) < 3:
                score -= 5
            
            # Penalize very long sentences (more than 25 words)
            if len(words) > 25:
                score -= 10
        
        # Check for repeated words
        words = text.lower().split()
        for i in range(len(words) - 1):
            if words[i] == words[i + 1]:
                score -= 5
        
        return max(0.0, min(100.0, score))
    
    def _calculate_coherence_score(self, text: str) -> float:
        """Calculate text coherence score"""
        if not text.strip():
            return 0.0
        
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        if len(sentences) < 2:
            return 75.0  # Default score for single sentence
        
        # Simple coherence based on connecting words
        connecting_words = [
            'and', 'but', 'or', 'so', 'because', 'although', 'however',
            'therefore', 'moreover', 'furthermore', 'meanwhile', 'consequently'
        ]
        
        coherence_score = 50.0  # Base score
        
        for sentence in sentences:
            words = sentence.lower().split()
            if any(word in connecting_words for word in words):
                coherence_score += 10
        
        return min(100.0, coherence_score)
    
    def get_detailed_analysis(self, text: str) -> Dict:
        """Get detailed text analysis"""
        if not text.strip():
            return {
                'word_count': 0,
                'character_count': 0,
                'sentence_count': 0,
                'paragraph_count': 0,
                'avg_words_per_sentence': 0,
                'readability_score': 0,
                'fluency_score': 0
            }
        
        word_count = self._count_words(text)
        char_count = len(text)
        sentence_count = self._count_sentences(text)
        paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
        
        avg_words_per_sentence = word_count / sentence_count if sentence_count > 0 else 0
        
        return {
            'word_count': word_count,
            'character_count': char_count,
            'sentence_count': sentence_count,
            'paragraph_count': paragraph_count,
            'avg_words_per_sentence': round(avg_words_per_sentence, 1),
            'readability_score': round(self.calculate_readability(text), 1),
            'fluency_score': round(self.calculate_fluency(text), 1)
        }