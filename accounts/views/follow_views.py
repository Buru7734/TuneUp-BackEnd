from rest_framework import status, permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from rest_framework.pagination import PageNumberPagination
import random
import math


from accounts.models import CustomUser, FollowRequest, Notification
from accounts.serializers import UserMiniSerializer


class UnfollowUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, user_id):
        target_user = get_object_or_404(CustomUser, id=user_id)
        print("this is the following", target_user)
        
        if target_user == request.user:
            return Response({"error": "You cannot unfollow yourself"}, status=400)
        
        if not target_user.followers.filter(id=request.user.id).exists():
            return Response({"error": "You are not following this User"})
        
        target_user.followers.remove(request.user)
        return Response({"message":"Unfollow Successful"})


# ============================================================
#  REMOVE FOLLOWER
# ============================================================


class RemoveFollowerView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, user_id):
        follower = get_object_or_404(CustomUser, id=user_id)
        
        if not request.user.followers.filter(id=follower.id).exists():
            return Response({"error": "This user is not your follower."}, status=400)
        
        request.user.followers.remove(follower)
        
        return Response({"message": "Follower removed successfully."}, status=200)
    

# ============================================================
#  FOLLOW REQUESTS (SEND / ACCEPT / REJECT / CANCEL)
# ============================================================
    
    
    
class SendFollowRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, user_id):
        target_user = get_object_or_404(CustomUser, id=user_id)
        
        if target_user == request.user:
            return Response({"error": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)
        
        if target_user in request.user.blocks.all() or request.user in target_user.blocks.all():
            return Response({"error": "You cannot interact with this user."},status=400)
    
        follow_request, created = FollowRequest.objects.get_or_create(
            from_user=request.user,
            to_user=target_user
        )
        
        
        if not created:
            if follow_request.accepted:
                return Response({"message":"You already follow this user."}, status=status.HTTP_200_OK)
            return Response({"message":"FollowRequest already sent."}, status=status.HTTP_200_OK)
            
        Notification.objects.create(
            user=target_user,
            message=f"{request.user.username} requested to follow you."
        )
        
        return Response({"message":"Follow request sent."})
  
    
class AcceptFollowRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, request_id):
        follow_request = get_object_or_404(
            FollowRequest, id=request_id, to_user=request.user
        )
        
        if follow_request.accepted:
            return Response({"message":"Already accepted"}, status=status.HTTP_200_OK)
        
        follow_request.accepted = True
        follow_request.save()
        
        follow_request.to_user.followers.add(follow_request.from_user)
        
        Notification.objects.create(
            user=follow_request.from_user,
            message=f"{request.user.username} accepted your follow request."
        )
        
        return Response({"message":"Follow request accepted."}, status=status.HTTP_200_OK)
    
class RejectFollowRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    
    def post(self, request, request_id):
        follow_request = get_object_or_404(
            FollowRequest, id=request_id, to_user=request.user
        )
        follow_request.delete()
        
        Notification.objects.create(
            user=follow_request.from_user,
            message=f"{request.user.username} rejected your follow request."
        )
        
        
        return Response({"message":"Follow request rejected."}, status=status.HTTP_200_OK)
    
class CancelFollowRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, user_id):
        target_user = get_object_or_404(CustomUser, id=user_id)
        
        follow_request = FollowRequest.objects.filter(
            from_user=request.user,
            to_user=target_user,
            accepted=False
        ).first()
        
        if not follow_request:
            return Response({
                "message":"No pending follow request to cancel."
            })
            
        follow_request.delete()
        
        Notification.objects.create(
            user=target_user,
            message=f"{request.user.username} canceled their follow request."
        )
        
        return Response({"message": "Follow request canceled."}, status=status.HTTP_200_OK)
    

    
class PendingFollowRequestsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        pending = FollowRequest.objects.filter(to_user=request.user, accepted=False)
        data = [
            {
                "id": fr.id,
                "from_user": fr.from_user.username,
                "from_user_id": fr.from_user.id,
                "created_at": fr.created_at
            }
            for fr in pending
        ]
        return Response(data)
    

class SentFollowRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        sent_requests = FollowRequest.objects.filter(from_user=request.user, accepted=False)
        data = [
            {
                "id": fr.id,
                "to_user": fr.to_user.username,
                "to_user_id": fr.to_user.id,
                "created_at": fr.created_at,
            }
            for fr in sent_requests
        ]
        return Response(data)
    
    
# ============================================================
#  MUTUAL FOLLOWERS / FOLLOWING
# ============================================================    


class MutualFollowersView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, user_id, other_id):
        user1 = get_object_or_404(CustomUser, id=user_id)
        user2 = get_object_or_404(CustomUser, id=other_id)
        
        user2_follower_ids = user2.followers.values_list("id", flat=True)
        
        mutuals = user1.followers.filter(id__in=user2_follower_ids)
        
        serializer = UserMiniSerializer(mutuals, many=True)
        
        return Response({
            "count": mutuals.count(),
            "results": serializer.data
        })
        
        
        
        
class MutualFollowingView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, user_id, other_id):
        user1 = get_object_or_404(CustomUser, id=user_id)
        user2 = get_object_or_404(CustomUser, id=other_id)
        
        user1_follows_user2 = user2.followers.filter(id=user1.id).exists()
        
        user2_follows_user1 = user1.followers.filter(id=user2.id).exists()
        
        mutual = user1_follows_user2 and user2_follows_user1
        
        return Response({
            "mutual_following": mutual,
            "user1_follows_user2": user1_follows_user2,
            "user2_follows_user1": user2_follows_user1
        })
        

