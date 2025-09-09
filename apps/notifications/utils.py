from .models import Notification
from apps.users.models import User
from apps.projects.models import Project

def create_comment_notification(comment):
    """ Create notification when someone ashyize comments on post """
    post_author = comment.post.user

    # Don't notify if user comments on their own post
    if comment.user != post_author:
        Notification.create_notification(
            user=post_author,
            title="New Comment kuri post yawe",
            message=f"{comment.user.first_name or comment.user.phone_number} commented on your post. {comment.post.type}",
            notification_type="new_comment",
            project=comment.post.project
        )

def create_upvote_notification(upvote):
    """ Create notification when someone upvotes a post """
    post_author = upvote.post.user

    #Don't notify if user upvotes their own post
    if upvote.user != post_author:
        Notification.create_notification(
            user=post_author,
            title="New Upvote kuri post yawe",
            message=f"{upvote.user.first_name or upvote.user.phone_number} upvoted your post. {upvote.post.type}",
            notification_type="upvote_received",
            project=upvote.post.project
        )

def create_project_notification(project, notification_type="project_created"):
    """ Create notification when a project is created """
    # Notify all users uretse the project creator
    users_to_notify = User.objects.exclude(id=project.admin.id)

    if notification_type == "project_created":
        title = "New Project Available"
        message = f"New project '{project.title}' has been created in {project.sector}"
    elif notification_type == "project_update":
        title = "Project Update"
        message = f"The project '{project.title}' has been updated."
    else:
        title = "Project Notification"
        message = f"Notification for the project '{project.title}'."

    # Create notification for all users
    notifications = []
    for user in users_to_notify:
        notifications.append(
            Notification(
                user=user,
                title=title,
                message=message,
                notification_type=notification_type,
                project=project
            )
        )
    # Bulk create for efficiency
    Notification.objects.bulk_create(notifications)

def create_project_reminder(project):
    """ Create reminder notification for upcoming projects """
    # Get users who have attended this project's events before
    # For now, notify all users
    users_to_notify = User.objects.all()

    notifications = []
    for user in users_to_notify:
        notifications.append(
            Notification(
                user=user,
                title="Project Reminder",
                message=f"Don't forget about the upcoming project '{project.title}' in {project.sector} is happening soon Murakoze! ",
                notification_type="project_reminder",
                project=project
            
            )
        )

    Notification.objects.bulk_create(notifications)
