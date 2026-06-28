# orchestrator.py
import os
import asyncio
import json
from dataclasses import dataclass
from dotenv import load_dotenv

from browser_use import Agent
from browser_use import Browser, BrowserProfile

from browser_use.llm.openai.chat import ChatOpenAI
from openai import AsyncOpenAI

from skill_loader import load_skill
from schemas import empty_report
from models import get_routes
from utils import safe_json_dump, domain_of, now_ms, generate_fake_credentials
# from skills.ssl_checker import check_ssl

# from groq_client import GroqClient
# from groq_router import pick_model

load_dotenv()


def write_debug_log(report: dict, filename: str = "phish_debug_log.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)


@dataclass
class OrchestratorConfig:
    max_steps: int = 25                    # More steps for deep exploration
    safe_mode: bool = False                  # Allow all interactions
    no_credentials: bool = False             # Allow credential input
    no_form_submit: bool = False             # Allow form submission
    headless: bool = False                    # Run headless in Docker
    use_fake_credentials: bool = True        # Use fake data generator
    max_form_attempts: int = 3               # Try multiple fake credentials
    follow_all_redirects: bool = True        # No redirect limits


class PhishOrchestrator:
    def __init__(self, config: OrchestratorConfig | None = None):
        self.config = config or OrchestratorConfig()
        self.routes = get_routes()

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("Missing OPENAI_API_KEY environment variable.")

        self.api_key = api_key

        # Browser-use browser + LLM (for navigation only)
        profile = BrowserProfile(
            headless=self.config.headless,
            window_size={"width": 1920, "height": 1080},
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            extra_chromium_args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-popup-blocking',
                '--disable-blink-features=AutomationControlled',
            ]
        )

        self.browser = Browser(browser_profile=profile)
        self.chatgpt = ChatOpenAI(
            api_key=self.api_key,
            model=self.routes["NAVIGATION"].model_id,
        )

        # Direct OpenAI client (for decision only, avoids browser-use serializer issues)
        self.oai = AsyncOpenAI(api_key=self.api_key)

        # Groq client for open-source skills
        # self.groq = GroqClient()

    async def run(self, target_url: str, brand_expected: str | None = None) -> dict:
        report = empty_report(target_url)

        report["signals"]["meta"] = {
            "timestamp_ms": now_ms(),
            "expected_brand": brand_expected,
            "target_domain": domain_of(target_url),
            "safe_mode": self.config.safe_mode,
            "no_credentials": self.config.no_credentials,
            "no_form_submit": self.config.no_form_submit,
        }

        # ---------------- OBSERVE (NAVIGATION) ----------------
        nav_result = await self._act_navigation(target_url)
        report["navigation"] = nav_result

        final_url = nav_result.get("final_url") or target_url
        redirect_chain = nav_result.get("redirect_chain", []) or []
        page_signals = nav_result.get("page_signals", {}) or {}
        visited_urls = nav_result.get("visited_urls", []) or []
        actions = nav_result.get("actions", []) or []

        report["signals"]["navigation"] = {
            "final_url": final_url,
            "redirect_chain": redirect_chain,
            "page_signals": page_signals,
            "visited_urls": visited_urls,
            "actions_count": len(actions),
        }

        # Evidence gating: if navigation did not explore enough, record that.
        if len(visited_urls) < 2 and len(actions) < 2:
            report.setdefault("evidence", []).append({
                "signal": "low_navigation_coverage",
                "why": "Navigation did not explore enough internal pages/actions; final decision should be conservative."
            })

        # ---------------- ORIENT (PICK SKILLS) ----------------
        skills_to_run = self._orient_skills(page_signals)

        # ---------------- ACT (RUN SKILLS) ----------------
        results = []
        for skill_name in skills_to_run:
            res = await self._act_opensource_skill(skill_name, final_url, brand_expected)
            results.append(res)

        report["signals"]["analysis_modules"] = results

        # ---------------- DECIDE (FINAL VERDICT) ----------------
        decision = await self._act_critical_decision(report)
        report["risk_score"] = decision.get("risk_score")
        report["verdict"] = decision.get("verdict")
        report["status"] = "done"
        report["evidence"] = decision.get("evidence", []) or report.get("evidence", [])


        risk_score = report.get("risk_score", 0)
        verdict = report.get("verdict")

        # HARD RULE: risk score must dominate verdict
        if risk_score >= 50 and verdict in ("legit", "not_phishing"):
            report["verdict"] = "suspicious"
            report["confidence"] = "medium"

            report.setdefault("evidence", []).append({
                "signal": "verdict_override",
                "why": "Risk score >= 50 cannot result in a legit verdict; downgraded to suspicious."
            })

        print("\n=== FINAL VERDICT ===")
        print(f"Verdict     : {report.get('verdict')}")
        print(f"Risk Score  : {report.get('risk_score')}")
        print("Reason(s):")

        for ev in report.get("evidence", []):
            print(f"- {ev.get('signal')}: {ev.get('why')}")

        write_debug_log(report)

        return report

    async def _act_navigation(self, target_url: str) -> dict:
        """
        Uses browser_use Agent to:
        - Open the URL
        - Dismiss overlays/cookies if present
        - Explore ALL links and submit ALL forms with fake data
        - Capture redirect chain, visited urls, actions and page signals
        - Follow ALL redirects (no domain restrictions)
        """
        skill_text = load_skill("navigation_clicking_skill.md")
        fake_identity_skill = load_skill("fake_identity_generator_skill.md")

        task = f"""
        === NAVIGATION SKILL ===
        {skill_text}
        === END NAVIGATION SKILL ===

        === FAKE IDENTITY GENERATOR SKILL ===
        {fake_identity_skill}
        === END FAKE IDENTITY GENERATOR SKILL ===

        ⚠️ CRITICAL INSTRUCTIONS - MUST FOLLOW ⚠️

        You are investigating a SUSPECTED PHISHING SITE: {target_url}

        Your job is to THOROUGHLY EXPLORE this site to find evidence of phishing behavior.

        MANDATORY STEPS (DO NOT SKIP):
        1. ✅ Navigate to the start URL
        2. ✅ Scroll the entire page to reveal all content
        3. ✅ Click EVERY single link on the page (even if it looks safe)
        4. ✅ Fill and submit EVERY form you find with fake data from the Fake Identity Generator
        5. ✅ Follow ALL redirects to their final destination
        6. ✅ Capture screenshots, HTML, and network logs
        7. ✅ Record ALL visited URLs and actions taken

        ⚠️ DO NOT conclude early just because the page looks safe or parked.
        ⚠️ Phishing sites often hide behind innocent-looking landing pages.
        ⚠️ You MUST click at least 3-5 links before finishing.
        ⚠️ You MUST explore for at least 10 steps before concluding.

        INPUT JSON:
        {{
        "start_url": "{target_url}",
        "goal": "AGGRESSIVELY explore this suspected phishing site. Click EVERY link. Submit EVERY form with fake credentials. Follow ALL redirect chains. Assume this IS phishing until proven otherwise.",
        "max_steps": {self.config.max_steps},
        "allowed_domains": [],
        "disallowed_patterns": [],
        "interaction_policy": {{
            "no_credentials": false,
            "no_form_submit": false,
            "safe_mode": false,
            "use_fake_identity_generator": true,
            "max_form_attempts": {self.config.max_form_attempts}
        }},
        "artifacts": {{
            "collect_screenshots": true,
            "collect_html": true,
            "collect_network_logs": true
        }}
        }}

        EXPLORATION CHECKLIST (mark each as you complete):
        [ ] Navigated to start URL
        [ ] Scrolled entire page
        [ ] Clicked link #1
        [ ] Clicked link #2
        [ ] Clicked link #3
        [ ] Clicked link #4
        [ ] Found and filled form (if exists)
        [ ] Submitted form with fake identity #1
        [ ] Submitted form with fake identity #2
        [ ] Submitted form with fake identity #3
        [ ] Followed redirect chain
        [ ] Captured final destination
        [ ] Recorded all visited URLs

        Return output strictly in the JSON schema defined in the navigation skill.
        """.strip()

        agent = Agent(task=task, llm=self.chatgpt, browser=self.browser)
        history = await agent.run()

        # 1) Best case: already a dict in the correct schema
        if isinstance(history, dict):
            # normalize a bit
            history.setdefault("visited_urls", history.get("redirect_chain", []) or [])
            history.setdefault("page_signals", history.get("page_signals", {}) or {})
            return history

        # 2) Try extracting JSON from final "done" step (browser_use returns AgentHistoryList)
        extracted = None
        page_signals = {}
        visited_urls = []
        redirect_chain = []
        actions = []
        final_url = target_url
        notes = []
        errors = []

        if hasattr(history, "all_results"):
            # Collect visited URLs from any extracted_content that looks like a URL
            for step in history.all_results:
                txt = getattr(step, "extracted_content", None)
                if isinstance(txt, str):
                    # capture page signals from evaluate() JSON
                    try:
                        data = json.loads(txt)
                        if isinstance(data, dict) and (
                            "hasLoginForm" in data or "hasCookieBanner" in data
                        ):
                            page_signals = {
                                "has_cookie_banner": data.get("hasCookieBanner", False),
                                "has_login_form": data.get("hasLoginForm", False),
                                "has_captcha": data.get("hasCaptcha", False),
                                "has_popup_overlay": data.get("hasPopupOverlay", False),
                            }
                    except Exception:
                        pass

            # Prefer the last step that contains JSON schema from the skill
            for step in reversed(history.all_results):
                txt = getattr(step, "extracted_content", None)
                if isinstance(txt, str) and ("final_url" in txt and "redirect_chain" in txt):
                    try:
                        extracted = json.loads(txt)
                        break
                    except Exception:
                        # try to extract {...}
                        start = txt.find("{")
                        end = txt.rfind("}")
                        if start != -1 and end != -1 and end > start:
                            try:
                                extracted = json.loads(txt[start:end + 1])
                                break
                            except Exception:
                                pass

        if isinstance(extracted, dict):
            final_url = extracted.get("final_url") or extracted.get("finalUrl") or final_url
            redirect_chain = extracted.get("redirect_chain") or extracted.get("redirectChain") or redirect_chain
            actions = extracted.get("actions") or actions
            ps = extracted.get("page_signals") or extracted.get("pageSignals") or {}
            if isinstance(ps, dict) and ps:
                page_signals = ps
            visited_urls = extracted.get("visited_urls") or extracted.get("visitedUrls") or []
            if not visited_urls:
                # fallback: at least keep redirect chain as "visited"
                visited_urls = list(dict.fromkeys(redirect_chain or []))

            return {
                "status": extracted.get("status", "success"),
                "final_url": final_url,
                "redirect_chain": redirect_chain or ([target_url] if target_url else []),
                "visited_urls": visited_urls,
                "actions": actions or [],
                "page_signals": page_signals or {},
                "notes": extracted.get("notes", []) or [],
                "errors": extracted.get("errors", []) or [],
            }

        # 3) Worst case fallback (no schema extracted)
        notes.append("Could not extract final JSON from browser_use history; returning conservative partial result.")
        errors.append(str(history))

        return {
            "status": "partial",
            "final_url": target_url,
            "redirect_chain": [target_url],
            "visited_urls": [target_url],
            "actions": [],
            "page_signals": page_signals or {},
            "notes": notes,
            "errors": errors,
        }

    def _orient_skills(self, page_signals: dict) -> list[str]:
        """
        Full analysis skill set for production.
        """
        skills = [
            "ssl_check_skill.md",
            "domain_check_skill.md",
            "redirects_navigation_skill.md",
            "risky_js_patterns_skill.md",
            "js_data_theft_skill.md",
        ]

        if page_signals.get("has_login_form") or page_signals.get("has_payment_form"):
            skills += ["brand_mismatch_skill.md"]

        # Deduplicate while preserving order
        return list(dict.fromkeys(skills))

