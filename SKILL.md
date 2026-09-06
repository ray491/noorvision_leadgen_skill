---
name: b2b-contact-enrichment
description: Enrich JSON company lead lists with a complete, currently employed B2B contact for every company using connected people-data providers such as Apollo or FullEnrich, then return the full JSON inline in chat. Use for account-to-contact matching and professional contact verification; do not use for consumer, private-person, or bulk personal-data discovery.
---

# B2B Contact Enrichment

Add one complete, best-fit current employee to every company record while preserving the input JSON structure and every original field and value. Append only `contact_enrichment`, unless the user explicitly requests a different schema.

Completion is all-or-nothing: every input company must have a verified current employee with a full name, current role, current employer, and verified work email. Do not return an enriched JSON result while any company is missing one of these fields. Never satisfy this requirement by guessing or synthesizing data.

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

If the first provider does not produce a complete contact, broaden relevant title and seniority variants, check the correct subsidiary or parent-company relationship, and query a second connected B2B provider when available. Record each provider actually used in `sources`. Stop before repeating equivalent searches that would only consume more credits.

### 5. Enforce complete coverage

Every output record must have `status: "complete"`. A complete contact requires verified identity, supported current employment at the resolved company, a current job title, and a provider-verified work email on a business domain. A professional profile or business phone may supplement the email but cannot replace it.

If any company remains unresolved after the available provider and title-search options are exhausted, do not output a partial JSON array and do not drop the company. Instead, state in chat which companies are blocked and whether the missing requirement is company identity, current employment, role fit, or verified work email. Ask the user to connect another provider or refine the target criteria, then resume the same batch when unblocked.

### 6. Validate and return

Return the same top-level JSON shape as the input. Maintain one output record per input record in the same order. Ensure the output is parseable JSON and conforms to the reference schema.

Return the full enriched JSON directly in the final chat response inside one fenced `json` code block. Do not create, save, attach, or link an output JSON file. Put no prose or comments inside the JSON block. A short completion note may appear before it. If the complete JSON would exceed a hard response limit, ask the user to split the input batch before enrichment; do not silently switch to a file or truncate the JSON.

Treat contact data as business-purpose data. Follow applicable provider terms, privacy requirements, suppression lists, and outreach rules; successful enrichment is not consent to contact.
