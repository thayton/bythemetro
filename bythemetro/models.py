import re

from django.contrib.auth.models import User
from django.db import models

class MetroSystem(models.Model):
    """
    name - eg, DC Metro, Boston T, Chicago L, ...
    rssfeed - craigslist link to rss feed
    """
    name = models.CharField(max_length=128, unique=True)
    rssfeed = models.URLField(unique=True)

    def __unicode__(self):
        return '%s' % (self.name)

class Station(models.Model):
    system = models.ForeignKey(MetroSystem)
    name = models.CharField(max_length=128, unique=True)
    lat = models.FloatField()
    lng = models.FloatField()

    def __unicode__(self):
        return self.name

class Apartment(models.Model):
    url = models.URLField(unique=True)
    lat = models.FloatField()
    lng = models.FloatField()
    title = models.CharField(max_length=128)
    price = models.IntegerField(null=True)
    num_bedrooms = models.IntegerField(default=False)
    allows_cats = models.BooleanField(default=False)
    allows_dogs = models.BooleanField(default=False)
    has_image = models.BooleanField(default=False)
    date = models.DateTimeField('date last checked')

    def __unicode__(self):
        return '%s [%s]' % (self.title, self.url)

class CheckedLink(models.Model):
    url = models.URLField(unique=True)
    date = models.DateTimeField('date last checked')

    def __unicode__(self):
        return '%s [%s]' % (self.url, self.date)

class ApartmentNearStation(models.Model):
    station = models.ForeignKey(Station)
    distance = models.FloatField()
    apartment = models.ForeignKey(Apartment)

    def __unicode__(self):
        return '%s (%.2f):\t%s' % (self.station, self.distance, self.apartment)

class ApartmentAlert(models.Model):
    user = models.ForeignKey(User)
    station = models.ForeignKey(Station)
    distance = models.IntegerField()
    num_bedrooms = models.IntegerField(null=True, blank=True)
    min_price = models.IntegerField(null=True, blank=True)
    max_price = models.IntegerField(null=True, blank=True)
    allows_cats = models.BooleanField(default=False)
    allows_dogs = models.BooleanField(default=False)
    has_image = models.BooleanField(default=False)

    def __unicode__(self):
        return '%s %d' % (self.station, self.distance)

class AlreadyAlerted(models.Model):
    apartment = models.ForeignKey(Apartment)
    alert = models.ForeignKey(ApartmentAlert)
    user = models.ForeignKey(User)
    date = models.DateTimeField('date alerted')
    
