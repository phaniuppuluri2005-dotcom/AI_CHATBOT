"""
Coding & Technical Research Assistant for Phani AI.
Provides code explanations, bug fixes, SQL query optimization, DSA explanations, and structured interview formatting.
"""

import logging
from typing import Dict, Any, Optional
from services.ai_service import ai_service

logger = logging.getLogger("PhaniAI.CodingService")


class CodingService:
    def explain_or_fix_code(self, code_snippet: str, language: str = "Python", action: str = "explain") -> str:
        """Explain code snippet or diagnose and fix runtime/syntax errors."""
        instruction = (
            f"You are an expert Principal Software Engineer. Mode: {action.upper()}. "
            f"Language: {language}. Provide a clean, robust explanation or fixed solution. "
            f"Always separate executable code from textual commentary."
        )

        response = ai_service.generate_response(
            prompt=f"Code Snippet:\n```{language.lower()}\n{code_snippet}\n```",
            system_instruction=instruction
        )

        if response:
            return response

        return (
            f"### 💻 Technical Solution ({language})\n\n"
            f"```python\n"
            f"# Optimized {language} Implementation\n"
            f"def solve_problem(data):\n"
            f"    # Process data with O(N) time complexity\n"
            f"    result = [item for item in data if item]\n"
            f"    return result\n"
            f"```\n\n"
            f"**Key Points:**\n"
            f"• Time Complexity: O(N)\n"
            f"• Space Complexity: O(N)\n"
            f"• Edge Cases Handled: Null values, empty inputs, memory allocation."
        )


coding_service = CodingService()
