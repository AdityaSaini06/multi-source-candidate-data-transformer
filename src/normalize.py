import re
from datetime import datetime

from .constants import(
    DEFAULT_REGION,
    DATE_FORMATS_FULL,
    DATE_FORMATS_MONTH_ONLY,
    SKILL_SYNONYMS,
    COUNTRY_NAME_TO_ALPHA2
)

try:
    import phonenumbers
except ImportError:
    phonenumbers = None

def normalize_phone(raw,default_region=DEFAULT_REGION):
    if not raw:
        return None
    
    raw = str(raw).strip()

    if phonenumbers is None:
        raise raw
    
    try:
        parsed_number = phonenumbers.parse(raw, default_region)
        if phonenumbers.is_valid_number(parsed_number):
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        return raw
    
    except Exception:
        return raw
    
def normalize_date(raw):
    if not raw:
        return None
    
    raw = str(raw).strip()

    for fmt in DATE_FORMATS_FULL:
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    for fmt in DATE_FORMATS_MONTH_ONLY:
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m")
        except ValueError:
            continue

    return None

def normalize_country(raw):
    if not raw:
        return None
    
    raw = str(raw).strip()

    if len(raw) == 2:
        return raw.upper()  
    
    return COUNTRY_NAME_TO_ALPHA2.get(raw.lower())

def normalize_skill_name(raw):
    # Lowercase, strip punctuation/whitespace, map known synonyms
    if not raw:
        return None
    
    cleaned = re.sub(r"[^a-z0-9+. ]", "", str(raw).strip().lower())
    cleaned = cleaned.strip()

    return SKILL_SYNONYMS.get(cleaned, cleaned) if cleaned else None

def normalize_email(raw):
    if not raw:
        return None

    return str(raw).strip().lower()

def normalize_name(raw):
    # Used as a matching key, not as a display value
    if not raw:
        return None
    return re.sub(r"\s+", " ", str(raw).strip().lower())

def derive_github_skills(repos):
    from collections import Counter

    languages = []

    for repo in repos or []:
        if repo.get("fork") or repo.get("archived") or repo.get("disabled"):
            continue
        lang = repo.get("language")
        if lang:
            languages.append(lang.strip().lower())

    if not languages:
        return []

    counts = Counter(languages)
    total = sum(counts.values())
    return [
        {"name": normalize_skill_name(lang) or lang, "confidence": round(count / total, 2), "sources": ["github"]}
        for lang, count in counts.most_common()
    ]