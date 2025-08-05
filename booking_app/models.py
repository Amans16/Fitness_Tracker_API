from django.db import models

class HealthClass(models.Model):
    name = models.CharField(max_length=100)
    instructor = models.CharField(max_length=100)
    datetime = models.DateTimeField()    
    available_slots = models.PositiveIntegerField(default=50)

    def __str__(self):
        return f"{self.name} | {self.datetime.strftime('%Y-%m-%d %H:%M')}"
    
class Booking(models.Model):
    health_class = models.ForeignKey(HealthClass, on_delete=models.CASCADE, related_name='bookings')
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField()
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client_name} | {self.health_class.name}"

