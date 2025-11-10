from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    reviewer_username = serializers.ReadOnlyField(source='reviewer.username')
    reviewed_username = serializers.ReadOnlyField(source='reviewed_user.username')
    gig_title = serializers.ReadOnlyField(source='gig.title')
    
    class Meta:
        model = Review
        fields = [
            "id",
            "reviewer",
            "reviewer_username",
            "reviewed_user",
            "reviewed_username",
            "gig",
            "gig_title",
            "rating",
            "comment",
            "created_at"
        ]
        read_only_fields = ['reviewer', 'created_at']