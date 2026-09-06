#!/usr/bin/env python3
"""Validate structural invariants of b2b-contact-enrichment output."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


STATUSES = {"complete", "partial", "not_found", "ambiguous", "error"}
EMAIL_STATUSES = {"verified", "catch_all", "unverified", "unavailable"}
PHONE_TYPES = {"direct_dial", "business_mobile", "company_main", "unavailable"}
EMPLOYMENT_STATUSES = {"current_verified", "current_reported", "unknown"}
PERSONAL_EMAIL_DOMAINS = {
    "gmail.com", "googlemail.com", "yahoo.com", "outlook.com", "hotmail.com",
    "live.com", "icloud.com", "aol.com", "gmx.de", "web.de",
}


def fail(errors: list[str], path: str, message: str) -> None:
    errors.append(f"{path}: {message}")


def nullable_string(value: Any) -> bool:
    return value is None or isinstance(value, str)


def validate_record(record: Any, index: int, errors: list[str]) -> None:
    base = f"records[{index}]"
    if not isinstance(record, dict):
        fail(errors, base, "must be an object")
        return

    enrichment = record.get("contact_enrichment")
    if not isinstance(enrichment, dict):
        fail(errors, base + ".contact_enrichment", "must be an object")
        return

    status = enrichment.get("status")
    if status not in STATUSES:
        fail(errors, base + ".contact_enrichment.status", f"must be one of {sorted(STATUSES)}")

    company = enrichment.get("company_match")
    if not isinstance(company, dict):
        fail(errors, base + ".contact_enrichment.company_match", "must be an object")
    else:
        for key in ("canonical_name", "domain", "provider_company_id"):
            if key not in company or not nullable_string(company[key]):
                fail(errors, f"{base}.contact_enrichment.company_match.{key}", "must be string or null")
        confidence = company.get("confidence")
        if not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0 <= confidence <= 1:
            fail(errors, base + ".contact_enrichment.company_match.confidence", "must be a number from 0 to 1")

    person = enrichment.get("person")
    if person is not None and not isinstance(person, dict):
        fail(errors, base + ".contact_enrichment.person", "must be an object or null")
    elif isinstance(person, dict):
        for key in ("full_name", "job_title", "current_employer"):
            if not isinstance(person.get(key), str) or not person[key].strip():
                fail(errors, f"{base}.contact_enrichment.person.{key}", "must be a non-empty string")
        for key in ("first_name", "last_name", "department", "seniority", "location", "professional_profile_url", "provider_person_id"):
            if key not in person or not nullable_string(person[key]):
                fail(errors, f"{base}.contact_enrichment.person.{key}", "must be string or null")

        email = person.get("work_email")
        if not isinstance(email, dict):
            fail(errors, base + ".contact_enrichment.person.work_email", "must be an object")
        else:
            email_value = email.get("value")
            email_status = email.get("status")
            if not nullable_string(email_value):
                fail(errors, base + ".contact_enrichment.person.work_email.value", "must be string or null")
            if email_status not in EMAIL_STATUSES:
                fail(errors, base + ".contact_enrichment.person.work_email.status", f"must be one of {sorted(EMAIL_STATUSES)}")
            if isinstance(email_value, str) and "@" in email_value:
                domain = email_value.rsplit("@", 1)[1].lower()
                if domain in PERSONAL_EMAIL_DOMAINS:
                    fail(errors, base + ".contact_enrichment.person.work_email.value", "must not use a personal webmail domain")
            if email_value is None and email_status != "unavailable":
                fail(errors, base + ".contact_enrichment.person.work_email.status", "must be unavailable when value is null")

        phone = person.get("business_phone")
        if not isinstance(phone, dict):
            fail(errors, base + ".contact_enrichment.person.business_phone", "must be an object")
        else:
            phone_value = phone.get("value")
            phone_type = phone.get("type")
            if not nullable_string(phone_value):
                fail(errors, base + ".contact_enrichment.person.business_phone.value", "must be string or null")
            if phone_type not in PHONE_TYPES:
                fail(errors, base + ".contact_enrichment.person.business_phone.type", f"must be one of {sorted(PHONE_TYPES)}")
            if phone_value is None and phone_type != "unavailable":
                fail(errors, base + ".contact_enrichment.person.business_phone.type", "must be unavailable when value is null")

    employment = enrichment.get("employment_evidence")
    if not isinstance(employment, dict):
        fail(errors, base + ".contact_enrichment.employment_evidence", "must be an object")
        employment_status = None
    else:
        employment_status = employment.get("status")
        if employment_status not in EMPLOYMENT_STATUSES:
            fail(errors, base + ".contact_enrichment.employment_evidence.status", f"must be one of {sorted(EMPLOYMENT_STATUSES)}")
        if "last_verified_at" not in employment or not nullable_string(employment["last_verified_at"]):
            fail(errors, base + ".contact_enrichment.employment_evidence.last_verified_at", "must be string or null")

    sources = enrichment.get("sources")
    if not isinstance(sources, list):
        fail(errors, base + ".contact_enrichment.sources", "must be an array")
    else:
        for source_index, source in enumerate(sources):
            source_path = f"{base}.contact_enrichment.sources[{source_index}]"
            if not isinstance(source, dict):
                fail(errors, source_path, "must be an object")
                continue
            if not isinstance(source.get("provider"), str) or not source["provider"].strip():
                fail(errors, source_path + ".provider", "must be a non-empty string")
            if not nullable_string(source.get("record_id_or_url")):
                fail(errors, source_path + ".record_id_or_url", "must be string or null")
            if not isinstance(source.get("retrieved_at"), str) or not source["retrieved_at"].strip():
                fail(errors, source_path + ".retrieved_at", "must be a non-empty RFC 3339 timestamp string")

    confidence = enrichment.get("confidence")
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0 <= confidence <= 1:
        fail(errors, base + ".contact_enrichment.confidence", "must be a number from 0 to 1")

    for key in ("selection_reason", "notes"):
        if key not in enrichment or not nullable_string(enrichment[key]):
            fail(errors, f"{base}.contact_enrichment.{key}", "must be string or null")

    if status in {"complete", "partial"} and person is None:
        fail(errors, base + ".contact_enrichment.person", f"must not be null for {status}")
    if status in {"complete", "partial"} and employment_status == "unknown":
        fail(errors, base + ".contact_enrichment.employment_evidence.status", f"must support current employment for {status}")
    if status == "complete" and isinstance(person, dict):
        email_value = (person.get("work_email") or {}).get("value")
        phone_value = (person.get("business_phone") or {}).get("value")
        profile = person.get("professional_profile_url")
        if not any(isinstance(value, str) and value.strip() for value in (email_value, phone_value, profile)):
            fail(errors, base + ".contact_enrichment.person", "complete requires at least one professional reachability field")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_file", type=Path)
    args = parser.parse_args()

    try:
        data = json.loads(args.json_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"ERROR: could not read valid JSON: {exc}", file=sys.stderr)
        return 2

    if isinstance(data, list):
        records = data
    elif isinstance(data, dict) and isinstance(data.get("companies"), list):
        records = data["companies"]
    else:
        print("ERROR: top level must be an array or an object with a companies array", file=sys.stderr)
        return 2

    errors: list[str] = []
    for index, record in enumerate(records):
        validate_record(record, index, errors)

    if errors:
        for error in errors:
            print("ERROR:", error, file=sys.stderr)
        print(f"Validation failed with {len(errors)} error(s).", file=sys.stderr)
        return 1

    counts = {status: 0 for status in sorted(STATUSES)}
    for record in records:
        counts[record["contact_enrichment"]["status"]] += 1
    print(json.dumps({"valid": True, "records": len(records), "status_counts": counts}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
