from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Post, PostUpvote, Comment
from .serializers import PostSerializer, PostUpvoteSerializer, CommentSerializer
from apps.notifications.utils import create_comment_notification, create_upvote_notification
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}
    @swagger_auto_schema(
        operation_description="Toggle upvote on a post",
        responses={
            200: openapi.Response('Upvote toggled successfully', examples={
                'application/json': {
                    'upvoted_removed': {
                        'message': 'Upvote removed successfully.',
                        'upvoted': False,
                        'upvotes_count': 4
                    },
                    'upvoted_added': {
                        'message': 'Upvoted successfully.',
                        'upvoted': True,
                        'upvotes_count': 5
                    }
                }
            }),
            404: 'Post not found'
        }
    )
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
            upvote = PostUpvote.objects.create(user=request.user, post=post)
            # Create notification
            create_upvote_notification(upvote)
            return Response({
                'message': 'Upvoted successfully.',
                'upvoted': True,
                'upvotes_count': post.upvotes_count
            })
    

    @swagger_auto_schema(
        methods=['get'],
        operation_description="Get all comments for a specific post",
        responses={
            200: openapi.Response('List of comments', CommentSerializer(many=True)),
            404: 'Post not found'
        }
    )
    @swagger_auto_schema(
        methods=['post'],
        operation_description="Add a new comment to a post",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'content': openapi.Schema(type=openapi.TYPE_STRING, description='Comment content'),
            },
            required=['content']
        ),
        responses={
            201: openapi.Response('Comment created successfully', CommentSerializer),
            400: 'Invalid comment data',
            404: 'Post not found'
        }
    )
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
                comment = serializer.save(post=post)
                # Create notification
                create_comment_notification(comment)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}
    
    @swagger_auto_schema(
        operation_description="Create a new comment",
        request_body=CommentSerializer,
        responses={
            201: CommentSerializer,
            400: 'Invalid comment data'
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Get all comments",
        responses={200: CommentSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
