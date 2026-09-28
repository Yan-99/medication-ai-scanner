import os
import base64
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

app = Flask(__name__, template_folder='../templates')

# For cloud hosting like Vercel, we read the key from the system environment
# You will paste this key securely into the Vercel Dashboard settings later!
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/verify', methods=['POST'])
def verify_medication():
    data = request.get_json()
    if not data or 'medImage' not in data or 'labelImage' not in data:
        return jsonify({'error': 'Both images are required'}), 400

    med_image_data = data['medImage'].split(',')[1]
    label_image_data = data['labelImage'].split(',')[1]

    prompt = (
        "You are a strict medical safety assistant. You have been provided two images.\n"
        "Image 1: The physical pill bottle or box.\n"
        "Image 2: The prescription or cartfill label.\n\n"
        "Please perform the following tasks:\n"
        "1. Identify the medication name and strength from Image 1.\n"
        "2. Identify the medication name and strength from Image 2.\n"
        "3. Compare them and state clearly if they MATCH or DO NOT MATCH.\n"
        "Provide your answer in a clear, easy-to-read format."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{med_image_data}"}},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{label_image_data}"}}
                    ]
                }
            ],
            max_tokens=300
        )
        return jsonify({'result': response.choices[0].message.content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Required for Vercel serverless execution
app.debug = True
handler = app