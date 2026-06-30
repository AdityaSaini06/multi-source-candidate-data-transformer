import csv
import requests

GITHUB_API = "https://api.github.com"
REQUEST_TIMEOUT = 5 

def extract_csv(path):
    # Returns: {"status": "ok"|"missing"|"error", "records": [...]}
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            records = []
            for row in reader:
                # normalize header whitespace/casing once at load time
                clean_row = {}
                for k, v in row.items():
                    if k is None:
                        continue
                    clean_row[k.strip().lower()] = v.strip() if isinstance(v, str) and v else None
                records.append(clean_row)
            return {"status": "ok", "records": records}
    except FileNotFoundError:
        return {"status": "missing", "records": []}
    except Exception as e:
        return {"status": "error", "records": [], "error": str(e)}


def extract_github(username):
    if not username:
        return {"status": "missing", "profile": {}, "repos": []}

    headers = {"Accept": "application/vnd.github+json"}

    try:
        profile_resp = requests.get(
            f"{GITHUB_API}/users/{username}", headers=headers, timeout=REQUEST_TIMEOUT
        )
        if profile_resp.status_code == 404:
            return {"status": "missing", "profile": {}, "repos": []}
        if profile_resp.status_code != 200:
            return {
                "status": "error",
                "profile": {},
                "repos": [],
                "error": f"profile fetch returned {profile_resp.status_code}",
            }
        profile = profile_resp.json()

        repos_resp = requests.get(
            f"{GITHUB_API}/users/{username}/repos",
            headers=headers,
            params={"per_page": 100},
            timeout=REQUEST_TIMEOUT,
        )
        repos = repos_resp.json() if repos_resp.status_code == 200 else []

        return {"status": "ok", "profile": profile, "repos": repos}

    except requests.exceptions.RequestException as e:
        # network error, timeout, DNS failure
        return {"status": "error", "profile": {}, "repos": [], "error": str(e)}
