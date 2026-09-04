# Medical Report Analyzer

Medical Report Analyzer is a Flask web app that extracts text from uploaded medical PDF reports and uses **Google Gemini** (`gemini-3.6-flash`) via the official `google-genai` SDK to generate structured, clinical summaries. The result is organized into patient details, provider details, key findings, possible concerns, recommended next steps, urgent flags, and questions to discuss with a healthcare professional.

> **Disclaimer**: This tool is for informational and educational purposes only. It does not provide medical diagnoses and should never replace professional clinical evaluation or advice.

---

## Features

- **PDF Text Extraction**: Extracts selectable text directly in the browser with PDF.js (supporting PDFs up to 20MB).
- **Google Gemini Integration**: Uses Google's modern `google-genai` SDK and the free, high-performance `gemini-3.6-flash` model.
- **Strict Structured JSON Schema**: Returns typed JSON matching an exact clinical analysis schema rather than unpredictable raw markdown.
- **Key Lab & Clinical Findings**: Details values, units, reference ranges, status (normal/abnormal), evidence, and plain-language interpretations.
- **Evidence-Based Concerns**: Distinguishes tentative concerns from explicit clinical evidence to prevent overconfident conclusions.
- **Actionable Next Steps**: Outlines follow-up recommendations, urgent flags, and clinician discussion points.
- **Safe Rendering**: Sanitized rendering prevents XSS vulnerabilities and raw HTML injection.
- **Vercel Ready**: Optimized for serverless deployment with customized 60-second function timeout for AI analysis.

---

## Demo

https://github.com/user-attachments/assets/20ccc0cb-99c8-4a27-ad1a-84dcc2897810

---

## Project Structure

```text
Medical-Report-Analyzer/
|-- api/
|   `-- index.py          # Flask backend & Gemini API integration
|-- templates/
|   `-- index.html        # Responsive frontend with PDF.js & UI
|-- requirements.txt      # Python dependencies (google-genai, Flask, etc.)
|-- vercel.json           # Vercel serverless configuration & 60s timeout
|-- .gitignore
`-- README.md
```

---

## Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/Poovarasan46/Medical-Report-Analyzer.git
cd Medical-Report-Analyzer
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.6-flash
```

> **Note**: Get a free API key at [Google AI Studio](https://aistudio.google.com/app/apikey). `GEMINI_MODEL` is optional and defaults to `gemini-3.6-flash`.

### 4. Run the application
```bash
python api/index.py
```

Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## Vercel Deployment

### 1. Environment Variables in Vercel
In your Vercel project dashboard under **Settings** > **Environment Variables**, add:

| Variable | Required | Default | Description |
| :--- | :---: | :---: | :--- |
| `GEMINI_API_KEY` | **Yes** | — | Your API key from Google AI Studio |
| `GEMINI_MODEL` | No | `gemini-3.6-flash` | The Gemini model to use |
| `MAX_REPORT_CHARS` | No | `45000` | Max characters sent to the model |
| `GEMINI_MAX_COMPLETION_TOKENS` | No | `8192` | Max token response length |

### 2. Deployment Steps
1. Push your repository to GitHub.
2. Import the repository into [Vercel](https://vercel.com).
3. Add the `GEMINI_API_KEY` in **Environment Variables**.
4. Deploy from the `main` branch.

---

## Notes & Limitations

- **Text-based PDFs only**: Scanned documents or image-only PDFs require OCR prior to analysis, as browser-based PDF.js extracts digital text.
- **Report Size**: Reports exceeding `MAX_REPORT_CHARS` (45,000 characters) are safely truncated to remain within token limits.
- **Resilient Fallback**: The backend automatically normalizes missing or partial schema fields before returning the response to the user.
