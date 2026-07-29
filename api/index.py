from __future__ import annotations

import json
import os
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

app = Flask(__name__, template_folder="../templates")
CORS(app)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_MODEL = os.getenv("GROQ_MODEL", "").strip() or DEFAULT_GROQ_MODEL
MAX_REPORT_CHARS = int(os.getenv("MAX_REPORT_CHARS", "45000"))
REQUEST_TIMEOUT_SECONDS = int(os.getenv("GROQ_TIMEOUT_SECONDS", "70"))
MAX_COMPLETION_TOKENS = int(os.getenv("GROQ_MAX_COMPLETION_TOKENS", "4096"))
STRICT_SCHEMA_MODELS = {"openai/gpt-oss-20b", "openai/gpt-oss-120b"}


ANALYSIS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "summary",
        "patient",
        "provider",
        "key_findings",
        "possible_concerns",
        "recommendations",
        "urgent_flags",
        "follow_up_questions",
        "safety_note",
    ],
    "properties": {
        "summary": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "report_type",
                "overall_assessment",
                "confidence",
                "data_quality",
            ],
            "properties": {
                "report_type": {"type": "string"},
                "overall_assessment": {"type": "string"},
                "confidence": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "unknown"],
                },
                "data_quality": {"type": "string"},
            },
        },
        "patient": {
            "type": "object",
            "additionalProperties": False,
            "required": ["name", "age", "gender", "patient_id", "collected_at", "reported_at"],
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "string"},
                "gender": {"type": "string"},
                "patient_id": {"type": "string"},
                "collected_at": {"type": "string"},
                "reported_at": {"type": "string"},
            },
        },
        "provider": {
            "type": "object",
            "additionalProperties": False,
            "required": ["doctor", "facility", "lab", "location"],
            "properties": {
                "doctor": {"type": "string"},
                "facility": {"type": "string"},
                "lab": {"type": "string"},
                "location": {"type": "string"},
            },
        },
        "key_findings": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "test",
                    "value",
                    "unit",
                    "reference_range",
                    "status",
                    "evidence",
                    "plain_language_meaning",
                ],
                "properties": {
                    "test": {"type": "string"},
                    "value": {"type": "string"},
                    "unit": {"type": "string"},
                    "reference_range": {"type": "string"},
                    "status": {
                        "type": "string",
                        "enum": ["low", "normal", "high", "critical", "unknown"],
                    },
                    "evidence": {"type": "string"},
                    "plain_language_meaning": {"type": "string"},
                },
            },
        },
        "possible_concerns": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["issue", "risk_level", "evidence", "what_to_discuss"],
                "properties": {
                    "issue": {"type": "string"},
                    "risk_level": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "unknown"],
                    },
                    "evidence": {"type": "string"},
                    "what_to_discuss": {"type": "string"},
                },
            },
        },
        "recommendations": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["priority", "category", "recommendation", "reason"],
                "properties": {
                    "priority": {
                        "type": "string",
                        "enum": ["routine", "soon", "urgent", "unknown"],
                    },
                    "category": {"type": "string"},
                    "recommendation": {"type": "string"},
                    "reason": {"type": "string"},
                },
            },
        },
        "urgent_flags": {
            "type": "array",
            "items": {"type": "string"},
        },
        "follow_up_questions": {
            "type": "array",
            "items": {"type": "string"},
        },
        "safety_note": {"type": "string"},
    },
}


EMPTY_ANALYSIS: dict[str, Any] = {
    "summary": {
        "report_type": "Unknown",
        "overall_assessment": "The report could not be analyzed completely.",
        "confidence": "unknown",
        "data_quality": "No data quality assessment available.",
    },
    "patient": {
        "name": "",
        "age": "",
        "gender": "",
        "patient_id": "",
        "collected_at": "",
        "reported_at": "",
    },
    "provider": {
        "doctor": "",
        "facility": "",
        "lab": "",
        "location": "",
    },
    "key_findings": [],
    "possible_concerns": [],
    "recommendations": [],
    "urgent_flags": [],
    "follow_up_questions": [],
    "safety_note": (
        "This AI summary is informational and is not a diagnosis. "
        "Please review the report with a qualified healthcare professional."
    ),
}


SYSTEM_PROMPT = """
You are a careful medical report analysis assistant for lab and diagnostic reports.

Your job:
- Extract patient, provider, report, and lab-test information from the supplied text.
- Identify notable abnormal or clinically relevant values using the value, unit, and reference range in the report.
- Explain possible concerns in cautious language.
- Produce practical follow-up recommendations that a patient can discuss with a clinician.

Safety and accuracy rules:
- Use only information present in the report text. Do not invent patient details, diagnoses, symptoms, dates, or medications.
- Do not claim a definitive diagnosis unless the report itself states it.
- If a value has no reference range, say the status is "unknown" unless the report explicitly marks it abnormal.
- Preserve numeric values, units, and reference ranges exactly as written when possible.
- Separate evidence from interpretation. Every concern must cite the report evidence behind it.
- If the text is incomplete, garbled, scanned poorly, or not a medical report, say so in data_quality and keep confidence low.
- Keep explanations patient-friendly, concise, and medically cautious.
- Return JSON only. No markdown, no code fences, no commentary outside JSON.
"""


