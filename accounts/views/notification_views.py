from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from accounts.models import Notification
from accounts.serializers import NotificationSerializer
from rest_framework.pagination import PageNumberPagination



# ============================================================
#  PAGINATION
# ============================================================
    
class NotificationPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50
    
 
# ============================================================
#  LIST NOTIFICATIONS
# ============================================================   
    
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = NotificationPagination
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')
    
    

# ============================================================
#  MARK A SINGLE NOTIFICATION AS READ
# ============================================================
    
class NotificationMarkReadView(generics.UpdateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        from django.shortcuts import get_object_or_404
        return get_object_or_404(Notification, id=self.kwargs['id'], user=self.request.user)
    
    def patch(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        
        return Response({
            "message": "Notification marked as read.",
            "unread_count": unread_count
            }, status=200)
    

# ============================================================
#  MARK ALL AS READ
# ============================================================


class NotificationMarkAllReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def patch(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        unread_count = 0
        return Response({
            "message": "All notifications marked as read.",
            "unread_count": unread_count
        }, status=status.HTTP_200_OK)
        

# ============================================================
#  GET UNREAD COUNT
# ============================================================

class UnreadNotificationCountView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({"unread_count": count}, status=status.HTTP_200_OK)
