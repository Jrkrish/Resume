import os
import json
import secrets
import logging
import random
import re
import uuid
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, Response, send_file
from dotenv import load_dotenv
import google.generativeai as genai
import razorpay
import pdfkit
from flask_debugtoolbar import DebugToolbarExtension
from datetime import datetime
import time
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

# Configure server-side session to handle large data
os.makedirs('flask_session', exist_ok=True)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = 'flask_session'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True

try:
    from flask_session import Session
    Session(app)
    print("Using server-side session storage")
except ImportError:
    print("flask_session not installed, falling back to cookie sessions")
    print("To install: pip install flask-session")

# Enable debug toolbar
app.debug = True
toolbar = DebugToolbarExtension(app)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# Configure Razorpay
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', '')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', '')
print(f"Razorpay Key ID: {RAZORPAY_KEY_ID}")
print(f"Razorpay Key Secret: {RAZORPAY_KEY_SECRET[:4]}...")  # Print partial secret for debugging

# Initialize Razorpay client if keys are available
if RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
    try:
        razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        print("Razorpay client initialized successfully")
    except Exception as e:
        print(f"Error initializing Razorpay client: {str(e)}")
        razorpay_client = None
else:
    print("Razorpay keys not properly configured")
    razorpay_client = None

# Pricing plans
PRICING_PLANS = {
    'free': {'price': 0, 'name': 'Free', 'features': ['Resume preview only', 'Basic template selection'], 'resume_variants': 1, 'max_templates': 1},
    'basic': {'price': 49, 'name': 'Basic', 'features': ['Download 1 PDF resume', 'All templates', 'Color customization'], 'resume_variants': 1, 'max_templates': 3},
    'pro': {'price': 99, 'name': 'Pro', 'features': ['3 resume variants', 'Cover letter', 'All templates', 'Color customization', 'ATS optimization'], 'resume_variants': 3, 'max_templates': 3},
    'premium': {'price': 199, 'name': 'Premium', 'features': ['3 resume variants', 'Cover letter', 'All templates', 'Color customization', 'ATS optimization', '1-on-1 feedback'], 'resume_variants': 3, 'max_templates': 3}
}

# Available templates
RESUME_TEMPLATES = {
    'modern': {
        'name': 'Modern',
        'description': 'Clean and professional design with a blue accent color',
        'preview_img': '/static/img/templates/modern.jpg',
        'colors': ['#3498db', '#2ecc71', '#e74c3c', '#9b59b6', '#f39c12']
    },
    'elegant': {
        'name': 'Elegant',
        'description': 'Sophisticated design with serif fonts and classic styling',
        'preview_img': '/static/img/templates/elegant.jpg',
        'colors': ['#8e7057', '#7d3c98', '#2e4053', '#186a3b', '#a04000']
    },
    'creative': {
        'name': 'Creative',
        'description': 'Eye-catching design with a sidebar and modern layout',
        'preview_img': '/static/img/templates/creative.jpg',
        'colors': ['#6a11cb', '#006266', '#1289a7', '#d980fa', '#b71540']
    }
}

# Create directories for saving generated resumes
os.makedirs('generated_resumes', exist_ok=True)

# Helper functions for resume formatting
def format_skills(skills_str, template_name='modern'):
    skills_list = [skill.strip() for skill in skills_str.split(',')]
    
    if template_name == 'modern':
        skills_html = '<div class="skills">\n'
        for skill in skills_list:
            skills_html += f'    <div class="skill">{skill}</div>\n'
        skills_html += '</div>'
    elif template_name == 'elegant':
        skills_html = '<ul class="skills-list">\n'
        for skill in skills_list:
            skills_html += f'    <li>{skill}</li>\n'
        skills_html += '</ul>'
    elif template_name == 'creative':
        skills_html = '<div class="skills-container">\n'
        for skill in skills_list:
            skills_html += f'    <span class="skill-tag">{skill}</span>\n'
        skills_html += '</div>'
    else:
        # Default generic format
        skills_html = '<ul>\n'
        for skill in skills_list:
            skills_html += f'    <li>{skill}</li>\n'
        skills_html += '</ul>'
    
    return skills_html

