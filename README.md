# Multi-Source Candidate Data Transformer

This project is a Python implementation of the Eightfold Engineering Intern
assignment: build a transformer that converts messy candidate inputs into one
clean, explainable candidate profile per person.

The pipeline accepts a structured recruiter CSV and optional unstructured GitHub
profile data, normalizes fields, deduplicates repeated candidates, merges
source values, records provenance, calculates confidence, and writes JSON
output. It also supports runtime output configs so the same canonical profile
can be reshaped for different consumers without changing code.

## Assignment 

The assignment asks for at least one structured source and one unstructured
source.

Implemented sources:

- Structured source: recruiter CSV
- Unstructured source: GitHub profile/repository API, driven by `github_username`

Descoped sources:

- ATS JSON blob
- LinkedIn profile URL
- Resume PDF/DOCX
- Recruiter notes text

These were intentionally left out to keep the solution focused on a
working core pipeline, clear source boundaries, robust edge-case handling, and
the required configurable output layer.

## What The Pipeline Does

For each candidate, the pipeline:

1. Extracts recruiter rows from CSV.
2. Deduplicates repeated CSV rows.
3. Normalizes emails, phones, countries, names, and skills.
4. Optionally fetches GitHub profile and repository data.
5. Merges CSV and GitHub values into a canonical candidate record.
6. Records provenance for populated fields.
7. Computes per-field confidence and overall confidence.
8. Validates the canonical record.
9. Applies an optional projection config.
10. Validates the projected output against the requested config.
11. Writes JSON output.

Pipeline shape:

```text
extract -> normalize -> match/dedupe -> merge -> confidence -> validate -> project -> validate
```

## Project Structure

