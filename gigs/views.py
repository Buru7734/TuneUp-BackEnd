
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from .models import Gig, GigApplication, Tag
from .serializers import GigSerializer, TagSerializer, GigApplicationSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from accounts.models import Notification




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
    
# Create your views here.

class ApplyToGigView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, gig_id):
        gig = get_object_or_404(Gig, id=gig_id)
        
        if gig.organizer == request.user:
            return Response({"error":"You cannot apply to your own gig."},status=status.HTTP_400_BAD_REQUEST)
        
        if GigApplication.objects.filter(gig=gig, applicant=request.user).exists():
            return Response({"message": "You already applied to this gig."}, status=status.HTTP_400_BAD_REQUEST)
        
        message = request.data.get("message", "")
        GigApplication.objects.create(applicant=request.user, gig=gig, message=message)
        
       

        Notification.objects.create(
            user=gig.organizer,
            message=f"{request.user.username} applied to your gig '{gig.title}'."
            )
        # Notification.cleanup_for_user(gig.organizer)
        
        return Response({"message": f"Application sent for gig '{gig.title}'."}, status=status.HTTP_201_CREATED)
    
class GigApplicationsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, gig_id):
        gig = get_object_or_404(Gig, id=gig_id)
        
        if gig.organizer != request.user:
            return Response({"error": "You can only view applications for your own gigs."}, status=status.HTTP_403_FORBIDDEN)
        
        applications = gig.applications.select_related('applicant').all().order_by('-created_at')
        serializer = GigApplicationSerializer(applications, many=True)    
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ReviewApplicationView(APIView):
    permission_classes = [IsAuthenticated]
        
    def post(self, request, app_id):
        application = get_object_or_404(GigApplication, id=app_id)
        gig = application.gig
            
        if gig.organizer != request.user:
            return Response({"error": "You can only review applications for your own gigs."}, status=status.HTTP_403_FORBIDDEN)
        
        action = request.data.get("action")
        
        if action not in ['accept', 'reject']:
            return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)
        
        if action == 'accept':
            application.status = 'accepted'
            gig.musicians.add(application.applicant)
        else:
            application.status = 'rejected'
        application.save()
        
        Notification.objects.create(
            user=application.applicant,
            message=f"Your application for '{gig.title}' was {application.status}"
        )
        
        # Notification.cleanup_for_user(application.applicant)
        
        return Response({"message": f"Application {action}ed successfully."}, status=status.HTTP_200_OK)

class TagListView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self,request):
        tags = Tag.objects.all().order_by('name')
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self,request):

        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TagDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    
    def get_object(self, id):
        return get_object_or_404(Tag, id=id)
    
    def get(self,request, id):
        tag = self.get_object(id) 
        serializer = TagSerializer(tag)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def put(self,request, id):
        tag = self.get_object(id)
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required."}, status=status.HTTP_403_FORBIDDEN)
        if tag.created_by != request.user:
            return Response({"error": "You can only edit tags you created."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = TagSerializer(tag, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):
        tag = self.get_object(id)
        
        if not request.user.is_authenticated:
            return Response({"error": "Only organizers can delete tags."}, status=status.HTTP_403_FORBIDDEN)
        
        if tag.created_by != request.user:
            
            return Response({"error": "You can only delete tags you created."}, status=status.HTTP_403_FORBIDDEN)
        
        tag.delete()
        return Response({"message": "Tag deleted successfully."}, status=status.HTTP_204_NO_CONTENT)