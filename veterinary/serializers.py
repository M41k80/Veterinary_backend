from datetime import timezone

from rest_framework import serializers
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from .models import User, Pet, Appointments, Messages, Schedule


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'role']


def validate_role(self, value):
    if value not in dict(User.ROLE_CHOICES).keys():
        raise serializers.ValidationError("Rol no válido.")
    return value


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email', 'role']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            role=validated_data['role'],
        )
        group = Group.objects.get(name=validated_data['role'])
        user.groups.add(group)
        return user


def validate_date(value):
    if value < timezone.now():
        raise serializers.ValidationError("Date cannot be in the past")
    return value


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointments
        fields = ['id', 'pet', 'veterinarian', 'date', 'reason', 'status', 'notes']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = ['id', 'owner', 'veterinarian', 'content', 'timestamp', 'is_read']


class PetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = ['id', 'name', 'breed', 'age', 'owner']


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['id', 'veterinarian', 'day', 'start_time', 'end_time']
