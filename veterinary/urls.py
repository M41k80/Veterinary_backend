from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from .schema import schema
from .views import (
    UserCreateView,
    AppointmentsListView,
    AppointmentsUpdateView,
    AppointmentsDeleteView,
    MessageListView,
    MessageMarkAsReadView,
    ScheduleListView,
    PetListView,
    SendEmailReminderView,
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
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema)), name='graphql'),
    path('send-appointment-reminder/', SendEmailReminderView.as_view(), name='send_appointment_reminder'),
]
