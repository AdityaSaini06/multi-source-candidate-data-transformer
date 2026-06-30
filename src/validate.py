def validate_canonical(record):
    # Returns a list of warning strings
    warnings = []

    if not isinstance(record.get("emails", []), list):
        warnings.append("emails should be a list")
    if not isinstance(record.get("phones", []), list):
        warnings.append("phones should be a list")
    if not isinstance(record.get("skills", []), list):
        warnings.append("skills should be a list")
    if not isinstance(record.get("location", {}), dict):
        warnings.append("location should be a dict")

    oc = record.get("overall_confidence")
    if oc is not None and not (0.0 <= oc <= 1.0):
        warnings.append(f"overall_confidence out of range: {oc}")

    return warnings


TYPE_CHECKERS = {
    "string": lambda v: isinstance(v, str),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "string[]": lambda v: isinstance(v, list) and all(isinstance(x, str) for x in v),
}


def type_matches(value, expected_type):
    checker = TYPE_CHECKERS.get(expected_type)
    if checker is None:
        return True  # unknown declared type
    return checker(value)


def validate_projection(output, config):
    # Validates a projected output dict against config["fields"].
    # Applies on_missing policy: "null" (default, leave as None), "omit" (drop the key), or "error" (raise ValueError listing problems).
    errors = []
    on_missing = config.get("on_missing", "null")

    for field_spec in config["fields"]:
        path = field_spec["path"]
        value = output.get(path)

        if value is None and field_spec.get("required"):
            if on_missing == "error":
                errors.append(f"required field '{path}' is missing")
            elif on_missing == "omit":
                output.pop(path, None)
                continue
            # "null": leave as None

        expected_type = field_spec.get("type")
        if value is not None and expected_type and not type_matches(value, expected_type):
            errors.append(f"field '{path}' type mismatch: expected {expected_type}, got {type(value).__name__}")

    if errors and on_missing == "error":
        raise ValueError("; ".join(errors))

    return output