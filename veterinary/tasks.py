from celery import shared_task
import requests
from django.utils.timezone import now, timedelta
from django.conf import settings
from .models import Appointments


@shared_task
def send_daily_appointment_reminders():
    """Busca citas para el día siguiente y envía recordatorios."""
    tomorrow = now().date() + timedelta(days=1)
    appointments = Appointments.objects.filter(date=tomorrow)

    for appointment in appointments:
        owner_email = appointment.pet.owner.email
        pet_name = appointment.pet.name
        appointment_date = appointment.date.strftime("%d/%m/%Y %H:%M")
        vet_name = appointment.veterinarian.first_name

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
        print(f"Email sent to {owner_email}: {response.status_code}")
