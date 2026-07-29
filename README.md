# Medical Report Analyzer

Medical Report Analyzer is a Flask web app that reads text from an uploaded medical PDF and sends it to Groq for a structured AI summary. The result is organized into patient details, provider details, key findings, possible concerns, recommended next steps, urgent flags, and questions to discuss with a clinician.

This tool is informational only. It is not a diagnosis and should not replace professional medical advice.

## Features

- Upload a text-based medical report PDF up to 20MB
- Extract selectable PDF text in the browser with PDF.js
- Analyze report text with Groq's OpenAI-compatible chat API
- Return structured JSON instead of free-form markdown
- Highlight key lab findings with values, units, reference ranges, status, evidence, and plain-language meaning
- Separate possible concerns from evidence to reduce overconfident diagnosis-style output
- Provide follow-up recommendations, urgent flags, and clinician questions
- Render results safely without injecting model output as raw HTML

## Demo

https://github.com/user-attachments/assets/6c51a9fd-2e67-424f-adb8-789034575fbd

## Project Structure

```text
Medical-Report-Analyzer/
|-- api/
|   `-- index.py
|-- templates/
|   `-- index.html
|-- requirements.txt
|-- vercel.json
|-- .gitignore
`-- README.md
```

## Local Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
```

`GROQ_MODEL` is optional. If it is not set, the app uses `llama-3.3-70b-versatile`.

Run the app:

```bash
python api/index.py
```

Open:

```text
http://127.0.0.1:5000
```

## Vercel Environment Variables

Set these in the Vercel project settings:

- `GROQ_API_KEY` - required
- `GROQ_MODEL` - optional
- `MAX_REPORT_CHARS` - optional, defaults to `45000`
- `GROQ_TIMEOUT_SECONDS` - optional, defaults to `70`
- `GROQ_MAX_COMPLETION_TOKENS` - optional, defaults to `4096`

## Deployment

1. Push the latest code to GitHub.
2. Import the GitHub repository into Vercel.
3. Add the environment variables above in Vercel project settings.
4. Deploy from the `main` branch.

## Notes

- Scanned PDFs need OCR before analysis because the browser extractor only reads selectable text.
- Very long reports are truncated on the server using `MAX_REPORT_CHARS`.
- The app uses strict JSON schema mode for Groq models that support it, and JSON object mode for broader model compatibility.
- The server normalizes missing sections before sending data to the UI.
