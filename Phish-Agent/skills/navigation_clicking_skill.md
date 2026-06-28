# Navigation & Clicking Skill (Browser Use + ChatGPT)

## Purpose
Investigate links for phishing behavior - analyze URL structure, scroll naturally, interact strategically.

**Goal:** Detect phishing signals quickly (URL + page content), avoid redundant checks, stop when confident.

---

## Safety Rules (HARD CONSTRAINTS)

❌ **NEVER:**
- Submit real credentials, OTPs, payment info
- Click: logout, delete, purchase, download, install
- Submit same form twice

✅ **ALWAYS:**
- Analyze URL BEFORE navigation
- Use synthetic test data only
- Scroll before interacting
- Stop immediately on safety violation

---


## Sandbox Mode Clarification (Docker / Safe Testing)

- Cross-domain navigation is allowed (redirects are common in phishing)
- Never submit real credentials/OTP/payment
- Never download/install anything
- Record evidence only (URLs, redirects, page signals)

## Investigation Flow
```
Phase 0: PRE-FLIGHT → Analyze URL structure
         ↓
Phase 1: GATHER → Load page, scroll, quick scan
         ↓
Phase 2: OBSERVE → Catalog elements
         ↓
Phase 3: ORIENT → Decide priority
         ↓
Phase 4: SOLVE → Pick one action
         ↓
Phase 5: EXECUTE → Act human-like
         ↓
      (Loop back to GATHER if needed)
```

---

## Phase 0: PRE-FLIGHT (URL Analysis)

**Analyze start_url BEFORE navigation:**

### URL Red Flags (Check These)
```
Random subdomain pattern:
  Examples: p1j2m3a4.site.com, abc123.example.com, x7k9m.domain.com
  Score: +80

Obfuscated/unusual path:
  Examples: /pdsvr/www/r, /track/click, /redir.php, /l.php, /out
  Score: +70

Tracking parameters (long encoded strings):
  Examples: ?1000010979.505.23.eUcT$DXPhW5$zo, ?tid=a8f7d9e2c4b1
  Score: +60

Known redirector/shortener domain:
  Examples: bit.ly, tinyurl.com, pdhost.com, shorturl.at, cutt.ly
  Score: +50

Suspicious TLD:
  Examples: .tk, .ml, .ga, .cf, .pw, .top, .click, .link
  Score: +40

IP address instead of domain:
  Examples: http://192.168.1.1, http://45.33.22.11
  Score: +30

Typosquatting (similar to known brand):
  Examples: paypa1.com, g00gle.com, microsfot.com
  Score: +90
```

### URL Decision Logic
```
Calculate total URL score:

IF score ≥ 150:
  VERDICT: PHISHING INFRASTRUCTURE
  CONFIDENCE: High
  REASON: Malicious redirector/tracker detected
  STOP (do not navigate or investigate further)

IF score 80-149:
  VERDICT: SUSPICIOUS URL
  CONFIDENCE: Medium
  FLAG: Mark as "suspicious_initial_url"
  PROCEED: Navigate but assume hostile (ignore safe final destination)

IF score < 80:
  PROCEED: Navigate normally and assess page content
```

### URL Analysis Examples
```
Example 1: PHISHING INFRASTRUCTURE
URL: http://p1j2m3a4.pdhost.com/pdsvr/www/r?1000010979.505.23.eUcT$DXPhW5$zo

Score breakdown:
+80 Random subdomain (p1j2m3a4)
+70 Obfuscated path (/pdsvr/www/r)
+60 Tracking parameters (1000010979.505.23.eUcT$DXPhW5$zo)
+50 Redirector domain (pdhost.com)
= 260 points

VERDICT: PHISHING (infrastructure detected)
ACTION: STOP (do not navigate)

---

Example 2: CLEAN URL
URL: https://www.amazon.com/dp/B08N5WRWNW

Score breakdown:
0 Known legitimate domain
0 Clean URL structure
= 0 points

VERDICT: Proceed to page analysis
ACTION: Navigate and investigate content

---

Example 3: SUSPICIOUS BUT NOT CONCLUSIVE
URL: https://secure-verify.account-services.com/login

Score breakdown:
+40 Suspicious TLD combo (account-services.com)
+30 Suspicious subdomain (secure-verify)
= 70 points

VERDICT: SUSPICIOUS (needs page investigation)
ACTION: Navigate but flag as "suspicious_initial_url"
```

---

## Phase 1: GATHER (Initial Scan + Blocker Removal)

