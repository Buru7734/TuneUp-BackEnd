from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta

from gigs.models import Gig
from reviews.models import Review
from accounts.serializers import ActivityItemSerializer

# ============================================================
#  FEED PAGINATION
# ============================================================


class FeedPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50
    
    
# ============================================================
#  USER FEED (GIGS + REVIEWS + SORTING + FILTERS)
# ============================================================
    
class UserFeedView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination
    
    def get(self, request):
        user = request.user
        
        
        # --------------------------------------------------------
        # Blocked users (cannot appear in your feed)
        # --------------------------------------------------------
        blocked_ids = set()
        if hasattr(user,"blocks"):
            blocked_ids.update(user.blocks.values_list("id", flat=True))
        if hasattr(user, "blocked_by"):
            blocked_ids.update(user.blocked_by.values_list("id", flat=True))
        
        
        # --------------------------------------------------------
        # Following + optional include self
        # --------------------------------------------------------
            
        following_ids = set(user.following.exclude(id__in=blocked_ids).values_list("id", flat=True))
        
        include_self = request.query_params.get("include_self","true").lower()== "true"
        if include_self:
            following_ids.add(user.id)
            
        now = timezone.now()
        recent_cutoff = now - timedelta(days=30)
            
        
        # --------------------------------------------------------
        # Fetch Gigs
        # --------------------------------------------------------    
            
        gigs_qs = (
            Gig.objects.filter(organizer_id__in=following_ids)
            .select_related("organizer")
            .annotate(
                review_count=Count("reviews", distinct=True),
                recent_score=Count("reviews", filter=Q(created_at__gte=recent_cutoff))
            )
        )
        
        
        # --------------------------------------------------------
        # Fetch Reviews (limit 200)
        # --------------------------------------------------------
        
        reviews_qs = (
            Review.objects.filter(reviewer_id__in=following_ids)
            .select_related("reviewer", "reviewed_user")
            .order_by("-created_at")[:200]
        )
        
        items = []
        
        
        # --------------------------------------------------------
        # Process Gigs → Feed Items
        # --------------------------------------------------------
        
    
        for g in gigs_qs:
            age_days = max((now - g.created_at).days, 1)
            trending_score = g.review_count * 2 + g.recent_score * 3 + (30 / age_days)
            items.append({
                
                "type": "gig",
                "id": g.id,
                "created_at": g.created_at,
                "user_id": g.organizer_id,
                "username": g.organizer.username,
                "profile_image_url": (g.organizer.profile_image.url if getattr(g.organizer, "profile_image", None)else None),
                "title": g.title,
                "location": getattr(g, "location", None),
                "date": getattr(g, "date", None),
                "score": trending_score
                
            })
            
        # --------------------------------------------------------
        # Process Reviews → Feed Items
        # --------------------------------------------------------    
            
            
        for r in reviews_qs:
            age_days = max((now - r.created_at).days, 1)
            trending_score = (10/ age_days) + (r.rating or 0)
            items.append({
                "type": "review",
                "id": r.id,
                "created_at": r.created_at,
                "user_id": r.reviewer_id,
                "username": r.reviewer.username,
                "profile_image_url": (r.reviewer.profile_image.url if getattr(r.reviewer, "profile_image", None)else None),
                "rating": r.rating,
                "comment": r.comment,
                "reviewed_user_id": r.reviewed_user_id,
                "reviewed_username": r.reviewed_user.username if r.reviewed_user else None,
                "score": trending_score
            })
            
         
        # --------------------------------------------------------
        # Optional: Filter feed by time window: ?since=24h | 7d | 3m
        # --------------------------------------------------------    
            
            
        since = request.query_params.get('since', 'all').lower()
        
        
        if since != 'all':
            now = timezone.now()
            cutoff = None
            
            try:
                if since.endswith('h'):
                    hours = int(since[:-1])
                    cutoff = now - timedelta(hours=hours)
                    
                elif since.endswith('d'):
                    days = int(since[:-1])
                    cutoff = now - timedelta(days=days)
                    
                elif since.endswith('m'):
                    months = int(since[:-1])
                    cutoff = now - timedelta(days=30 * months)  
            
                    
                if cutoff:
                    filtered = []
                    for i in items:
                        created_dt = i['created_at']
                        if created_dt >= cutoff:
                            filtered.append(i)
                    items = filtered
                   
            except Exception as e:
                print("SINCE FILTER ERROR:", e)
                pass             
        
        
        
        # --------------------------------------------------------
        # Filter by type ?type=gig or ?type=review
        # --------------------------------------------------------
        
            
        sort_mode = request.query_params.get('sort', 'recent').lower()
        
        activity_type = request.query_params.get("type", "all").lower()
        
        if activity_type in ["gig", "gigs"]:
            items = [i for i in items if i["type"] == "gig"]
            
        elif activity_type in ["review", "reviews"]:
            items = [i for i in items if i["type"] == "review"]
            
        
        # --------------------------------------------------------
        # Sorting Mode ?sort=trending or ?sort=recent
        # --------------------------------------------------------
        
        if sort_mode == "trending":    
            items.sort(key=lambda x: x["score"], reverse=True)
        else:
            items.sort(key=lambda x: x["created_at"], reverse=True)
            
        
        # --------------------------------------------------------
        # Paginate
        # --------------------------------------------------------
        
        paginator = FeedPagination()
        page = paginator.paginate_queryset(items, request)
        serializer = ActivityItemSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)