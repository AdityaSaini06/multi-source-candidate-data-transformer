"""
Usage:
    python run.py --csv data/candidates.csv --out output/default_result.json
    python run.py --csv data/candidates.csv --config configs/example_config.json --out output/custom_result.json
"""

import argparse
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.pipeline import run_pipeline


def main():
    parser = argparse.ArgumentParser(description="Multi-Source Candidate Data Transformer")
    parser.add_argument("--csv", required=True, help="Path to recruiter CSV export")
    parser.add_argument("--config", required=False, help="Path to output config JSON (optional)")
    parser.add_argument("--out", required=True, help="Path to write output JSON")
    args = parser.parse_args()

    if not os.path.exists(args.csv):
        print(f"Error: CSV file not found at '{args.csv}'", file=sys.stderr)
        sys.exit(1)

    config = None
    if args.config:
        if not os.path.exists(args.config):
            print(f"Error: config file not found at '{args.config}'", file=sys.stderr)
            sys.exit(1)
        try:
            with open(args.config) as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: config file is not valid JSON: {e}", file=sys.stderr)
            sys.exit(1)

    try:
        result = run_pipeline(args.csv, config=config)
    except ValueError as e:
        print(f"Error: validation failed - {e}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(result["results"], f, indent=2)

    print(f"Wrote {len(result['results'])} candidate profile(s) to {args.out}")
    if result["warnings"]:
        print(f"\n{len(result['warnings'])} warning(s) during run:")
        for w in result["warnings"]:
            print(f"  - {w}")


if __name__ == "__main__":
    main()