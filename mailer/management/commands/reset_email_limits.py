from django.core.management.base import BaseCommand
from mailer.models import EmailUsage

class Command(BaseCommand):
    help = 'Reset daily email limits for all users'

    def handle(self, *args, **kwargs):
        for usage in EmailUsage.objects.all():
            usage.reset_daily_limit()
        self.stdout.write(self.style.SUCCESS('Successfully reset email limits for all users.'))
