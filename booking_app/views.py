from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.utils import timezone
from .models import HealthClass, Booking
from .serializers import HealthClassSerializer, BookingSerializer
import pytz
from datetime import datetime
from django.conf import settings
from datetime import timedelta


# View to get all fitness/health classes and add a new fitness/health class.
@api_view(['GET','POST'])
def classes_view(request):
    if request.method == 'GET':
        classes = HealthClass.objects.filter(datetime__gte=timezone.now()).order_by('datetime')
        serializer = HealthClassSerializer(classes, many=True)
        return Response(serializer.data)
    else:
        name = request.data.get('name')
        instructor = request.data.get('instructor')
        datetime = request.data.get('datetime')                    
        available_slots = request.data.get('available_slots',50)        
        
        if not all([name, instructor, datetime]):
            return Response({"error": "name, instructor, datetime fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        converted_dtm_dict = convert_datetime(datetime)
        if converted_dtm_dict["error_flag"]:
            return Response({"error": converted_dtm_dict['msg']}, status=status.HTTP_400_BAD_REQUEST)
        
        converted_dtm = converted_dtm_dict['datetime']
        
        

        day_start = converted_dtm.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        health_class_record = HealthClass.objects.filter(
                                                        name=name,
                                                        instructor=instructor,
                                                        datetime__gte=day_start,
                                                        datetime__lt=day_end
                                                    )
        
        if health_class_record.exists():
            return Response({"error": f"Class already exist for date: {converted_dtm.date()} with name: {name} and instructor: {instructor}"}, status=status.HTTP_400_BAD_REQUEST)

        
        health_class = HealthClass.objects.create(
            name=name,
            instructor=instructor,
            datetime=converted_dtm,            
            available_slots=available_slots            
        )
        
        serializer = HealthClassSerializer(health_class)
        return Response(serializer.data)
    
# function to convert datetime string      
def convert_datetime(datetime_str):
    res_dict = {"error_flag":False,"msg":None}    
    ist = pytz.timezone(settings.TIME_ZONE)
    
    try:
        dt = datetime.strptime(datetime_str, '%d-%m-%Y %H:%M')        
        if dt.tzinfo is None:
            converted_dtm = ist.localize(dt)
            res_dict['datetime'] = converted_dtm
    except ValueError:
        res_dict.update({"error_flag":True,"msg":"Invalid datetime format. Use DD-MM-YYYY HH:MM"})                
        
    return res_dict


# View to create a new booking.
@api_view(['POST'])
def create_booking_view(request):
    class_id = request.data.get('class_id')
    client_name = request.data.get('client_name')
    client_email = request.data.get('client_email')

    
    if not all([class_id, client_name, client_email]):
        return Response({"error": "class_id, client_name, client_email are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        health_class = HealthClass.objects.get(id=class_id)
    except HealthClass.DoesNotExist:
        return Response({"error": "Class not found."}, status=status.HTTP_404_NOT_FOUND)

    if health_class.available_slots <= 0:
        return Response({"error": "No slots available."}, status=status.HTTP_400_BAD_REQUEST)

    booking_record = Booking.objects.filter(client_email=client_email,health_class=health_class)
    if booking_record.exists():
        return Response({"error": f"Booking Already exist for client {booking_record.first().client_name}"}, status=status.HTTP_400_BAD_REQUEST)
    
    booking = Booking.objects.create(
        health_class=health_class,
        client_name=client_name,
        client_email=client_email
    )

    
    health_class.available_slots -= 1
    health_class.save()

    serializer = BookingSerializer(booking)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# View to create a new booking.
@api_view(['GET'])
def get_bookings_view(request):
    email = request.query_params.get('email')
    if not email:
        return Response({"error": "Email query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

    bookings = Booking.objects.filter(client_email=email).select_related('health_class').order_by('-booked_at')
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)
