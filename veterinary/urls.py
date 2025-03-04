from django.urls import path
from .views import (
    UserCreateView,
    AppointmentsListView,
    AppointmentsUpdateView,
    AppointmentsDeleteView,
    MessageListView,
    MessageMarkAsReadView,
    ScheduleListView,
    PetListView,
)

urlpatterns = [
    path('users/create/', UserCreateView.as_view(), name='user-create'),
    path('appointments/', AppointmentsListView.as_view(), name='appointments-list'),
    path('appointments/<int:pk>/update/', AppointmentsUpdateView.as_view(), name='appointments-update'),
    path('appointments/<int:pk>/delete/', AppointmentsDeleteView.as_view(), name='appointments-delete'),
    path('messages/', MessageListView.as_view(), name='messages-list'),
    path('messages/<int:pk>/mark-as-read/', MessageMarkAsReadView.as_view(), name='messages-mark-as-read'),
    path('schedule/', ScheduleListView.as_view(), name='schedule-list'),
    path('pets/', PetListView.as_view(), name='pets-list'),
]
