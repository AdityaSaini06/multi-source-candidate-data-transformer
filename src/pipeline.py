
# detect -> extract -> normalize -> match -> merge -> confidence -> validate -> project

from .extract import extract_csv, extract_github
from .match import dedupe_csv_records, match_key
from .normalize import (
    normalize_phone, normalize_email, normalize_country, normalize_date,
    derive_github_skills,
)
from .merge import merge_candidate
from .validate import validate_canonical, validate_projection
from .project import project_default, project
import hashlib


def make_candidate_id(raw_record):
    tier, key = match_key(raw_record)
    digest = hashlib.sha256(f"{tier}:{key}".encode("utf-8")).hexdigest()[:12]
    return f"cand_{digest}"


def normalize_csv_record(raw):
    return {
        "full_name": raw.get("full_name"),
        "email": normalize_email(raw.get("email")),
        "phone": normalize_phone(raw.get("phone")),
        "city": raw.get("city"),
        "region": raw.get("region"),
        "country": normalize_country(raw.get("country")),
        "linkedin": raw.get("linkedin"),
        "github_url": raw.get("github_url"),
        "github_username": raw.get("github_username"),
        "portfolio": raw.get("portfolio"),
        "current_company": raw.get("current_company"),
        "title": raw.get("title"),
        "years_experience": raw.get("years_experience"),
    }


def run_pipeline(csv_path, config=None):
    warnings = []

    csv_extraction = extract_csv(csv_path)
    if csv_extraction["status"] != "ok":
        warnings.append(f"CSV source unavailable: {csv_extraction['status']}")
        return {"results": [], "warnings": warnings}

    deduped = dedupe_csv_records(csv_extraction["records"])

    results = []
    for raw_record in deduped:
        candidate_id = make_candidate_id(raw_record)
        csv_record = normalize_csv_record(raw_record)

        github_username = csv_record.get("github_username")
        github_profile = {}
        github_skills = []

        if github_username:
            gh = extract_github(github_username)
            if gh["status"] == "ok":
                github_profile = gh["profile"]
                github_skills = derive_github_skills(gh["repos"])
            else:
                warnings.append(
                    f"{candidate_id}: GitHub source unavailable for "
                    f"'{github_username}' ({gh['status']})"
                )

        canonical_record, provenance, confidence_map = merge_candidate(
            csv_record, github_profile, github_skills, candidate_id
        )

        sanity_warnings = validate_canonical(canonical_record)
        warnings.extend(f"{candidate_id}: {w}" for w in sanity_warnings)

        if config:
            output = project(canonical_record, config, provenance, confidence_map)
            output = validate_projection(output, config)
        else:
            output = project_default(canonical_record, provenance, confidence_map)

        results.append(output)

    return {"results": results, "warnings": warnings}