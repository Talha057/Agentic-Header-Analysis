# Redirects & Navigation Behavior Skill

## Purpose
Analyze URL redirection chains and navigation behavior to detect anomalies commonly associated with phishing, cloaking, traffic brokering, and malicious infrastructure.

This skill focuses on **how users are moved between URLs**, not page content or credentials.

---

## Scope
### In scope
- HTTP redirect chains (3xx responses)
- Cross-domain redirects
- Meta refresh redirects
- JavaScript-driven navigation
- Redirect loops and excessive hops
- Referrer stripping or manipulation

### Out of scope
- Content legitimacy or branding analysis
- TLS / certificate inspection
- Form behavior or data exfiltration

---

## Inputs
```json
{
  "url": "https://example.com"
}
