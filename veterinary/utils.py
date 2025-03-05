import resend
import os
from django.conf import settings

# Asegúrate de que la clave de API está configurada correctamente
resend.api_key = settings.RESEND_API_KEY

def send_appointment_reminder(owner_email, pet_name, appointment_date, vet_name):
    """
    Envía un recordatorio de cita usando Resend.
    """
    message = f"""
        <p>Hi,</p>
        <p>This is a reminder that your pet <strong>{pet_name}</strong> has an appointment.</p>
        <p><strong>Date:</strong> {appointment_date}</p>
        <p><strong>Veterinarian:</strong> {vet_name}</p>
        <p>If you need to reschedule or cancel the appointment, please contact us.</p>
        <p>Thank you,</p>
        <p>The Veterinary Team</p>
    """

    params = {
        "from": "onboarding@resend.dev",  # Asegúrate de que este correo esté verificado en Resend
        "to": [owner_email],
        "subject": f"Reminder: Appointment for {pet_name}",
        "html": message
    }

    try:
        # Enviar correo usando Resend
        email = resend.Emails.send(params)
        print("Email sent successfully!")
        return email
    except Exception as e:
        print(f"Error sending email: {e}")
        return None
