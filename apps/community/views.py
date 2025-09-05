from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Post, PostUpvote, Comment
from .serializers import PostSerializer, PostUpvoteSerializer, CommentSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}
    
    @action(detail=True, methods=['post'])
    def upvote(self, request, pk=None):
        """ Toggle upvote on a post """
        post = self.get_object()

        #Check if user already upvoted 
        upvote = PostUpvote.objects.filter(user=request.user, post=post).first()

        if upvote:
            # Remove upvote
            upvote.delete()
            return Response({
                'message': 'Upvote removed successfully.',
                'upvoted': False,
                'upvotes_count': post.upvotes_count
            })
        else:
            # Add upvote
            PostUpvote.objects.create(user=request.user, post=post)
            return Response({
                'message': 'Upvoted successfully.',
                'upvoted': True,
                'upvotes_count': post.upvotes_count
            })
    
    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        """ Get or create comments for a post or add a new comment """
        post = self.get_object()

        if request.method == 'GET':
            comments = post.comments.all().order_by('-created_at')
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = CommentSerializer(data=request.data, context={'request': request})                            
            if serializer.is_valid():
                serializer.save(post=post)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    