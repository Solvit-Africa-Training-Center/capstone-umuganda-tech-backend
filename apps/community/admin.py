from django.contrib import admin
from .models import Post

# -------------------------------
# Post Admin
# -------------------------------
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'project', 'type', 'upvotes', 'created_at')
    list_filter = ('type', 'project')
    search_fields = ('user__phone_number', 'content', 'project__title')
    readonly_fields = ('created_at',)
