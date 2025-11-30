from rest_framework import serializers
from .models import CustomUser, Notification, FollowRequest
from gigs.models import Tag, Gig
from reviews.models import Review


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    skills = serializers.PrimaryKeyRelatedField(
    many=True,
    queryset=Tag.objects.all(),
    required=False
)

    
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'email',
            'bio',
            'profile_image',
            'skills',
            'city',
            'country',
            'latitude',
            'longitude',
            'website',
            'instagram',
            'soundcloud',
            'youtube',
            'is_available',
            'rating',
            'total_reviews',
            'password'
        ]
        
    def create(self, validated_data):
        skills = validated_data.pop('skills', None)
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            bio=validated_data.get('bio', ''),
            city=validated_data.get('city', ''),
            country=validated_data.get('country', ''),
            latitude=validated_data.get('latitude'),
            longitude=validated_data.get('longitude'),
            website=validated_data.get('website', ''),
            instagram=validated_data.get('instagram', ''),
            soundcloud=validated_data.get('soundcloud', ''),
            youtube=validated_data.get('youtube', ''),
            is_available=validated_data.get('is_available', True),
            rating=validated_data.get('rating', 0),
            total_reviews=validated_data.get('total_reviews', 0),
        )
        if skills:
            user.skills.set(skills)
        return user
    
    def update(self,instance, validated_data):
        skills = validated_data.pop('skills', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if skills is not None:
            instance.skills.set([tag for tag in skills if tag is not None])
        return instance
    
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'created_at', 'is_read']
        


class ReviewSummarySerializer(serializers.ModelSerializer):
    reviewer_username = serializers.ReadOnlyField(source='reviewer.username')
    
    class Meta:
        model = Review
        fields = ['id', 'reviewer_username', 'rating', 'comment', 'created_at']
        
class GigSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gig
        fields = ['id', 'title', 'date', 'location', 'is_open']
 
class FollowUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id','username', 'profile_image_url', 'city', 'rating']
         
class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'profile_image']
        
class PublicProfileSerializer(serializers.ModelSerializer):
    profile_image_url = serializers.SerializerMethodField()
    skills = serializers.StringRelatedField(many=True)
    recent_reviews = serializers.SerializerMethodField()
    recent_organized_gigs = serializers.SerializerMethodField()
    recent_joined_gigs = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()
    reviews_received = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    is_followed_by= serializers.SerializerMethodField()
    is_mutual = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    follow_status = serializers.SerializerMethodField()
    is_blocked = serializers.SerializerMethodField()
    
    
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'bio',
            'profile_image_url',
            'skills',
            'city',
            'country',
            'website',
            'instagram',
            'soundcloud',
            'youtube',
            'is_available',
            'rating',
            'recent_reviews',
            'reviews_received',
            'recent_organized_gigs',
            'recent_joined_gigs',
            'followers',
            'following',
            'followers_count',
            'following_count',
            'is_following',
            'is_followed_by',
            'is_mutual',
            'is_owner',
            'follow_status',
            'is_blocked'
        ]
        
    def get_is_blocked(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return (
            obj in request.user.blocks.all()
            or request.user in obj.blocks.all()
        )

    def get_followers_count(self, obj):
        return obj.followers.count()
    
    def get_following_count(self, obj):
        return obj.following.count()
    
    
    def get_is_followed_by(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return request.user.followers.filter(id=obj.id).exists()
    
    def get_is_mutual(self, obj):
        return(
            self.get_is_following(obj)
            and self.get_is_followed_by(obj)
        )
        
    def get_is_owner(self, obj):
        request = self.context.get('request')
        return request.user.is_authenticated and request.user == obj
    

    def get_recent_reviews(self, obj):
        reviews = Review.objects.filter(reviewed_user=obj).order_by('-created_at')[:5]
        return ReviewSummarySerializer(reviews, many=True).data
    
    def get_recent_organized_gigs(self, obj):
        gigs = Gig.objects.filter(organizer=obj).order_by('-created_at')[:3]
        return GigSummarySerializer(gigs, many=True).data
        
    def get_recent_joined_gigs(self, obj):
        gigs = obj.joined_gigs.order_by('-created_at')[:3]
        return GigSummarySerializer(gigs, many=True).data
    
    def get_followers(self, obj):
        followers = obj.followers.all()[:10]
        data = []
        for u in followers:
            
                profile_image_url = (
                    u.profile_image.url if u.profile_image and hasattr(u.profile_image, 'url') else None
                )
                data.append({
                    "id": u.id,
                    "username": u.username,
                    "profile_image": profile_image_url  
                })
                
        return data
    
    def get_following(self, obj):
        following = obj.following.all()[:10]
        data = []
        for u in following:
            
            
            profile_image_url = (
                u.profile_image.url if u.profile_image and hasattr(u.profile_image, 'url') else None
            )
            data.append({
                "id": u.id,
                "username": u.username,
                "profile_image": profile_image_url  
            })
            
        return data
    
    def get_profile_image_url(self,obj):
        if obj.profile_image:
            return obj.profile_image.url
        return None
    def get_reviews_received(self, obj):
        return Review.objects.filter(reviewed_user=obj).count()
    
    def get_is_following(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj in request.user.following.all()
    
    def get_follow_status(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return "none"
        
        user = request.user
        
        if obj.followers.filter(id=user.id).exists():
            return "accepted"
        
        if FollowRequest.objects.filter(from_user=user, to_user=obj, accepted=False).exists():
            return "pending"
        
        if FollowRequest.objects.filter(from_user=obj, to_user=user, accepted=False).exists():
            return "incoming"
        
        return "none"
    
class ActivityItemSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["gig", "review"])
    id = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    profile_image_url = serializers.DateTimeField()
    
    title = serializers.CharField(required=False)
    location = serializers.CharField(required=False)
    date = serializers.DateField(required=False)
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, required=False)
    comment = serializers.CharField(required=False)
    reviewed_user_id = serializers.IntegerField(required=False)
    reviewed_username = serializers.CharField(required=False)