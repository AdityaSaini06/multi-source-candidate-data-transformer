# The projector never mutates the canonical record
import re
from .normalize import normalize_phone, normalize_skill_name, normalize_date

NORMALIZERS = {
    "E164": normalize_phone,
    "canonical": normalize_skill_name,
    "ISO8601": normalize_date,
}


def get_by_path(record, path):
    """
    Supports:
      'full_name'        -> plain field
      'location.city'    -> nested dict field
      'emails[0]'        -> array index
      'skills[].name'    -> array of objects -> array of one field
    """
    if "[]." in path:
        array_field, sub_field = path.split("[].", 1)
        items = record.get(array_field, []) or []
        return [item.get(sub_field) for item in items if item.get(sub_field) is not None]

    match = re.match(r"^(\w+)\[(\d+)\]$", path)
    if match:
        field, idx = match.group(1), int(match.group(2))
        arr = record.get(field, []) or []
        return arr[idx] if idx < len(arr) else None

    val = record
    for part in path.split("."):
        if not isinstance(val, dict):
            return None
        val = val.get(part)
    return val


def apply_normalize(value, normalize_key):
    if not normalize_key or value is None:
        return value
    fn = NORMALIZERS.get(normalize_key)
    if not fn:
        return value  # unknown normalize key 
    if isinstance(value, list):
        return [fn(v) for v in value if v is not None]
    return fn(value)


def project_default(canonical_record, provenance, confidence_map):
    output = dict(canonical_record)  # shallow copy, never mutate original
    output["provenance"] = provenance
    return output


def project(canonical_record, config, provenance, confidence_map):
    output = {}

    for field_spec in config["fields"]:
        out_path = field_spec["path"]
        source_path = field_spec.get("from", out_path)
        value = get_by_path(canonical_record, source_path)
        value = apply_normalize(value, field_spec.get("normalize"))
        output[out_path] = value

    if config.get("include_confidence", False):
        output["overall_confidence"] = canonical_record.get("overall_confidence")
        output["provenance"] = [
            {**p, "confidence": confidence_map.get(p["field"])} for p in provenance
        ]
    else:
        output["provenance"] = provenance

    return output