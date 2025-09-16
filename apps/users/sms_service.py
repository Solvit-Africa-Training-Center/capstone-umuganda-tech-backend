from twilio.rest import Client
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class SMSService:
    def __init__(self):
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.from_number = settings.TWILIO_PHONE_NUMBER
    
    def send_otp(self, phone_number, otp_code):
        """Send OTP via SMS"""
        try:
            # Format phone number for Rwanda (+250)
            if not phone_number.startswith('+'):
                if phone_number.startswith('250'):
                    phone_number = '+' + phone_number
                else:
                    phone_number = '+250' + phone_number
            
            message = self.client.messages.create(
                body=f'Your UmugandaTech verification code is: {otp_code}. Valid for 5 minutes.',
                from_=self.from_number,
                to=phone_number
            )
            
            logger.info(f'SMS sent successfully to {phone_number}. SID: {message.sid}')
            return True, message.sid
            
        except Exception as e:
            logger.error(f'Failed to send SMS to {phone_number}: {str(e)}')
            return False, str(e)
