from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('vet', 'Veterinarian'),
        ('receptionist', 'Receptionist'),
        ('owner', 'Pet Owner'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    # Agregar related_name único para evitar conflictos
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="veterinary_user_groups",  # Nombre único para groups
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="veterinary_user_permissions",  # Nombre único para user_permissions
        related_query_name="user",
    )


class Pet(models.Model):
    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Appointments(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE)
    veterinarian = models.ForeignKey(User, limit_choices_to={'role': 'vet'}, on_delete=models.CASCADE)
    date = models.DateTimeField()
    reason = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved')])
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if self.veterinarian.role != 'vet':
            raise ValueError("The role is not a veterinarian")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Appointment for {self.pet.name} with {self.veterinarian} on {self.date}"


class Messages(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    veterinarian = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipient')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def mark_as_read(self):
        self.is_read = True
        self.save()

    def __str__(self):
        return f"Message from {self.owner} to {self.veterinarian}"


class Schedule(models.Model):
    veterinarian = models.ForeignKey(User, on_delete=models.CASCADE)
    day = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"Schedule for {self.veterinarian} on {self.day} from {self.start_time} to {self.end_time}"
