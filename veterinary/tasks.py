from celery import shared_task
from django.utils.timezone import now, timedelta
from .models import Appointments
from .utils import send_appointment_reminder


@shared_task
def send_daily_appointment_reminders():
    """
    Busca citas programadas para el día siguiente y envía recordatorios por email usando Resend.
    """
    tomorrow = now().date() + timedelta(days=1)
    appointments = Appointments.objects.filter(date=tomorrow)

    for appointment in appointments:
        try:
            owner_email = appointment.pet.owner.email
            pet_name = appointment.pet.name
            appointment_date = appointment.date.strftime("%d/%m/%Y %H:%M")
            vet_name = appointment.veterinarian.first_name

            send_appointment_reminder(owner_email, pet_name, appointment_date, vet_name)
        except Exception as e:
            print(f"Error sending reminder for {appointment.pet.name}: {e}")