**After navigation (if URL score allowed it):**

### Step 1: Wait for page load
```
Wait 3-5 seconds for full page load

Delayed Content Check:
- If page looks empty/benign, wait extra 3-5 seconds
- Re-scan once (some phishing loads late)
```

### Step 2: IMMEDIATELY check for blockers (PRIORITY)
```
Common blockers to dismiss (in order):
1. Cookie consent banners
2. Newsletter popups
3. Age verification
4. Location/notification requests
5. GDPR notices
6. Sticky headers/overlays

Look for buttons/elements:
- "Accept", "Accept All", "I Agree"
- "Reject All", "Decline"  
- "Close", "X", "Dismiss"
- "Continue", "Proceed"
```

### Step 3: Auto-dismiss strategy
```
IF blocker detected:
  1. Try "Accept All" / "Accept" button first
  2. If not found, try "X" / "Close" button
  3. If not found, try clicking overlay background
  4. If not found, press ESC key
  5. Wait 1 second after dismissal
  6. Check if blocker is gone
  7. If still there, retry once
  8. If still blocking, record and proceed anyway

CRITICAL: Never spend more than 10 seconds on blocker removal
```

### Step 4: After blockers cleared, then scroll
```
1. Scroll slowly top to bottom:
   - Scroll to 30% → wait 1s
   - Scroll to 60% → wait 1s
   - Scroll to 100% → wait 2s
   - Scroll back to top
2. Quick visual scan:
   ✓ Current URL (check for redirects)
   ✓ SSL warnings
   ✓ Visible urgency text
   ✓ Brand logos/impersonation
   ✓ Page loads successfully?
```

### Common blocker patterns to recognize:
```
Cookie banners:
- Text contains: "cookies", "privacy", "consent", "GDPR"
- Buttons: "Accept", "Reject", "Cookie settings"

Newsletter popups:
- Text contains: "newsletter", "subscribe", "email updates"
- Usually appears after 2-3 seconds

Age verification:
- Text contains: "18+", "age", "verify", "birth date"

Location requests:
- Browser native popup (can't dismiss with click)
- Text: "wants to know your location"
```

---

## Phase 2: OBSERVE (Full Inventory)

**After scrolling, catalog what exists:**
```json
{
  "current_url": "https://...",
  "initial_url_suspicious": true/false,
  "page_type": "login | payment | home | product | error | empty",
  "forms": {
    "login_form": true,
    "payment_form": false,
    "contact_form": false
  },
  "fields": {
    "password": true,
    "email": true,
    "credit_card": false,
    "otp": false
  },
  "interactive_elements": {
    "login_buttons": 1,
    "external_links": 3,
    "download_buttons": 0
  },
  "link_candidates": [
    {
      "text": "Verify your account",
      "element_type": "button | div | span | a",
      "trigger": "href | onclick | js_navigation | deeplink",
      "suspected_destination": "external | internal | unknown"
    }
  ],
  "warning_signs": {
    "urgency_words": ["suspended", "verify now"],
    "brand_logos": ["PayPal"],
    "brand_domain_mismatch": true,
    "ssl_warning": false,
    "grammar_errors": true
  }
}
```

### Self-Check Questions
```
"Have I seen this page type before?"
  → If YES: Skip similar interactions
  
"Is this new information?"
  → If NO: Stop investigating
  
"Was initial URL suspicious?"
  → If YES: Don't trust current page (assume hostile)
  
"Can I give verdict now?"
  → If YES: Stop and report
```

---

## Phase 3: ORIENT (Decide Priority)

### Pattern Recognition
```
IF visited 2+ pages with same page_type:
  → Mark as "redundant pattern"
  → STOP (no new information)

IF page_type is NEW:
  → Investigate further

IF initial_url_suspicious == true:
  → Any credential form = PHISHING
  → Don't wait for more evidence

IF current_step >= 12:
  → Only critical actions
  → Prepare to stop
```

### Priority Matrix
```
CRITICAL (investigate immediately):
- Login forms (if initial URL suspicious)
- Payment forms
- Credential harvesting attempts

HIGH:
- Login forms (if URL was clean)
- External redirects
- Suspicious CTAs

LOW:
- About pages
- Blog/news
- Privacy policy

SKIP:
- Already-tested patterns
- Low-signal content
```

---

## Phase 4: SOLVE (Pick ONE Action)

