from .normalize import normalize_name, normalize_skill_name

from .constants import (
    TRUST_CSV,
    TRUST_GITHUB
)

def pick_winner(csv_val, github_val, field_name, trust_csv=TRUST_CSV, trust_github=TRUST_GITHUB):
    # Returns (value, provenance_entry or None, confidence)
    # Returns (None, None, 0) if both sources are empty.
    if csv_val and github_val:
        if normalize_name(str(csv_val)) == normalize_name(str(github_val)):
            confidence = min(1.0, round(trust_csv + 0.1, 2))
            method = "agreement"
        else:
            confidence = max(0.0, round(trust_csv - 0.1, 2))
            method = "source_priority_conflict"
        value, source = csv_val, "csv"

    elif csv_val:
        value, source, confidence, method = csv_val, "csv", trust_csv, "only_source"

    elif github_val:
        value, source, confidence, method = github_val, "github", trust_github, "only_source"

    else:
        return None, None, 0.0

    provenance_entry = {"field": field_name, "source": source, "method": method}
    return value, provenance_entry, confidence


def merge_skills(csv_skills, github_skills):
    # csv_skills / github_skills: list of {"name", "confidence", "sources"}.
    # Union by normalized name; if a skill appears in both, keep the max
    # confidence and merge the sources list.
    # Returns (skills_list, provenance_entry_or_None).
    merged = {}

    for skill in (csv_skills or []) + (github_skills or []):
        if "confidence" not in skill:
            raise ValueError(
                f"Skill '{skill.get('name')}' is missing required 'confidence'. "
                "Every extractor must provide a confidence score."
            )

        confidence = skill["confidence"]
        name = normalize_skill_name(skill.get("name"))
        if not name:
            continue
        if name not in merged:
            merged[name] = {
                "name": name,
                "confidence": confidence,
                "sources": list(skill.get("sources", [])),
            }
        else:
            existing = merged[name]
            existing["confidence"] = max(existing["confidence"], skill.get("confidence", confidence))
            for s in skill.get("sources", []):
                if s not in existing["sources"]:
                    existing["sources"].append(s)

    skills_list = sorted(merged.values(), key=lambda s: -s["confidence"])

    if not skills_list:
        return [], None

    sources_used = sorted({s for skill in skills_list for s in skill["sources"]})
    provenance_entry = {
        "field": "skills",
        "source": "+".join(sources_used),
        "method": "union_merge",
    }
    return skills_list, provenance_entry


def merge_candidate(csv_record, github_profile, github_skills, candidate_id):
    # Returns (canonical_record, provenance_list, internal_confidence_map)
    record = {"candidate_id": candidate_id}
    provenance = []
    confidence_map = {}

    def set_field(field_name, csv_val, github_val=None, trust_github=TRUST_GITHUB):
        value, prov, conf = pick_winner(csv_val, github_val, field_name, trust_github=trust_github)
        record[field_name] = value
        if prov:
            provenance.append(prov)
        confidence_map[field_name] = conf

    set_field("full_name", csv_record.get("full_name"), github_profile.get("name"))
    set_field("headline", None, github_profile.get("bio"))  # GitHub-only field

    # emails / phones / location / links are CSV-only by policy - no GitHub fallback
    record["emails"] = [csv_record["email"]] if csv_record.get("email") else []
    if record["emails"]:
        provenance.append({"field": "emails", "source": "csv", "method": "only_source"})
        confidence_map["emails"] = TRUST_CSV
    else:
        confidence_map["emails"] = 0.0

    record["phones"] = [csv_record["phone"]] if csv_record.get("phone") else []
    if record["phones"]:
        provenance.append({"field": "phones", "source": "csv", "method": "only_source"})
        confidence_map["phones"] = TRUST_CSV
    else:
        confidence_map["phones"] = 0.0

    record["location"] = {
        "city": csv_record.get("city"),
        "region": csv_record.get("region"),
        "country": csv_record.get("country"),
    }
    has_location = any(record["location"].values())
    if has_location:
        provenance.append({"field": "location", "source": "csv", "method": "only_source"})
        confidence_map["location"] = TRUST_CSV
    else:
        confidence_map["location"] = 0.0

    record["links"] = {
        "linkedin": csv_record.get("linkedin"),
        "github": csv_record.get("github_url"),
        "portfolio": csv_record.get("portfolio"),
        "other": [],
    }
    if record["links"]["github"]:
        provenance.append({"field": "links", "source": "csv", "method": "only_source"})
        confidence_map["links"] = TRUST_CSV
    else:
        confidence_map["links"] = 0.0

    raw_years = csv_record.get("years_experience")
    try:
        record["years_experience"] = float(raw_years) if raw_years not in (None, "") else None
        if record["years_experience"] is not None and record["years_experience"].is_integer():
            record["years_experience"] = int(record["years_experience"])
    except (TypeError, ValueError):
        record["years_experience"] = None  # unparseable 

    if record["years_experience"] is not None:
        provenance.append({"field": "years_experience", "source": "csv", "method": "only_source"})
        confidence_map["years_experience"] = TRUST_CSV
    else:
        confidence_map["years_experience"] = 0.0

    # skills - union merge pattern
    csv_skills = []
    if csv_record.get("title"):
        # title is weak skill evidence at best , keep low confidence, separate from real skills
        pass  # not treated as a skill source as it's too unreliable
    skills, skills_prov = merge_skills(csv_skills, github_skills)
    record["skills"] = skills
    if skills_prov:
        provenance.append(skills_prov)
    confidence_map["skills"] = max([s["confidence"] for s in skills], default=0.0)

    # experience - single entry from CSV title/company, CSV-only
    if csv_record.get("current_company") or csv_record.get("title"):
        record["experience"] = [{
            "company": csv_record.get("current_company"),
            "title": csv_record.get("title"),
            "start": None,
            "end": None,
            "summary": None,
        }]
        provenance.append({"field": "experience", "source": "csv", "method": "only_source"})
        confidence_map["experience"] = TRUST_CSV * 0.7  
    else:
        record["experience"] = []
        confidence_map["experience"] = 0.0

    record["education"] = []  # not available from either source in this scope
    confidence_map["education"] = 0.0

    populated_confidences = [c for c in confidence_map.values() if c > 0]
    record["overall_confidence"] = (
        round(sum(populated_confidences) / len(populated_confidences), 2)
        if populated_confidences else 0.0
    )

    return record, provenance, confidence_map