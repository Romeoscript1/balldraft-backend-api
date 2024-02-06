from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from .serializers import UserRegisterSerializer
from rest_framework.response import Response
from rest_framework import status
from .utils import send_code_to_user



class RegisterUserView(GenericAPIView):
    serializer_class=UserRegisterSerializer

    def post(self, request):
        user_data=request.data
        serializer=self.serializer_class(data=user_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user=serializer.data
            send_code_to_user(user['email'])
            #send email function user['email]
            return Response({
                'status': 200,
                'data':user,
                'message':f'Welcome {user['first_name']} to Balldraft. Thanks for signing up. Check your mail for you passcode.'
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)