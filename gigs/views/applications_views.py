from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models import Gig, GigApplication
from ..serializers import GigApplicationSerializer
from accounts.models import Notification


class ApplyToGigView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
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
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, gig_id):
        gig = get_object_or_404(Gig, id=gig_id)
        
        if gig.organizer != request.user:
            return Response({"error": "You can only view applications for your own gigs."}, status=status.HTTP_403_FORBIDDEN)
        
        applications = gig.applications.select_related('applicant').all().order_by('-created_at')
        serializer = GigApplicationSerializer(applications, many=True)    
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ReviewApplicationView(APIView):
    permission_classes = [permissions.IsAuthenticated]
        
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

