import requests
from django.conf import settings


def trigger_email(trigger_type, recipient, context=None):
    try:
        response = requests.post(
            settings.EMAIL_SERVICE_URL,
            json={
                "trigger_type": trigger_type,
                "recipient": recipient,
                "context": context or {},
            },
            timeout=10,
        )

        return response.json()

    except Exception as e:
        print("Email Service Error:", e)
        return None