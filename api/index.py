import os
import base64
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

# By moving 'templates' inside the 'api' folder, Flask finds it automatically
app = Flask(__name__)

def get_openai_client():
    """Safely initializes the OpenAI client when a request is made."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is missing on Vercel dashboard.")
    return OpenAI(api_key=api_key.strip())

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/verify', methods=['POST'])
def verify_medication():
    data = request.get_json()
    if not data or 'medImage' not in data or 'labelImage' not in data:
        return jsonify({'error': 'Both images are required'}), 400

    try:
        # Securely parse base64 image streams 
        med_image_data = data['medImage'].split(',')[1]
        label_image_data = data['labelImage'].split(',')[1]
    except IndexError:
        return jsonify({'error': 'Invalid image format received'}), 400

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
        client = get_openai_client()
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

# Expose global app handler mapping for Vercel
app.debug = True
handler = app
