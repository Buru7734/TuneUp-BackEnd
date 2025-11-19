
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from ..models import Gig
from ..serializers import GigSerializer
from django.shortcuts import get_object_or_404






class GigListCreateView(APIView):
    permission_classes= [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        
        recommended = request.query_params.get("recommended", "false").lower() == "true"
        
        if recommended:
            if not request.user.is_authenticated:
                return Response(
                    {"error": "Login to see recommended gigs."},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            user_skills = request.user.skills.all()
            gigs = Gig.objects.filter(tags__in=user_skills, is_open=True).distinct().order_by('-created_at')
        else:
            gigs = Gig.objects.filter(is_open=True).order_by('-created_at')
        serializer = GigSerializer(gigs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
    def post(self, request):
        serializer = GigSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(organizer=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GigDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id):
        gig = get_object_or_404(Gig, id=id)
        serializer = GigSerializer(gig)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, id):
        gig = get_object_or_404(Gig, id=id)
        
        if gig.organizer != request.user:
            print("This is the value",gig.organizer)
            print("This is the value2", request.user)
            return Response({"error": "You can only edit your own gigs."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = GigSerializer(gig, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):
        gig = get_object_or_404(Gig, id=id)
        
        if gig.organizer != request.user:
            return Response({"error": "You can only delete your own gigs."}, status=status.HTTP_403_FORBIDDEN)
        
        gig.delete()
        return Response({"message": "Gig deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
