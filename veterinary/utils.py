import requests
from django.conf import settings


def send_appointment_reminder(owner_email, pet_name, appointment_date, vet_name):
    subject = f"REMINDER: Appointment for {pet_name}"
    message = f"""
        <p>Hi {owner_email},</p>
        <p>This is a reminder that you have an appointment for <strong>{pet_name}</strong>.</p>
        <p><strong>Date:</strong> {appointment_date}</p>
        <p><strong>Veterinarian:</strong> {vet_name}</p>
        <p>If you need to reschedule or cancel the appointment, please contact us.</p>
        <p>Thank you,</p>
        <p>The Veterinary Team</p>
    """

    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "from": "onboarding@resend.dev",
        "to": [owner_email],
        "subject": subject,
        "html": message
    }

    response = requests.post(url, json=data, headers=headers)
    return response.json()