def format_experience(exp_str):
    # Simple parsing for demo purposes
    experiences = exp_str.split(',')
    html = ''
    
    for exp in experiences:
        exp = exp.strip()
        if ' at ' in exp and ' (' in exp and ')' in exp:
            title, rest = exp.split(' at ', 1)
            company, years = rest.split(' (', 1)
            years = years.rstrip(')')
            
            html += f'''
<div class="experience-item">
    <h3 class="job-title">{title}</h3>
    <div class="company">{company}</div>
    <div class="date">{years}</div>
    <p>Responsible for designing, developing, and maintaining software solutions that meet business requirements and user needs.</p>
</div>
'''
        else:
            # Fallback for unparseable experience
            html += f'<div class="experience-item"><p>{exp}</p></div>'
    
    return html if html else exp_str

def apply_color_scheme(html_content, color_scheme):
    """Apply a color scheme to the HTML resume"""
    # Replace primary color in the template with the chosen color
    if 'modern' in html_content:
        # Modern template uses #3498db as primary color
        html_content = html_content.replace('#3498db', color_scheme)
    elif 'elegant' in html_content:
        # Elegant template uses #8e7057 as primary color
        html_content = html_content.replace('#8e7057', color_scheme)
    elif 'creative' in html_content:
        # Creative template uses gradient with #6a11cb
        html_content = html_content.replace('#6a11cb', color_scheme)
    
    return html_content

def generate_ats_tips(form_data):
    """Generate ATS optimization tips based on the resume content"""
    skills = form_data.get('skills', '')
    experience = form_data.get('experience', '')
    
    # Use Gemini to generate personalized ATS optimization tips
    prompt = f"""
    Generate 3-5 specific ATS optimization tips for this resume:
    
    Skills: {skills}
    Experience: {experience}
    
    The tips should be concise, specific to the resume content, and actionable.
    Format the response as a JSON array of strings.
    """
    
    try:
        response = model.generate_content(prompt)
        tips_text = response.text
        
        # Extract JSON array from response
        if '[' in tips_text and ']' in tips_text:
            tips_json = tips_text[tips_text.find('['):tips_text.rfind(']')+1]
            tips = json.loads(tips_json)
        else:
            # Fallback if proper JSON not found
            tips = ["Include keywords from the job description", 
                   "Use standard section headings", 
                   "Avoid complex formatting and tables"]
    except Exception as e:
        logger.error(f"Error generating ATS tips: {str(e)}")
        tips = ["Include keywords from the job description", 
               "Use standard section headings", 
               "Avoid complex formatting and tables"]
    
    return tips

@app.route('/')
def home():
    return render_template('index.html', plans=PRICING_PLANS)

@app.route('/templates')
def templates():
    """Display all available resume templates"""
    return render_template('templates.html', templates=RESUME_TEMPLATES, plans=PRICING_PLANS)

@app.route('/pricing')
def pricing():
    """Display the pricing page"""
    return render_template('pricing.html', plans=PRICING_PLANS)

@app.route('/resume-tips')
def resume_tips():
    """Display resume writing tips and advice"""
    return render_template('resume_tips.html')

@app.route('/career-advice')
def career_advice():
    """Display career advice and guidance"""
    return render_template('career_advice.html')

@app.route('/faq')
def faq():
    """Display frequently asked questions"""
    return render_template('faq.html', plans=PRICING_PLANS)

@app.route('/blog')
def blog():
    """Display the blog with articles and guides"""
    return render_template('blog.html')

@app.route('/resume-form')
def resume_form():
    plan = request.args.get('plan', 'free')
    template = request.args.get('template', 'modern')
    
    if plan not in PRICING_PLANS:
        return redirect(url_for('home'))
    
    # Determine which templates are available for this plan
    available_templates = {}
    if plan == 'free':
        # Only modern template for free plan
        available_templates = {'modern': RESUME_TEMPLATES['modern']}
    else:
        # All templates for paid plans
        available_templates = RESUME_TEMPLATES
    
    # Check if the requested template is available for this plan
    selected_template = template if template in available_templates else 'modern'
    
    return render_template('resume_form.html', 
                          plan=plan, 
                          plan_details=PRICING_PLANS[plan],
                          templates=available_templates,
                          selected_template=selected_template)

