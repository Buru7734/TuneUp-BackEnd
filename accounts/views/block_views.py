from rest_framework import permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

from accounts.models import CustomUser, FollowRequest, Notification
from accounts.serializers import UserMiniSerializer



# ============================================================
#  BLOCK USER
# ============================================================

class BlockUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, user_id):
        target_user = get_object_or_404(CustomUser, id=user_id)
        
        if target_user == request.user:
            return Response({"error":"You cannot block yourself."},status=400)
        
        request.user.following.remove(target_user)
        request.user.followers.remove(target_user)
        FollowRequest.objects.filter(
            Q(from_user=request.user, to_user=target_user) |
            Q(from_user=target_user, to_user=request.user)
        ).delete()
        
        request.user.blocks.add(target_user)
        
        Notification.objects.create(
            user=target_user,
            message=f"{request.user.username} has blocked you."
        )
        
        return Response({"message":f"You blocked {target_user.username}."}, status=200)
 
 

# ============================================================
#  UNBLOCK USER
# ============================================================ 
   
    
class UnblockUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, user_id):
        target_user = get_object_or_404(CustomUser, id=user_id)
        
        if not request.user.blocks.filter(id=target_user.id).exists():
            return Response({"message":"User is not blocked."}, status=200)
        
        request.user.blocks.remove(target_user)
        
        return Response({"message":f"You unblocked {target_user.username}"}, status=200)
   

 
# ============================================================
#  LIST BLOCKED USERS (PAGINATED)
# ============================================================  
 
class BlockedUsersPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50

    
    
class BlockedUsersListView(generics.ListAPIView):
    serializer_class = UserMiniSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        return self.request.user.blocks.all().order_by('username')
    

   