#     async def _act_opensource_skill(
#         self,
#         skill_filename: str,
#         url: str,
#         brand_expected: str | None
#     ) -> dict:
#         skill_text = load_skill(skill_filename)
#         skill_key = skill_filename.replace("_skill.md", "")
#         model = pick_model(skill_key)

#         prompt = f"""
# === SKILL SPEC ===
# {skill_text}
# === END SKILL ===

# Analyze this URL:
# {url}

# Expected brand:
# {brand_expected}

# Return ONLY valid JSON as defined in the skill.
# """.strip()

#         output = await asyncio.to_thread(self.groq.run, model, prompt)

#         return {
#             "skill": skill_key,
#             "model": model,
#             "raw_output": output,
#         }


    async def _act_opensource_skill(
            self,
            skill_filename: str,
            url: str,
            brand_expected: str | None
        ) -> dict:
            skill_text = load_skill(skill_filename)
            skill_key = skill_filename.replace("_skill.md", "")

            prompt = f"""
            === SKILL SPEC ===
            {skill_text}
            === END SKILL ===

            Analyze this URL:
            {url}

            Expected brand:
            {brand_expected}

            Return ONLY valid JSON as defined in the skill.
            """.strip()


            # Use OpenAI for all analysis skills
            resp = await self.oai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            output = (resp.choices[0].message.content or "").strip()

            parsed = None
            try:
                parsed = json.loads(output)
            except Exception:
                start = output.find("{")
                end = output.rfind("}")
                if start != -1 and end != -1 and end > start:
                    try:
                        parsed = json.loads(output[start:end + 1])
                    except Exception:
                        parsed = None

            return {
                "skill": skill_key,
                "model": "gpt-4o-mini",
                "raw_output": output,
                "parsed": parsed,
            }




    async def _act_critical_decision(self, report: dict) -> dict:
        """
        IMPORTANT:
        - Do NOT use browser_use Agent() here.
        - Use direct OpenAI call with AsyncOpenAI, and parse strict JSON.
        """
        skill = load_skill("authenticity_signals_skill.md")

        decision_prompt = f"""
You are the final decision agent.

Return strict JSON ONLY (no markdown, no extra text):
{{
  "verdict": "legit"|"suspicious"|"phishing",
  "risk_score": 0-100,
  "evidence": [{{"signal":"...", "why":"..."}}]
}}

Hard rule:
- You may output "legit" ONLY if navigation explored at least 2 internal pages OR clearly found real footer/help links (privacy/terms/help/contact/security) consistent with the expected brand.
- If navigation coverage is low or uncertain, output "suspicious".

Be conservative. If outputs are incomplete/uncertain, choose "suspicious".

Reference:
{skill}

REPORT:
{safe_json_dump(report)}
""".strip()

        try:
            resp = await self.oai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": decision_prompt}],
                temperature=0,
            )
            content = (resp.choices[0].message.content or "").strip()

            # Try parse directly
            try:
                obj = json.loads(content)
                if isinstance(obj, dict):
                    return obj
            except Exception:
                start = content.find("{")
                end = content.rfind("}")
                if start != -1 and end != -1 and end > start:
                    obj = json.loads(content[start:end + 1])
                    if isinstance(obj, dict):
                        return obj

            return {
                "verdict": "suspicious",
                "risk_score": 55,
                "evidence": [
                    {"signal": "decision_parse_failed", "why": "Decision step did not return valid JSON."}
                ],
            }

        except Exception as e:
            return {
                "verdict": "suspicious",
                "risk_score": 55,
                "evidence": [
                    {"signal": "decision_failed", "why": f"Decision step failed: {type(e).__name__}: {e}"}
                ],
            }