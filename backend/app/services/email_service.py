import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
from jinja2 import Template
import os

from app.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """Email service for sending verification, password reset, and notification emails."""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_USER
        
        # Load email templates
        self.templates = self._load_templates()
    
    def _load_templates(self) -> dict:
        """Load email templates from files."""
        templates_dir = os.path.join(os.path.dirname(__file__), 'templates', 'emails')
        templates = {}
        
        template_files = {
            'verification': 'verification.html',
            'password_reset': 'password_reset.html',
            'welcome': 'welcome.html',
            'notification': 'notification.html'
        }
        
        for name, filename in template_files.items():
            template_path = os.path.join(templates_dir, filename)
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    templates[name] = Template(f.read())
            else:
                # Use default templates
                templates[name] = self._get_default_template(name)
        
        return templates
    
    def _get_default_template(self, template_name: str) -> Template:
        """Get default email templates."""
        default_templates = {
            'verification': """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background-color: #4f46e5; color: white; padding: 20px; text-align: center; }
                    .content { padding: 30px; background-color: #f9f9f9; }
                    .button { display: inline-block; padding: 12px 24px; background-color: #4f46e5; 
                            color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
                    .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Legal Model Finetuner</h1>
                    </div>
                    <div class="content">
                        <h2>Verify Your Email Address</h2>
                        <p>Hello {{username}},</p>
                        <p>Thank you for registering with Legal Model Finetuner. Please verify your email address by clicking the button below:</p>
                        <p style="text-align: center;">
                            <a href="{{verification_url}}" class="button">Verify Email Address</a>
                        </p>
                        <p>Or copy and paste this link in your browser:</p>
                        <p style="word-break: break-all;">{{verification_url}}</p>
                        <p>This link will expire in 48 hours.</p>
                        <p>If you didn't create an account with us, please ignore this email.</p>
                    </div>
                    <div class="footer">
                        <p>&copy; 2024 Legal Model Finetuner. All rights reserved.</p>
                        <p>This is an automated message, please do not reply to this email.</p>
                    </div>
                </div>
            </body>
            </html>
            """,
            'password_reset': """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background-color: #4f46e5; color: white; padding: 20px; text-align: center; }
                    .content { padding: 30px; background-color: #f9f9f9; }
                    .button { display: inline-block; padding: 12px 24px; background-color: #4f46e5; 
                            color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
                    .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Legal Model Finetuner</h1>
                    </div>
                    <div class="content">
                        <h2>Reset Your Password</h2>
                        <p>Hello {{username}},</p>
                        <p>We received a request to reset your password. Click the button below to create a new password:</p>
                        <p style="text-align: center;">
                            <a href="{{reset_url}}" class="button">Reset Password</a>
                        </p>
                        <p>Or copy and paste this link in your browser:</p>
                        <p style="word-break: break-all;">{{reset_url}}</p>
                        <p>This link will expire in 24 hours.</p>
                        <p>If you didn't request a password reset, please ignore this email.</p>
                        <p><strong>Security Tip:</strong> Never share your password with anyone.</p>
                    </div>
                    <div class="footer">
                        <p>&copy; 2024 Legal Model Finetuner. All rights reserved.</p>
                        <p>This is an automated message, please do not reply to this email.</p>
                    </div>
                </div>
            </body>
            </html>
            """,
            'welcome': """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background-color: #4f46e5; color: white; padding: 20px; text-align: center; }
                    .content { padding: 30px; background-color: #f9f9f9; }
                    .button { display: inline-block; padding: 12px 24px; background-color: #4f46e5; 
                            color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }
                    .feature { margin: 15px 0; padding: 10px; background: white; border-left: 4px solid #4f46e5; }
                    .footer { text-align: center; padding: 20px; color: #666; font-size: 12px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Welcome to Legal Model Finetuner!</h1>
                    </div>
                    <div class="content">
                        <p>Hello {{username}},</p>
                        <p>Welcome to Legal Model Finetuner! We're excited to have you on board.</p>
                        
                        <div class="feature">
                            <h3>📊 Upload Legal Datasets</h3>
                            <p>Upload JSON files containing legal documents for training.</p>
                        </div>
                        
                        <div class="feature">
                            <h3>🤖 Fine-tune Models</h3>
                            <p>Train BART and PEGASUS models for summarization and simplification.</p>
                        </div>
                        
                        <div class="feature">
                            <h3>📄 Process PDFs</h3>
                            <p>Extract text, generate summaries, and simplify legal documents.</p>
                        </div>
                        
                        <div class="feature">
                            <h3>🌐 Multi-language Support</h3>
                            <p>Translate and transliterate text between English and Indian languages.</p>
                        </div>
                        
                        <p style="text-align: center; margin-top: 30px;">
                            <a href="{{dashboard_url}}" class="button">Get Started</a>
                        </p>
                        
                        <p>Need help? Check out our <a href="{{docs_url}}">documentation</a> or contact support.</p>
                    </div>
                    <div class="footer">
                        <p>&copy; 2024 Legal Model Finetuner. All rights reserved.</p>
                        <p>This is an automated message, please do not reply to this email.</p>
                    </div>
                </div>
            </body>
            </html>
            """
        }
        
        return Template(default_templates.get(template_name, "<p>{{message}}</p>"))
    
    def send_email(self, to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
        """Send an email."""
        if not all([self.smtp_host, self.smtp_port, self.smtp_user, self.smtp_password]):
            logger.warning("SMTP configuration not set. Email not sent.")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Create plain text version
            if text_content:
                msg.attach(MIMEText(text_content, 'plain'))
            
            # Create HTML version
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent to {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def send_verification_email(self, to_email: str, username: str, token: str) -> bool:
        """Send email verification email."""
        verification_url = f"http://localhost:3000/verify-email?token={token}"
        
        html_content = self.templates['verification'].render(
            username=username,
            verification_url=verification_url
        )
        
        text_content = f"""Hello {username},

Please verify your email address by clicking the link below:
{verification_url}

This link will expire in 48 hours.

If you didn't create an account with us, please ignore this email.

Legal Model Finetuner Team
"""
        
        return self.send_email(
            to_email=to_email,
            subject="Verify Your Email Address - Legal Model Finetuner",
            html_content=html_content,
            text_content=text_content
        )
    
    def send_password_reset_email(self, to_email: str, username: str, token: str) -> bool:
        """Send password reset email."""
        reset_url = f"http://localhost:3000/reset-password?token={token}"
        
        html_content = self.templates['password_reset'].render(
            username=username,
            reset_url=reset_url
        )
        
        text_content = f"""Hello {username},

We received a request to reset your password. Click the link below to create a new password:
{reset_url}

This link will expire in 24 hours.

If you didn't request a password reset, please ignore this email.

Security Tip: Never share your password with anyone.

Legal Model Finetuner Team
"""
        
        return self.send_email(
            to_email=to_email,
            subject="Reset Your Password - Legal Model Finetuner",
            html_content=html_content,
            text_content=text_content
        )
    
    def send_welcome_email(self, to_email: str, username: str) -> bool:
        """Send welcome email."""
        dashboard_url = "http://localhost:3000/dashboard"
        docs_url = "http://localhost:3000/docs"
        
        html_content = self.templates['welcome'].render(
            username=username,
            dashboard_url=dashboard_url,
            docs_url=docs_url
        )
        
        text_content = f"""Hello {username},

Welcome to Legal Model Finetuner! We're excited to have you on board.

Here's what you can do:
• Upload legal datasets in JSON format
• Fine-tune BART and PEGASUS models
• Process PDF documents
• Translate between languages
• Generate summaries and simplifications

Get started: {dashboard_url}

Need help? Check out our documentation: {docs_url}

Legal Model Finetuner Team
"""
        
        return self.send_email(
            to_email=to_email,
            subject="Welcome to Legal Model Finetuner!",
            html_content=html_content,
            text_content=text_content
        )
    
    def send_notification_email(self, to_email: str, username: str, notification_type: str, data: dict) -> bool:
        """Send notification email."""
        notifications = {
            'training_completed': {
                'subject': 'Training Completed - Legal Model Finetuner',
                'template_data': {
                    'title': 'Training Completed',
                    'message': f"Your model '{data.get('model_name', '')}' has completed training.",
                    'details': data
                }
            },
            'training_failed': {
                'subject': 'Training Failed - Legal Model Finetuner',
                'template_data': {
                    'title': 'Training Failed',
                    'message': f"Your model training job '{data.get('job_id', '')}' has failed.",
                    'details': data
                }
            },
            'inference_completed': {
                'subject': 'Inference Completed - Legal Model Finetuner',
                'template_data': {
                    'title': 'Inference Completed',
                    'message': 'Your inference request has been processed.',
                    'details': data
                }
            }
        }
        
        if notification_type not in notifications:
            logger.warning(f"Unknown notification type: {notification_type}")
            return False
        
        notification = notifications[notification_type]
        template_data = notification['template_data']
        template_data['username'] = username
        
        html_content = self.templates['notification'].render(**template_data)
        
        return self.send_email(
            to_email=to_email,
            subject=notification['subject'],
            html_content=html_content
        )