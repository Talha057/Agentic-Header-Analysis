import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class ModelRoute:
    name: str           
    model_id: str | None 

def get_routes():
    # ChatGPT model for navigation + critical decisions
    chatgpt_model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    return {
        "NAVIGATION": ModelRoute("chatgpt", chatgpt_model),
        "CRITICAL_DECISION": ModelRoute("chatgpt", chatgpt_model),
        "DEFAULT": ModelRoute("opensource", None),
    }
