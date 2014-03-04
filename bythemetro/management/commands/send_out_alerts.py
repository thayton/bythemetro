import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from bythemetro_app.models import *

def matches(apt_near_station, apt_alert):
    ''' Returns true if apt_near_station matches apt_alert '''
    if apt_alert.distance:
        if apt_near_station.distance > apt_alert.distance:
            return False

    if apt_alert.min_price:
        if not apt_near_station.apartment.price or apt_near_station.apartment.price < apt_alert.min_price:
            return False

    if apt_alert.max_price:
        if not apt_near_station.apartment.price or apt_near_station.apartment.price > apt_alert.max_price:
            return False

    if apt_alert.allows_cats:
        if not apt_near_station.apartment.allows_cats:
            return False

    if apt_alert.allows_dogs:
        if not apt_near_station.apartment.allows_dogs:
            return False

    if apt_alert.has_image:
        if not apt_near_station.apartment.has_image:
            return False

    return True

class Command(BaseCommand):
    help = 'Send out alerts for apartments for rent near stations'

    def handle(self, *args, **options):
        for user in User.objects.all():
            apartments = []
            for apt_alert in user.apartmentalert_set.all():
                for apt_near_station in apt_alert.station.apartmentnearstation_set.all():
                    try:
                        user.alreadyalerted_set.get(user=user, alert=apt_alert, apartment=apt_near_station.apartment)
                        continue
                    except AlreadyAlerted.DoesNotExist:
                        pass

                    if matches(apt_near_station, apt_alert):
                        apartments.append(apt_near_station)

            if len(apartments) > 0:
                msg = '\n\n'.join(['%s\n%s\ndist=%.2f miles from %s metro station\n' % \
                                   (x.apartment.title, x.apartment.url, x.distance, x.station.name) \
                                   for x in apartments])
                with open('/home/thayton/bythemetro.txt', 'w') as f:
                    f.write(msg)
                    f.close()
                    os.system('cat /home/thayton/bythemetro.txt | sendmail todd.hayton@gmail.com')
                
                                                                                                            
