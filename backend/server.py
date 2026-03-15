from flask import Flask, request, jsonify
import requests

API_KEY = ""

app = Flask(__name__)


#  CLEAN 

def clean_code(text: str):

    if not text:
        return ""

    text = text.replace("```python", "")
    text = text.replace("```", "")

    lines = text.splitlines()

    cleaned = []

    for line in lines:

        l = line.strip()

        if l.startswith("* "):
            l = l[2:]

        if "**" in l:
            if " ** " not in l:
                l = l.replace("**", "")

        cleaned.append(l)

    return "\n".join(cleaned).strip()


#  GEMINI 

def call_gemini(prompt):

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
            "maxOutputTokens": 4096
        }
    }

    r = requests.post(url, json=body)

    try:
        result = r.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except:
        print(r.text)
        return ""


#  FIX 

@app.route("/fix", methods=["POST"])
def fix():

    code = request.json.get("code", "")

    prompt = f"""
Fix python code.

Return only code.

Code:
{code}
"""

    text = call_gemini(prompt)

    text = clean_code(text)

    return jsonify({"result": text})


#  REVERSE 

@app.route("/reverse", methods=["POST"])
def reverse():

    data = request.json

    code = data.get("code", "")
    expected = data.get("expected", "")

    prompt = f"""
Fix code and explain.

Expected: {expected}

Code:
{code}

Return format:

FIXED:
code

EXPLANATION:
text
"""

    text = call_gemini(prompt)

    fixed = ""
    explanation = ""

    if "FIXED:" in text:

        rest = text.split("FIXED:")[1]

        if "EXPLANATION:" in rest:

            parts = rest.split("EXPLANATION:")

            fixed = parts[0].strip()
            explanation = parts[1].strip()

        else:
            fixed = rest.strip()

    fixed = clean_code(fixed)

    return jsonify({
        "fixed": fixed,
        "explanation": explanation
    })


#  EXPLAIN

@app.route("/explain", methods=["POST"])
def explain():

    code = request.json.get("code", "")

    prompt = f"""
Explain python code.

Code:
{code}
"""

    text = call_gemini(prompt)

    text = clean_code(text)

    return jsonify({
        "explanation": text
    })



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)