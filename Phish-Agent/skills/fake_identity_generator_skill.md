# Fake Identity Generator Skill

## Purpose
Generate fake data for form fields during phishing analysis.

**Goal:** Create realistic fake credentials that pass validation. Never use real data.

---

## Input Schema
```json
{
  "fields_detected": ["email", "password", "phone"],
  "form_type": "login | payment | contact"
}
```

---

## Output Schema
```json
{
  "email": "falcon8472@gmail.com",
  "password": "Tiger123!@falcon",
  "phone": "+12025551234"
}
```

---

## Generation Rules

### Email
```
{word}{4digits}@{domain}

Words: falcon, sunset, river, storm, tiger, eagle
Domains: gmail.com, yahoo.com, outlook.com

Example: falcon8472@gmail.com
```

### Password
```
{Capital}{lowercase}{digits}{special}

8-16 chars, 1+ uppercase/lowercase/digit/special

Example: Tiger123!@falcon
```

### Phone (US)
```
+1{area}555{4digits}

Areas: 202, 213, 415, 510, 650

Example: +12025551234
Format: (202) 555-1234
```

### Name
```
First: James, John, Michael, Mary, Patricia, Jennifer
Last: Smith, Johnson, Williams, Brown, Jones

Example: James Anderson
```

### Address
```
{number} {street} {type}, {city}, {state} {zip}

Streets: Oak, Maple, Pine, Main
Types: Street, Avenue, Road
Cities: Los Angeles CA 90012, New York NY 10001

Example: 4523 Oak Street, Los Angeles, CA 90012
```

### Credit Card
```
Visa: 4532148803436467
MC: 5425233430109903
Amex: 378282246310005

Use valid Luhn checksum
```

### CVV
```
Visa/MC: 123, 456, 789
Amex: 1234
```

### Expiry
```
MM/YY format
Month: 01-12
Year: +1 to +5 years

Example: 12/26
```

### SSN (Test)
```
987-65-43XX (XX = 20-29)

Example: 987-65-4321
```

### DOB
```
MM/DD/YYYY
Age: 21-65

Example: 03/15/1985
```

### OTP
```
Test codes: 123456, 000000, 111111

Example: 123456
```

---

## Field Mapping
```
email/mail → email
password/pass → password
phone/tel → phone
card/cc → card_number
cvv/cvc → cvv
exp → expiry
firstname → firstname
lastname → lastname
ssn → ssn
address → street
city → city
state → state
zip → zip
```

---

## Validation

**Email:** Has @ and domain  
**Phone:** 10 digits, valid area code  
**Card:** Luhn checksum valid  
**Password:** 8+ chars, uppercase/lowercase/digit/special  

---

## Multiple Identities
```json
{
  "identities": [
    {"email": "falcon8472@gmail.com", "password": "Tiger123!@falcon"},
    {"email": "sunset1923@yahoo.com", "password": "Mountain$2847River"},
    {"email": "river5634@outlook.com", "password": "Storm#9472Eagle"}
  ]
}
```

Use for testing multiple submissions.

---

## Key Rules

1. **Always fake** - Never real data
2. **Match fields** - Generate only what's needed
3. **Pass validation** - Use valid formats
4. **Stay consistent** - Same identity per form
5. **Random values** - No sequential patterns

---

## Example Output

**Login form:**
```json
{"email": "falcon8472@gmail.com", "password": "Tiger123!@falcon"}
```

**Payment form:**
```json
{
  "card_number": "4532 1488 0343 6467",
  "cvv": "123",
  "expiry": "12/26",
  "name": "JAMES ANDERSON"
}
```

---
