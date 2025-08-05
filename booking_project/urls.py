from django.contrib import admin
from django.urls import path
from booking_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('classes/', views.classes_view,name="classes"),
    path('book/', views.create_booking_view,name="book_class"),
    path('bookings/', views.get_bookings_view,name="bookings"),
]

