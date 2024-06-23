from rest_framework.generics import RetrieveUpdateAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated 
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser, FormParser

from profiles.serializers import (
                                ProfileSerializer, EmailChangeSerializer)
from profiles.models import Profile

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_email(subject,body,recipient):
    name = "Balldraft Fantasy"
    address = "Balldraft Fantasy Club"
    phone_number = "support@balldraft.com"
    context ={
        "subject": subject,
        "body":body,
        "name": name,
        "address": address,
        "phone_number":phone_number
        }
    html_content = render_to_string("emails.html", context)
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.EMAIL_HOST_USER ,
        [recipient]
    )
    email.attach_alternative(html_content, 'text/html')
    email.send()



from accounts.views import VerifyUserEmail
class ProfileView(RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]


    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

    @swagger_auto_schema(request_body=ProfileSerializer)
    def put(self, request, *args, **kwargs):
        user = self.get_object()  # Get the profile object associated with the user
        serializer = ProfileSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=ProfileSerializer)
    def patch(self, request, *args, **kwargs):
        return self.put(request, *args, **kwargs)

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Notification
from .serializers import NotificationSerializer

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(profile=self.request.user.profile).order_by('-time')

@api_view(['POST'])
def mark_as_read(request, pk):
    try:
        notification = Notification.objects.get(pk=pk, profile=request.user.profile)
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
    
    notification.read = True
    notification.save()
    return Response({'status': 'Notification marked as read'}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_notification(request, pk):
    try:
        notification = Notification.objects.get(pk=pk, profile=request.user.profile)
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
    
    notification.delete()
    return Response({'status': 'Notification deleted'}, status=status.HTTP_200_OK)


class EmailChangeView(UpdateAPIView):
    serializer_class = EmailChangeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    @swagger_auto_schema(request_body=EmailChangeSerializer)
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_email = serializer.validated_data['new_email']

        user.email = new_email
        user.save()
        
        # Update the email in the Profile model
        profile = Profile.objects.get(user=user)
        profile.email = new_email
        profile.save()

        return Response({'detail': 'Email updated successfully'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=EmailChangeSerializer)
    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)