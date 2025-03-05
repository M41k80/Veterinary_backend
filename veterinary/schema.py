import graphene
from graphene_django.types import DjangoObjectType
from .models import User, Pet, Appointments, Messages, Schedule
from graphql_jwt.decorators import login_required
import graphql_jwt
from django.contrib.auth import get_user_model
from django.conf import settings
from celery import shared_task
import requests
import graphene
from graphene.types.datetime import DateTime


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email", "role")


class PetType(DjangoObjectType):
    class Meta:
        model = Pet
        fields = ("id", "name", "breed", "age", "owner")


class AppointmentType(DjangoObjectType):
    date = DateTime()

    class Meta:
        model = Appointments
        fields = ("id", "pet", "veterinarian", "date", "reason", "status", "notes")


class MessageType(DjangoObjectType):
    class Meta:
        model = Messages
        fields = ("id", "owner", "veterinarian", "content", "timestamp", "is_read")


class ScheduleType(DjangoObjectType):
    class Meta:
        model = Schedule
        fields = ("id", "veterinarian", "day", "start_time", "end_time")


@shared_task
def send_email_reminder(email, pet_name, appointment_date):
    api_key = settings.RESEND_API_KEY
    url = "https://api.resend.com/emails"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "from": "clinic@yourdomain.com",
        "to": email,
        "subject": "Appointment Reminder",
        "text": f"Hello,\n\nThis is a reminder that your pet {pet_name} has an appointment on {appointment_date}.\n\nBest regards,\nYour Veterinary Clinic"
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()


class CreateOwner(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)

    owner = graphene.Field(UserType)

    @login_required
    def mutate(self, info, username, email, first_name, last_name):
        user = info.context.user
        if user.role != 'receptionist':
            raise Exception("Only receptionists can create owners.")
        owner = User(username=username, email=email, first_name=first_name, last_name=last_name, role='owner')
        owner.set_password("defaultpassword")
        owner.save()
        return CreateOwner(owner=owner)


class CreatePet(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        breed = graphene.String(required=True)
        age = graphene.Int(required=True)
        owner_id = graphene.Int(required=True)

    pet = graphene.Field(PetType)

    @login_required
    def mutate(self, info, name, breed, age, owner_id):
        user = info.context.user
        if user.role != 'receptionist':
            raise Exception("Only receptionists can create pets.")
        owner = User.objects.get(id=owner_id, role='owner')
        pet = Pet(name=name, breed=breed, age=age, owner=owner)
        pet.save()
        return CreatePet(pet=pet)


from graphql import GraphQLError


class CreateAppointment(graphene.Mutation):
    class Arguments:
        pet_id = graphene.Int(required=True)
        veterinarian_id = graphene.Int(required=True)
        date = graphene.String(required=True)
        reason = graphene.String(required=True)

    appointment = graphene.Field(AppointmentType)

    @login_required
    def mutate(self, info, pet_id, veterinarian_id, date, reason):
        user = info.context.user
        print(f"Usuario autenticado: {user.username}")  # Depuración
        print(f"Rol del usuario: {user.role}")  # Depuración

        # Verifica que el usuario sea un dueño (owner)
        if user.role != 'owner':
            raise GraphQLError("Only owners can create appointments.")

        try:
            # Verifica que la mascota exista y pertenezca al usuario
            pet = Pet.objects.get(id=pet_id, owner=user)
        except Pet.DoesNotExist:
            raise GraphQLError("Pet not found or does not belong to the user.")

        try:
            # Verifica que el veterinario exista y tenga el rol correcto
            veterinarian = User.objects.get(id=veterinarian_id, role='vet')
        except User.DoesNotExist:
            raise GraphQLError("Veterinarian not found or does not have the correct role.")

        # Crea la cita
        appointment = Appointments(
            pet=pet,
            veterinarian=veterinarian,
            date=date,
            reason=reason,
            status='pending'
        )
        appointment.save()

        return CreateAppointment(appointment=appointment)


class TokenAuthMutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


class Mutation(TokenAuthMutation, graphene.ObjectType):
    create_owner = CreateOwner.Field()
    create_pet = CreatePet.Field()
    create_appointment = CreateAppointment.Field()


class Query(graphene.ObjectType):
    all_pets = graphene.List(PetType)
    all_appointments = graphene.List(AppointmentType)
    all_messages = graphene.List(MessageType)
    all_schedules = graphene.List(ScheduleType)

    @login_required
    def resolve_all_pets(self, info):
        user = info.context.user
        if user.role == 'owner':
            return Pet.objects.filter(owner=user)
        return Pet.objects.all()

    @login_required
    def resolve_all_appointments(self, info):
        user = info.context.user
        if user.role == 'vet':
            return Appointments.objects.filter(veterinarian=user)
        elif user.role == 'owner':
            return Appointments.objects.filter(pet__owner=user)
        return Appointments.objects.all()

    @login_required
    def resolve_all_messages(self, info):
        user = info.context.user
        if user.role == 'vet':
            return Messages.objects.filter(veterinarian=user)
        elif user.role == 'owner':
            return Messages.objects.filter(owner=user)
        return Messages.objects.all()

    @login_required
    def resolve_all_schedules(self, info):
        user = info.context.user
        if user.role == 'vet':
            return Schedule.objects.filter(veterinarian=user)
        return Schedule.objects.all()


schema = graphene.Schema(query=Query, mutation=Mutation)
