# Contact enrichment schema

Append this object to every company record under `contact_enrichment`. Use JSON `null` for unavailable scalar fields and `[]` for no sources. Do not omit keys from `company_match`; `person` may be `null` when no person is safely identified.

```json
{
  "contact_enrichment": {
    "status": "complete | partial | not_found | ambiguous | error",
    "company_match": {
      "canonical_name": "string or null",
      "domain": "string or null",
      "provider_company_id": "string or null",
      "confidence": 0.0
    },
    "person": {
      "full_name": "string",
      "first_name": "string or null",
      "last_name": "string or null",
      "job_title": "string",
      "department": "string or null",
      "seniority": "string or null",
      "current_employer": "string",
      "location": "string or null",
      "professional_profile_url": "string or null",
      "work_email": {
        "value": "string or null",
        "status": "verified | catch_all | unverified | unavailable"
      },
      "business_phone": {
        "value": "string or null",
        "type": "direct_dial | business_mobile | company_main | unavailable"
      },
      "provider_person_id": "string or null"
    },
    "selection_reason": "string or null",
    "employment_evidence": {
      "status": "current_verified | current_reported | unknown",
      "last_verified_at": "RFC 3339 timestamp or null"
    },
    "sources": [
      {
        "provider": "string",
        "record_id_or_url": "string or null",
        "retrieved_at": "RFC 3339 timestamp"
      }
    ],
    "confidence": 0.0,
    "notes": "string or null"
  }
}
```

## Field rules

- `confidence` fields are numbers from `0` through `1`; they express matching confidence, not provider guarantees.
- `provider_company_id` and `provider_person_id` must be values returned by a provider, never synthesized.
- `complete` requires a non-null `person`, `employment_evidence.status` other than `unknown`, and at least one of: professional profile URL, non-null work email, or non-null business phone.
- `partial` requires a non-null `person` whose current employment is supported, but allows all reachability values to be unavailable.
- `not_found`, `ambiguous`, and `error` normally use `person: null`.
- A work email on a personal webmail domain is invalid even when a provider returns it.
- `selection_reason` should explain role fit in one sentence, not restate private data.
- `sources` identifies only providers queried for that record. It should not include invented citations or a provider that was merely available.

## Example appended object

```json
{
  "contact_enrichment": {
    "status": "complete",
    "company_match": {
      "canonical_name": "Example GmbH",
      "domain": "example.de",
      "provider_company_id": "provider-company-123",
      "confidence": 0.98
    },
    "person": {
      "full_name": "Erika Mustermann",
      "first_name": "Erika",
      "last_name": "Mustermann",
      "job_title": "Head of Warehouse Logistics",
      "department": "Supply Chain",
      "seniority": "Head",
      "current_employer": "Example GmbH",
      "location": "Germany",
      "professional_profile_url": "https://professional.example/erika-mustermann",
      "work_email": {
        "value": "erika.mustermann@example.de",
        "status": "verified"
      },
      "business_phone": {
        "value": null,
        "type": "unavailable"
      },
      "provider_person_id": "provider-person-456"
    },
    "selection_reason": "Owns warehouse logistics and closely matches the EWM initiative in the account record.",
    "employment_evidence": {
      "status": "current_verified",
      "last_verified_at": "2026-09-06T08:00:00Z"
    },
    "sources": [
      {
        "provider": "Example B2B Provider",
        "record_id_or_url": "provider-person-456",
        "retrieved_at": "2026-09-06T08:00:00Z"
      }
    ],
    "confidence": 0.94,
    "notes": null
  }
}
```

The example values are fictional and demonstrate shape only.
