# Risky JS Patterns Skill

## Purpose
Detect suspicious or high-risk JavaScript behaviors that are commonly used by phishing sites, scam pages, traffic brokers, or evasive infrastructure — even when no obvious credential stealing is present.

This skill focuses on **behavioral JavaScript signals**, not intent confirmation.

---

## Scope
### In scope
- JavaScript obfuscation techniques
- Dynamic script loading and injection
- Clipboard manipulation
- Anti-debugging and analysis evasion
- Forced navigation and timer-based behavior

### Out of scope
- Proving malware execution
- Network-level payload analysis
- Backend code inspection
- Legitimate analytics scripts unless abused

## Inputs
```json
{
  "url": "https://example.com"
}

---

## Output (STRICT JSON ONLY)
```json
{
  "url": "https://example.com",
  "risk_signals": {
    "obfuscation": false,
    "dynamic_script_loading": false,
    "clipboard_manipulation": false,
    "forced_navigation": false,
    "timer_based_behavior": false
  },
  "severity": {
    "obfuscation": "low",
    "dynamic_script_loading": "low",
    "clipboard_manipulation": "low",
    "forced_navigation": "low",
    "timer_based_behavior": "low"
  },
  "behavioral_abuse": false,
  "risk_score_delta": {
    "obfuscation": 0,
    "dynamic_script_loading": 0,
    "clipboard_manipulation": 0,
    "forced_navigation": 0,
    "timer_based_behavior": 0
  },
  "behavioral_risk_score": 0,
  "suspicious_patterns": []
}
```