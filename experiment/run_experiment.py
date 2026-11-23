import csv
import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from groq import Groq

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from scanner.scanner import scan_code


load_dotenv(PROJECT_DIR / ".env")

PROMPTS_FILE = BASE_DIR / "prompts.json"
RESULTS_FILE = BASE_DIR / "results.csv"
RESPONSES_FILE = BASE_DIR / "responses.json"
PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
MODEL_NAME = (
    os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
    if PROVIDER == "groq"
    else os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
)


def load_prompts():
    with open(PROMPTS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def get_file_extension(prompt_id: int) -> str:
    if prompt_id in {8, 9}:
        return ".js"

    return ".py"


def create_client():
    env_name = "GROQ_API_KEY" if PROVIDER == "groq" else "GEMINI_API_KEY"
    api_key = os.getenv(env_name)

    if not api_key:
        raise RuntimeError(
            f"{env_name} is missing. Add it to the project .env file."
        )

    if PROVIDER == "groq":
        return Groq(api_key=api_key)

    return genai.Client(api_key=api_key)


def generate_code(client, prompt: dict, extension: str) -> str:
    language = "JavaScript" if extension == ".js" else "Python"
    request = (
        f"{prompt['prompt']}\n\n"
        f"Return only executable {language} source code. "
        "Do not include Markdown fences, explanations, or comments "
        "outside the code."
    )

    if PROVIDER == "groq":
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": request}],
        )
        response_text = response.choices[0].message.content or ""
    else:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=request,
        )
        response_text = response.text or ""

    generated_code = clean_generated_code(response_text)

    if not generated_code:
        raise RuntimeError(
            f"{PROVIDER} returned an empty response for prompt {prompt['id']}."
        )

    return generated_code


def clean_generated_code(code: str) -> str:
    """Remove accidental Markdown fences before scanning generated code."""
    cleaned = code.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return cleaned


def generate_with_retry(
    client,
    prompt: dict,
    extension: str,
    retries: int = 4,
) -> str:
    for attempt in range(retries):
        try:
            return generate_code(client, prompt, extension)
        except Exception as error:
            error_text = str(error)
            quota_exhausted = any(
                marker in error_text
                for marker in ("RESOURCE_EXHAUSTED", "free_tier_requests")
            )
            transient_error = any(
                marker in error_text
                for marker in ("429", "500", "502", "503", "504", "UNAVAILABLE")
            )

            if quota_exhausted or not transient_error or attempt == retries - 1:
                raise

            wait_seconds = 2 ** attempt
            print(
                f"Temporary {PROVIDER} error for prompt {prompt['id']}. "
                f"Retrying in {wait_seconds}s..."
            )
            time.sleep(wait_seconds)


def run_experiment():
    prompts = load_prompts()
    client = create_client()
    rows = []
    saved_responses = []

    for prompt in prompts:
        prompt_id = prompt["id"]
        category = prompt["category"]
        difficulty = prompt["difficulty"]
        extension = get_file_extension(prompt_id)
        language = "javascript" if extension == ".js" else "python"

        print(f"Generating response for prompt {prompt_id}...")

        try:
            generated_code = generate_with_retry(client, prompt, extension)
            scan_results = scan_code(generated_code, extension)
        except Exception as error:
            error_text = str(error).upper()
            if (
                "RESOURCE_EXHAUSTED" in error_text
                or "FREE_TIER_REQUESTS" in error_text
                or "RATE LIMIT" in error_text
                or "RATE_LIMIT" in error_text
                or "MODEL_NOT_FOUND" in error_text
            ):
                if "MODEL_NOT_FOUND" in error_text:
                    raise RuntimeError(
                        f"Groq model '{MODEL_NAME}' is unavailable. "
                        "Set GROQ_MODEL to a model listed by your Groq account."
                    ) from error
                raise RuntimeError(
                    f"{PROVIDER} quota is exhausted; stopping without writing partial results."
                ) from error
            print(f"Error scanning prompt {prompt_id}: {error}")
            continue

        saved_responses.append(
            {
                "prompt_id": prompt_id,
                "category": category,
                "difficulty": difficulty,
                "language": language,
                "model": MODEL_NAME,
                "prompt": prompt["prompt"],
                "response": generated_code,
            }
        )

        for result in scan_results:
            rows.append(
                {
                    "prompt_id": prompt_id,
                    "category": category,
                    "difficulty": difficulty,
                    "language": language,
                    "model": MODEL_NAME,
                    "package": result["package"],
                    "registry": result["registry"],
                    "exists": result["exists"],
                    "risk_score": result.get("risk_score", 0),
                    "risk_level": result.get(
                        "risk_level",
                        "UNKNOWN",
                    ),
                    "hallucinated": not result["exists"],
                }
            )

    save_results(rows)
    save_responses(saved_responses)

    print()
    print("Experiment complete.")
    print(f"Prompts processed: {len(saved_responses)}")
    print(f"Package results recorded: {len(rows)}")
    print(f"Results: {RESULTS_FILE}")
    print(f"Responses: {RESPONSES_FILE}")


def save_results(rows):
    fieldnames = [
        "prompt_id",
        "category",
        "difficulty",
        "language",
        "model",
        "package",
        "registry",
        "exists",
        "risk_score",
        "risk_level",
        "hallucinated",
    ]

    with open(
        RESULTS_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)


def save_responses(responses):
    with open(
        RESPONSES_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            responses,
            file,
            indent=2,
            ensure_ascii=False,
        )


if __name__ == "__main__":
    run_experiment()
