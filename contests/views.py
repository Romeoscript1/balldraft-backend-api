from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from .models import ContestHistory
from .serializers import ContestHistorySerializer

class ContestHistoryCreateView(generics.CreateAPIView):
    serializer_class = ContestHistorySerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=ContestHistorySerializer)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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
