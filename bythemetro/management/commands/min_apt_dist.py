import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from bythemetro_app.models import *

class Command(BaseCommand):
    help = '''
    An apartment may show up multiple times in ApartmentNearStation if it
    is within 1 mile of multiple stations. If an apartment does show up more
    than once, find the station it is closest to and remove the other instances.
    '''
    def handle(self, *args, **options):
        for apt in Apartment.objects.all():
            list = ApartmentNearStation.objects.filter(apartment=apt)
            closest = None
            if len(list) > 1:
                for apt_near_station in list:
                    if closest is None:
                        closest = apt_near_station
                    elif apt_near_station.distance < closest.distance:
                        closest = apt_near_station
                        
                for apt_near_station in list.exclude(pk=closest.pk):
                    apt_near_station.delete()
            
