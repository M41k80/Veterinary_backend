import graphene
from graphene_django.types import DjangoObjectType
from .models import User, Pet, Appointments, Messages, Schedule
from graphql_jwt.decorators import login_required
import graphql_jwt
from django.contrib.auth import get_user_model


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email", "role")


class PetType(DjangoObjectType):
    class Meta:
        model = Pet
        fields = ("id", "name", "breed", "age", "owner")


class AppointmentType(DjangoObjectType):
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
        owner = User.objects.get(id=owner_id, role='owner')
        pet = Pet(name=name, breed=breed, age=age, owner=owner)
        pet.save()
        return CreatePet(pet=pet)


class CreateAppointment(graphene.Mutation):
    class Arguments:
        pet_id = graphene.Int(required=True)
        veterinarian_id = graphene.Int(required=True)
        date = graphene.String(required=True)
        reason = graphene.String(required=True)

    appointment = graphene.Field(AppointmentType)

    @login_required
    def mutate(self, info, pet_id, veterinarian_id, date, reason):
        pet = Pet.objects.get(id=pet_id)
        veterinarian = User.objects.get(id=veterinarian_id, role='vet')
        appointment = Appointments(pet=pet, veterinarian=veterinarian, date=date, reason=reason, status='pending')
        appointment.save()
        return CreateAppointment(appointment=appointment)


class UpdateAppointmentStatus(graphene.Mutation):
    class Arguments:
        appointment_id = graphene.Int(required=True)
        status = graphene.String(required=True)

    appointment = graphene.Field(AppointmentType)

    @login_required
    def mutate(self, info, appointment_id, status):
        appointment = Appointments.objects.get(id=appointment_id)
        appointment.status = status
        appointment.save()
        return UpdateAppointmentStatus(appointment=appointment)


class SendMessage(graphene.Mutation):
    class Arguments:
        owner_id = graphene.Int(required=True)
        veterinarian_id = graphene.Int(required=True)
        content = graphene.String(required=True)

    message = graphene.Field(MessageType)

    @login_required
    def mutate(self, info, owner_id, veterinarian_id, content):
        owner = User.objects.get(id=owner_id, role='owner')
        veterinarian = User.objects.get(id=veterinarian_id, role='vet')
        message = Messages(owner=owner, veterinarian=veterinarian, content=content)
        message.save()
        return SendMessage(message=message)


class MarkMessageAsRead(graphene.Mutation):
    class Arguments:
        message_id = graphene.Int(required=True)

    message = graphene.Field(MessageType)

    @login_required
    def mutate(self, info, message_id):
        message = Messages.objects.get(id=message_id)
        message.mark_as_read()
        return MarkMessageAsRead(message=message)


class ManageSchedule(graphene.Mutation):
    class Arguments:
        veterinarian_id = graphene.Int(required=True)
        day = graphene.String(required=True)
        start_time = graphene.String(required=True)
        end_time = graphene.String(required=True)

    schedule = graphene.Field(ScheduleType)

    @login_required
    def mutate(self, info, veterinarian_id, day, start_time, end_time):
        veterinarian = User.objects.get(id=veterinarian_id, role='vet')
        schedule = Schedule(veterinarian=veterinarian, day=day, start_time=start_time, end_time=end_time)
        schedule.save()
        return ManageSchedule(schedule=schedule)


class TokenAuthMutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


class Mutation(TokenAuthMutation, graphene.ObjectType):
    create_owner = CreateOwner.Field()
    create_pet = CreatePet.Field()
    create_appointment = CreateAppointment.Field()
    update_appointment_status = UpdateAppointmentStatus.Field()
    send_message = SendMessage.Field()
    mark_message_as_read = MarkMessageAsRead.Field()
    manage_schedule = ManageSchedule.Field()


class Query(graphene.ObjectType):
    all_pets = graphene.List(PetType)
    all_appointments = graphene.List(AppointmentType)
    all_messages = graphene.List(MessageType)
    all_schedules = graphene.List(ScheduleType)

    @login_required
    def resolve_all_pets(root, info):
        user = info.context.user
        if user.role == 'owner':
            return Pet.objects.filter(owner=user)
        return Pet.objects.all()

    @login_required
    def resolve_all_appointments(root, info):
        user = info.context.user
        if user.role == 'vet':
            return Appointments.objects.filter(veterinarian=user)
        elif user.role == 'owner':
            return Appointments.objects.filter(pet__owner=user)
        return Appointments.objects.all()

    @login_required
    def resolve_all_messages(root, info):
        user = info.context.user
        if user.role == 'vet':
            return Messages.objects.filter(veterinarian=user)
        elif user.role == 'owner':
            return Messages.objects.filter(owner=user)
        return Messages.objects.all()

    @login_required
    def resolve_all_schedules(root, info):
        user = info.context.user
        if user.role == 'vet':
            return Schedule.objects.filter(veterinarian=user)
        return Schedule.objects.all()


schema = graphene.Schema(query=Query, mutation=Mutation)