@app.route('/generate-resume', methods=['POST'])
def generate_resume():
    # Get form data
    form_data = request.form.to_dict()
    logger.info(f"Received form data: {form_data}")
    
    # Store data in session
    session['resume_data'] = form_data
    session['selected_plan'] = form_data.get('plan', 'free')
    session['selected_template'] = form_data.get('template', 'modern')
    session['selected_color'] = form_data.get('color', '#3498db')
    logger.info(f"Selected plan: {session['selected_plan']}")
    logger.info(f"Selected template: {session['selected_template']}")
    
    try:
        # Format the fields
        template_name = session['selected_template']
        formatted_skills = format_skills(form_data.get('skills', ''), template_name)
        formatted_experience = format_experience(form_data.get('experience', ''))
        
        # Read the template file
        template_path = os.path.join('resume_templates', f'{template_name}.html')
        with open(template_path, 'r') as f:
            template = f.read()
        
        # Replace placeholders with data
        resume_html = template
        for key, value in form_data.items():
            if key == 'skills':
                resume_html = resume_html.replace(f'{{{{{key}}}}}', formatted_skills)
            elif key == 'experience':
                resume_html = resume_html.replace(f'{{{{{key}}}}}', formatted_experience)
            elif key in ['name', 'email', 'phone', 'linkedin', 'summary', 'education', 'projects']:
                resume_html = resume_html.replace(f'{{{{{key}}}}}', value)
        
        # Handle the first letter of name for the creative template avatar
        if template_name == 'creative' and 'name' in form_data:
            first_letter = form_data.get('name', 'A')[0]
            resume_html = resume_html.replace('{{name|slice:0:1}}', first_letter)
        
        # Apply color scheme if specified
        if session['selected_color']:
            resume_html = apply_color_scheme(resume_html, session['selected_color'])
        
        # Generate a unique ID for this resume
        resume_id = str(uuid.uuid4())
        session['resume_id'] = resume_id
        
        # Save the resume to the generated resumes directory
        resume_filename = f"resume_{resume_id}.html"
        resume_path = os.path.join('generated_resumes', resume_filename)
        with open(resume_path, 'w') as f:
            f.write(resume_html)
        logger.info(f"Saved resume to {resume_path}")
        
        # For debugging
        with open('debug_resume.html', 'w') as f:
            f.write(resume_html)
        logger.info("Saved debug resume to debug_resume.html")
        
        # Store the generated HTML in session
        session['resume_html'] = resume_html
        session['resume_template'] = template_name
        logger.info("Stored resume HTML in session")
        
        # Generate ATS optimization tips for pro and premium plans
        if session['selected_plan'] in ['pro', 'premium']:
            ats_tips = generate_ats_tips(form_data)
            session['ats_tips'] = ats_tips
            logger.info(f"Generated ATS tips: {ats_tips}")
        
        # Redirect based on plan
        if session['selected_plan'] == 'free':
            logger.info("Free plan selected, redirecting to preview")
            return redirect(url_for('preview_resume'))
        else:
            logger.info("Paid plan selected, redirecting to payment")
            return redirect(url_for('payment'))
    
    except Exception as e:
        error_msg = f"Error generating resume: {str(e)}"
        logger.error(error_msg)
        flash(error_msg)
        return redirect(url_for('resume_form'))

@app.route('/preview-resume')
def preview_resume():
    resume_html = session.get('resume_html', '')
    
    # Debug session data
    logger.info(f"Session contains resume_html: {'Yes' if resume_html else 'No'}")
    logger.info(f"Session keys: {list(session.keys())}")
    
    if not resume_html:
        logger.warning("No resume HTML found in session")
        flash("Please generate a resume first")
        return redirect(url_for('home'))
    
    # For debugging - save current session resume to a file
    try:
        with open('session_resume.html', 'w') as f:
            f.write(resume_html)
        logger.info("Saved session resume to session_resume.html")
    except Exception as e:
        logger.error(f"Error saving session resume: {str(e)}")
    
    plan = session.get('selected_plan', 'free')
    can_download = plan != 'free'
    template = session.get('resume_template', 'modern')
    template_info = RESUME_TEMPLATES.get(template, {})
    
    # Get ATS tips if available
    ats_tips = session.get('ats_tips', []) if plan in ['pro', 'premium'] else []
    
    logger.info(f"Rendering preview with plan: {plan}, can_download: {can_download}, template: {template}")
    
    return render_template('preview.html', 
                          resume_html=resume_html, 
                          can_download=can_download, 
                          plan=plan,
                          plan_details=PRICING_PLANS[plan],
                          template=template,
                          template_info=template_info,
                          templates=RESUME_TEMPLATES,
                          ats_tips=ats_tips)

