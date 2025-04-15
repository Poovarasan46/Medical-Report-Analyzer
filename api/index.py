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
@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    user_text = data.get("text", "")

    # Enhanced prompt to get detailed analysis, including patient and doctor information
    prompt = f"""
    You are an expert medical analyst with comprehensive knowledge of laboratory medicine, hematology, and gastroenterology. 

    If this is a follow-up question about a report you've already analyzed, refer to your previous analysis and focus on answering the specific question while maintaining consistency with your earlier findings.

    When analyzing a new blood report, consider:
    1. Identify the disease or condition the patient is suffering from.
    2. Extract and list any patient-related information such as name, age, gender, or other relevant details.
    3. Extract and list any doctor or healthcare professional information (name, specialization, etc.) present in the report.
    4. Identify any hospital or healthcare facility mentioned in the report.

    1. Complete Blood Count (CBC)
       - Anemia, Polycythemia
       - Leukemia, Infections
       - Thrombocytopenia, Thrombocytosis

    2. Liver function tests (ALT, AST, ALP, Bilirubin)
       - Hepatitis
       - Cirrhosis
       - Fatty Liver Disease
       - Cholestasis

    3. Pancreatic markers (Amylase, Lipase)
       - Pancreatitis
       - Pancreatic Cancer

    4. Metabolic Panel
       - Diabetes
       - Kidney Disease
       - Electrolyte Imbalances

    5. Lipid Profile
       - Hyperlipidemia
       - Atherosclerosis
       - Metabolic Syndrome

    6. Common Infections & Diseases
       - Bacterial Infections
       - Viral Infections
       - Thyroid Disorders
       - Autoimmune Conditions
       - Nutritional Deficiencies
       - Allergies
       - Inflammatory Conditions

    Based on the provided blood report, provide a single comprehensive analysis in the following format:

    - **Potential Health Risks:**
      - [List specific conditions the patient might be at risk for]
      - [Include risk level: Low/Medium/High]
      - [Supporting evidence from blood values]

    - **Recommendations:**
      - [Lifestyle modifications needed]
      - [Dietary recommendations]
      - [Follow-up tests required]
      - [Preventive measures]
      - [Urgency of medical consultation if needed]

    Note: Focus on early detection and prevention. Explain how current blood values might indicate future health risks and what can be done to prevent them.
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
