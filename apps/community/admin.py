from django.contrib import admin
from .models import Post, PostUpvote, Comment
from django.db.models import Count


# -------------------------------
# Post Admin
# -------------------------------
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'project', 'type', 'upvotes_count', 'created_at')
    list_filter = ('type', 'project')
    search_fields = ('user__phone_number', 'content', 'project__title')
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            upvotes_count_annotated=Count('upvotes')
        )

    def upvotes_count(self, obj):
        return obj.upvotes_count_annotated
    upvotes_count.short_description = 'Upvotes' #type: ignore

# -------------------------------
# Post Upvote Admin
# -------------------------------

@admin.register(PostUpvote)
class PostUpvoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__phone_number', 'post__content')

# -------------------------------
# Comment Admin
# -------------------------------

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__phone_number', 'post__content', 'content')