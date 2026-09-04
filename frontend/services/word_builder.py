"""
Word and Sentence Builder for Sign Language Translator.
Accumulates sequential character or word signs into complete sentences,
handling space insertions, punctuation, and formatting.
"""

from typing import List


class WordBuilder:
    """
    Assembles recognized signs/characters into words and sentences.
    Provides editing controls like backspace, space, and clear.
    """

    def __init__(self):
        self._tokens: List[str] = []
        self._current_sentence: str = ""

    def add_sign(self, sign: str) -> str:
        """
        Add a recognized sign.
        If the sign is a single character, it appends to current word;
        if it is a full word or phrase, it is appended with proper spacing.
        """
        if not sign or sign in ("—", "None", ""):
            return self.get_text()

        sign = sign.strip()

        # Handle special tokens
        if sign == "[SPACE]":
            self.add_space()
            return self.get_text()
        elif sign == "[BACKSPACE]":
            self.backspace()
            return self.get_text()
        elif sign == "[CLEAR]":
            self.clear()
            return self.get_text()

        # Character or word appending
        if len(sign) == 1 and sign.isalpha():
            self._tokens.append(sign)
            self._current_sentence += sign
        else:
            if self._current_sentence and not self._current_sentence.endswith(" "):
                self._current_sentence += " "
            self._current_sentence += sign
            self._tokens.append(sign)

        return self.get_text()

    def add_space(self) -> str:
        """Append a space delimiter."""
        if self._current_sentence and not self._current_sentence.endswith(" "):
            self._current_sentence += " "
        return self.get_text()

    def backspace(self) -> str:
        """Delete the last character or token."""
        if self._current_sentence:
            self._current_sentence = self._current_sentence[:-1].rstrip()
        if self._tokens:
            self._tokens.pop()
        return self.get_text()

    def clear(self) -> str:
        """Reset the buffer."""
        self._tokens.clear()
        self._current_sentence = ""
        return ""

    def get_text(self) -> str:
        """Get formatted sentence."""
        return self._current_sentence.strip()


# Global singleton instance
word_builder = WordBuilder()
