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

# ---------------------------------------
# for leader notification
# ---------------------------------------

def notify_registered_users(project, notification_type="project_reminder"):
    """Notify users who registered for project updates"""
    from apps.projects.models import ProjectRegistration
    
    registered_users = User.objects.filter(
        project_registrations__project=project,
        project_registrations__status='registered'
    )
    
    notifications = []
    for user in registered_users:
        if notification_type == "project_reminder":
            title = "Project Reminder"
            message = f"Reminder: '{project.title}' is happening soon!"
        elif notification_type == "project_update":
            title = "Project Update"
            message = f"Update for '{project.title}' you joined"
        
        notifications.append(Notification(
            user=user, title=title, message=message, #type: ignore
            notification_type=notification_type, project=project
        ))
    
    Notification.objects.bulk_create(notifications)

# ---------------------------------
# Notification on leader
# ---------------------------------


def notify_leader_followers(leader, project):
    """Notify followers when leader creates new project"""
    from apps.projects.models import LeaderFollowing
    
    followers = User.objects.filter(following_leaders__leader=leader)
    
    notifications = []
    for follower in followers:
        notifications.append(Notification(
            user=follower,
            title="New Project from Leader",
            message=f"Leader you follow created '{project.title}'",
            notification_type="leader_new_project",
            project=project
        ))
    
    Notification.objects.bulk_create(notifications)

# ----------------------------
# notify new registration on project to leader
# ----------------------------

def notify_project_leader_new_registration(project, user):
    """Notify project leader when someone joins their project"""
    if project.admin != user:  # Don't notify if leader joins their own project
        Notification.create_notification(
            user=project.admin,
            title="New Registration",
            message=f"{user.first_name or user.phone_number} joined your project '{project.title}'",
            notification_type="project_registration",
            project=project
        )
