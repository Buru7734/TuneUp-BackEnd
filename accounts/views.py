# from rest_framework import status, permissions, generics
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from django.contrib.auth import authenticate, get_user_model
# from .serializers import UserSerializer, NotificationSerializer, PublicProfileSerializer, FollowUserSerializer, UserMiniSerializer, ActivityItemSerializer
# from .models import CustomUser, Notification, FollowRequest
# from rest_framework.permissions import AllowAny
# from rest_framework_simplejwt.tokens import RefreshToken
# from django.shortcuts import get_object_or_404
# from django.db.models import Count, Q, FloatField, Value
# from django.utils import timezone
# from django.core.cache import cache
# from datetime import timedelta
# from django.db.models.functions import Coalesce
# import math, random
# from rest_framework.pagination import PageNumberPagination
# from rest_framework.exceptions import PermissionDenied
# from gigs.models import Gig
# from reviews.models import Review
# from django.utils.dateparse import parse_datetime



 

# User = get_user_model()


    
# class StandardResultSetPagination(PageNumberPagination):
#     page_size = 5
#     page_size_query_param = 'page_size'
#     max_page_size = 50
    

# class AdvancedFollowSuggestionsView(APIView):
#     permission_classes = [permissions.AllowAny]

#     def get(self, request, user_id):
#         user = get_object_or_404(CustomUser, id=user_id)
#         cache_key = f"suggestions_{user_id}"

#         # ✅ 1. Check cache
#         cached = cache.get(cache_key)
#         if cached:
#             return Response(cached)

#         already_following = set(user.following.values_list("id", flat=True))

#         # ✅ 2. Exclude self + already following
#         qs = CustomUser.objects.exclude(id=user.id).exclude(id__in=already_following)
#         qs = qs.exclude(id_in=user.blocked_users.values_list("id", flat=True))
#         qs = qs.exclude(id_in=user.blocked_by.values_list("id", flat=True))

#         # ✅ 3. Exclude inactive users
#         recent_cutoff = timezone.now() - timedelta(days=30)
#         qs = qs.filter(last_login__gte=recent_cutoff)

#         # ✅ 4. Annotate with base signals
#         qs = qs.annotate(
#             same_city=Count("id", filter=Q(city=user.city)),
#             shared_skills=Count("skills", filter=Q(skills__in=user.skills.all()), distinct=True),
#             mutual_followers=Count("followers", filter=Q(followers__in=user.followers.all()), distinct=True),
#             followed_by_following=Count("followers", filter=Q(followers__in=user.following.all()), distinct=True),
#         )

#         # ✅ 5. Trending score (followers gained recently)
#         trending_cutoff = timezone.now() - timedelta(days=7)
#         qs = qs.annotate(
#             trending=Count("followers", filter=Q(followers__last_login__gte=trending_cutoff))
#         )

#         suggestions = []

#         # ✅ 6. Convert queryset into list so we can compute distances + scoring
#         for candidate in qs:
#             # Distance (apply only if both have lat/lng)
#             distance_score = 0
#             if user.latitude and user.longitude and candidate.latitude and candidate.longitude:
#                 try:
#                     lat1, lon1 = math.radians(user.latitude), math.radians(user.longitude)
#                     lat2, lon2 = math.radians(candidate.latitude), math.radians(candidate.longitude)
#                     distance = 6371 * math.acos(
#                         math.cos(lat1)*math.cos(lat2)*math.cos(lon2 - lon1) +
#                         math.sin(lat1)*math.sin(lat2)
#                     )
#                     distance_score = max(0, 10 - (distance / 10))
#                 except:
#                     distance_score = 0

#             # Role score
#             role_score = 2 if getattr(candidate, "role", None) == "musician" else 0

#             # Random freshness
#             random_boost = random.uniform(0, 1)

#             # Final score
#             score = (
#                 candidate.mutual_followers * 4 +
#                 candidate.followed_by_following * 3 +
#                 candidate.shared_skills * 2 +
#                 candidate.same_city * 2 +
#                 candidate.trending * 1 +
#                 distance_score * 1 +
#                 role_score +
#                 random_boost
#             )

#             suggestions.append({
#                 "user": candidate,
#                 "score": round(score, 3)
#             })

#         # ✅ 7. Sort by score descending
#         suggestions.sort(key=lambda x: x["score"], reverse=True)

#         # ✅ 8. Serialize top results
#         results = [
#             {
#                 "id": s["user"].id,
#                 "username": s["user"].username,
#                 "profile_image": s["user"].profile_image.url if s["user"].profile_image else None,
#                 "score": s["score"]
#             }
#             for s in suggestions[:20]
#         ]

#         response = {"count": len(results), "results": results}

#         # ✅ 9. Cache for 10 minutes
#         cache.set(cache_key, response, timeout=600)

#         return Response(response)
    



    
