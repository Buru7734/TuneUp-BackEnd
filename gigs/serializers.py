from rest_framework import serializers
from .models import Gig, Tag, GigApplication

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
        model = GigApplication
        fields = [
            'id',
            'gig',
            'gig_title',
            'message',
            'status',
            'created_at',
            'applicant_username'
        ]
        read_only_fields = ['applicant_username', 'status', 'created_at']