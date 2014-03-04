from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from bythemetro_app.models import *

class Command(BaseCommand):
    args = '<metro_system_id> <filename>'
    help = 'Upload station information from file into database'

    def handle(self, *args, **options):
        metro_system_id = int(args[0])
        filename = args[1]

        try:
            metro_system = MetroSystem.objects.get(pk=metro_system_id)
        except MetroSystem.DoesNotExist:
            raise CommandError('Metro system "%s" does not exist' % metro_system_id)

        metro_system.station_set.all().delete()
        with open(filename, 'r') as f:
            stations = eval(f.read())
            for tuple in stations:
                station, created = metro_system.station_set.get_or_create(name=tuple[0], 
                                                                          lat=tuple[-1][0], 
                                                                          lng=tuple[-1][1])
                station.save()

            
