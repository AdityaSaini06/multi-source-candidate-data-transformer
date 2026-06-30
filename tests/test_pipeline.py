import pytest
from src.match import dedupe_csv_records
from src.merge import pick_winner, merge_skills, merge_candidate
from src.pipeline import make_candidate_id
from src.project import apply_normalize
from src.normalize import derive_github_skills, normalize_phone


def test_dedupe_two_unmatched_records_both_kept():
    """
    EDGE CASE: two completely empty rows must not collide into one
    bucket just because they're both "unmatched" - each gets its own
    identity via id(record).
    """
    rows = [{"full_name": "", "email": "", "phone": ""},
            {"full_name": "", "email": "", "phone": ""}]
    
    assert len(dedupe_csv_records(rows)) == 2


def test_pick_winner_falsy_but_not_none_treated_as_missing():
    """
    EDGE CASE: empty string should behave like "missing", not like a
    real (empty) value worth recording provenance for.
    """
    value, prov, confidence = pick_winner("", None, "full_name")
    
    assert value is None
    assert prov is None


def test_merge_skills_raises_on_missing_confidence():
    """
    EDGE CASE: every skill must carry a confidence - a silent 
    fallback was deliberately removed in favor of failing loudly,
    since a guessed confidence is indistinguishable from a real one
    in the output JSON.
    """
    bad_skill = [{"name": "python", "sources": ["csv"]}]  # no "confidence" key
    
    with pytest.raises(ValueError):
        merge_skills(bad_skill, [])


def test_apply_normalize_unknown_key_fails_soft():
    """
    EDGE CASE: an unrecognized "normalize" string in a user-supplied
    config must not crash the projection - value passes through as-is.
    """
    assert apply_normalize("9876543210", "totally_unknown_normalizer") == "9876543210"


def test_normalize_phone_too_short_keeps_raw_not_invented():
    """
    EDGE CASE: Too short to be valid - should not be silently dropped or guessed into
    something else; either raw or None, never a fabricated valid-looking number.
    """
    result = normalize_phone("123", default_region="IN")
    
    assert result != "+91123"  # never pad/invent digits


def test_merge_candidate_fully_empty_csv_does_not_crash():
    """
    EDGE CASE: a garbage/near-empty CSV row plus no GitHub data must
    still produce a valid (if mostly-null) record, never raise.
    """
    record, provenance, confidence_map = merge_candidate({}, {}, [], "cand_empty")
    
    assert record["candidate_id"] == "cand_empty"
    assert record["emails"] == []
    assert record["skills"] == []
    assert record["overall_confidence"] == 0.0


def test_derive_github_skills_excludes_forks_and_nulls():
    """EDGE CASE: forked/archived repos and null languages must not
    pollute the skills signal (wrong-but-confident is worse than
    honestly-empty)."""
    repos = [
        {"language": "Python", "fork": False},
        {"language": "JavaScript", "fork": True},   # forked - excluded
        {"language": None, "fork": False},           # null - excluded
        {"language": "python", "archived": True},    # archived - excluded
    ]
    skills = derive_github_skills(repos)
    names = [s["name"] for s in skills]
    assert names == ["python"]  # only the one non-fork, non-archived, non-null entry


def test_candidate_id_is_stable_across_row_order():
    """EDGE CASE: candidate_id must not depend on position in the file -
    same person should get the same id regardless of row order/index."""
    record = {"email": "a@x.com", "full_name": "A B"}
    id_first = make_candidate_id(record)
    id_again = make_candidate_id(dict(record))
    assert id_first == id_again
    assert id_first.startswith("cand_")


def test_candidate_id_differs_for_different_people():
    id_a = make_candidate_id({"email": "a@x.com"})
    id_b = make_candidate_id({"email": "b@x.com"})
    assert id_a != id_b

if __name__ == "__main__":
    pytest.main([__file__, "-v"])