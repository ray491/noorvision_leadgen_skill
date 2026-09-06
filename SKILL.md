---
name: b2b-contact-enrichment
description: Enrich JSON company lead lists with one relevant, currently employed B2B contact per company using connected people-data providers such as Apollo or FullEnrich. Use for account-to-contact matching and professional contact verification; do not use for consumer, private-person, or bulk personal-data discovery.
---

# B2B Contact Enrichment

Add one best-fit current employee to every company record while preserving the input JSON structure and every original field and value. Append only `contact_enrichment`, unless the user explicitly requests a different schema.

Read [references/contact-schema.md](references/contact-schema.md) before enriching records. Run `scripts/validate_enriched_json.py` on a saved result when local file tools are available.

## Provider routing

Use connected, purpose-built B2B people/company data tools. Prefer a provider that supports both company resolution and current-employment people search.

- Use Apollo when available for company resolution, employee discovery, and professional contact fields.
- Use FullEnrich when available for person/contact enrichment or cross-provider work-email verification.
- Other connected B2B databases are acceptable when they return equivalent provenance and employment evidence.
- If no suitable provider is connected, stop before enrichment and ask the user to connect one. Do not replace a missing B2B database with guessed contacts or broad web scraping.

Never claim that a provider was queried unless its tool actually returned the data. Respect provider limits, permissions, and the user's requested batch scope. Do not install a provider, spend credits, or expand the batch without authorization.

## Workflow

### 1. Inspect and preserve the input

Accept either a top-level JSON array of company objects or an object whose `companies` field is that array. Reject malformed JSON and identify records missing a usable company name.

Copy each original object unchanged, including key names, values, language, and ordering where the serializer permits. Add `contact_enrichment` last. Do not rewrite evidence, estimates, or outreach copy, and do not replace placeholders such as `[FirstName]` unless requested.

Infer the desired buyer function from the record. Give explicit user criteria priority. Otherwise use signals in fields such as `key_rationale`, job evidence, technology evidence, warehouse evidence, and the email draft. For the supplied SAP EWM-style records, prioritize current leaders or owners in warehouse logistics, supply chain, intralogistics, SAP/EWM, enterprise applications, or logistics IT.

### 2. Resolve the company first

Search the company database before searching people. Match on normalized company name plus available website/domain, country, city, subsidiary/parent context, and industry.

Do not silently match a similarly named company. Treat the match as ambiguous when material identifiers conflict or two candidates remain plausible. Store the canonical company name, domain, provider ID when returned, and match confidence.

### 3. Find eligible current employees

Search only within the resolved company. Build a compact title set from the buying signal and search close synonyms in the company's language when supported. Prefer decision-makers who plausibly own the identified initiative, but select a hands-on manager or subject-matter owner when that is a closer functional match than a distant executive.

A person is eligible only when the B2B record reports the resolved company as the person's current employer. A past employee, advisor, recruiter, agency contact, generic inbox, or unnamed profile is not eligible.

Rank eligible people using this order:

1. Direct function and initiative ownership.
2. Current-employer confidence and record freshness.
3. Appropriate seniority: head/director/VP/C-level for strategic buying; manager/lead/process owner for operational or technical buying.
4. Geography or business-unit fit.
5. Availability of provider-returned professional contact channels.

Select one primary contact. Do not return a less relevant person merely because more contact fields are available.

### 4. Enrich without guessing

Request the selected person's professional details from the connected provider. Keep only business-context fields needed by the schema.

- Never invent or pattern-generate an email address, phone number, title, URL, or provider ID.
- Label provider verification states exactly; `catch_all` and `unverified` are not `verified`.
- Prefer a work email on the resolved company domain. Exclude personal webmail addresses.
- Include a phone number only when the provider identifies it as a business or direct-dial number. Exclude personal/home numbers and uncertain mobile numbers.
- Use a public professional profile URL only when returned by the provider and tied to the matched person.
- Minimize data: do not add home address, personal email, personal social profiles, age, family data, or sensitive traits.

If a second provider is available, use it only to resolve a conflict, verify a high-value field, or complete a requested field. Record each provider actually used in `sources`.

### 5. Set status conservatively

Use `complete` only when identity, current employment, role, and at least one professional reachability field are present. Use `partial` when a relevant current employee is verified but no professional email, business phone, or professional profile URL is available. Use `not_found` when no eligible employee is returned, `ambiguous` when company or person identity cannot be resolved safely, and `error` only for a provider/tool failure after limited retry.

For non-complete results, keep the record and populate the status, company match evidence when known, sources, and a concise `notes` value. Never drop unresolved companies.

### 6. Validate and return

Return the same top-level JSON shape as the input. Maintain one output record per input record in the same order. Ensure the output is parseable JSON and conforms to the reference schema.

When processing a file, save the enriched result as a new file by default so the original remains intact. Report counts for `complete`, `partial`, `not_found`, `ambiguous`, and `error` outside the JSON unless the user requested JSON-only output.

Treat contact data as business-purpose data. Follow applicable provider terms, privacy requirements, suppression lists, and outreach rules; successful enrichment is not consent to contact.
