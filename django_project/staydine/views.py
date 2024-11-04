from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from .models import Contact, Dining, MenuItem, Accommodation, RoomType, Highlights, BedType

# Create your views here.
def home(request):
    highlights = Highlights.objects.all()
    return render(request, 'staydine/home.html', {'highlights': highlights})

def about(request):
    return render(request, 'staydine/about.html', {'title': 'About Us'})

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        desc = request.POST.get('desc')
        date = timezone.now().date()

        contact = Contact(name=name, email=email, phone=phone, desc=desc, date=date)
        contact.save()

        messages.success(request, 'Your message has been successfully submitted!')
        return redirect('staydine-contact')

    return render(request, 'staydine/contact.html', {'title': 'Contact Us'})

def services(request):
    return render(request,'staydine/services.html')

def bed_types(request):
    bed_types = BedType.objects.all()
    return render(request, 'staydine/bed_types.html', {'bed_types': bed_types})

def bookings(request):
    if request.method == "POST":
        email = request.POST.get('email')
        room_id = request.POST.get('room_id')
        bed_type_id = request.POST.get('bed_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
            return redirect('staydine-room-bookings')

        if start_date >= end_date:
            messages.error(request, "Start date must be before the end date.")
            return redirect('staydine-room-bookings')

        unavailable_rooms = Accommodation.objects.filter(
            start_date__lt=end_date,
            end_date__gt=start_date
        ).values_list('room__pk', flat=True)

        available_rooms = RoomType.objects.exclude(pk__in=unavailable_rooms)

        if available_rooms.count() == 0:
            messages.error(request, "No rooms are available for the selected dates.")
            return redirect('staydine-room-bookings')

        if room_id:
            room_type = RoomType.objects.get(pk=room_id)
            bed_type = BedType.objects.get(name=bed_type_id)

            number_of_nights = (end_date - start_date).days
            total_amount = number_of_nights * room_type.price_per_night
            
            roombookings = Accommodation(email=email, room=room_type, bed_type=bed_type, start_date=start_date, end_date=end_date)
            roombookings.save()
            messages.success(request, "Your room booking has been placed successfully.")
            
            return redirect(f'/payment/?amount={total_amount}')

    rooms = RoomType.objects.all()
    bed_types = BedType.objects.all()
    return render(request, 'staydine/bookings.html', {'rooms': rooms, 'bed_types': bed_types, 'title':'Bookings'})

def restaurant(request):
    menu_items = MenuItem.objects.all()
    #print(menu_items)
    if request.method == "POST":
        email = request.POST.get('email')
        item_no = request.POST.get('item_no')
        quantity = request.POST.get('quantity')
        
        if not (email and item_no and quantity):
            messages.error(request, "Please fill all fields correctly.")
            return redirect('staydine-restaurant')
        
        try:
            item_no = int(item_no)
            quantity = int(quantity)
        except ValueError:
            messages.error(request, "Item number and quantity must be valid numbers.")
            return redirect('staydine-restaurant')

        try:
            menu_item = MenuItem.objects.get(pk=item_no)
        except MenuItem.DoesNotExist:
            messages.error(request, "Menu item does not exist.")
            return redirect('staydine-restaurant')
        
        total_amount = menu_item.price * quantity

        order = Dining(email=email, item_no=item_no, quantity=quantity)
        order.save()
        messages.success(request, "Your order has been placed successfully.")

        return redirect(f'/payment/?amount={total_amount}')

    return render(request, 'staydine/restaurant.html', {'menu_items': menu_items, 'title': 'Menu Bookings'})
