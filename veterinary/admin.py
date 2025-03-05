from django.contrib import admin
from .models import User, Pet, Appointments, Messages, Schedule


@admin.register(User)
class VeterinarianAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name', 'email', 'role')


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'breed', 'age', 'owner')


@admin.register(Appointments)
class AppointmentsAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'pet', 'veterinarian', 'reason', 'status', 'notes')


def mark_as_read(request, queryset):
    queryset.update(is_read=True)


@admin.register(Messages)
class MessagesAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'veterinarian', 'content', 'timestamp', 'is_read')
    actions = ['mark_as_read']

