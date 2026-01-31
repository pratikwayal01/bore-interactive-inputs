"""
Reads /tmp/bore-interactive-results.json (written by main.py)
and appends every key=value line to $GITHUB_OUTPUT so the
composite action's outputs bubble up to the caller workflow.
"""
import json
import os
import sys

RESULTS_FILE = "/tmp/bore-interactive-results.json"


def main():
    github_output = os.environ.get("GITHUB_OUTPUT")
    if not github_output:
        print("ERROR: GITHUB_OUTPUT env var is not set", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(RESULTS_FILE):
        print("ERROR: Results file not found – form was not submitted", file=sys.stderr)
        sys.exit(1)

    with open(RESULTS_FILE) as f:
        data = json.load(f)

    print("──────────────────────────────────────")
    print(f"Setting outputs from {RESULTS_FILE}")
    print("──────────────────────────────────────")

    with open(github_output, "a") as out:
        for key, value in data.items():
            out.write(f"{key}={value}\n")
            print(f"  ✓ {key}={value}")

    print("──────────────────────────────────────")
    print("✓ All outputs set successfully")


if __name__ == "__main__":
    main()
