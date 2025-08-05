from rest_framework import serializers
from .models import HealthClass, Booking
import pytz
from django.conf import settings

class HealthClassSerializer(serializers.ModelSerializer):
    datetime = serializers.SerializerMethodField()

    class Meta:
        model = HealthClass
        fields = ['name', 'datetime', 'instructor', 'available_slots']

    def get_datetime(self, obj):
        ist = pytz.timezone(settings.TIME_ZONE)
        return obj.datetime.astimezone(ist).strftime('%d-%m-%Y %H:%M')

class BookingSerializer(serializers.ModelSerializer):
    booked_at = serializers.SerializerMethodField()
    health_class_name = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = ['health_class_name', 'client_name', 'client_email', 'booked_at']

    def get_booked_at(self, obj):
        ist = pytz.timezone(settings.TIME_ZONE)
        return obj.booked_at.astimezone(ist).strftime('%d-%m-%Y %H:%M')

    def get_health_class_name(self, obj):
        return obj.health_class.name