**Decision tree (first match wins):**
```
0. POPUP/BLOCKER/COOKIE BANNER visible?
   → Dismiss it FIRST (Accept/Close/X)
   → Wait 1 second
   → Re-scan page
   → Reason: Can't investigate if page is blocked

1. Initial URL suspicious + credential form detected?
   → VERDICT: PHISHING
   → STOP (infrastructure + harvesting = confirmed)

2. LOGIN FORM detected + forms_submitted < 1?
   → Fill ONLY (do not submit if policy forbids)
   → If submit is allowed by policy, submit once with synthetic data
   → Reason: Detect credential harvesting safely


3. EXTERNAL LINK + not followed yet + redirects_tracked < 3?
   → Click and track
   → Reason: Map redirect chain

4. NEW high-value element?
   → Click if safe
   → Reason: Discover new patterns

5. Nothing new OR budget exhausted?
   → STOP
   → Reason: Investigation complete
```

---

**Only ONE action per cycle**

---

## Phase 5: EXECUTE (Act Human-Like)

### For Clicks
```
1. Scroll element into view
2. Wait 1 second (human delay)
3. Click element
4. Wait for page response (max 4s)
5. If redirected: scroll new page
6. Back to GATHER (Phase 1)
```

### For Form Submission
```
Policy Gate:
- IF action_policy.allow_form_submit == false → DO NOT SUBMIT
- Only fill fields and record page reaction (if any)
- STOP after fill (one fill max)

IF password_field + forms_submitted < 1:
  1. Scroll to form
  2. Fill fields one by one:
     - Email: test{random6}@analysis.local
     - Password: TestPass{random6}!
  3. Wait 1 second
  4. IF action_policy.allow_form_submit == true:
       - Click submit (one submission max)
       - Observe outcome
     ELSE:
       - Do NOT click submit
       - Record "filled_only_no_submit"
  5. Observe outcome (max 4s):
     - Redirect?
     - Error message?
     - Success message?
  6. Record outcome
  7. STOP


IF payment/otp/2fa form:
  → DO NOT SUBMIT
  → Record as checkpoint
  → STOP
```

### Record Critical Events Only
```json
{
  "action": "submit_login_form",
  "outcome": "redirected_to_error",
  "url_after": "https://site.com/dashboard",
  "network_domains": ["site.com", "cdn.site.com", "tracker.example"]
}

```

---

## State Memory (Self-Tracking)
```json
{
  "initial_url_score": 260,
  "initial_url_suspicious": true,
  "visited_page_types": ["login"],
  "forms_submitted": 1,
  "redirects_tracked": 2,
  "redirect_chain": ["url1", "url2"],
  "current_step": 5,
  "pattern_detected": "login_loop | none"
}
```

### Auto-Stop Conditions
```
IF initial_url_score ≥ 150:
  → STOP before navigation

IF initial_url_suspicious + credential_form:
  → STOP (phishing confirmed)

IF same page_type visited 2+ times:
  → STOP (redundant)

IF redirect_chain has 3+ URLs:
  → STOP (chain mapped)

IF forms_submitted >= 1:
  → STOP (tested)

IF current_step >= 15:
  → STOP (max steps)

IF pattern_detected == "login_loop":
  → STOP (infinite redirect)
```

---

## Phishing Detection Logic

### Two-Phase Verdict System

**Phase A: Initial URL Verdict**
```
IF URL score ≥ 150:
  VERDICT: PHISHING
  TYPE: Infrastructure/Redirector
  STOP: Do not navigate

IF URL score 80-149:
  FLAG: suspicious_initial_url
  PROCEED: But assume hostile
```

**Phase B: Page Content Verdict**
```
IF suspicious_initial_url + ANY credential form:
  VERDICT: PHISHING
  TYPE: Credential harvesting via redirector
  STOP: Ignore "safe" final destination

IF clean_initial_url + 3+ page red flags:
  VERDICT: PHISHING
  TYPE: Direct phishing page
  STOP: Confirmed attack

IF clean_initial_url + known legit domain + no forms:
  VERDICT: NOT PHISHING
  STOP: Safe link
```

### Red Flags Scoring (Page Content)
```
+50 Password field
+40 Urgency language ("verify", "suspended", "act now")
+90 Typosquatting domain (paypa1.com)
+60 Brand detected but domain mismatch
+20 Fake security badges
+45 SSL warnings

Green flags:
-50 Known legitimate domain
-20 Valid SSL certificate
-10 Professional design
```

**Threshold:**
```
Total ≥ 100 → PHISHING
Total ≤ 20 → NOT PHISHING
21-99 → SUSPICIOUS (needs more investigation)
```

