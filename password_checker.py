"""Password strength checking logic, kept separate from the GUI so it can be tested and reused."""

import hashlib
import math
import re
import urllib.request
from dataclasses import dataclass, field

MINIMUM_LENGTH = 12     # Minimum length for any password
PASSPHRASE_LENGTH = 20  # Passwords this long skip the character-type rules (NIST SP 800-63B favours length)


# Function to list every run of min_length+ consecutive characters from the given lines
def runs_of(lines, min_length):
    runs = set()
    for line in lines:
        for length in range(min_length, len(line) + 1):
            for start in range(len(line) - length + 1):
                runs.add(line[start:start + length])
    return runs


# Function to build a regex matching any of the given strings
# Longest strings first, so 'abcdef' is matched as a whole instead of just 'abc'
def any_of(strings):
    return "|".join(re.escape(s) for s in sorted(strings, key=len, reverse=True))


# ---Weak password patterns---
#     1. Three or more identical consecutive characters (e.g., 'aaa', '111').
#     2. Ascending / descending letter sequences of 3+ characters (e.g., 'abc', 'zyx').
#     3. Ascending / descending digit sequences of 3+ characters (e.g., '123', '987').
#     4. Runs of 4+ neighbouring keys on a keyboard row (e.g., 'qwer', 'lkjh'),
#        plus the vertical columns people often use (e.g., '1qaz', '2wsx').
ALPHABET = "abcdefghijklmnopqrstuvwxyz"
DIGITS = "0123456789"
KEYBOARD_ROWS = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]
KEYBOARD_COLUMNS = ["1qaz", "2wsx", "3edc", "4rfv", "5tgb", "6yhn", "7ujm"]

IDENTICAL_PATTERN = r"(.)\1{2,}"
ASCENDING_LETTER_PATTERN = any_of(runs_of([ALPHABET], 3))
DESCENDING_LETTER_PATTERN = any_of(runs_of([ALPHABET[::-1]], 3))
ASCENDING_DIGIT_PATTERN = any_of(runs_of([DIGITS], 3))
DESCENDING_DIGIT_PATTERN = any_of(runs_of([DIGITS[::-1]], 3))
KEYBOARD_PATTERN = any_of(
    runs_of(KEYBOARD_ROWS + [row[::-1] for row in KEYBOARD_ROWS], 4)
    | set(KEYBOARD_COLUMNS + [col[::-1] for col in KEYBOARD_COLUMNS])
)

# ---Common passwords and words---
# Passwords (and words inside passwords) that attackers try first.
# Expand this list for better protection.
COMMON_PASSWORDS = {
    "password", "passw", "pass", "welcome", "qwerty", "admin", "administrator",
    "letmein", "monkey", "dragon", "master", "shadow", "sunshine", "princess",
    "football", "baseball", "soccer", "hockey", "cricket", "iloveyou", "trustno",
    "superman", "batman", "starwars", "whatever", "freedom", "michael", "jennifer",
    "jordan", "hunter", "ranger", "buster", "thomas", "robert", "charlie", "ashley",
    "bailey", "summer", "winter", "spring", "autumn", "flower", "hello", "secret",
    "login", "access", "mustang", "harley", "pepper", "ginger", "cookie", "cheese",
    "computer", "internet", "samsung", "google", "apple", "orange", "banana",
    "chocolate", "maggie", "tigger", "killer", "matrix", "ninja", "pokemon",
    "naruto", "love", "angel", "lovely", "family", "friend", "india", "london",
    "america", "changeme", "default", "guest", "test", "user", "root", "temp",
    "office", "company", "money", "purple", "yellow", "silver", "golden",
    "diamond", "liverpool", "chelsea", "arsenal", "qazwsx",
}
COMMON_WORD_PATTERN = any_of(COMMON_PASSWORDS)

# Leetspeak substitutions, so 'P@ssw0rd' is recognised as 'password'
LEET_MAP = str.maketrans({"@": "a", "4": "a", "3": "e", "1": "i", "!": "i",
                          "0": "o", "$": "s", "5": "s", "7": "t", "+": "t"})

# Ratings from weakest to strongest: (name, minimum bits of entropy)
RATINGS = [("Weak", 0), ("Fair", 45), ("Good", 60), ("Strong", 75)]


@dataclass
class Evaluation:
    """Result of checking a password."""
    requirements: list = field(default_factory=list)  # (description, passed) pairs
    is_passphrase: bool = False  # Long enough to skip the character-type rules
    is_common: bool = False      # Based on a common password
    bits: float = 0.0            # Estimated entropy
    rating: str = ""             # 'Weak', 'Fair', 'Good' or 'Strong' ('' for empty input)
    warnings: list = field(default_factory=list)  # Weak patterns found

    @property
    def meets_requirements(self):
        return all(passed for _, passed in self.requirements)

    @property
    def level(self):
        """Rating as a number from 0 (empty) to 4 (Strong), e.g. for a meter."""
        names = [name for name, _ in RATINGS]
        return names.index(self.rating) + 1 if self.rating else 0