# ============================================================
#  BASIC FOLLOW SUGGESTIONS
# ============================================================

class FollowSuggestionsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)

        # Get IDs of people the user is already following
        already_following = user.following.values_list("id", flat=True)

        # A base queryset of all other users, excluding yourself and people you already follow
        qs = CustomUser.objects.exclude(id__in=already_following).exclude(id=user.id)
        
        qs = qs.exclude(id__in=user.blocked_by.values_list("id", flat=True))
        qs = qs.exclude(id__in=user.blocks.values_list("id", flat=True))
        # Annotate suggestion relevance:
        qs = qs.annotate(
            # Same city score
            same_city=Count("id", filter=Q(city=user.city)),

            # Skill overlap score
            shared_skills=Count("skills", filter=Q(skills__in=user.skills.all()), distinct=True),

            # Mutual followers (people who follow both)
            mutual_followers=Count(
                "followers",
                filter=Q(followers__in=user.followers.all()),
                distinct=True
            ),

            # People you follow who follow them
            followed_by_following=Count(
                "followers",
                filter=Q(followers__in=user.following.all()),
                distinct=True
            )
        ).order_by(
            "-mutual_followers",
            "-followed_by_following",
            "-shared_skills",
            "-same_city",
            "username",
        )

        # Limit results
        results = qs[:20]

        serializer = UserMiniSerializer(results, many=True)

        return Response({
            "count": qs.count(),
            "results": serializer.data,
        })
        
        
        
# ============================================================
#  ADVANCED FOLLOW SUGGESTIONS
# ============================================================        
        
               
class AdvancedFollowSuggestionsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        cache_key = f"suggestions_{user_id}"

        # ✅ 1. Check cache
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        already_following = set(user.following.values_list("id", flat=True))

        # ✅ 2. Exclude self + already following
        qs = CustomUser.objects.exclude(id=user.id).exclude(id__in=already_following)
        qs = qs.exclude(id__in=user.blocked_by.values_list("id", flat=True))
        qs = qs.exclude(id__in=user.blocks.values_list("id", flat=True))

        # ✅ 3. Exclude inactive users
        recent_cutoff = timezone.now() - timedelta(days=30)
        qs = qs.filter(last_login__gte=recent_cutoff)

        # ✅ 4. Annotate with base signals
        qs = qs.annotate(
            same_city=Count("id", filter=Q(city=user.city)),
            shared_skills=Count("skills", filter=Q(skills__in=user.skills.all()), distinct=True),
            mutual_followers=Count("followers", filter=Q(followers__in=user.followers.all()), distinct=True),
            followed_by_following=Count("followers", filter=Q(followers__in=user.following.all()), distinct=True),
        )

        # ✅ 5. Trending score (followers gained recently)
        trending_cutoff = timezone.now() - timedelta(days=7)
        qs = qs.annotate(
            trending=Count("followers", filter=Q(followers__last_login__gte=trending_cutoff))
        )

        suggestions = []

        # ✅ 6. Convert queryset into list so we can compute distances + scoring
        for candidate in qs:
            # Distance (apply only if both have lat/lng)
            distance_score = 0
            if user.latitude and user.longitude and candidate.latitude and candidate.longitude:
                try:
                    lat1, lon1 = math.radians(user.latitude), math.radians(user.longitude)
                    lat2, lon2 = math.radians(candidate.latitude), math.radians(candidate.longitude)
                    distance = 6371 * math.acos(
                        math.cos(lat1)*math.cos(lat2)*math.cos(lon2 - lon1) +
                        math.sin(lat1)*math.sin(lat2)
                    )
                    distance_score = max(0, 10 - (distance / 10))
                except:
                    distance_score = 0

            # Role score
            role_score = 2 if getattr(candidate, "role", None) == "musician" else 0

            # Random freshness
            random_boost = random.uniform(0, 1)

            # Final score
            score = (
                candidate.mutual_followers * 4 +
                candidate.followed_by_following * 3 +
                candidate.shared_skills * 2 +
                candidate.same_city * 2 +
                candidate.trending * 1 +
                distance_score * 1 +
                role_score +
                random_boost
            )

            suggestions.append({
                "user": candidate,
                "score": round(score, 3)
            })

        # ✅ 7. Sort by score descending
        suggestions.sort(key=lambda x: x["score"], reverse=True)

        # ✅ 8. Serialize top results
        results = [
            {
                "id": s["user"].id,
                "username": s["user"].username,
                "profile_image": s["user"].profile_image.url if s["user"].profile_image else None,
                "score": s["score"]
            }
            for s in suggestions[:20]
        ]

        response = {"count": len(results), "results": results}

        # ✅ 9. Cache for 10 minutes
        cache.set(cache_key, response, timeout=600)

        return Response(response)
    
    
# ============================================================
#  FOLLOWERS LIST / FOLLOWING LIST
# ============================================================


class StandardResultSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50   

class FollowersListView(generics.ListAPIView):
    serializer_class = UserMiniSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultSetPagination
    
    def get_queryset(self):
        user = get_object_or_404(CustomUser, id=self.kwargs['user_id'])
        return user.followers.all()
    
class FollowingListView(generics.ListAPIView):
    serializer_class = UserMiniSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultSetPagination
    
    def get_queryset(self):
        user = get_object_or_404(CustomUser, id=self.kwargs['user_id'])
        return user.following.all()
    
