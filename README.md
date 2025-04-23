# AI Resume Generator

An AI-powered resume generator that creates professional, ATS-friendly resumes in minutes. Built with Flask, Gemini AI, and Razorpay for payments.

## Features

- AI-generated professional resume content
- ATS-friendly formatting
- Instant PDF download
- Mobile-friendly interface
- Secure payment integration with Razorpay
- Multiple pricing tiers

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **AI**: Gemini API
- **PDF Generation**: PDFKit
- **Payment Processing**: Razorpay
- **Deployment**: Render/Replit (recommended)

## Setup Instructions

### Prerequisites

- Python 3.7+
- pip (Python package installer)
- wkhtmltopdf (for PDF generation)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ai-resume-generator.git
   cd ai-resume-generator
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Install wkhtmltopdf:
   - **Windows**: Download from https://wkhtmltopdf.org/downloads.html
   - **macOS**: `brew install wkhtmltopdf`
   - **Ubuntu/Debian**: `sudo apt-get install wkhtmltopdf`

5. Create a `.env` file by copying `.env.example`:
   ```
   cp .env.example .env
   ```

6. Update the `.env` file with your API keys:
   - Get a Gemini API key from [Google AI Studio](https://ai.google.dev/)
   - Get Razorpay keys from the [Razorpay Dashboard](https://dashboard.razorpay.com/)

### Running the Application

```
python app.py
```

Visit `http://127.0.0.1:5000` in your browser.

## Deployment

### Deploying to Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Use the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
4. Add environment variables from your `.env` file

### Deploying to Replit

1. Create a new Repl and import from GitHub
2. Add the environment variables in the Secrets tab
3. Run the application using the Run button

## Monetization Strategy

- **Free Tier**: Preview-only
- **Basic Tier (₹49)**: Download 1 PDF resume
- **Pro Tier (₹99)**: 3 resume variants + cover letter
- **Premium Tier (₹199)**: 1-on-1 feedback + resume optimization

## Marketing Ideas

- WhatsApp groups for college students
- LinkedIn posts showcasing the tool
- Instagram reels demonstrating the resume creation process
- Campus ambassador/referral program

## License

[MIT License](LICENSE)

## Contact

For support or business inquiries, please contact support@resumeai.com 