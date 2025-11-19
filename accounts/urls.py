
from django.urls import path


from accounts.views.auth_views import RegisterView, LoginView
from accounts.views.profile_views import ProfileView, PublicProfileView, UserListView, UserDetailView
from accounts.views.follow_views import (
    RemoveFollowerView,
    FollowersListView,
    FollowingListView,
    MutualFollowersView,
    MutualFollowingView,
    FollowSuggestionsView,
    AdvancedFollowSuggestionsView,
    SendFollowRequestView,
    AcceptFollowRequestView,
    RejectFollowRequestView,
    PendingFollowRequestsView,
    CancelFollowRequestView,
    SentFollowRequestView,
    UnfollowUserView
)

from accounts.views.notification_views import (
    NotificationListView,
    NotificationMarkReadView,
    NotificationMarkAllReadView,
    UnreadNotificationCountView,
)
from accounts.views.block_views import (
    BlockUserView,
    UnblockUserView,
    BlockedUsersListView,
)


from accounts.views.feed_views import UserFeedView
from accounts.views.search_views import UserSearchView

urlpatterns = [
    #Auth
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    
    #Profiles
    path('profile/', ProfileView.as_view(), name='profile'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:id>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<int:id>/public/', PublicProfileView.as_view(), name='public-profile'),
    
    # Follow system
    path('users/<int:user_id>/remove-follower/', RemoveFollowerView.as_view(), name="remove-follower"),
    path('users/<int:user_id>/followers/', FollowersListView.as_view(), name='followers-list'),
    path('users/<int:user_id>/following/', FollowingListView.as_view(), name='following-list'),
    path('users/<int:user_id>/mutual-followers/<int:other_id>/', MutualFollowersView.as_view(), name='mutual-followers'),
    path('users/<int:user_id>/mutual-following/<int:other_id>/', MutualFollowingView.as_view(), name="mutual-following"),
    path('users/<int:user_id>/suggestions/', FollowSuggestionsView.as_view(), name='follow-suggestions'),
    path('users/<int:user_id>/advanced-suggestions/', AdvancedFollowSuggestionsView.as_view(), name="advanced-follow-suggestions"),
    path('users/<int:user_id>/follow-request/', SendFollowRequestView.as_view(), name="send-follow-request"),
    path('follow-request/<int:request_id>/accept/', AcceptFollowRequestView.as_view(), name="accept-follow-request"),
    path('follow-request/<int:request_id>/reject/', RejectFollowRequestView.as_view(), name="reject-follow-request"),
    path('follow-request/pending/', PendingFollowRequestsView.as_view(), name="pending-follow-request"),
    path('users/<int:user_id>/cancel-follow-request/', CancelFollowRequestView.as_view(), name='cancel-follow-request'),
    path('users/follow-requests/sent/', SentFollowRequestView.as_view(), name='sent-follow-requests'),
    path('users/<int:user_id>/unfollow/', UnfollowUserView.as_view(), name="unfollow"),
    
    
    #Notifications
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/<int:id>/read/', NotificationMarkReadView.as_view(), name='notification-read'),
    path('notifications/mark-all-read/', NotificationMarkAllReadView.as_view(), name='notifications-mark-all-read'),
    path('notifications/unread-count/', UnreadNotificationCountView.as_view(), name='unread-notification-count'),
    
    #Feed 
    path('feed/', UserFeedView.as_view(), name='user-feed'),
    
    #Search
    path('search/', UserSearchView.as_view(), name='user-search'),
    
    #Block
    path('users/<int:user_id>/block/', BlockUserView.as_view(), name='block-user'),
    path('users/<int:user_id>/unblock/', UnblockUserView.as_view(), name='unblock-user'),
    path('users/blocked/', BlockedUsersListView.as_view(), name='blocked-users'),
    
]

