# Brand Mismatch Detection Skill

## Purpose
Detect mismatch between claimed brand and domain/page content.

## Checks
- expected brand vs domain (paypal.com vs paypaI.com)
- logo/text claims vs actual domain
- favicon + title mismatch patterns

## Output JSON
{
  "skill":"brand_mismatch",
  "signals":[{"name":"brand_domain_mismatch","value":true|false,"weight":22,"why":"..."}],
  "risk_notes":[]
}
