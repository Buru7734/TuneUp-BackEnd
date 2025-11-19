from django.urls import path
from .views.gigs_views import GigListCreateView, GigDetailView
from .views.tag_views import TagListView, TagDetailView
from .views.applications_views import ApplyToGigView, GigApplicationsView, ReviewApplicationView

urlpatterns = [
    path('tags/', TagListView.as_view(), name='tag-list'),
    path('tags/<int:id>/', TagDetailView.as_view(), name='tag-detail'),
    path('gigs/', GigListCreateView.as_view(), name='gig-list-create'),
    path('gigs/<int:id>/', GigDetailView.as_view(), name='gig-detail'),
    path('gigs/<int:gig_id>/apply/', ApplyToGigView.as_view(), name='apply-to-gig'),
    path('gigs/<int:gig_id>/applications/', GigApplicationsView.as_view(), name='gig-applications'),
    path('applications/<int:app_id>/review/', ReviewApplicationView.as_view(), name='review-application')
    
]