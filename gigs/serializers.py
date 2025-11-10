from rest_framework import serializers
from .models import Gig, Tag

class GigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gig
        fields = '__all__'
        
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']
        
class GigApplicationSerializer(serializers.ModelSerializer):
    applicant_username = serializers.ReadOnlyField(source='applicants.username')
    gig_title = serializers.ReadOnlyField(source='gig.title')
    
    class Meta:
        fields = [
            'id',
            'applicants',
            'gig',
            'gig_title',
            'message',
            'status',
            'created_at'
        ]
        read_only_fields = ['applicants', 'status', 'created_at']