# Function to list each basic requirement and whether the password meets it
def check_requirements(password):
    is_passphrase = len(password) >= PASSPHRASE_LENGTH
    character_rules = [
        ("At least 1 uppercase letter (A-Z)", r"[A-Z]"),
        ("At least 1 lowercase letter (a-z)", r"[a-z]"),
        ("At least 1 digit (0-9)", r"\d"),
        ("At least 1 special character (!, @, #, etc.)", r"[^a-zA-Z0-9]"),
    ]
    requirements = [(f"At least {MINIMUM_LENGTH} characters long", len(password) >= MINIMUM_LENGTH)]
    for description, pattern in character_rules:
        # Long passphrases pass the character-type rules automatically
        requirements.append((description, is_passphrase or bool(re.search(pattern, password))))
    return requirements, is_passphrase


# Function to check if a password is (or is built on) a common password
def is_common_password(password):
    # Remove digits/symbols added at the start or end (e.g., 'Password123!' -> 'Password')
    core = re.sub(r"^[^a-zA-Z]+|[^a-zA-Z]+$", "", password).lower()
    # Undo leetspeak, trying '1' as both 'i' and 'l'
    candidates = {core, core.translate(LEET_MAP), core.replace("1", "l").translate(LEET_MAP)}
    return any(candidate in COMMON_PASSWORDS for candidate in candidates)


# Function to estimate password strength in bits of entropy
# Each random character adds log2(pool size) bits. Characters that are part of a
# guessable pattern (common word, keyboard run, sequence, repeat) only add a small
# fixed amount, because attackers try those patterns first.
# Returns (bits, list of warnings)
def estimate_strength(password):
    # Size of the character pool the password draws from
    pool = 0
    if re.search(r"[a-z]", password): pool += 26
    if re.search(r"[A-Z]", password): pool += 26
    if re.search(r"\d", password): pool += 10
    if re.search(r"[^a-zA-Z0-9]", password): pool += 33
    bits_per_char = math.log2(pool) if pool else 0

    lowered = password.lower()
    deleeted = lowered.translate(LEET_MAP)  # Same length, so positions line up

    # (regex, text to search, bits the whole match is worth, warning message)
    pattern_checks = [
        (COMMON_WORD_PATTERN, deleeted, 12, "Contains a common word ('{}')"),
        (KEYBOARD_PATTERN, lowered, 8, "Contains a keyboard pattern ('{}')"),
        (ASCENDING_LETTER_PATTERN, lowered, 8, "Contains an ascending letter sequence ('{}')"),
        (DESCENDING_LETTER_PATTERN, lowered, 8, "Contains a descending letter sequence ('{}')"),
        (ASCENDING_DIGIT_PATTERN, lowered, 8, "Contains an ascending digit sequence ('{}')"),
        (DESCENDING_DIGIT_PATTERN, lowered, 8, "Contains a descending digit sequence ('{}')"),
        (IDENTICAL_PATTERN, lowered, 8, "Contains repeated characters ('{}')"),
    ]

    covered = [False] * len(password)  # Characters already counted as part of a pattern
    bits = 0
    warnings = []
    for pattern, text, pattern_bits, warning in pattern_checks:
        for match in re.finditer(pattern, text):
            # Skip matches overlapping a pattern that was already counted
            if any(covered[match.start():match.end()]):
                continue
            covered[match.start():match.end()] = [True] * (match.end() - match.start())
            bits += pattern_bits
            message = warning.format(password[match.start():match.end()])
            if message not in warnings:
                warnings.append(message)

    # Every character not in a pattern counts as random
    bits += bits_per_char * covered.count(False)
    return bits, warnings


# Function to turn bits of entropy into a rating name
def rate_strength(bits):
    rating = RATINGS[0][0]
    for name, minimum_bits in RATINGS:
        if bits >= minimum_bits:
            rating = name
    return rating


# Function to fully check a password
def evaluate(password):
    if password == "":
        return Evaluation()

    requirements, is_passphrase = check_requirements(password)
    bits, warnings = estimate_strength(password)
    evaluation = Evaluation(
        requirements=requirements,
        is_passphrase=is_passphrase,
        is_common=is_common_password(password),
        bits=bits,
        warnings=warnings,
    )
    # Passwords failing a requirement or based on a common password are always weak
    if not evaluation.meets_requirements or evaluation.is_common:
        evaluation.rating = "Weak"
    else:
        evaluation.rating = rate_strength(bits)
    return evaluation


# Function to count how often a password appears in known data breaches
# Uses the Have I Been Pwned range API with k-anonymity: only the first 5 characters
# of the password's SHA-1 hash are sent, never the password itself.
# Raises OSError (e.g., no internet connection) if the lookup fails.
def check_breach(password, timeout=5):
    sha1 = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]
    request = urllib.request.Request(
        f"https://api.pwnedpasswords.com/range/{prefix}",
        headers={"User-Agent": "Password-Strength-Tester", "Add-Padding": "true"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read().decode("utf-8")
    # Each line is 'HASH_SUFFIX:COUNT'
    for line in body.splitlines():
        line_suffix, _, count = line.partition(":")
        if line_suffix == suffix:
            return int(count)
    return 0
