# Authenticity & Phishing Decision Signals

## Purpose
Provide a conservative decision framework to classify a website as **legit**, **suspicious**, or **phishing** based on combined evidence from navigation behavior, technical checks, and behavioral analysis skills.

This is a **decision reference**, not a detection skill.

---

## Legit Indicators (STRONG)
- Consistent branding across pages
- Real footer links (privacy, terms, contact, security)
- No forced redirects or deceptive JS behavior
- Clean SSL with known CA
- Domain age > 1 year and reputable TLD
- No credential harvesting behavior

---

## Suspicious Indicators (MODERATE)
- Low navigation coverage
- Behavioral abuse without credential theft
- Obfuscated or dynamic JS without explanation
- Short-lived or unknown domains
- Redirect chains without clarity

---

## Phishing Indicators (STRONG)
- Login/payment forms + brand mismatch
- Credential submission endpoints
- Forced redirection after form submission
- Clipboard manipulation tied to credential flow
- Lookalike domains impersonating real brands
- Social-engineering language + technical abuse

---

## Decision Rules
- Output **legit** ONLY if strong legit indicators exist AND no suspicious behavior detected
- Output **phishing** ONLY if clear credential or impersonation intent is observed
- Otherwise output **suspicious**
- If evidence is incomplete or uncertain → choose **suspicious**

---

## Risk Interpretation Guidance
- Behavioral risk alone ≠ phishing
- Risk score ≥ 50 cannot result in legit
- Multiple moderate indicators can escalate to phishing

---
