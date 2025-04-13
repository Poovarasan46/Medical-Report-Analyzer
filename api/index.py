from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__, template_folder='../templates')
CORS(app)

# Securely get API key from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Serve the frontend
@app.route("/")
def home():
    return render_template("index.html")

# Handle analysis request
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    user_text = data.get("text", "")

    # Enhanced prompt to get detailed analysis, including patient and doctor information
    prompt = f"""
    You are a helpful medical assistant. Analyze the following medical report and provide a detailed analysis, including the following:
    1. Identify the disease or condition the patient is suffering from.
    2. Extract and list any patient-related information such as name, age, gender, or other relevant details.
    3. Extract and list any doctor or healthcare professional information (name, specialization, etc.) present in the report.
    4. Identify any hospital or healthcare facility mentioned in the report.
    5. Provide a clear, easy-to-understand explanation of the disease or condition.
    6. Offer specific instructions or recommendations for the patient to manage or treat the condition, including lifestyle changes, medications, additional tests, or further actions.
    7. Summarize the next steps for the patient to take in terms of follow-up appointments or additional care needed.

    Medical Report:
    {user_text}
    """

    # Send request to Groq's LLM with enhanced instructions
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system", "content": prompt}
            ]
        }
    )

    try:
        result = response.json()
        return jsonify({"response": result["choices"][0]["message"]["content"]})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