---

## Critical Decision: Suspicious URL Override

**IMPORTANT RULE:**
```
IF initial_url_suspicious == true:
  THEN final destination is IRRELEVANT
  
  Even if redirects to:
  - Legitimate domain (amazon.com, google.com)
  - Safe-looking page
  - No visible phishing
  
  VERDICT: Still PHISHING
  REASON: Attack infrastructure detected
```

**Why?**
```
Phishing redirectors can:
- Switch destinations based on time/location/user-agent
- Show safe page to scanners, attack page to victims
- Log clicks for targeting
- Change behavior after detection
```

**Example:**
```
URL: http://p1j2m3a4.pdhost.com/track?id=victim123
Redirects to: https://www.hugedomains.com

VERDICT: PHISHING (not "not_phishing")
REASON: Malicious redirector infrastructure (score: 260)
IGNORE: Final destination irrelevant
```

---

## Output Format (Minimal)
```json
{
  "verdict": "phishing | not_phishing | suspicious",
  "confidence": "high | medium | low",
  "phishing_type": "infrastructure | credential_harvest | brand_impersonation | none",
  "initial_url_analysis": {
    "score": 260,
    "flags": ["random_subdomain", "obfuscated_path", "tracking_params", "redirector_domain"]
  },
  "redirect_chain": ["url1", "url2", "url3"],
  "key_actions": [
    {
      "action": "url_analysis",
      "outcome": "phishing_infrastructure_detected"
    }
  ],
  "red_flags": ["suspicious_url", "redirector"],
  "stopped_reason": "infrastructure_detected | login_tested | fast_verdict"
}
```

---

## Example Flows

### Example 1: Phishing Infrastructure (Instant Detection)
```
PHASE 0: PRE-FLIGHT
→ URL: http://p1j2m3a4.pdhost.com/pdsvr/www/r?1000010979.505.23.eUcT$DXPhW5$zo

Analyze:
+80 Random subdomain (p1j2m3a4)
+70 Obfuscated path (/pdsvr/www/r)
+60 Tracking parameters (encoded string)
+50 Redirector domain (pdhost.com)
= 260 points

Decision: Score ≥ 150 → PHISHING INFRASTRUCTURE

OUTPUT:
{
  "verdict": "phishing",
  "confidence": "high",
  "phishing_type": "infrastructure",
  "initial_url_analysis": {
    "score": 260,
    "flags": ["random_subdomain", "obfuscated_path", "tracking_params", "redirector"]
  },
  "redirect_chain": [],
  "key_actions": [{
    "action": "url_analysis",
    "outcome": "malicious_redirector_detected"
  }],
  "red_flags": ["suspicious_url_structure", "tracking_infrastructure"],
  "stopped_reason": "infrastructure_detected"
}

→ STOP (no navigation needed)
```

---

### Example 2: Suspicious URL + Credential Form
```
PHASE 0: PRE-FLIGHT
→ URL: https://secure-verify.account-update.tk/login

Analyze:
+40 Suspicious TLD (.tk)
+30 Suspicious subdomain (secure-verify)
= 70 points

Decision: Score < 150 → Proceed but flag as suspicious

PHASE 1: GATHER
→ Navigate to URL
→ Scroll top to bottom
→ Observe: Login form visible

PHASE 2: OBSERVE
→ page_type: "login"
→ has_password_field: true
→ initial_url_suspicious: true

PHASE 3: ORIENT
→ CRITICAL: suspicious URL + credential form detected

PHASE 4: SOLVE
→ Decision: PHISHING confirmed
→ Reason: Suspicious infrastructure + credential harvesting

OUTPUT:
{
  "verdict": "phishing",
  "confidence": "high",
  "phishing_type": "credential_harvest",
  "initial_url_analysis": {
    "score": 70,
    "flags": ["suspicious_tld", "suspicious_subdomain"]
  },
  "redirect_chain": ["https://secure-verify.account-update.tk/login"],
  "key_actions": [{
    "action": "detected_credential_form_on_suspicious_url",
    "outcome": "phishing_confirmed"
  }],
  "red_flags": ["suspicious_url", "credential_form", "unusual_tld"],
  "stopped_reason": "suspicious_url_with_credential_harvesting"
}

→ STOP (do not submit form)
```

---

