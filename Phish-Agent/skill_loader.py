from pathlib import Path

SKILLS_DIR = Path("skills")

def load_skill(skill_filename: str) -> str:
    path = SKILLS_DIR / skill_filename
    if not path.exists():
        raise FileNotFoundError(f"Skill not found: {path.resolve()}")
    return path.read_text(encoding="utf-8")