RESPONSE_SHAPE_PROMPT = """
Return exactly this JSON shape. Use empty strings or empty arrays when information is missing:
{
  "summary": {
    "report_type": "string",
    "overall_assessment": "string",
    "confidence": "low|medium|high|unknown",
    "data_quality": "string"
  },
  "patient": {
    "name": "string",
    "age": "string",
    "gender": "string",
    "patient_id": "string",
    "collected_at": "string",
    "reported_at": "string"
  },
  "provider": {
    "doctor": "string",
    "facility": "string",
    "lab": "string",
    "location": "string"
  },
  "key_findings": [
    {
      "test": "string",
      "value": "string",
      "unit": "string",
      "reference_range": "string",
      "status": "low|normal|high|critical|unknown",
      "evidence": "string",
      "plain_language_meaning": "string"
    }
  ],
  "possible_concerns": [
    {
      "issue": "string",
      "risk_level": "low|medium|high|unknown",
      "evidence": "string",
      "what_to_discuss": "string"
    }
  ],
  "recommendations": [
    {
      "priority": "routine|soon|urgent|unknown",
      "category": "string",
      "recommendation": "string",
      "reason": "string"
    }
  ],
  "urgent_flags": ["string"],
  "follow_up_questions": ["string"],
  "safety_note": "string"
}
"""


class GroqAPIError(Exception):
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return jsonify(
        {
            "ok": True,
            "model": GROQ_MODEL,
            "groq_key_configured": bool(GROQ_API_KEY),
        }
    )


@app.route("/api/analyze", methods=["POST"])
def analyze():
    try:
        print("\n========== /api/analyze ==========")

        data = request.get_json(force=True)

        report_text = normalize_report_text(data.get("text", ""))

        print("Report length:", len(report_text))

        if not report_text:
            return jsonify({
                "error": "No readable report text received."
            }), 400

        if not GROQ_API_KEY:
            return jsonify({
                "error": "Groq API key missing."
            }), 500

        if len(report_text) > MAX_REPORT_CHARS:
            report_text = report_text[:MAX_REPORT_CHARS]
            truncated = True
        else:
            truncated = False

        analysis = analyze_report_with_groq(report_text)

        return jsonify({
            "analysis": analysis,
            "model": GROQ_MODEL,
            "truncated": truncated,
            "max_report_chars": MAX_REPORT_CHARS
        })

    except Exception as e:
        import traceback
        traceback.print_exc()

        return jsonify({
            "error": str(e)
        }), 500


def analyze_report_with_groq(report_text):

    print("Preparing request...")

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content":
                RESPONSE_SHAPE_PROMPT +
                "\n\nREPORT TEXT:\n" +
                report_text
        }
    ]

    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.1,
        "max_completion_tokens": MAX_COMPLETION_TOKENS
    }

    print("Sending request to Groq...")

    result = create_chat_completion(payload)

    print("Response received.")

    content = result["choices"][0]["message"]["content"]

    print(content[:300])

    parsed = parse_json_response(content)

    return normalize_analysis(parsed)


def build_response_format(model: str) -> dict[str, Any]:
    if model in STRICT_SCHEMA_MODELS:
        return {
            "type": "json_schema",
            "json_schema": {
                "name": "medical_report_analysis",
                "strict": True,
                "schema": ANALYSIS_SCHEMA,
            },
        }

    return {"type": "json_object"}


def create_chat_completion(payload):

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    print("Calling Groq...")

    response = requests.post(
        GROQ_API_URL,
        headers=headers,
        json=payload,
        timeout=70
    )

    print("Status:", response.status_code)

    print(response.text[:1000])

    if response.status_code != 200:
        raise Exception(response.text)

    return response.json()

def extract_groq_error(response: requests.Response) -> str:
    try:
        body = response.json()
    except ValueError:
        return f"AI service error ({response.status_code})."

    message = body.get("error", {}).get("message") or body.get("message")
    if message:
        return f"AI service error: {message}"

    return f"AI service error ({response.status_code})."


def normalize_report_text(value: Any) -> str:
    if not isinstance(value, str):
        return ""

    text = value.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_json_response(content: str) -> dict[str, Any]:
    if not content:
        raise GroqAPIError("The AI service returned an empty response.", 502)

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, flags=re.DOTALL)
        if not match:
            raise GroqAPIError("The AI service returned an unreadable response.", 502)
        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise GroqAPIError("The AI service returned malformed JSON.", 502) from exc

    if not isinstance(parsed, dict):
        raise GroqAPIError("The AI service returned an invalid response shape.", 502)

    return parsed


def normalize_analysis(raw: dict[str, Any]) -> dict[str, Any]:
    analysis = deepcopy(EMPTY_ANALYSIS)

    merge_object(analysis["summary"], raw.get("summary"))
    merge_object(analysis["patient"], raw.get("patient"))
    merge_object(analysis["provider"], raw.get("provider"))

    analysis["key_findings"] = normalize_list(raw.get("key_findings"))
    analysis["possible_concerns"] = normalize_list(raw.get("possible_concerns"))
    analysis["recommendations"] = normalize_list(raw.get("recommendations"))
    analysis["urgent_flags"] = normalize_string_list(raw.get("urgent_flags"))
    analysis["follow_up_questions"] = normalize_string_list(raw.get("follow_up_questions"))

    safety_note = raw.get("safety_note")
    if isinstance(safety_note, str) and safety_note.strip():
        analysis["safety_note"] = safety_note.strip()

    return analysis


def merge_object(target: dict[str, Any], source: Any) -> None:
    if not isinstance(source, dict):
        return

    for key in target:
        value = source.get(key)
        if isinstance(value, str):
            target[key] = value.strip()


def normalize_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []

    return [item for item in value if isinstance(item, dict)]


def normalize_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []

    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
    )
