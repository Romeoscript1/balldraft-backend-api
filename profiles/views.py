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
                                ProfileSerializer, EmailChangeSerializer,HelpSerializer,  WithdrawSerializer,NotificationSerializer, PaymentSerializer, PaymentVerifySerializer, UserActivitySerializer, TransactionHistorySerializer)
from profiles.models import *
from paystackapi.paystack import Paystack
from paystackapi.transaction import Transaction
from paystackapi.transfer import Transfer
from paystackapi.paystack import TransferRecipient
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from paystackapi.transaction import Transaction
import uuid
paystack = Paystack(secret_key=settings.PAYSTACK_SECRET_KEY)

from django.conf import settings

import logging

logger = logging.getLogger(__name__)




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


class UserActivityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.profile

        # Get the last login time
        last_login = request.user.last_login
        

        # Get the most recent deposit made by the user, if any
        recent_deposit = Deposit.objects.filter(profile=profile, verified=True).order_by('-time').first()

        if recent_deposit:
            # Ensure that recent_deposit.time is treated as a datetime object
            if isinstance(recent_deposit.time, (str, bytes)):
                recent_deposit_time = "Invalid date format"
            else:
                recent_deposit_time = recent_deposit.time.strftime('%B %d, %Y')  # Convert datetime to "January 4, 2023" format
            recent_deposit_amount = str(recent_deposit.ngn_amount)  # Convert Decimal to string
        else:
            recent_deposit_time = "No recent deposit made"
            recent_deposit_amount = "No recent deposit made"

        # Get the total points from the Profile model
        total_points = profile.total_points

        # Prepare the data for the response
        data = {
            "last_login": last_login,
            "recent_deposit_time": recent_deposit_time,
            "recent_deposit_amount": recent_deposit_amount,
            "total_points": total_points,
        }

        # Serialize the data
        serializer = UserActivitySerializer(data=data)
        if serializer.is_valid():
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)


