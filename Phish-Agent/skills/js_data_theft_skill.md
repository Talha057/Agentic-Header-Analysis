# JS Stealing Data Skill

## Purpose
Detect JavaScript behavior that attempts to **capture, manipulate, or exfiltrate sensitive user data**, such as credentials, payment details, or personal identifiers.

This skill focuses on **active data theft patterns**, not general obfuscation or suspicious-but-benign JavaScript.

---

## Scope
### In scope
- Keylogging and input interception
- Form value harvesting
- Network exfiltration of sensitive data
- Obfuscation specifically wrapping stolen values
- Suspicious external endpoints receiving user data

### Out of scope
- Legitimate analytics or form submission to same-site backends
- Generic JavaScript obfuscation without data access
- Browser extensions or injected third-party scripts outside page scope

---

## Inputs
```json
{
  "url": "https://example.com"
}
