import sys
import time
import webcli
import urllib
import datetime

from BeautifulSoup import BeautifulStoneSoup
from geopy import geocoders
from geopy.distance import distance
from django.core.management.base import BaseCommand, CommandError
from bythemetro_app.models import *

GMAPS_LINK_RE = re.compile(r'(http://maps\.google\.com/\?q=loc.*?)"')
IMAGE_LINK_RE = re.compile(r'http://images\.craigslist\.org/\w+\.jpg$')
ALLOWS_CATS_RE = re.compile(r'catsAreOK=on.*?cats are OK - purrr')
ALLOWS_DOGS_RE = re.compile(r'dogsAreOK=on.*?dogs are OK - wooof')
PRICE_RE = re.compile(r'\$(\d+)')
ROOM_RE = re.compile(r'(\d)bd\b')

class Command(BaseCommand):
    args = '<metro_system_id> <metro_system_id> ...'
    help = 'Updates listing of apartments for rent near stations'

    def handle(self, *args, **options):
        """
        Get a list of apartments that have a location specified. Then compare each 
        apartment's location to all of the metro station locations and save those
        that are within one mile of a metro station.
        """
        for metro_system_id in args:
            try:
                metro_system = MetroSystem.objects.get(pk=int(metro_system_id))
            except MetroSystem.DoesNotExist:
                raise CommandError('Metro system "%s" does not exist' % metro_system_id)

            for apt in self.get_apartments_to_check(metro_system):
                for station in metro_system.station_set.all():
                    dist = distance((apt.lat, apt.lng), (station.lat, station.lng)).miles
                    if dist > 1:
                        continue

                    try:
                        station.apartmentnearstation_set.get(apartment__url=apt.url)
                        continue
                    except ApartmentNearStation.DoesNotExist:
                        pass

                    sys.stderr.write('Apartment %s near (%.2f) station %s\n' % (apt.url, dist, station.name))

                    apt.save()
                    apt_near_station = ApartmentNearStation()
                    apt_near_station.apartment = apt
                    apt_near_station.station = station
                    apt_near_station.distance = dist
                    apt_near_station.save()

        # An apartment may show up multiple times in ApartmentNearStation if it
        # is within 1 mile of multiple stations. If an apartment does show up more
        # than once, find the station it is closest to and remove the other instances.
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

    def get_apartments_to_check(self, metro_system):
        """
        Return a list of apartments that have a location specified (via google maps).
        """
        parser = RSSItemParser()
        apartments = []

        s = BeautifulStoneSoup(webcli.get(metro_system.rssfeed))
        for item in s.findAll('item'):
            try:
                CheckedLink.objects.get(url=item.link.text)
                sys.stderr.write('Skipping link %s\n' % item.link.text)
                continue
            except CheckedLink.DoesNotExist:
                pass
                
            try:
                apt = Apartment.objects.get(url=item.link.text)
                sys.stderr.write('Skipping link %s\n' % item.link.text)
                continue
            except Apartment.DoesNotExist:
                pass

            apt = Apartment(url=item.link.text, title=item.title.text, date=datetime.datetime.now())
            parser.parse(apt, item)            

            if apt.lat is not None:
                apartments.append(apt)
                sys.stderr.write('Added link %s\n' % item.link.text)

            CheckedLink(url=item.link.text, date=datetime.datetime.now()).save()

        return apartments
        
class RSSItemParser():
    """
    Parse an RSS item element from the craigslist RSS feed.
    """
    def __init__(self):
        pass

    def parse(self, apt, item):
        self.set_lat_lng(apt, item)
        self.set_price(apt, item)
        self.set_num_rooms(apt, item)
        self.set_has_image(apt, item)
        self.set_allows_cats(apt, item)
        self.set_allows_dogs(apt, item)

    def set_allows_cats(self, apt, item):
        l = re.search(ALLOWS_CATS_RE, item.description.text)
        if l:
            apt.allows_cats = True

    def set_allows_dogs(self, apt, item):
        l = re.search(ALLOWS_DOGS_RE, item.description.text)
        if l:
            apt.allows_dogs = True

    def set_has_image(self, apt, item):
        i = re.search(IMAGE_LINK_RE, item.description.text)
        if i:
            apt.has_image = True

    def set_lat_lng(self, apt, item):
        m = re.search(GMAPS_LINK_RE, item.description.text)
        if not m:
            return

        gmaps_link = urllib.unquote_plus(m.group(1))

        m = re.search(r'\?q=loc:(.*)', gmaps_link)
        if not m:
            return

        g = geocoders.Google()
        try:
            place, coord = g.geocode(m.group(1))
        except:
            return

        apt.lat,apt.lng = coord[0],coord[1]
        
    def set_price(self, apt, item):
        m = re.search(PRICE_RE, item.title.text)
        if m:
            apt.price = int(m.group(1))

    def set_num_rooms(self, apt, item):
        m = re.search(ROOM_RE, item.title.text)
        if m:
            apt.num_bedrooms = int(m.group(1))