@app.route('/payment')
def payment():
    # Make sure we have resume data
    if not session.get('resume_html'):
        flash("Please generate a resume first")
        return redirect(url_for('home'))
    
    # Set default plan if not in session
    if not session.get('selected_plan'):
        session['selected_plan'] = 'basic'
    
    plan = session.get('selected_plan', 'basic')
    if plan == 'free':
        plan = 'basic'  # Default to basic for payments
    
    plan_details = PRICING_PLANS.get(plan, PRICING_PLANS['basic'])
    amount = plan_details['price'] * 100  # Convert to paise
    
    # Check if Razorpay client is configured
    if not razorpay_client:
        flash("Payment system is not properly configured. Please try again later or contact support.")
        return redirect(url_for('preview_resume'))
    
    # Create a unique receipt ID
    receipt_id = f"order_{secrets.token_hex(8)}"
    
    # Create Razorpay order
    order_data = {
        'amount': amount,
        'currency': 'INR',
        'receipt': receipt_id,
        'payment_capture': 1
    }
    
    try:
        print(f"Creating Razorpay order with data: {order_data}")
        order = razorpay_client.order.create(data=order_data)
        print(f"Order created: {order}")
        return render_template('payment.html', 
                              order=order, 
                              plan=plan_details,
                              key_id=RAZORPAY_KEY_ID)
    except Exception as e:
        error_msg = f"Payment error: {str(e)}"
        print(error_msg)
        flash(error_msg)
        return redirect(url_for('preview_resume'))

