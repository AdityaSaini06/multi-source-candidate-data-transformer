from .normalize import normalize_email, normalize_phone, normalize_name

def match_key(record):
    # Priority: email > phone > name. Returns (tier, key) so callers can
    # tell how strong the match is and never let a weak key override a
    # conflicting strong one
    email = normalize_email(record.get("email"))
    if email:
        return ("email", email)

    phone = normalize_phone(record.get("phone"))
    if phone:
        return ("phone", phone)

    name = normalize_name(record.get("full_name"))
    if name:
        return ("name", name)

    return ("unmatched", id(record))  

def dedupe_csv_records(records):
    # Groups raw CSV rows by match_key
    # If multiple rows share a key, keep the most complete one (most non-empty fields) 
    buckets = {}
    for record in records:
        key = match_key(record)
        if key not in buckets:
            buckets[key] = record
        else:
            existing_fields = sum(1 for v in buckets[key].values() if v)
            new_fields = sum(1 for v in record.values() if v)
            if new_fields > existing_fields:
                buckets[key] = record

    return list(buckets.values())