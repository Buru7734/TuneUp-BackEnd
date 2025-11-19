from ..serializers import TagSerializer
from rest_framework import permissions, status
from ..models import Tag
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView



class TagListView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get(self,request):
        tags = Tag.objects.all().order_by('name')
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self,request):

        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TagDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    
    def get_object(self, id):
        return get_object_or_404(Tag, id=id)
    
    def get(self,request, id):
        tag = self.get_object(id) 
        serializer = TagSerializer(tag)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def put(self,request, id):
        tag = self.get_object(id)
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required."}, status=status.HTTP_403_FORBIDDEN)
        if tag.created_by != request.user:
            return Response({"error": "You can only edit tags you created."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = TagSerializer(tag, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):
        tag = self.get_object(id)
        
        if not request.user.is_authenticated:
            return Response({"error": "Only organizers can delete tags."}, status=status.HTTP_403_FORBIDDEN)
        
        if tag.created_by != request.user:
            
            return Response({"error": "You can only delete tags you created."}, status=status.HTTP_403_FORBIDDEN)
        
        tag.delete()
        return Response({"message": "Tag deleted successfully."}, status=status.HTTP_204_NO_CONTENT)