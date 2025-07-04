from flask_mail import Mail, Message
import secrets
from database.connection import get_db_connection
from utils.mail_templates import get_contact_email, get_approve_email, get_deny_mail

mail = Mail()

def setup_mail(app):
    """Initialize mail service"""
    mail.init_app(app)

class MailService:
    @staticmethod
    def send_contact_email(name, email, message):
        """Send contact email"""
        try:
            from flask import current_app
            msg = Message(
                subject='OptiRoad Contact!', 
                sender=current_app.config['MAIL_USERNAME'], 
                recipients=[email]
            )
            msg.html = get_contact_email(name, message)
            mail.send(msg)
            return True, 'Email sent!'
        except Exception as e:
            print(f"Error sending contact email: {e}")
            return False, 'Failed to send email'
    
    @staticmethod
    def send_approve_email(key, name, email):
        """Send registration key email"""
        try:
            from flask import current_app
            msg = Message(
                subject='Your Registration Key', 
                sender=current_app.config['MAIL_USERNAME'], 
                recipients=[email]
            )
            msg.html = get_approve_email(name, key)
            mail.send(msg)
            return True, 'Key email sent!'
        except Exception as e:
            print(f"Error sending key email: {e}")
            return False, 'Failed to send key email'
    
    @staticmethod
    def send_deny_email(name, email):
        """Send email when a user is denied"""
        try:
            from flask import current_app
            msg = Message(
                subject='Your Registration Request', 
                sender=current_app.config['MAIL_USERNAME'], 
                recipients=[email]
            )
            msg.html = get_deny_mail(name)
            mail.send(msg)
            return True, 'Denial email sent!'
        except Exception as e:
            print(f"Error sending denial email: {e}")
            return False, 'Failed to send denial email'