### Example 3: Clean URL, Legitimate Site
```
PHASE 0: PRE-FLIGHT
→ URL: https://www.amazon.com/dp/B08N5WRWNW

Analyze:
0 Known legitimate domain
0 Clean URL structure
= 0 points

Decision: Proceed normally

PHASE 1: GATHER
→ Navigate and scroll
→ Observe: Product page, no forms

PHASE 2: OBSERVE
→ page_type: "product"
→ has_password_field: false
→ known_legitimate_domain: true

PHASE 3: ORIENT
→ Fast verdict: Legit domain + no credential forms

PHASE 4: SOLVE
→ Decision: NOT PHISHING

OUTPUT:
{
  "verdict": "not_phishing",
  "confidence": "high",
  "phishing_type": "none",
  "initial_url_analysis": {
    "score": 0,
    "flags": []
  },
  "redirect_chain": ["https://www.amazon.com/dp/B08N5WRWNW"],
  "key_actions": [
    {
      "action": "observe_page",
      "outcome": "no_credential_forms_detected"
    }
  ],
  "red_flags": [],
  "stopped_reason": "legitimate_site_confirmed"
}

→ STOP
```

---

### Example 4: Clean URL, Test Login
```
PHASE 0: PRE-FLIGHT
→ URL: https://new-service-login.com

Analyze:
0 No suspicious patterns
= 0 points

Decision: Proceed

PHASE 1: GATHER
→ Navigate and scroll
→ Login form visible
→ No urgency language

PHASE 2: OBSERVE
→ page_type: "login"
→ has_password_field: true
→ initial_url_suspicious: false

PHASE 3: ORIENT
→ Clean URL but has login form
→ Need to test: Submit form

PHASE 4: SOLVE
→ Decision: Submit login form

PHASE 5: EXECUTE
→ Scroll to form
→ Fill: test472819@analysis.local / TestPass472819!
→ Submit
→ Observe: "Invalid credentials" error

OUTPUT:
{
  "verdict": "suspicious",
  "confidence": "medium",
  "phishing_type": "potential_credential_harvest",
  "initial_url_analysis": {
    "score": 0,
    "flags": []
  },
  "redirect_chain": ["https://new-service-login.com"],
  "key_actions": [{
    "action": "submit_login",
    "outcome": "invalid_credentials_error"
  }],
  "red_flags": ["credential_form", "unknown_service"],
  "stopped_reason": "login_tested"
}

→ STOP
```

---

## Budgets
```json
{
  "max_steps": 15,
  "max_form_submissions": 1,
  "max_clicks": 6,
  "max_redirects_tracked": 3
}
```

**Enforcement:**
```
Before each action:
  IF current_step >= 15 → STOP
  IF forms_submitted >= 1 → STOP
  IF clicks >= 6 → STOP
```

---

## Navigation Rules

**Allowed:**
- Login pages
- Verification pages
- Password reset (observe only)

**Avoid (low-signal) unless evidence needed:**
- About / Blog / Terms / FAQ (ONLY if you need proof: contact mismatch, fake support, brand impersonation)
- Pagination / Category browsing (ONLY if it is part of the phishing flow)



**External links:**
- Track redirect chain
- Cross-domain navigation is allowed (sandbox)
- Stop ONLY if action violates safety rules (download/install/payment/otp/real creds)
---

## Anti-Hallucination Rules

**Stay grounded:**
```
✓ Only analyze URLs you actually see
✓ Only interact with elements visible after scroll
✓ Only report outcomes that happened
✓ If element not found → skip it, don't assume

✗ Never invent URL patterns
✗ Never assume page content
✗ Never guess outcomes
```

---

## Key Principles

1. **URL first, page second** - Analyze URL before navigation
2. **Don't trust redirects** - Suspicious URL = phishing even if safe destination
3. **Scroll reveals truth** - Always scroll before deciding
4. **Act human** - Natural delays and movements
5. **Fast verdicts** - Stop as soon as confident
6. **No redundancy** - Skip repeated patterns
7. **One submission max** - Test once, done
8. **Track everything** - URL score, redirects, actions

---

## Input Schema
```json
{
  "start_url": "https://example.com",
  "max_steps": 15,
  "sandbox_mode": true,
  "action_policy": {
    "allow_navigation_any_domain": true,
    "allow_clicks": true,
    "allow_form_fill": true,
    "allow_form_submit": false,
    "allow_downloads": false,
    "allow_installs": false,
    "allow_payments": false,
    "allow_otp": false
  }
}

```

---

**Optimized for GPT-4o-mini - URL-first analysis prevents false negatives**