from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
import math

from accounts.models import CustomUser
from accounts.serializers import UserSerializer

from accounts.views.follow_views import StandardResultSetPagination


# ============================================================
#  USER SEARCH VIEW (keywords, skills, city, ranking)
# ============================================================


class UserSearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        q = request.query_params.get("q", "").strip()
        skill_id = request.query_params.get("skill")
        city = request.query_params.get("city")
        country = request.query_params.get("country")
        
        user = request.user
        
        
        # ------------------------------------------------------
        # Blocked users cannot appear in search
        # ------------------------------------------------------
        
        blocked_ids = set(user.blocks.values_list("id", flat=True))
        blocked_by_ids = set(user.blocked_by.values_list("id", flat=True))
        excluded_ids = blocked_ids.union(blocked_by_ids)
        
        qs = CustomUser.objects.exclude(id__in=excluded_ids)
        
        # ------------------------------------------------------
        # Text search
        # ------------------------------------------------------

        
        if q:
            qs = qs.filter(
                Q(username__icontains=q) |
                Q(bio__icontains=q)
            )
            
        # ------------------------------------------------------
        # Skill filter
        # ------------------------------------------------------   
            
        if skill_id:
            qs =qs.filter(skills__id=skill_id)
            
        
        # ------------------------------------------------------
        # Location filters
        # ------------------------------------------------------    
            
        if city:
            qs = qs.filter(city__iexact=city)
        if country:
            qs =qs.filter(country__iexact=country)
            
        # ------------------------------------------------------
        # Ranking signals data
        # ------------------------------------------------------
            
        user_skill_ids = set(user.skills.values_list("id", flat=True))
        user_follower_ids = set(user.followers.values_list("id", flat=True))
        
        now = timezone.now()
        results = []
        
        
        # ------------------------------------------------------
        # Build ranking score for every candidate
        # ------------------------------------------------------
        
        for candidate in qs.select_related().prefetch_related("skills", "followers"):
            
            score = 0
            
            #  1. Shared Skills (strong weight)
            candidate_skill_ids = set(candidate.skills.values_list("id", flat=True))
            shared_skill_count = len(user_skill_ids & candidate_skill_ids)
            score += shared_skill_count * 3
            
            # 2. Mutual followers
            candidate_follower_ids = set(candidate.followers.values_list("id", flat=True))
            mutual_followers = len(user_follower_ids & candidate_follower_ids)
            score += mutual_followers * 2
            
            # 3. Recent activity
            last_login = candidate.last_login
            
            if last_login:
                days_inactive = (now - last_login).days
                if days_inactive <= 7:
                    score += 10
                elif days_inactive <= 30:
                    score += 5
                elif days_inactive <= 60:
                    score += 1
                else:
                    score -= 3
                    
            distance_score = 0
            
            # --------------------------------------------------
            # Physical distance scoring (optional)
            # --------------------------------------------------
            
            if user.latitude and user.longitude and candidate.latitude and candidate.longitude:
                try:
                    dist = self.geo_distance(user.latitude, user.longitude, candidate.latitude, candidate.longitude)
                    distance_score = max(0,5 - (dist / 10))
                except:
                    distance_score = 0
            score += distance_score
            
            
           
            # --------------------------------------------------
            # Query match boost (name relevance)
            # -------------------------------------------------- 
            
            if q:
                
                uname = candidate.username.lower()
                q_lower = q.lower()
                
                if uname.startswith(q_lower):
                    score += 5
                elif q.lower() in uname:
                    score += 2
                    
            results.append({
                "user": candidate,
                "score": round(score, 3)
            })
            
           
        # ------------------------------------------------------
        # Sort results
        # ------------------------------------------------------    
            
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # ------------------------------------------------------
        # Pagination
        # ------------------------------------------------------
        
        paginator = StandardResultSetPagination()
        page = paginator.paginate_queryset(results, request)
        
        serializer = UserSerializer([item['user'] for item in page], many=True)
        return paginator.get_paginated_response(serializer.data)        
        
        
        # ============================================================
        #  GEO DISTANCE FUNCTION
        # ============================================================
        
        
    def geo_distance(self, lat1, lon1, lat2, lon2):
        lat1, lon1 = math.radians(lat1), math.radians(lon1)
        lat2, lon2 = math.radians(lat2), math.radians(lon2)
        
        return 6371 * math.acos(
            math.cos(lat1)*math.cos(lat2)*math.cos(lon2-lon1) +
            math.sin(lat1)*math.sin(lat2)
        )
    
       