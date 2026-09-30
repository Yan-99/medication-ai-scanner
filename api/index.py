import os
import json
from supabase import create_client, Client
from flask import Flask, render_template, request, jsonify
from openai import OpenAI


current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, "templates")

app = Flask(__name__, template_folder=template_dir)


# ============================================================
# OPENAI CONFIGURATION
# ============================================================

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()

client = OpenAI(
    api_key=OPENAI_API_KEY
)


# ============================================================
# SUPABASE CONFIGURATION
# ============================================================

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "").strip()

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():
    return render_template("index.html")


# ============================================================
# MEDICATION VERIFICATION
# ============================================================

@app.route("/verify", methods=["POST"])
def verify_medication():

    data = request.get_json()

    # --------------------------------------------------------
    # Validate request
    # --------------------------------------------------------

    if (
        not data
        or "staffId" not in data
        or "medImage" not in data
        or "labelImage" not in data
    ):
        return jsonify({
            "error": "Staff ID, medication image, and prescription label image are required."
        }), 400

    staff_id = data["staffId"]


    # --------------------------------------------------------
    # Extract Base64 image data
    # --------------------------------------------------------

    try:

        med_image_clean = data["medImage"].split(",")[1]
        label_image_clean = data["labelImage"].split(",")[1]

    except (IndexError, AttributeError):

        return jsonify({
            "error": "Invalid image format received."
        }), 400


    # ========================================================
    # AI VERIFICATION PROMPT
    # ========================================================

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


    # ========================================================
    # CALL OPENAI
    # ========================================================

    try:

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [

                        {
                            "type": "text",
                            "text": prompt
                        },

                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{med_image_clean}"
                            }
                        },

                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{label_image_clean}"
                            }
                        }

                    ]
                }
            ],
            max_tokens=300
        )


        raw_result = response.choices[0].message.content


        # ----------------------------------------------------
        # Parse AI JSON
        # ----------------------------------------------------

        try:

            result = json.loads(raw_result)

        except json.JSONDecodeError:

            print(
                "Invalid AI JSON response:",
                raw_result
            )

            return jsonify({
                "error": "The AI returned an invalid response format.",
                "raw_response": raw_result
            }), 500


        # ====================================================
        # SAVE AUDIT RECORD TO SUPABASE
        # ====================================================

        record = {
            "staff_id": staff_id,

            "medication_name": result.get(
                "medication_name"
            ),

            "medication_strength": result.get(
                "medication_strength"
            ),

            "label_name": result.get(
                "label_name"
            ),

            "label_strength": result.get(
                "label_strength"
            ),

            "match": result.get(
                "match"
            ),

            "confidence": result.get(
                "confidence"
            ),

            "reason": result.get(
                "reason"
            )
        }


        # ----------------------------------------------------
        # Insert audit record
        # ----------------------------------------------------

        try:

            supabase_response = (
                supabase
                .table("scan_records")
                .insert(record)
                .execute()
            )


            print(
                "Supabase insert successful:",
                supabase_response.data
            )


        except Exception as db_error:

            print(
                "Supabase database error type:",
                type(db_error).__name__
            )

            print(
                "Supabase database error:",
                repr(db_error)
            )

            return jsonify({
                "error": "Verification succeeded, but the audit record could not be saved."
            }), 500


        # ====================================================
        # RETURN RESULT TO FRONTEND
        # ====================================================

        result["staff_id"] = staff_id

        return jsonify({
            "result": result
        })


    except Exception as e:

        print(
            "Verification error:",
            repr(e)
        )

        return jsonify({
            "error": "An error occurred during medication verification."
        }), 500


# ============================================================
# SCAN HISTORY
# ============================================================

@app.route("/history", methods=["GET"])
def scan_history():

    try:

        # Retrieve scan records from Supabase
        response = (
            supabase
            .table("scan_records")
            .select("*")
            .order("created_at", desc=True)
            .limit(100)
            .execute()
        )

        return jsonify({
            "records": response.data
        })

    except Exception as e:

        print(
            "Scan history error:",
            repr(e)
        )

        return jsonify({
            "error": "Unable to retrieve scan history."
        }), 500

# ============================================================
# SCANNING PRODUCT BARCODE/QR & MED LABEL BARCODE VERIFICATION
# ============================================================

@app.route("/")
def qr_page():
    return render_template("qr.html")

# ============================================================
# VERCEL HANDLER
# ============================================================

app.debug = True

handler = app