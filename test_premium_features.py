import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys
from flask import session
from app import app, model, generate_ats_tips

class TestPremiumFeatures(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SERVER_NAME'] = 'localhost:5000'
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        
        # Create a session with premium plan
        with self.app.session_transaction() as sess:
            sess['selected_plan'] = 'premium'
            sess['payment_successful'] = True
            sess['resume_data'] = {
                'name': 'Test User',
                'email': 'test@example.com',
                'phone': '123-456-7890',
                'linkedin': 'linkedin.com/in/testuser',
                'summary': 'Experienced software developer with a passion for building scalable applications.',
                'education': 'Bachelor of Science in Computer Science, Stanford University, 2020',
                'experience': 'Software Engineer at Tech Corp (2020-2023), Intern at StartupX (2019-2020)',
                'skills': 'Python, JavaScript, React, Node.js, Cloud Computing, AI/ML'
            }
            sess['resume_html'] = '<div>Sample Resume</div>'
    
    def tearDown(self):
        self.app_context.pop()
    
    @patch('app.model.generate_content')
    def test_multiple_resume_variants(self, mock_generate):
        # Setup mock response for AI model
        mock_response = MagicMock()
        mock_response.text = '<div>AI Generated Resume Content</div>'
        mock_generate.return_value = mock_response
        
        # Test accessing the generate-resume endpoint multiple times
        for i in range(3):
            response = self.app.post('/generate-resume', data={
                'plan': 'premium',
                'name': f'Test User {i}',
                'email': 'test@example.com',
                'phone': '123-456-7890',
                'linkedin': 'linkedin.com/in/testuser',
                'summary': f'Professional summary version {i}',
                'education': 'Bachelor of Science in Computer Science, Stanford University, 2020',
                'experience': f'Software Engineer at Tech Corp (2020-202{i})',
                'skills': 'Python, JavaScript, React, Node.js'
            })
            self.assertEqual(response.status_code, 302)  # Should redirect to preview
    
    @patch('app.model.generate_content')
    def test_cover_letter_generation(self, mock_generate):
        # Setup mock response for AI model
        mock_response = MagicMock()
        mock_response.text = '<div>AI Generated Cover Letter</div>'
        mock_generate.return_value = mock_response
        
        # Test cover letter generation
        with self.app.session_transaction() as sess:
            sess['job_title'] = 'Senior Software Engineer'
            sess['company_name'] = 'Google'
        
        response = self.app.get('/generate-cover-letter')
        self.assertEqual(response.status_code, 302)  # Should redirect to cover letter preview
        
        # Test cover letter download for premium users
        with self.app.session_transaction() as sess:
            sess['cover_letter'] = '<div>Cover Letter Content</div>'
        
        response = self.app.get('/download-cover-letter')
        self.assertEqual(response.status_code, 200)  # Should return the PDF file
    
    @patch('app.generate_ats_tips')
    def test_ats_optimization(self, mock_ats_tips):
        # Setup mock response for ATS tips
        mock_ats_tips.return_value = [
            "Include more keywords relevant to the job description",
            "Use standard section headings",
            "Keep formatting simple for ATS compatibility"
        ]
        
        # Test ATS optimization endpoint (this would need to be added to your app)
        with self.app as client:
            with client.session_transaction() as sess:
                sess['resume_data'] = {
                    'skills': 'Python, JavaScript, React, Node.js',
                    'experience': 'Software Engineer at Tech Corp (2020-2023)'
                }
            
            # Use the '/ats-optimize' endpoint that was added
            response = client.post('/ats-optimize')
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(len(data['tips']), 3)
    
    def test_template_customization(self):
        # Test changing templates
        response = self.app.get('/change-template/elegant')
        self.assertEqual(response.status_code, 302)  # Should redirect to preview
        
        # Test changing colors
        response = self.app.get('/change-color/%237d3c98')  # Purple color
        self.assertEqual(response.status_code, 302)  # Should redirect to preview

if __name__ == '__main__':
    unittest.main() 