from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth import get_user_model

from accounts.serializers import (
    UserSerializer,
    PublicProfileSerializer,
    UserMiniSerializer,
)
from accounts.models import CustomUser
from rest_framework.exceptions import PermissionDenied

User = get_user_model()

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def put(self,request):
        serializer= UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        user = request.user
        username = user.username
        user.delete()
        return Response(
            {"message": f"User '{username}' deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
            )
    
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        qs = User.objects.all()

        if user.is_authenticated:
            qs = qs.exclude(id__in=user.blocks.values_list("id", flat=True))
            qs = qs.exclude(id__in=user.blocked_by.values_list("id", flat=True))

        return qs
            
        


class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'
    

class PublicProfileView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = PublicProfileSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "id"
    
    def get_object(self):
        obj = super().get_object()
        request = self.request
        
        if request.user.is_authenticated:
            if(
                obj in request.user.blocks.all()
                or request.user in obj.blocks.all()
            ):
                raise PermissionDenied("You cannot view this profile")
        return obj
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context