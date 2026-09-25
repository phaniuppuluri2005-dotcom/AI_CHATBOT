"""
Typo Tolerance & Fuzzy String Matching Utility for Phani AI.
Translates informal, misspelt queries into standard intents and entities.
"""

import re
from typing import List, Tuple, Optional


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate the Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def similarity_ratio(s1: str, s2: str) -> float:
    """Calculate a 0.0 to 1.0 similarity ratio between two strings."""
    s1_clean = re.sub(r'[^a-z0-9]', '', s1.lower())
    s2_clean = re.sub(r'[^a-z0-9]', '', s2.lower())
    if not s1_clean or not s2_clean:
        return 0.0
    if s1_clean == s2_clean:
        return 1.0
    dist = levenshtein_distance(s1_clean, s2_clean)
    max_len = max(len(s1_clean), len(s2_clean))
    return 1.0 - (dist / max_len)


# Common typo dictionary mapping misspelt words to canonical terms
TYPO_DICTIONARY = {
    "pythonn": "Python",
    "pyhton": "Python",
    "pythn": "Python",
    "jvaa": "Java",
    "javva": "Java",
    "powr": "Power",
    "powre": "Power",
    "tablue": "Tableau",
    "tableu": "Tableau",
    "wether": "weather",
    "wather": "weather",
    "wheather": "weather",
    "temp": "temperature",
    "temprature": "temperature",
    "criket": "cricket",
    "crickut": "cricket",
    "scoor": "score",
    "skore": "score",
    "bitcion": "bitcoin",
    "btcoin": "bitcoin",
    "ethrium": "ethereum",
    "crypto": "cryptocurrency",
    "newz": "news",
    "incepton": "Inception",
    "puspha": "Pushpa",
    "pushpaa": "Pushpa",
    "poshpa": "Pushpa",
    "hyderbad": "Hyderabad",
    "hyd": "Hyderabad",
    "blore": "Bangalore",
    "bengaluru": "Bangalore",
    "del": "Delhi",
    "usd": "USD",
    "inr": "INR",
    "doller": "dollar",
    "dollers": "dollars",
    "rupee": "rupees",
    "rupes": "rupees",
    "translat": "translate",
    "telgu": "Telugu",
    "hndi": "Hindi",
    "scor": "score",
    "scrore": "score"
}


def correct_typos(text: str) -> str:
    """Correct common typos and slang in a query string."""
    tokens = text.split()
    corrected = []
    for token in tokens:
        clean_tok = re.sub(r'[^a-zA-Z]', '', token).lower()
        if clean_tok in TYPO_DICTIONARY:
            # Preserve original non-alpha characters around the token
            replacement = TYPO_DICTIONARY[clean_tok]
            token_corr = re.sub(clean_tok, replacement, token, flags=re.IGNORECASE)
            corrected.append(token_corr)
        else:
            corrected.append(token)
    return " ".join(corrected)


def find_best_fuzzy_match(word: str, candidates: List[str], threshold: float = 0.75) -> Optional[Tuple[str, float]]:
    """Find the best fuzzy candidate match for a given word."""
    best_candidate = None
    best_score = 0.0
    for cand in candidates:
        score = similarity_ratio(word, cand)
        if score > best_score and score >= threshold:
            best_score = score
            best_candidate = cand
    if best_candidate:
        return best_candidate, best_score
    return None
