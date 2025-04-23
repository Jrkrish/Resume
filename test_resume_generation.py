import os
import random
import re
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
print(f"Using API key: {GEMINI_API_KEY[:5]}...{GEMINI_API_KEY[-4:]}")

# Sample resume data
sample_data = {
    'name': 'John Doe',
    'email': 'john.doe@example.com',
    'phone': '555-123-4567',
    'linkedin': 'linkedin.com/in/johndoe',
    'summary': 'Experienced software developer with 5 years of experience in web development.',
    'education': 'Bachelor of Science in Computer Science, XYZ University, 2018',
    'experience': 'Software Developer at ABC Corp (2018-2022), Senior Developer at XYZ Inc (2022-Present)',
    'skills': 'Python, JavaScript, React, Node.js, SQL, AWS',
    'projects': 'Developed an e-commerce platform, Created a task management application'
}

# Function to format skills as HTML tags
def format_skills(skills_str):
    skills_list = [skill.strip() for skill in skills_str.split(',')]
    if random.choice([True, False]):  # Randomly choose between list and tags format
        skills_html = '<ul class="skills-list">\n'
        for skill in skills_list:
            skills_html += f'    <li>{skill}</li>\n'
        skills_html += '</ul>'
    else:
        skills_html = '<div class="skills-container">\n'
        for skill in skills_list:
            skills_html += f'    <span class="skill-tag">{skill}</span>\n'
        skills_html += '</div>'
    return skills_html

# Function to format experience more professionally
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
    <p>Responsible for designing, developing, and maintaining software solutions.</p>
</div>
'''
    
    return html if html else exp_str

# Available templates
templates = ['modern', 'elegant', 'creative']

try:
    print("Initializing Gemini API...")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Format the fields
    formatted_skills = format_skills(sample_data['skills'])
    formatted_experience = format_experience(sample_data['experience'])
    
    # Choose a random template
    template_name = random.choice(templates)
    template_path = f'resume_templates/{template_name}.html'
    
    print(f"Using template: {template_name}")
    
    # Read the template file
    with open(template_path, 'r') as f:
        template = f.read()
    
    # Replace placeholders with data
    resume_html = template
    for key, value in sample_data.items():
        if key == 'skills':
            resume_html = resume_html.replace(f'{{{{{key}}}}}', formatted_skills)
        elif key == 'experience':
            resume_html = resume_html.replace(f'{{{{{key}}}}}', formatted_experience)
        else:
            resume_html = resume_html.replace(f'{{{{{key}}}}}', value)
    
    # Handle the first letter of name for the creative template avatar
    if template_name == 'creative':
        resume_html = resume_html.replace('{{name|slice:0:1}}', sample_data['name'][0])
    
    # Save the generated HTML to a file
    with open('test_resume.html', 'w') as f:
        f.write(resume_html)
    
    print("Resume generation successful!")
    print(f"Resume saved to 'test_resume.html'")
    print("\nPreview of the generated HTML:")
    print(resume_html[:300] + "...")  # Print just the first 300 characters
    
except Exception as e:
    print(f"Error generating resume: {str(e)}") 