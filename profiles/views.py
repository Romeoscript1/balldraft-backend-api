from rest_framework.generics import RetrieveUpdateAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated 
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser, FormParser

from profiles.serializers import (
                                ProfileSerializer)
from profiles.models import Profile

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
    
    
class EmailChangeView(UpdateAPIView):
    serializer_class = EmailChangeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
    @swagger_auto_schema(request_body=EmailChangeSerializer)
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
