import sys
import asyncio
from orchestrator import PhishOrchestrator, OrchestratorConfig
from utils import safe_json_dump

async def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <url> [brand]")
        sys.exit(2)

    url = sys.argv[1].strip()
    brand = sys.argv[2].strip() if len(sys.argv) >= 3 else ""

    orch = PhishOrchestrator(
        OrchestratorConfig(
            max_steps=25,
            safe_mode=True,
            no_credentials=True,
            no_form_submit=True,
        )
    )

    report = await orch.run(url, brand_expected=brand)

    # Print JSON to stdout (so docker logs show the result)
    print(safe_json_dump(report))

if __name__ == "__main__":
    asyncio.run(main())
