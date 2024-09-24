from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from .models import ContestHistory,Slider
from .serializers import ContestHistorySerializer, SliderSerializer
from rest_framework.exceptions import ValidationError
import requests



class ContestHistoryCreateView(generics.CreateAPIView):
    serializer_class = ContestHistorySerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=ContestHistorySerializer)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = request.user.profile  # Get the profile from the authenticated user
        entry_amount = serializer.validated_data.get('entry_amount')
        game_id = serializer.validated_data.get('game_id')

        if profile.account_balance < entry_amount:
            extra_needed = entry_amount - profile.account_balance
            raise ValidationError(
                {"detail": f"Insufficient balance. You need {extra_needed} more to enter the contest."}
            )

        # Deduct entry amount from account balance
        profile.account_balance -= entry_amount
        profile.save()

        # Send PUT request to update fixture
        response = requests.put(
            f'https://microservice.balldraft.com/update-fixture/{game_id}',
            headers={
                'accept': 'application/json',
                'Content-Type': 'application/json'
            },
            json={'current_entry': 1}
        )

        # Print response
        print(response.text)

        response_data = response.json()
        if response_data.get('message') == "The contest is full":
            # Return entry amount to account balance
            profile.account_balance += entry_amount
            profile.save()
            return Response(
                {"detail": "The contest is already full"},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif response.status_code == 200:
            self.perform_create(serializer)
            return Response("Contest Created Successfully", status=status.HTTP_201_CREATED)
        else:
            # Handle unexpected errors
            return Response(
                {"detail": "An unexpected error occurred while entering the contest"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def perform_create(self, serializer):
        profile = self.request.user.profile  # Get the profile from the authenticated user
        serializer.save(profile=profile)


class ContestHistoryDetailView(generics.RetrieveAPIView):
    serializer_class = ContestHistorySerializer
    permission_classes = [IsAuthenticated]
    queryset = ContestHistory.objects.all()
    lookup_field = 'pk'

    def get_queryset(self):
        return ContestHistory.objects.filter(profile=self.request.user.profile)


class ContestHistoryListView(generics.ListAPIView):
    serializer_class = ContestHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ContestHistory.objects.filter(profile=self.request.user.profile)


class ContestHistoryUpdateView(generics.UpdateAPIView):
    serializer_class = ContestHistorySerializer
    permission_classes = [IsAuthenticated]
    queryset = ContestHistory.objects.all()
    lookup_field = 'pk'

    @swagger_auto_schema(request_body=ContestHistorySerializer)
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SliderListCreateView(generics.ListAPIView):
    queryset = Slider.objects.all().order_by('-created_at')
    serializer_class = SliderSerializer

    @swagger_auto_schema(
        operation_summary="List all slider items",
        operation_description="Retrieve a list of all slider items with text and images.",
        responses={200: SliderSerializer(many=True)},
        tags=["Slider"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class SliderDetailView(generics.RetrieveAPIView):
    queryset = Slider.objects.all()
    serializer_class = SliderSerializer

    @swagger_auto_schema(
        operation_summary="Retrieve a slider item",
        operation_description="Retrieve a specific slider item by its ID.",
        responses={200: SliderSerializer},
        tags=["Slider"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

