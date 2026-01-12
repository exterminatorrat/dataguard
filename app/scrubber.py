"""
Text Scrubber Module
Detects and redacts PII using regex patterns and validation algorithms.
Zero external API calls - 100% local processing.
"""

import re
from typing import Tuple, Dict


class TextScrubber:
    """High-performance PII detector and redactor"""
    
    # Regex patterns for PII detection
    PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'ssn': r'\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b|\b(?!000|666|9\d{2})\d{3}(?!00)\d{2}(?!0000)\d{4}\b',
        'credit_card': r'\b(?:4\d{3}|5[1-5]\d{2}|6(?:011|5\d{2})|3[47]\d{2}|3(?:0[0-5]|[68]\d)\d|(?:2131|1800|35\d{2}))\s?-?\s?\d{4}\s?-?\s?\d{4}\s?-?\s?\d{4}\b',
        'ipv4': r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
        'ipv6': r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b|\b(?:[0-9a-fA-F]{1,4}:){1,7}:\b|\b(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}\b',
        'aws_key': r'\b(AKIA[0-9A-Z]{16})\b',
    }
    
    # Replacement tokens
    REPLACEMENTS = {
        'email': '[EMAIL]',
        'ssn': '[SSN]',
        'credit_card': '[CREDIT_CARD]',
        'ipv4': '[IP_ADDRESS]',
        'ipv6': '[IP_ADDRESS]',
        'aws_key': '[AWS_KEY]',
    }
    
    @staticmethod
    def luhn_check(card_number: str) -> bool:
        """
        Validate credit card using Luhn algorithm.
        Returns True if valid, False otherwise.
        """
        # Remove spaces and dashes
        card_number = re.sub(r'[\s-]', '', card_number)
        
        if not card_number.isdigit():
            return False
        
        # Luhn algorithm
        total = 0
        reverse_digits = card_number[::-1]
        
        for i, digit in enumerate(reverse_digits):
            n = int(digit)
            if i % 2 == 1:  # Every second digit from the right
                n *= 2
                if n > 9:
                    n -= 9
            total += n
        
        return total % 10 == 0
    
    def scrub_text(self, text: str) -> Tuple[str, Dict[str, int]]:
        """
        Scrub PII from text and return cleaned text with redaction counts.
        
        Args:
            text: The input text to scrub
            
        Returns:
            Tuple of (cleaned_text, redaction_counts_dict)
        """
        if not text:
            return text, {}
        
        cleaned_text = text
        redaction_counts = {key: 0 for key in self.PATTERNS.keys()}
        
        # Process credit cards with Luhn validation
        credit_card_matches = list(re.finditer(self.PATTERNS['credit_card'], cleaned_text))
        valid_cards = []
        
        for match in credit_card_matches:
            card_num = match.group()
            if self.luhn_check(card_num):
                valid_cards.append(match)
        
        # Replace valid credit cards (process from end to start to maintain positions)
        for match in reversed(valid_cards):
            cleaned_text = (
                cleaned_text[:match.start()] + 
                self.REPLACEMENTS['credit_card'] + 
                cleaned_text[match.end():]
            )
            redaction_counts['credit_card'] += 1
        
        # Process other patterns
        for pattern_name, pattern in self.PATTERNS.items():
            if pattern_name == 'credit_card':  # Already processed
                continue
            
            matches = list(re.finditer(pattern, cleaned_text))
            
            # Replace from end to start to maintain string positions
            for match in reversed(matches):
                cleaned_text = (
                    cleaned_text[:match.start()] + 
                    self.REPLACEMENTS[pattern_name] + 
                    cleaned_text[match.end():]
                )
                redaction_counts[pattern_name] += 1
        
        # Calculate total redactions
        total_redactions = sum(redaction_counts.values())
        
        return cleaned_text, {
            'total': total_redactions,
            'details': redaction_counts
        }


# Singleton instance for reuse
scrubber = TextScrubber()
