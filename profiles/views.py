from rest_framework.generics import RetrieveUpdateAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated 

from profiles.serializers import (MobileNumberSerializer, 
                                AddressSerializer,
                                UserNameUpdateSerializer,
                                EmailChangeSerializer,
                                ProfileSerializer)
from profiles.models import Profile

from accounts.views import VerifyUserEmail

class ProfileView(RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return Profile.objects.get_or_create(user=self.request.user)[0]

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)

class MobileNumberView(RetrieveUpdateAPIView):
    serializer_class = MobileNumberSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return Profile.objects.get_or_create(user=self.request.user)[0]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.get_object()
        instance.mobile_number = serializer.validated_data.get('mobile_number')
        instance.save()
        return Response({'message': 'Mobile number updated successfully'}, status=status.HTTP_200_OK)

class AddressView(RetrieveUpdateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return Profile.objects.get_or_create(user=self.request.user)[0]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.get_object()
        instance.address = serializer.validated_data.get('address')
        instance.country = serializer.validated_data.get('country')
        instance.state = serializer.validated_data.get('state')
        instance.city = serializer.validated_data.get('city')
        instance.zip_code = serializer.validated_data.get('zip_code')
        instance.save()
        return Response({'message': 'Address updated successfully'}, status=status.HTTP_200_OK)

class UserNameUpdateView(UpdateAPIView):
    serializer_class = UserNameUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=self.get_object(), data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Username updated successfully'}, status=status.HTTP_200_OK)

class EmailChangeView(UpdateAPIView):
    serializer_class = EmailChangeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=self.get_object(), data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.get_object()
        new_email = serializer.validated_data['new_email']

        user.email = new_email
        user.save()

        verify_email_view = VerifyUserEmail.as_view()
        response = verify_email_view(request._request)
        return Response(response.data, status=response.status_code)