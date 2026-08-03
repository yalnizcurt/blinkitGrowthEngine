#!/usr/bin/env python3
import sys
import re
import json
from pathlib import Path

# PII regex patterns
EMAIL_PATTERN = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
PHONE_PATTERN = re.compile(r'\+?\d[\d\s-]{8,}\d')
HANDLE_PATTERN = re.compile(r'@[A-Za-z0-9_]+')
NUMERIC_ID_PATTERN = re.compile(r'\b\d{10,}\b')

def scan_text(text):
    findings = []
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        line_num = idx + 1
        # Email check
        for m in EMAIL_PATTERN.finditer(line):
            findings.append({"type": "email", "match": m.group(0), "line": line_num})
        # Phone check
        for m in PHONE_PATTERN.finditer(line):
            val = m.group(0)
            # Filter out simple dates like YYYY-MM-DD
            if re.search(r'\d{4}-\d{2}-\d{2}', val):
                continue
            # Filter out simple short dashes
            if "-" in val and len(val.replace("-", "").strip()) < 8:
                continue
            if "%" in line:
                continue
            findings.append({"type": "phone", "match": val, "line": line_num})
        # Handle check
        for m in HANDLE_PATTERN.finditer(line):
            findings.append({"type": "handle", "match": m.group(0), "line": line_num})
        # Numeric ID check
        for m in NUMERIC_ID_PATTERN.finditer(line):
            findings.append({"type": "long_numeric_id", "match": m.group(0), "line": line_num})
    return findings

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/check_pii.py <file_path_or_text>")
        sys.exit(1)

    target_path = Path(sys.argv[1])
    if not target_path.exists():
        print(f"Error: File not found {target_path}")
        sys.exit(1)

    text = target_path.read_text(encoding="utf-8")
    findings = scan_text(text)

    # Write blockers.json
    blockers_path = Path("data/weekly/blockers.json")
    blockers_path.parent.mkdir(parents=True, exist_ok=True)

    if findings:
        blockers_data = {
            "passed": False,
            "blockers_count": len(findings),
            "findings": findings
        }
        blockers_path.write_text(json.dumps(blockers_data, indent=2), encoding="utf-8")
        print("❌ PII gate FAILED! Blocked publishing.")
        for f in findings:
            print(f"  Line {f['line']}: Found {f['type']} -> '{f['match']}'")
        sys.exit(1)
    else:
        blockers_data = {
            "passed": True,
            "blockers_count": 0,
            "findings": []
        }
        blockers_path.write_text(json.dumps(blockers_data, indent=2), encoding="utf-8")
        print("✅ PII gate passed. No customer identifiers detected.")
        sys.exit(0)

if __name__ == "__main__":
    main()
