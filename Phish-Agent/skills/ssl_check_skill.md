# SSL / TLS Check Skill

## Purpose
Assess whether a target site uses HTTPS correctly and whether its TLS/certificate setup shows risk indicators commonly associated with phishing, scam shops, or misconfigured sites.

This skill focuses on:
- HTTPS availability and enforcement
- Mixed-content risk
- Certificate validity and basic sanity checks
- HSTS usage (often part of broader security posture)

---

## Scope
### In scope
- Detect HTTP → HTTPS behavior
- Confirm final URL uses HTTPS
- Identify mixed content (HTTP resources on an HTTPS page)
- Inspect certificate basics (issuer, validity, SAN/CN match, self-signed)
- Check HSTS presence (header)

### Out of scope
- Deep PKI chain auditing (OCSP stapling, CT logs, etc.)
- Proving site legitimacy (this only evaluates TLS/HTTPS signals)
- Malware scanning

---

## Inputs
```json
{
  "url": "https://example.com"
}