@app.route('/payment-success', methods=['POST'])
def payment_success():
    payment_id = request.form.get('razorpay_payment_id', '')
    order_id = request.form.get('razorpay_order_id', '')
    signature = request.form.get('razorpay_signature', '')
    
    # Verify payment signature
    try:
        razorpay_client.utility.verify_payment_signature({
            'razorpay_payment_id': payment_id,
            'razorpay_order_id': order_id,
            'razorpay_signature': signature
        })
        
        # Mark payment as successful in session
        session['payment_successful'] = True
        
        # Record transaction details
        transaction = {
            'payment_id': payment_id,
            'order_id': order_id,
            'plan': session.get('selected_plan', 'basic'),
            'amount': PRICING_PLANS[session.get('selected_plan', 'basic')]['price'],
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        session['transaction'] = transaction
        
        flash("Payment successful! You can now download your resume.")
        return redirect(url_for('preview_resume'))
    
    except Exception as e:
        flash(f"Payment verification failed: {str(e)}")
        return redirect(url_for('payment'))

@app.route('/download-resume')
def download_resume():
    # Check if payment was successful or if on a plan that doesn't require payment
    if not session.get('payment_successful') and session.get('selected_plan') != 'free':
        flash("Please complete payment before downloading")
        return redirect(url_for('payment'))
    
    resume_html = session.get('resume_html', '')
    if not resume_html:
        return redirect(url_for('home'))
    
    # Generate PDF from HTML
    try:
        # Add custom filename with the user's name if available
        user_name = session.get('resume_data', {}).get('name', 'resume').replace(' ', '_')
        filename = f"{user_name}_resume.pdf"
        
        # First try: Use wkhtmltopdf_config.py if it exists
        pdf = None
        error_messages = []
        
        try:
            # Try to import from our config file first
            if os.path.exists('wkhtmltopdf_config.py'):
                try:
                    sys.path.insert(0, os.getcwd())
                    from wkhtmltopdf_config import WKHTMLTOPDF_PATH
                    config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
                    pdf = pdfkit.from_string(resume_html, False, configuration=config)
                    logger.info(f"PDF generated using wkhtmltopdf_config.py: {WKHTMLTOPDF_PATH}")
                except Exception as e:
                    error_messages.append(f"Config file method failed: {str(e)}")
                    
            # Try common installation paths if config import failed
            if pdf is None:
                wkhtmltopdf_paths = [
                    r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
                    r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe",
                    r"/usr/local/bin/wkhtmltopdf",
                    r"/usr/bin/wkhtmltopdf"
                ]
                
                for path in wkhtmltopdf_paths:
                    if os.path.exists(path):
                        try:
                            config = pdfkit.configuration(wkhtmltopdf=path)
                            pdf = pdfkit.from_string(resume_html, False, configuration=config)
                            logger.info(f"PDF generated using path: {path}")
                            break
                        except Exception as e:
                            error_messages.append(f"Path {path} method failed: {str(e)}")
            
            # Try default configuration if still no PDF
            if pdf is None:
                try:
                    pdf = pdfkit.from_string(resume_html, False)
                    logger.info("PDF generated using default configuration")
                except Exception as e:
                    error_messages.append(f"Default configuration method failed: {str(e)}")
            
            # If all PDF generation methods fail, return HTML instead
            if pdf is None:
                logger.warning(f"All PDF methods failed. Errors: {'; '.join(error_messages)}")
                response = app.make_response(resume_html)
                response.headers['Content-Type'] = 'text/html'
                response.headers['Content-Disposition'] = f'attachment; filename="{user_name}_resume.html"'
                flash("PDF generation failed. Providing HTML file instead. To enable PDF downloads, please install wkhtmltopdf.")
                return response
        except Exception as outer_e:
            # Final fallback to HTML if everything else fails
            logger.error(f"Comprehensive PDF generation failed: {str(outer_e)}")
            response = app.make_response(resume_html)
            response.headers['Content-Type'] = 'text/html'
            response.headers['Content-Disposition'] = f'attachment; filename="{user_name}_resume.html"'
            flash("PDF generation failed. Providing HTML file instead. To enable PDF downloads, please install wkhtmltopdf.")
            return response
        
        # Return the PDF 
        response = app.make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    except Exception as e:
        flash(f"Error generating PDF: {str(e)}")
        return redirect(url_for('preview_resume'))

@app.route('/change-template/<template_name>')
def change_template(template_name):
    """Change the resume template and regenerate"""
    if template_name not in RESUME_TEMPLATES:
        flash("Invalid template selected")
        return redirect(url_for('preview_resume'))
    
    # Check if we have form data
    form_data = session.get('resume_data')
    if not form_data:
        flash("Please generate a resume first")
        return redirect(url_for('home'))
    
    # Update the template in session
    session['selected_template'] = template_name
    
    # Format the fields
    formatted_skills = format_skills(form_data.get('skills', ''), template_name)
    formatted_experience = format_experience(form_data.get('experience', ''))
    
    # Read the template file
    template_path = os.path.join('resume_templates', f'{template_name}.html')
    try:
        with open(template_path, 'r') as f:
            template = f.read()
        
        # Replace placeholders with data
        resume_html = template
        for key, value in form_data.items():
            if key == 'skills':
                resume_html = resume_html.replace(f'{{{{{key}}}}}', formatted_skills)
            elif key == 'experience':
                resume_html = resume_html.replace(f'{{{{{key}}}}}', formatted_experience)
            elif key in ['name', 'email', 'phone', 'linkedin', 'summary', 'education', 'projects']:
                resume_html = resume_html.replace(f'{{{{{key}}}}}', value)
        
        # Handle the first letter of name for the creative template avatar
        if template_name == 'creative' and 'name' in form_data:
            first_letter = form_data.get('name', 'A')[0]
            resume_html = resume_html.replace('{{name|slice:0:1}}', first_letter)
        
        # Apply color scheme if specified
        if session.get('selected_color'):
            resume_html = apply_color_scheme(resume_html, session.get('selected_color'))
        
        # Update session with new HTML
        session['resume_html'] = resume_html
        session['resume_template'] = template_name
        
        flash(f"Template changed to {RESUME_TEMPLATES[template_name]['name']}")
    except Exception as e:
        flash(f"Error changing template: {str(e)}")
    
    return redirect(url_for('preview_resume'))

@app.route('/change-color/<color>')
def change_color(color):
    """Change the resume color scheme"""
    # Check if we have resume HTML
    resume_html = session.get('resume_html')
    if not resume_html:
        flash("Please generate a resume first")
        return redirect(url_for('home'))
    
    # Validate the color (simple validation)
    if not color.startswith('#') or len(color) != 7:
        color = '#3498db'  # Default to blue if invalid
    
    # Update color in session
    session['selected_color'] = color
    
    # Apply color scheme to the current HTML
    try:
        updated_html = apply_color_scheme(resume_html, color)
        session['resume_html'] = updated_html
        flash(f"Color scheme updated")
    except Exception as e:
        flash(f"Error changing color: {str(e)}")
    
    return redirect(url_for('preview_resume'))

@app.route('/generate-cover-letter')
def generate_cover_letter():
    """Generate a matching cover letter for pro and premium plans"""
    # Check if user has pro or premium plan
    plan = session.get('selected_plan')
    if plan not in ['pro', 'premium'] or not session.get('payment_successful'):
        flash("Cover letter generation is only available for Pro and Premium subscribers")
        return redirect(url_for('preview_resume'))
    
    # Get resume data
    resume_data = session.get('resume_data')
    if not resume_data:
        flash("Please generate a resume first")
        return redirect(url_for('home'))
    
    # Generate cover letter using Gemini
    prompt = f"""
    Generate a professional cover letter based on the following resume information:
    
    Name: {resume_data.get('name', '')}
    Email: {resume_data.get('email', '')}
    Phone: {resume_data.get('phone', '')}
    Summary: {resume_data.get('summary', '')}
    Experience: {resume_data.get('experience', '')}
    Skills: {resume_data.get('skills', '')}
    
    Create a general-purpose cover letter that highlights the candidate's strengths.
    Use a professional tone and format it properly with date, recipient placeholder, and signature.
    """
    
    try:
        response = model.generate_content(prompt)
        cover_letter = response.text
        
        # Store cover letter in session
        session['cover_letter'] = cover_letter
        
        return render_template('cover_letter.html', 
                              cover_letter=cover_letter,
                              name=resume_data.get('name', ''))
    except Exception as e:
        flash(f"Error generating cover letter: {str(e)}")
        return redirect(url_for('preview_resume'))

@app.route('/download-cover-letter')
def download_cover_letter():
    """Download the generated cover letter as PDF"""
    # Check if user has pro or premium plan and payment
    plan = session.get('selected_plan')
    if plan not in ['pro', 'premium'] or not session.get('payment_successful'):
        flash("Cover letter download is only available for Pro and Premium subscribers")
        return redirect(url_for('preview_resume'))
    
    # Get cover letter from session
    cover_letter = session.get('cover_letter')
    if not cover_letter:
        flash("Please generate a cover letter first")
        return redirect(url_for('generate_cover_letter'))
    
    # Format as HTML for PDF conversion
    name = session.get('resume_data', {}).get('name', 'User')
    
    # Replace newlines with <br> tags separately
    cover_letter_with_breaks = cover_letter.replace('\n', '<br>')
    
    # Then create the HTML template with the pre-processed cover letter content
    cover_letter_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Cover Letter - {name}</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 2cm; }}
            .cover-letter {{ max-width: 800px; margin: 0 auto; }}
            .header {{ margin-bottom: 40px; }}
            .date {{ margin-bottom: 20px; }}
            .recipient {{ margin-bottom: 20px; }}
            .content {{ margin-bottom: 40px; }}
            .signature {{ margin-top: 40px; }}
        </style>
    </head>
    <body>
        <div class="cover-letter">
            {cover_letter_with_breaks}
        </div>
    </body>
    </html>
    """
    
    try:
        # Add custom filename with the user's name
        filename = f"{name.replace(' ', '_')}_cover_letter.pdf"
        
        # Use multiple methods to try generating PDF
        pdf = None
        error_messages = []
        
        # First try: Use wkhtmltopdf_config.py if it exists
        try:
            if os.path.exists('wkhtmltopdf_config.py'):
                try:
                    sys.path.insert(0, os.getcwd())
                    from wkhtmltopdf_config import WKHTMLTOPDF_PATH
                    config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
                    pdf = pdfkit.from_string(cover_letter_html, False, configuration=config)
                    logger.info(f"Cover letter PDF generated using wkhtmltopdf_config.py")
                except Exception as e:
                    error_messages.append(f"Config file method failed: {str(e)}")
            
            # Try common installation paths if config import failed
            if pdf is None:
                wkhtmltopdf_paths = [
                    r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
                    r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe",
                    r"/usr/local/bin/wkhtmltopdf",
                    r"/usr/bin/wkhtmltopdf"
                ]
                
                for path in wkhtmltopdf_paths:
                    if os.path.exists(path):
                        try:
                            config = pdfkit.configuration(wkhtmltopdf=path)
                            pdf = pdfkit.from_string(cover_letter_html, False, configuration=config)
                            logger.info(f"Cover letter PDF generated using path: {path}")
                            break
                        except Exception as e:
                            error_messages.append(f"Path {path} method failed: {str(e)}")
            
            # Try default configuration if still no PDF
            if pdf is None:
                try:
                    pdf = pdfkit.from_string(cover_letter_html, False)
                    logger.info("Cover letter PDF generated using default configuration")
                except Exception as e:
                    error_messages.append(f"Default configuration method failed: {str(e)}")
            
            # If all PDF generation methods fail, return HTML instead
            if pdf is None:
                logger.warning(f"All PDF methods failed for cover letter. Errors: {'; '.join(error_messages)}")
                # Save HTML version for manual testing
                with open("demo_cover_letter.html", "w", encoding="utf-8") as f:
                    f.write(cover_letter_html)
                    
                response = app.make_response(cover_letter_html)
                response.headers['Content-Type'] = 'text/html'
                response.headers['Content-Disposition'] = f'attachment; filename="{filename.replace(".pdf", ".html")}"'
                flash("PDF generation failed. Providing HTML file instead. To enable PDF downloads, please install wkhtmltopdf.")
                return response
                
        except Exception as outer_e:
            # Final fallback to HTML if everything else fails
            logger.error(f"Comprehensive cover letter PDF generation failed: {str(outer_e)}")
            # Save HTML version for manual testing
            with open("demo_cover_letter.html", "w", encoding="utf-8") as f:
                f.write(cover_letter_html)
                
            response = app.make_response(cover_letter_html)
            response.headers['Content-Type'] = 'text/html'
            response.headers['Content-Disposition'] = f'attachment; filename="{filename.replace(".pdf", ".html")}"'
            flash("PDF generation failed. Providing HTML file instead. To enable PDF downloads, please install wkhtmltopdf.")
            return response
        
        # Return the PDF
        response = app.make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Also save a copy for testing purposes
        with open("demo_cover_letter.pdf", "wb") as f:
            f.write(pdf)
            
        return response
    except Exception as e:
        flash(f"Error generating cover letter PDF: {str(e)}")
        return redirect(url_for('generate_cover_letter'))

@app.route('/ats-optimize', methods=['POST'])
def ats_optimize():
    """Generate ATS optimization tips for the resume"""
    # Check if user has access to premium features
    plan = session.get('selected_plan', 'free')
    
    # Special case for testing: if no session, still provide demo data
    if not session or app.debug and 'resume_data' not in session:
        # For testing purposes, provide demo tips
        demo_tips = [
            "Include keywords from the job description",
            "Use standard section headings", 
            "Avoid complex formatting and tables",
            "Tailor your skills section to match job requirements",
            "Quantify your achievements with numbers and metrics"
        ]
        return jsonify({
            "tips": demo_tips,
            "plan": "demo",
            "testing_mode": True
        })
    
    if plan not in ['pro', 'premium']:
        return jsonify({"error": "This feature is only available for Pro and Premium plans"}), 403
    
    form_data = session.get('resume_data', {})
    if not form_data:
        return jsonify({"error": "No resume data found"}), 400
    
    # Generate ATS optimization tips
    tips = generate_ats_tips(form_data)
    
    return jsonify({
        "tips": tips,
        "plan": plan
    })

@app.route('/debug/simulate-payment')
def debug_simulate_payment():
    """Debug route to simulate a successful payment"""
    # Only allow in debug mode
    if not app.debug:
        return jsonify({"error": "Debug routes only available in debug mode"}), 403
    
    plan = request.args.get('plan', 'basic')
    session['selected_plan'] = plan  # Use selected_plan instead of plan
    session['payment_successful'] = True  # Use payment_successful instead of payment_completed
    session['payment_id'] = f"debug_payment_{int(time.time())}"
    
    # Set transaction details for completeness
    transaction = {
        'payment_id': session['payment_id'],
        'order_id': f"debug_order_{int(time.time())}",
        'plan': plan,
        'amount': PRICING_PLANS[plan]['price'],
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    session['transaction'] = transaction
    
    flash(f"Debug: Payment for {plan.title()} plan simulated successfully")
    return redirect(url_for('preview_resume'))

@app.route('/debug/generate-variant', methods=['POST'])
def debug_generate_variant():
    """Debug route to simulate generating a resume variant"""
    # Only allow in debug mode
    if not app.debug:
        return jsonify({"error": "Debug routes only available in debug mode"}), 403
    
    # Check if user has premium plan - Fix: Use selected_plan instead of plan
    plan = session.get('selected_plan', 'free')  # Changed from 'plan' to 'selected_plan'
    if plan not in ['pro', 'premium']:
        return jsonify({"error": f"This feature requires a Pro or Premium plan. Current plan: {plan}"}), 403
    
    # Get variant parameters
    data = request.json
    emphasis = data.get('emphasis', 'general')
    tone = data.get('tone', 'professional')
    
    # Get the form data
    form_data = session.get('resume_data', {})  # Changed from 'form_data' to 'resume_data'
    if not form_data:
        return jsonify({"error": "No resume data found"}), 400
    
    # In a real implementation, this would call the AI model with different parameters
    # For demo purposes, we'll just simulate it
    
    # Generate a simple variant based on the emphasis and tone
    variant_html = f"""
    <div class="resume-variant" data-emphasis="{emphasis}" data-tone="{tone}">
        <h1>{form_data.get('name', 'John Doe')}</h1>
        <p>Email: {form_data.get('email', 'email@example.com')}</p>
        <p>Phone: {form_data.get('phone', '123-456-7890')}</p>
        
        <h2>Professional Summary</h2>
        <p>This is a {tone} resume variant with emphasis on {emphasis} skills and experience.</p>
        
        <h2>Experience</h2>
        <p>{form_data.get('experience', 'No experience provided')}</p>
        
        <h2>Education</h2>
        <p>{form_data.get('education', 'No education provided')}</p>
        
        <h2>Skills</h2>
        <p>{form_data.get('skills', 'No skills provided')}</p>
    </div>
    """
    
    # Store the variant in the session
    variants = session.get('resume_variants', [])
    variants.append({
        'html': variant_html,
        'emphasis': emphasis,
        'tone': tone,
        'timestamp': int(time.time())
    })
    session['resume_variants'] = variants
    
    return jsonify({
        "success": True,
        "variant_id": len(variants),
        "emphasis": emphasis,
        "tone": tone
    })

# Add a debug route to view all variants
@app.route('/debug/view-variants')
def debug_view_variants():
    """Debug route to view all generated variants"""
    # Only allow in debug mode
    if not app.debug:
        return jsonify({"error": "Debug routes only available in debug mode"}), 403
    
    variants = session.get('resume_variants', [])
    
    if not variants:
        return "No variants have been generated yet."
    
    # Create a simple HTML page to display all variants
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Resume Variants</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
            .variant { border: 1px solid #ddd; margin: 20px 0; padding: 20px; border-radius: 5px; }
            .meta { background: #f5f5f5; padding: 10px; margin-bottom: 10px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h1>Resume Variants</h1>
    """
    
    for i, variant in enumerate(variants):
        html += f"""
        <div class="variant">
            <div class="meta">
                <strong>Variant {i+1}</strong> | 
                Emphasis: {variant.get('emphasis', 'Not specified')} | 
                Tone: {variant.get('tone', 'Not specified')}
            </div>
            {variant.get('html', 'No HTML content')}
        </div>
        """
    
    html += """
    </body>
    </html>
    """
    
    return html

