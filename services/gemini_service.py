import os
import json
import google.generativeai as genai

from dotenv import load_dotenv

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    os.getenv(
        "GEMINI_MODEL",
        "gemini-2.5-flash"
    )
)


def analyze_symptoms(symptoms):

    prompt = f"""
You are an expert hospital triage AI.

Analyze the following symptoms:

{symptoms}

Return ONLY valid JSON.

{{
    "urgency": "Critical | High | Medium | Low",
    "department": "",
    "priority_score": "",
    "estimated_wait": "",
    "explanation": ""
}}

Return ONLY JSON.
"""

    try:

        response = model.generate_content(
            prompt
        )

        text = response.text.strip()

        print("\n========== GEMINI RAW RESPONSE ==========")
        print(text)
        print("=========================================\n")

        text = text.replace(
            "```json",
            ""
        )

        text = text.replace(
            "```",
            ""
        )

        text = text.strip()

        result = json.loads(text)

        print("\n========== PARSED JSON ==========")
        print(result)
        print("=================================\n")

        return result

    except Exception as e:

        print("\n========== GEMINI ERROR ==========")
        print(str(e))
        print("==================================\n")

        return {
            "urgency": "Medium",
            "department": "General Medicine",
            "priority_score": "50",
            "estimated_wait": "20 Minutes",
            "explanation": f"AI analysis unavailable: {str(e)}"
        }