# Domain Check Skill

## Purpose
Evaluate domain-level risk indicators commonly associated with phishing, scam sites, and abusive infrastructure.

This skill focuses on **domain structure, age, and naming patterns**, not page content.

---

## Scope
### In scope
- WHOIS-based domain age and registration signals
- Subdomain abuse patterns
- IP-based URLs
- Suspicious or brand-inappropriate TLDs
- Domain name entropy and structure analysis

### Out of scope
- DNS reputation scoring from third-party feeds
- Content-based legitimacy checks
- TLS / certificate analysis (handled by SSL skill)

---

## Inputs
```json
{
  "url": "https://example.com"
}