@app.route('/debug/variant-data', methods=['GET'])
def debug_variant_data():
    """Debug endpoint to provide variant data in JSON format for testing"""
    # Only allow in debug mode
    if not app.debug:
        return jsonify({"error": "Debug routes only available in debug mode"}), 403
    
    variants = session.get('resume_variants', [])
    
    # If no variants in session, create demo variants
    if not variants:
        variants = [
            {
                'emphasis': 'technical',
                'tone': 'professional',
                'html': '<div class="demo-variant"><h2>Technical Emphasis Variant</h2><p>This is a demo variant for testing.</p></div>',
                'timestamp': int(time.time())
            },
            {
                'emphasis': 'leadership',
                'tone': 'confident',
                'html': '<div class="demo-variant"><h2>Leadership Emphasis Variant</h2><p>This is a demo variant for testing.</p></div>',
                'timestamp': int(time.time())
            },
            {
                'emphasis': 'creative',
                'tone': 'enthusiastic',
                'html': '<div class="demo-variant"><h2>Creative Emphasis Variant</h2><p>This is a demo variant for testing.</p></div>',
                'timestamp': int(time.time())
            }
        ]
    
    # Return JSON data that's easier to parse than HTML
    return jsonify({
        "variants": variants,
        "count": len(variants),
        "demo_mode": len(session.get('resume_variants', [])) == 0
    })

if __name__ == '__main__':
    app.run(debug=True) 