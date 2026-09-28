import os
import json
from supabase import create_client, Client
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

# Find the templates folder relative to this script's directory in the cloud
current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, "templates")

app = Flask(__name__, template_folder=template_dir)

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/verify", methods=["POST"])
def verify_medication():
    data = request.get_json()

    # Check that all required data was received
    if (
        not data
        or "staffId" not in data
        or "medImage" not in data
        or "labelImage" not in data
    ):
        return jsonify(
            {
                "error": "Staff ID, medication image, and prescription label image are required."
            }
        ), 400

    staff_id = data["staffId"]

    try:
        # Extract only the Base64 image data
        med_image_clean = data["medImage"].split(",")[1]
        label_image_clean = data["labelImage"].split(",")[1]
    except (IndexError, AttributeError):
        return jsonify({"error": "Invalid image format received."}), 400

    # Ask the AI to return a predictable JSON structure
    prompt = """
You are a strict medication verification assistant.

You have been provided with two images:

Image 1:
The physical medication box or bottle.

Image 2:
The prescription or cartfill label.

Your task is to carefully compare the medication information visible in the two images.

Extract the following information:

1. Medication name from Image 1
2. Medication strength from Image 1
3. Medication name from Image 2
4. Medication strength from Image 2
5. Whether the medication name AND strength match
6. Your confidence in the comparison
7. A short explanation for your conclusion

IMPORTANT SAFETY RULES:

- Only use information that is actually visible in the images.
- Do not guess missing information.
- If text is unclear or unreadable, say so.
- If either medication name or strength cannot be reliably identified, set "match" to false.
- Do not assume that two medications match just because they look similar.
- The medication name and strength must both correspond for a MATCH.
- This is an AI verification aid and not a replacement for professional clinical verification.

Return ONLY valid JSON in exactly this structure:

{
  "medication_name": "string or Unknown",
  "medication_strength": "string or Unknown",
  "label_name": "string or Unknown",
  "label_strength": "string or Unknown",
  "match": true,
  "confidence": "high, medium, or low",
  "reason": "short explanation"
}

Do not include Markdown.
Do not include ```json.
Do not include any text outside the JSON object.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{med_image_clean}"
                            },
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{label_image_clean}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=300,
        )

        # Get the AI's response
        raw_result = response.choices[0].message.content

        # Convert the AI's JSON response into a Python dictionary
        try:
            result = json.loads(raw_result)

        except json.JSONDecodeError:
            # If the AI returned something other than valid JSON,
            # return the raw response so we can diagnose the problem.
            return jsonify(
                {
                    "error": "The AI returned an invalid response format.",
                    "raw_response": raw_result,
                }
            ), 500

        # Add Staff ID to the structured result
        result["staff_id"] = staff_id

        # Return structured verification result
        return jsonify(
            {
                "result": result
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Expose app for Vercel WSGI
app.debug = True
handler = app
