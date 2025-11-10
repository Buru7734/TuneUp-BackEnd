from django.shortcuts import render
from .models import Review
from .serializers import ReviewSerializer 
from rest_framework import generics, permissions

# Create your views here.

class ReviewListCreateView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)
        
class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"
    
    def perform_update(self, serializer):
        serializer.save(reviewer=self.request.user)
