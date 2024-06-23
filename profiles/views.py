from rest_framework.generics import RetrieveUpdateAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser, FormParser
from accounts.views import VerifyUserEmail
from profiles.serializers import (
                                ProfileSerializer, EmailChangeSerializer, ReferralSerializer,NotificationSerializer, PaymentSerializer, PaymentVerifySerializer)
from profiles.models import *

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from paystackapi.transaction import Transaction
import uuid


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


import logging

logger = logging.getLogger(__name__)

class PaymentCreateView(generics.CreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=PaymentSerializer)
    def create(self, request, *args, **kwargs):
        profile = request.user.profile
        ngn_amount = request.data.get('ngn_amount')
        
        # debugging to check if amount is null
        if ngn_amount is None:
            return Response({'error': 'ngn_amount is required'}, status=status.HTTP_400_BAD_REQUEST)


        # Generate unique reference
        reference = str(uuid.uuid4())

        # Create payment record
        payment = Payment.objects.create(profile=profile, ngn_amount=ngn_amount, reference=reference)

        # Initialize Paystack transaction
        transaction = Transaction.initialize(reference=reference, amount=int(ngn_amount) * 100, email=request.user.email, callback_url='http://127.0.0.1/docs/')
        logger.debug(transaction)  # Log the Paystack response

        if not transaction['status']:
            payment.delete()
            return Response({'error': 'Unable to create Paystack transaction', 'details': transaction}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'payment_url': transaction['data']['authorization_url']}, status=status.HTTP_201_CREATED)
    

class PaymentVerifyView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=PaymentVerifySerializer)
    def post(self, request, *args, **kwargs):
        reference = request.data.get('reference')
        try:
            payment = Payment.objects.get(reference=reference, profile=request.user.profile)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)

        # Verify Paystack transaction
        response = Transaction.verify(reference)
        if not response['status']:
            return Response({'error': 'Unable to verify Paystack transaction'}, status=status.HTTP_400_BAD_REQUEST)

        # Update payment status
        if response['data']['status'] == 'success':
            payment.status = 'success'
            payment.profile.account_balance += float(payment.ngn_amount)
            payment.profile.save()
        else:
            payment.status = 'failed'
        payment.save()

        return Response({'status': payment.status}, status=status.HTTP_200_OK)




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
    
    
class ReferralListView(generics.ListAPIView):
    serializer_class = ReferralSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Referral.objects.filter(profile=self.request.user.profile)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": "No referrals "}, status=200)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ReferralCreateView(generics.CreateAPIView):
    serializer_class = ReferralSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=ReferralSerializer)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

class ReferralDetailView(generics.RetrieveAPIView):
    serializer_class = ReferralSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return Referral.objects.filter(profile=self.request.user.profile) 
