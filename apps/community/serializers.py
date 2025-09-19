from rest_framework import serializers
from .models import Post, PostUpvote, Comment
from apps.users.serializers import UserSerializer

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "user", "content", "created_at"]
        read_only_fields = ["created_at"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)

class PostSerializer(serializers.ModelSerializer):
    upvotes_count = serializers.ReadOnlyField()
    has_upvoted = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'description', 'sector', 'datetime', 'location',
            'content', 'type', 'user', 'user_name', 'project', 
            'upvotes_count', 'has_upvoted', 'comments_count', 'created_at'
        ]
        read_only_fields = ['created_at', 'user']

    def get_has_upvoted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.has_upvoted(request.user)
        return False
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.phone_number
    
    def get_comments_count(self, obj):
        return obj.comments.count()
    
    def create(self, validated_data):
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request context is required to create a post.")
        validated_data['user'] = request.user
        return super().create(validated_data)
    
class PostUpvoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostUpvote
        fields = ["id", "user", "post", "created_at"]
        read_only_fields = ["user","created_at"]