```text
.
|-- configs/              # Runtime output projection configs
|-- data/                 # Sample recruiter CSV input
|-- output/               # Generated JSON output files
|-- src/                  # Pipeline source code
|-- tests/                # Pytest test suite
|-- requirements.txt      # Python dependencies
`-- run.py                # CLI entry point
```

Important modules:

- `src/extract.py`: CSV and GitHub extraction
- `src/normalize.py`: phone, email, country, date, name, and skill normalization
- `src/match.py`: matching and deduplication keys
- `src/merge.py`: source conflict policy, provenance, confidence, canonical record creation
- `src/project.py`: runtime configurable output projection
- `src/validate.py`: canonical and projected output validation
- `src/pipeline.py`: end-to-end orchestration

## Canonical Output Schema

The internal canonical record uses one fixed shape before projection:

```text
candidate_id          string
full_name             string | null
emails                string[]
phones                string[]              E.164 when parseable
location              { city, region, country }
links                 { linkedin, github, portfolio, other }
headline              string | null
years_experience      number | null
skills                [{ name, confidence, sources }]
experience            [{ company, title, start, end, summary }]
education             []
provenance            [{ field, source, method }]
overall_confidence    number
```

Notes:

- Phone numbers are normalized with `phonenumbers` when possible.
- Countries are normalized to ISO alpha-2 where known.
- Skills are canonicalized through a synonym table.
- Education is returned as an empty list because neither implemented source
  provides reliable education data.
- Experience is a thin CSV-derived entry from `current_company` and `title`;
  start/end dates are left as `null` because the CSV does not provide them.

## Matching And Candidate IDs

Deduplication uses the strongest available key in this order:

1. normalized email
2. normalized phone
3. normalized full name
4. unmatched row identity fallback

`candidate_id` is generated as a stable hash of the selected match key:

```text
cand_<12-char-sha256-prefix>
```

This avoids positional IDs like `cand_0001`, which would change if CSV row
order changed.

## Merge And Conflict Policy

CSV is treated as the higher-trust source for recruiter-owned fields. GitHub is
used as optional enrichment.

Single-value fields use `pick_winner()`:

```text
Only CSV value present       -> choose CSV
Only GitHub value present    -> choose GitHub
Both present and agree       -> choose CSV, mark agreement
Both present and conflict    -> choose CSV, mark source_priority_conflict
Neither present              -> null, no provenance
```

CSV-only fields:

- emails
- phones
- location
- links
- years_experience
- experience

GitHub-enriched fields:

- headline from GitHub bio
- skills from GitHub repository languages

The pipeline never invents missing values. Unknown, malformed, or absent values
become `null`, empty lists, or warnings depending on the field.

## Confidence Policy

Current source trust weights:

```text
CSV trust     = 0.9
GitHub trust  = 0.6
Agreement     = CSV trust + 0.1, capped at 1.0
Conflict      = CSV trust - 0.1
Missing value = 0.0
```

Examples:

```text
CSV-only field        -> 0.9
GitHub-only field     -> 0.6
CSV/GitHub agreement  -> 1.0
CSV/GitHub conflict   -> 0.8
```

Skill confidence is different: GitHub skills are derived from repository
language frequency. If Python appears in half of a candidate's eligible repos,
the Python skill confidence is `0.5`.

`overall_confidence` is the average of populated field confidences. Empty fields
with confidence `0.0` are not included in the average, so missing education does
not unfairly reduce the score.

## Provenance

Every populated field records where it came from and how it was selected.

Example provenance entry:

```json
{
  "field": "full_name",
  "source": "csv",
  "method": "only_source"
}
```

Common methods:

- `only_source`: only one source had a value
- `agreement`: CSV and GitHub agreed after normalization
- `source_priority_conflict`: both sources had values, but CSV won
- `union_merge`: list-like values such as skills were merged

When a config sets `"include_confidence": true`, projected provenance entries
also include each field's confidence.

## Configurable Output

The assignment requires a runtime config that can reshape output without code
changes. This project supports that through JSON files in `configs/`.

Each field spec can include:

- `path`: output field name
- `from`: source path in the canonical record
- `type`: expected output type
- `required`: whether the value must exist
- `normalize`: optional per-field normalizer

Example:

```json
{
  "path": "primary_email",
  "from": "emails[0]",
  "type": "string",
  "required": true
}
```

Supported source path patterns:

- `full_name`
- `location.city`
- `emails[0]`
- `skills[].name`

Supported validation types:

- `string`
- `number`
- `boolean`
- `string[]`

Unknown validation types are currently allowed rather than fatal. This keeps the
config layer flexible, but it also means types such as `object[]` are not
strictly enforced yet.

Supported projection normalizers:

- `E164`: normalize phone numbers
- `canonical`: normalize skill names
- `ISO8601`: normalize dates

Unknown normalizers are ignored and leave the value unchanged. This is
intentional fail-soft behavior for user-provided configs.

## Missing Field Behavior

Configs control required-but-missing fields with `on_missing`:

```text
null   -> keep the field with value null
omit   -> remove the field from output
error  -> fail the run with a validation error
```

Use `error` for strict import contracts. Use `null` or `omit` for UI/API
payloads that can tolerate partial data.

## Available Config Files

### `configs/example_config.json`

Compact payload with contact and skill fields:

- `full_name`
- `primary_email`
- `phone`
- `skills`
- confidence and provenance enabled

Run:

```bash
python run.py --csv data/candidates.csv --config configs/example_config.json --out output/example_config.json
```

### `configs/clean_ui_payload.json`

Small UI-friendly payload:

- `full_name`
- `current_city`
- `country_code`
- `top_skills`
- confidence disabled

Run:

```bash
python run.py --csv data/candidates.csv --config configs/clean_ui_payload.json --out output/clean_ui_payload.json
```

Note: this config currently uses `"normalize": "alpha2"`. The project does not
define an `alpha2` projection normalizer, so that key is ignored. Country values
are already normalized earlier in the canonical pipeline.

### `configs/full_audit_record.json`

Audit-oriented payload:

- `candidate_id`
- `full_name`
- `contact_info.primary_email`
- `contact_info.primary_phone`
- `history.education`
- `history.work`
- confidence and provenance enabled

Run:

```bash
python run.py --csv data/candidates.csv --config configs/full_audit_record.json --out output/full_audit_record.json
```

### `configs/strict_importer.json`

Strict importer payload:

- `id`
- `name`
- `github_link`
- `experience_years`
- `"on_missing": "error"`

Run:

```bash
python run.py --csv data/candidates.csv --config configs/strict_importer.json --out output/strict_importer.json
```

This config is expected to fail with the current sample CSV if any row is
missing `years_experience`. That is correct behavior because the config declares
`experience_years` as required and asks the validator to error on missing
values.

## Setup

Create and activate a virtual environment if desired, then install
dependencies:

```bash
python -m pip install -r requirements.txt
```

Dependencies:

- `phonenumbers`
- `requests`
- `pytest`

## Run

Default canonical output:

```bash
python run.py --csv data/candidates.csv --out output/default_result.json
```

Config-projected output:

```bash
python run.py --csv data/candidates.csv --config configs/example_config.json --out output/example_config.json
python run.py --csv data/candidates.csv --config configs/clean_ui_payload.json --out output/clean_ui_payload.json
python run.py --csv data/candidates.csv --config configs/full_audit_record.json --out output/full_audit_record.json
```

Strict importer check:

```bash
python run.py --csv data/candidates.csv --config configs/strict_importer.json --out output/strict_importer.json
```

Expected behavior for the strict importer on partial sample data:

```text
Error: validation failed - required field 'experience_years' is missing
```

## Output File Naming

For config runs, output files are named after their input config:

```text
configs/example_config.json      -> output/example_config.json
configs/clean_ui_payload.json    -> output/clean_ui_payload.json
configs/full_audit_record.json   -> output/full_audit_record.json
configs/strict_importer.json     -> output/strict_importer.json
```

## Tests

Run all tests:

```bash
python -m pytest -q tests
```

The current tests cover:

- unmatched empty records do not collapse into one candidate
- empty strings are treated as missing values
- skills must include explicit confidence
- unknown config normalizers fail softly
- invalid short phone numbers are not invented into valid-looking numbers
- empty CSV records still produce a valid mostly-null candidate
- GitHub skill derivation excludes forks, archived repos, and null languages
- candidate IDs are stable and differ for different people

## Robustness And Edge Cases

Handled intentionally:

- Missing CSV file returns a clear error.
- Invalid config JSON returns a clear error.
- GitHub failures become warnings, not fatal errors.
- Missing GitHub usernames skip GitHub enrichment.
- Extra malformed CSV columns are ignored safely.
- Duplicate CSV candidates are deduped by normalized email, phone, or name.
- Unknown normalizers do not crash config projection.
- Missing required fields can be handled as `null`, omitted, or hard errors.
- Unparseable `years_experience` becomes `null`.
- Invalid phone numbers are preserved as raw values rather than fabricated.

Known limitations:

- Only recruiter CSV and GitHub are implemented.
- `object[]` config validation is not strictly enforced.
- Nested output paths such as `contact_info.primary_email` are emitted as flat
  keys, not expanded nested objects.
- GitHub enrichment depends on network/API availability.
- CSV job title is not treated as a skill source because it is weak evidence.
- Experience history is limited to one current-company/title entry.
- Education is not inferred from unsupported sources.

## Demo Checklist

For a short demo , a simple flow is:

1. Run the default pipeline.
2. Open `output/default_result.json`.
3. Run `example_config.json` or `clean_ui_payload.json`.
4. Show that the output shape changed without code changes.
5. Run `strict_importer.json` and explain why it correctly fails on missing
   required experience data.
6. Run the test suite.

Commands:

```bash
python run.py --csv data/candidates.csv --out output/default_result.json
python run.py --csv data/candidates.csv --config configs/example_config.json --out output/example_config.json
python run.py --csv data/candidates.csv --config configs/strict_importer.json --out output/strict_importer.json
python -m pytest -q tests
```

## Design Tradeoffs

The solution favors a small, explainable pipeline over a larger framework-style
architecture. A production system might introduce dataclasses, a plugin system
for sources, async GitHub calls, stronger schema validation, and richer resume
parsing. For this assignment, the priority is a correct working core with clear
separation between canonical records and projected output.

Key choices:

- Use dictionaries for speed of implementation and easy JSON serialization.
- Keep one file per concern instead of deeply nested packages.
- Treat GitHub as enrichment, not a hard dependency.
- Keep confidence simple and explainable.
- Fail softly for optional source failures, but fail loudly when a strict config
  asks for required fields.
