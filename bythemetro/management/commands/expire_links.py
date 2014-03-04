import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from bythemetro_app.models import *

class Command(BaseCommand):
    help = 'Expire CheckedLinks that are over 30 days old'

    def handle(self, *args, **options):
        now = datetime.datetime.now()
        for link in CheckedLink.objects.all():
            if now > link.date:
                if (now - link.date).days > 30:
                    try:
                        apt = Apartment.objects.get(url=link.url)
                        apt.delete()
                    except Apartment.DoesNotExist:
                        pass

                    alerts = AlreadyAlerted.objects.filter(apartment__url=link.url)
                    for alert in alerts:
                        alert.delete()

                    link.delete()
                    
