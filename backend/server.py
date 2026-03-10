from flask import Flask, request, jsonify
import requests

API_KEY = "AIzaSyCtsYDPJyW6BlxReImky8xJA7g8xH3A1es"

app = Flask(__name__)


# =========================
# Helper: clean AI output
# =========================

def clean_code(text: str) -> str:
    if not text:
        return ""

    text = text.strip()

    if "```" in text:
        parts = text.split("```")
        for p in parts:
            if "\n" in p:
                text = p
                break

    text = text.replace("```", "").strip()

    lines = text.splitlines()

    if len(lines) > 1:
        first = lines[0].strip().lower()

        if first.isalpha() and len(first) < 12:
            text = "\n".join(lines[1:])

    return text.strip()


# =========================
# FIX
# =========================

@app.route("/fix", methods=["POST"])
def fix():

    data = request.json
    code = data.get("code", "")

    prompt = f"""
You are an expert Python debugger.

Fix all errors in the code.
Return FULL corrected code.
Make sure code runs without errors.

Broken code:
{code}

Correct code:
"""

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-2.5-flash:generateContent?key=" + API_KEY
    )

    body = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0,
            "maxOutputTokens": 2048,
            "responseMimeType": "text/plain"
        }
    }

    r = requests.post(url, json=body)
    result = r.json()
    print("GEMINI RESPONSE:", result)
    try:
        text = result["candidates"][0]["content"]["parts"][0]["text"]
    except:
        text = code

    text = clean_code(text)

    return jsonify({"fixed": text})


# =========================
# REVERSE DEBUG
# =========================

@app.route("/reverse", methods=["POST"])
def reverse():

    data = request.json

    code = data.get("code", "")
    expected = data.get("expected", "")

    prompt = f"""
Expected output:
{expected}

Fix the code and explain.

Code:
{code}

Return:

FIXED:
<code>

EXPLANATION:
<text>
"""

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-2.5-flash:generateContent?key=" + API_KEY
    )

    body = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 2048
        }
    }

    r = requests.post(url, json=body)
    result = r.json()

    try:
        text = result["candidates"][0]["content"]["parts"][0]["text"]
    except:
        text = ""

    fixed = ""
    explanation = ""

    if "EXPLANATION:" in text:
        parts = text.split("EXPLANATION:")
        fixed = parts[0].replace("FIXED:", "").strip()
        explanation = parts[1].strip()
    else:
        fixed = text.strip()

    fixed = clean_code(fixed)

    return jsonify({
        "fixed": fixed,
        "explanation": explanation
    })


# =========================
# EXPLAIN
# =========================

@app.route("/explain", methods=["POST"])
def explain():

    data = request.json

    code = data.get("code", "")
    error = data.get("error", "")

    prompt = f"""
Explain the code.

Format:

Code Status:
Mistake:
Correction:
What code does:

Code:
{code}

Error:
{error}
"""

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        "gemini-2.5-flash:generateContent?key=" + API_KEY
    )

    body = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 2048
        }
    }

    r = requests.post(url, json=body)
    result = r.json()

    try:
        text = result["candidates"][0]["content"]["parts"][0]["text"]
    except:
        text = ""

    return jsonify({
        "explanation": text.strip()
    })


# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)