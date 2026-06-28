def empty_report(url: str) -> dict:
    return {
        "target_url": url,
        "status": "unknown",
        "risk_score": None,  
        "verdict": None,     # "legit"|"suspicious"|"phishing"
        "signals": {},
        "evidence": [],
        "navigation": {},
        "errors": [],
    }
