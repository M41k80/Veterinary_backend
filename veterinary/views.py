from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from .models import User, Pet, Appointments, Messages, Schedule
from .serializers import UserSerializer, UserCreateSerializer, PetSerializer, AppointmentSerializer, MessageSerializer, \
    ScheduleSerializer
from rest_framework.permissions import BasePermission, IsAuthenticated

class IsVeterinarian(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'Veterinarian'

class IsOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'owner'


class UserCreateView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.IsAdminUser]


class AppointmentsListView(generics.ListCreateAPIView):
    queryset = Appointments.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated, IsVeterinarian | IsOwner]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'Veterinarian':
            return Appointments.objects.filter(veterinarian=user)
        elif user.role == 'owner':
            return Appointments.objects.filter(pet__owner=user)
        return Appointments.objects.all()


class MessageListView(generics.ListCreateAPIView):
    queryset = Messages.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Vets only can see their own Messages
        if self.request.user.role == 'Veterinarian':
            return Messages.objects.filter(veterinarian=self.request.user)
        return Messages.objects.all()


class MessageMarkAsReadView(generics.UpdateAPIView):
    queryset = Messages.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        serializer.instance.mark_as_read()
        serializer.save()


class ScheduleListView(generics.ListCreateAPIView):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'Veterinarian':
            return Schedule.objects.filter(veterinarian=self.request.user)
        return Schedule.objects.all()


class AppointmentsUpdateView(generics.UpdateAPIView):
    queryset = Appointments.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if obj.veterinarian != self.request.user:
            raise PermissionDenied('You do not have permission to update this appointment.')
        return obj


class AppointmentsDeleteView(generics.DestroyAPIView):
    queryset = Appointments.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if obj.veterinarian != self.request.user:
            raise PermissionDenied('You do not have permission to delete this appointment.')
        return obj


class PetListView(generics.ListCreateAPIView):
    queryset = Pet.objects.all()
    serializer_class = PetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Owners only can see their own Pets
        if self.request.user.role == 'Owner':
            return self.queryset.filter(owner=self.request.user)
        return Pet.objects.all()
