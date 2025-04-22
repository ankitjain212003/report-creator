from django_q.models import Schedule
from django.utils import timezone
from django.core.mail import send_mail
from project.models import Project

def send_project_reminders():
    target_date = timezone.now().date() + timezone.timedelta(days=3)
    upcoming_projects = Project.objects.filter(startdate=target_date)

    for project in upcoming_projects:
        for user in project.owner.all():
            send_mail(
                f"Reminder: '{project.name}' starts in 3 days",
                f"Hi {user.get_full_name() or user.email},\n\nThis is a reminder for the project '{project.name}' starting on {project.startdate}.",
                'noreply@yourdomain.com',
                [user.email],
                fail_silently=True,
            )