class HelpmeView(APIView):

    @swagger_auto_schema(request_body=HelpSerializer)
    def post(self, request, *args, **kwargs):
        serializer = HelpSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data['name']
            email = serializer.validated_data['email']
            subject = serializer.validated_data['subject']
            message = serializer.validated_data['message']

            # Prepare email content
            email_subject = f"Support Request from {name}: {subject}"
            email_message = f"Message from {name} ({email}):\n\n{message}"
            recipient_list = settings.SUPPORT_EMAIL  
            
            # Send email
            try:
                send_email(
                    subject,
                    message,
                    recipient_list
                )
                return Response({'message': 'Your message has been sent successfully!'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e), 'message': 'Failed to send the message. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WithdrawCreateView(generics.CreateAPIView):
    serializer_class = WithdrawSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=WithdrawSerializer)
    def create(self, request, *args, **kwargs):
        profile = request.user.profile
        ngn_amount = request.data.get('ngn_amount')
        bank_name = request.data.get('bank_name')
        account_number = request.data.get('account_number')
        comment = request.data.get('comment')

        if not ngn_amount or not bank_name or not account_number:
            return Response({'error': 'ngn_amount, bank_name, and account_number are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if profile.account_balance < float(ngn_amount):
            return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

        # Create transfer recipient
        recipient_data = {
            "type": "nuban",
            "name": profile.username,
            "account_number": account_number,
            "bank_code": self.get_bank_code(bank_name),
            "currency": "NGN"
        }
        recipient_response = TransferRecipient.create(**recipient_data)
        if not recipient_response['status']:
            return Response({'error': 'Unable to create transfer recipient', 'details': recipient_response['message']}, status=status.HTTP_400_BAD_REQUEST)

        recipient_code = recipient_response['data']['recipient_code']

        # Create payment record
        reference = str(uuid.uuid4())
        print(reference)
        withdrawal = Withdraw.objects.create(
            profile=profile,
            ngn_amount=ngn_amount,
            bank_name=bank_name,
            account_number=account_number,
            comment=comment,
            reference=reference
        )


        # Initialize Paystack transfer
        transfer_data = {
            "source": "balance",
            "reason": "Withdrawal to bank account",
            "amount": int(float(ngn_amount) * 100),
            "recipient": recipient_code,
            "reference": reference
        }
        transfer_response = paystack.transfer.initiate(**transfer_data)

        if not transfer_response['status']:
            withdrawal.delete()
            TransactionHistory.objects.create(
            profile=profile,
            action=f"Withdrawal of NGN {ngn_amount} to {bank_name} - {account_number} Failed",
            action_title="Withdrawal Failed",
            category="Withdrawal"
        )
            return Response({'error': 'Unable to initiate Paystack transfer', 'details': transfer_response['message']}, status=status.HTTP_400_BAD_REQUEST)

        # Update profile balance
        profile.account_balance -= float(ngn_amount)
        profile.save()

        TransactionHistory.objects.create(
            profile=profile,
            action=f"Withdrawal of NGN {ngn_amount} to {bank_name} - {account_number}",
            action_title="Withdrawal Pending",
            category="Withdrawal"
        )

        return Response({'message': 'Withdrawal request created successfully'}, status=status.HTTP_201_CREATED)

    def get_bank_code(self, bank_name):
        bank_codes = {
        'Access Bank': '044',
        'Citibank Nigeria': '023',
        'Diamond Bank': '063',
        'Ecobank Nigeria': '050',
        'Fidelity Bank': '070',
        'First Bank of Nigeria': '011',
        'First City Monument Bank': '214',
        'Guaranty Trust Bank': '058',
        'Heritage Bank': '030',
        'Keystone Bank': '082',
        'Polaris Bank': '076',
        'Providus Bank': '101',
        'Stanbic IBTC Bank': '221',
        'Standard Chartered Bank': '068',
        'Sterling Bank': '232',
        'Suntrust Bank': '100',
        'Union Bank of Nigeria': '032',
        'United Bank for Africa': '033',
        'Unity Bank': '215',
        'Wema Bank': '035',
        'Zenith Bank': '057',
        'AB Microfinance Bank': '090134',
        'Addosser Microfinance Bank': '090135',
        'BoI Microfinance Bank': '090136',
        'Fina Trust Microfinance Bank': '090137',
        'Fortis Microfinance Bank': '090138',
        'Lapo Microfinance Bank': '090139',
        'Mainstreet Microfinance Bank': '090140',
        'Microcred Microfinance Bank': '090141',
        'Mutual Trust Microfinance Bank': '090142',
        'NPF Microfinance Bank': '090143',
        'Seed Capital Microfinance Bank': '090144',
        'Sparkle Microfinance Bank': '090145',
        'VFD Microfinance Bank': '090146',
        'Opay': '305',
        'Palmpay': '311',
        'Kuda': '50211',
        'Moniepoint': '50515'
            
        }
        return bank_codes.get(bank_name, None)
      

# class WithdrawVerifyView(generics.UpdateAPIView):
#     serializer_class = WithdrawSerializer
#     permission_classes = [IsAuthenticated]
#     queryset = Withdraw.objects.all()
#     lookup_field = 'reference'

#     @swagger_auto_schema(request_body=PaymentVerifySerializer)
#     def update(self, request, *args, **kwargs):
#         withdrawal = self.get_object()

#         if not withdrawal.verified:
#             reference = request.data.get('reference')
#             try:
#                 withdraw = withdrawal.objects.get(reference=reference, profile=request.user.profile)
#                 return Response({'error': 'Withdrawal request not found'}, status=status.HTTP_404_NOT_FOUND)
#             except Withdraw.DoesNotExist:
#                 return Response({'error': 'Withdrawal does not exist'}, status=status.HTTP_404_NOT_FOUND)
#         else:
#             return Response({'message': 'Withdrawal is already verified'}, status=status.HTTP_400_BAD_REQUEST)

class WithdrawVerifyView(generics.ListAPIView):
    serializer_class = WithdrawSerializer
    permission_classes = [IsAuthenticated]
    queryset = Withdraw.objects.all()
    lookup_field = 'reference'

    @swagger_auto_schema(request_body=PaymentVerifySerializer)
    def update(self, request, *args, **kwargs):
        withdrawal = self.get_object()

        if not withdrawal.verified:
            reference = request.data.get('reference')
            try:
                withdrawal = Withdraw.objects.get(reference=reference, profile=request.user.profile)
            except Withdraw.DoesNotExist:
                return Response({'error': 'Withdrawal request not found'}, status=status.HTTP_404_NOT_FOUND)

            # Assume withdrawal verification logic here
            withdrawal.verified = True
            withdrawal.save()

            # Log the transaction history for verified withdrawal
            TransactionHistory.objects.create(
                profile=request.user.profile,
                action=f"Verified withdrawal of NGN {withdrawal.ngn_amount}",
                action_title="Withdrawal Successful !!",
                category="Withdrawal"
            )

            return Response({'message': 'Withdrawal verified successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Withdrawal is already verified'}, status=status.HTTP_400_BAD_REQUEST)


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
        # Log the transaction history
        TransactionHistory.objects.create(
                profile=request.user.profile,
                action=f"Deposit of NGN {payment.ngn_amount} Pending",
                action_title="Deposit Pending",
                category="Deposit"
            )

        # Initialize Paystack transaction
        transaction = Transaction.initialize(reference=reference, amount=int(ngn_amount) * 100, email=request.user.email, callback_url=settings.PAYMENT_TRANSACTION_CALLBACK_URL)
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
        logger.debug(response)
        if not response['status']:
            return Response({'error': 'Unable to verify Paystack transaction'}, status=status.HTTP_400_BAD_REQUEST)

        # Update payment status
        if response['data']['status'] == 'success':
            payment.status = 'success'
            payment.profile.account_balance += float(payment.ngn_amount)
            payment.profile.save()

            # Log the transaction history for successful payment
            TransactionHistory.objects.create(
                profile=request.user.profile,
                action=f"Deposit of NGN {payment.ngn_amount} verified",
                action_title="Deposit Successful!!",
                category="Deposit"
            )
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

    def retrieve(self, request, *args, **kwargs):
        profile = self.get_object()
        user = request.user

        # Fetch the user activity data
        last_login = user.last_login

        # Get the most recent verified deposit made by the user
        recent_deposit = Deposit.objects.filter(profile=profile, verified=True).order_by('-time').first()
        if recent_deposit:
            recent_deposit_time = recent_deposit.time.strftime('%B %d, %Y') if recent_deposit.time else "Invalid date format"
            recent_deposit_amount = str(recent_deposit.ngn_amount)
        else:
            recent_deposit_time = "No recent deposit made"
            recent_deposit_amount = "No recent deposit made"

        # Fetch total points from the profile property
        total_points = profile.total_points

        # Update the profile object with user activity data
        data = {
            'last_login': last_login,
            'recent_deposit_time': recent_deposit_time,
            'recent_deposit_amount': recent_deposit_amount,
            'total_points': total_points
        }

        serializer = self.get_serializer(profile)
        response_data = serializer.data
        response_data.update(data)  # Merge user activity data with profile data

        return Response(response_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=ProfileSerializer)
    def put(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = ProfileSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return self.retrieve(request, *args, **kwargs)  # Include updated data with activity info
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=ProfileSerializer)
    def patch(self, request, *args, **kwargs):
        return self.put(request, *args, **kwargs)
     

# class ProfileView(RetrieveUpdateAPIView):
#     serializer_class = ProfileSerializer
#     permission_classes = [IsAuthenticated]


#     def get_object(self):
#         profile, created = Profile.objects.get_or_create(user=self.request.user)
#         return profile

#     @swagger_auto_schema(request_body=ProfileSerializer)
#     def put(self, request, *args, **kwargs):
#         user = self.get_object()  # Get the profile object associated with the user
#         serializer = ProfileSerializer(user, data=request.data, partial=True)

#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     @swagger_auto_schema(request_body=ProfileSerializer)
#     def patch(self, request, *args, **kwargs):
#         return self.put(request, *args, **kwargs)


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

        # Update the email directly in the User model
        user.email = new_email
        user.save()

        return Response({'detail': 'Email updated successfully'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=EmailChangeSerializer)
    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
class TransactionHistoryListView(generics.ListAPIView):
    serializer_class = TransactionHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TransactionHistory.objects.filter(profile=self.request.user.profile).order_by('-time')

class TransactionHistoryDetailView(generics.RetrieveAPIView):
    serializer_class = TransactionHistorySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return TransactionHistory.objects.filter(profile=self.request.user.profile)

