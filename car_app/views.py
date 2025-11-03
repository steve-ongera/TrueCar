# cars/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count, Avg, Min, Max
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from django.core.paginator import Paginator
from .models import *
from decimal import Decimal
import requests
import base64
import json
from datetime import datetime
import paypalrestsdk


# ============= HOME & LISTINGS =============

from django.shortcuts import render
from django.db.models import Count, Avg, Min, Max
from django.shortcuts import render
from django.db.models import Count, Avg, Min, Max, Q
from .models import Car, CarMake, Review, User

def home(request):
    """
    Home page view with featured cars, statistics, and navigation options
    """
    
    # Get total number of active cars
    total_cars = Car.objects.filter(status='active').count()
    
    # Get featured cars (latest 6 cars)
    featured_cars = Car.objects.filter(
        status='active'
    ).select_related(
        'make', 'model', 'seller'
    ).prefetch_related(
        'images'
    ).order_by('-created_at')[:6]
    
    # Get cars for different categories
    # Shop by budget - cars under different price ranges
    budget_cars = {
        'under_20k': Car.objects.filter(
            status='active',
            price__lt=20000
        ).select_related('make', 'model').prefetch_related('images').order_by('price')[:3],
        'under_30k': Car.objects.filter(
            status='active',
            price__lt=30000,
            price__gte=20000
        ).select_related('make', 'model').prefetch_related('images').order_by('price')[:3],
        'luxury': Car.objects.filter(
            status='active',
            price__gte=50000
        ).select_related('make', 'model').prefetch_related('images').order_by('-price')[:3],
    }
    
    # Get popular makes with car counts
    popular_makes = CarMake.objects.annotate(
        car_count=Count('car', filter=Q(car__status='active'))
    ).filter(car_count__gt=0).order_by('-car_count', 'name')[:12]
    
    # Get cars by body style with counts
    body_styles = Car.objects.filter(
        status='active'
    ).values('body_type').annotate(
        car_count=Count('id')
    ).order_by('-car_count')[:8]
    
    # Get expert reviews (latest 3) - filter for car reviews that are approved
    expert_reviews = Review.objects.filter(
        review_type='car',
        is_approved=True,
        car__isnull=False
    ).select_related('car', 'reviewer', 'car__make', 'car__model').order_by('-created_at')[:3]
    
    # Get customer testimonials (latest 4) - highly rated reviews
    customer_reviews = Review.objects.filter(
        review_type='car',
        is_approved=True,
        rating__gte=4,
        car__isnull=False
    ).select_related('car', 'reviewer', 'car__make', 'car__model').order_by('-created_at')[:4]
    
    # Calculate average savings or price statistics
    price_stats = Car.objects.filter(status='active').aggregate(
        avg_price=Avg('price'),
        min_price=Min('price'),
        max_price=Max('price')
    )
    
    # Get best deals (featured cars sorted by price)
    best_deals = Car.objects.filter(
        status='active',
        is_featured=True
    ).select_related('make', 'model').prefetch_related('images').order_by('price')[:6]
    
    # Additional useful data
    # Get recently added cars
    recent_cars = Car.objects.filter(
        status='active'
    ).select_related('make', 'model').prefetch_related('images').order_by('-created_at')[:4]
    
    # Get urgent sales
    urgent_cars = Car.objects.filter(
        status='active',
        is_urgent=True
    ).select_related('make', 'model').prefetch_related('images').order_by('-created_at')[:4]
    
    context = {
        'total_cars': total_cars,
        'featured_cars': featured_cars,
        'budget_cars': budget_cars,
        'popular_makes': popular_makes,
        'body_styles': body_styles,
        'expert_reviews': expert_reviews,
        'customer_reviews': customer_reviews,
        'price_stats': price_stats,
        'best_deals': best_deals,
        'recent_cars': recent_cars,
        'urgent_cars': urgent_cars,
    }
    
    return render(request, 'home.html', context)



def search_cars(request):
    """
    Search and filter cars based on user criteria
    """
    cars = Car.objects.filter(is_active=True)
    
    # Get filter parameters from request
    make_id = request.GET.get('make')
    model_id = request.GET.get('model')
    min_year = request.GET.get('min_year')
    max_year = request.GET.get('max_year')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    body_style_id = request.GET.get('body_style')
    fuel_type_id = request.GET.get('fuel_type')
    transmission_id = request.GET.get('transmission')
    min_mileage = request.GET.get('min_mileage')
    max_mileage = request.GET.get('max_mileage')
    
    # Apply filters
    if make_id:
        cars = cars.filter(make_id=make_id)
    
    if model_id:
        cars = cars.filter(model_id=model_id)
    
    if min_year:
        cars = cars.filter(year__gte=min_year)
    
    if max_year:
        cars = cars.filter(year__lte=max_year)
    
    if min_price:
        cars = cars.filter(price__gte=min_price)
    
    if max_price:
        cars = cars.filter(price__lte=max_price)
    
    if body_style_id:
        cars = cars.filter(body_style_id=body_style_id)
    
    if fuel_type_id:
        cars = cars.filter(fuel_type_id=fuel_type_id)
    
    if transmission_id:
        cars = cars.filter(transmission_id=transmission_id)
    
    if min_mileage:
        cars = cars.filter(mileage__gte=min_mileage)
    
    if max_mileage:
        cars = cars.filter(mileage__lte=max_mileage)
    
    # Select related for optimization
    cars = cars.select_related(
        'make', 'model', 'body_style', 'fuel_type', 'transmission'
    ).order_by('-created_at')
    
    context = {
        'cars': cars,
        'total_results': cars.count(),
    }
    
    return render(request, 'search_results.html', context)


# Import Q for complex queries
from django.db.models import Q
from django.shortcuts import get_object_or_404


from django.shortcuts import render
from django.db.models import Q, Count, Min, Max
from django.core.paginator import Paginator
from .models import Car, CarMake, CarModel, Favorite
from decimal import Decimal


def car_listing(request):
    """Car listing view with filters and search"""
    
    # Get all active cars
    cars = Car.objects.filter(status='active').select_related(
        'make', 'model', 'seller', 'dealer'
    ).prefetch_related('images')
    
    # Search query
    search_query = request.GET.get('q', '')
    if search_query:
        cars = cars.filter(
            Q(title__icontains=search_query) |
            Q(make__name__icontains=search_query) |
            Q(model__name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by make
    make_filter = request.GET.get('make', '')
    if make_filter:
        cars = cars.filter(make__slug=make_filter)
    
    # Filter by model
    model_filter = request.GET.get('model', '')
    if model_filter:
        cars = cars.filter(model__slug=model_filter)
    
    # Filter by body type
    body_type = request.GET.get('body_type', '')
    if body_type:
        cars = cars.filter(body_type=body_type)
    
    # Filter by condition
    condition = request.GET.get('condition', '')
    if condition:
        cars = cars.filter(condition=condition)
    
    # Filter by fuel type
    fuel_type = request.GET.get('fuel_type', '')
    if fuel_type:
        cars = cars.filter(fuel_type=fuel_type)
    
    # Filter by transmission
    transmission = request.GET.get('transmission', '')
    if transmission:
        cars = cars.filter(transmission=transmission)
    
    # Filter by year range
    year_min = request.GET.get('year_min', '')
    year_max = request.GET.get('year_max', '')
    if year_min:
        cars = cars.filter(year__gte=year_min)
    if year_max:
        cars = cars.filter(year__lte=year_max)
    
    # Filter by price range
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    if price_min:
        cars = cars.filter(price__gte=Decimal(price_min))
    if price_max:
        cars = cars.filter(price__lte=Decimal(price_max))
    
    # Filter by mileage range
    mileage_min = request.GET.get('mileage_min', '')
    mileage_max = request.GET.get('mileage_max', '')
    if mileage_min:
        cars = cars.filter(mileage__gte=mileage_min)
    if mileage_max:
        cars = cars.filter(mileage__lte=mileage_max)
    
    # Filter by city
    city_filter = request.GET.get('city', '')
    if city_filter:
        cars = cars.filter(city__iexact=city_filter)
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    valid_sorts = [
        '-created_at', 'price', '-price', 'mileage', '-mileage', 
        'year', '-year', 'title', '-title'
    ]
    if sort_by in valid_sorts:
        cars = cars.order_by(sort_by)
    
    # Get filter options for sidebar
    makes = CarMake.objects.all().annotate(
        car_count=Count('car', filter=Q(car__status='active'))
    ).filter(car_count__gt=0)
    
    body_types = Car.BODY_TYPE_CHOICES
    conditions = Car.CONDITION_CHOICES
    fuel_types = Car.FUEL_TYPE_CHOICES
    transmissions = Car.TRANSMISSION_CHOICES
    
    # Get price range
    price_range = cars.aggregate(
        min_price=Min('price'),
        max_price=Max('price')
    )
    
    # Get year range
    year_range = cars.aggregate(
        min_year=Min('year'),
        max_year=Max('year')
    )
    
    # Get unique cities
    cities = cars.values_list('city', flat=True).distinct().order_by('city')
    
    # Get user favorites if authenticated
    favorite_car_ids = []
    if request.user.is_authenticated:
        favorite_car_ids = list(
            Favorite.objects.filter(user=request.user).values_list('car_id', flat=True)
        )
    
    # Pagination
    paginator = Paginator(cars, 12)  # 12 cars per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'cars': page_obj,
        'page_obj': page_obj,
        'total_cars': paginator.count,
        'makes': makes,
        'body_types': body_types,
        'conditions': conditions,
        'fuel_types': fuel_types,
        'transmissions': transmissions,
        'cities': cities,
        'price_range': price_range,
        'year_range': year_range,
        'favorite_car_ids': favorite_car_ids,
        'search_query': search_query,
        'current_filters': {
            'make': make_filter,
            'model': model_filter,
            'body_type': body_type,
            'condition': condition,
            'fuel_type': fuel_type,
            'transmission': transmission,
            'year_min': year_min,
            'year_max': year_max,
            'price_min': price_min,
            'price_max': price_max,
            'mileage_min': mileage_min,
            'mileage_max': mileage_max,
            'city': city_filter,
            'sort': sort_by,
        }
    }
    
    return render(request, 'listings.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import (
    Car, CarImage, CarSpecification, InspectionReport, 
    Favorite, Review, Inquiry
)
from decimal import Decimal
import random


def car_detail(request, slug):
    """Car detail view with all related information"""
    
    # Get car with related data
    car = get_object_or_404(
        Car.objects.select_related('make', 'model', 'seller', 'dealer')
        .prefetch_related('images', 'specifications', 'reviews', 'inspections'),
        slug=slug
    )
    
    # Increment view count
    Car.objects.filter(id=car.id).update(views=models.F('views') + 1)
    
    # Get all images
    images = car.images.all().order_by('order', '-is_primary')
    primary_image = images.filter(is_primary=True).first() or images.first()
    
    # Get specifications grouped by category
    specifications = car.specifications.all().order_by('category', 'order')
    specs_by_category = {}
    for spec in specifications:
        category = spec.category or 'General'
        if category not in specs_by_category:
            specs_by_category[category] = []
        specs_by_category[category].append(spec)
    
    # Get reviews
    reviews = car.reviews.filter(is_approved=True).order_by('-created_at')[:5]
    average_rating = car.average_rating
    total_reviews = car.reviews.filter(is_approved=True).count()
    
    # Check if user has favorited
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, car=car).exists()
    
    # Get inspection reports
    inspections = car.inspections.all().order_by('-inspection_date')
    latest_inspection = inspections.first()
    
    # Parse features
    features_list = []
    if car.features:
        features_list = [f.strip() for f in car.features.split(',') if f.strip()]
    
    # Get recommended/similar cars
    similar_cars = Car.objects.filter(
        status='active'
    ).filter(
        Q(make=car.make) | Q(body_type=car.body_type)
    ).exclude(
        id=car.id
    ).select_related(
        'make', 'model'
    ).prefetch_related(
        'images'
    )[:4]
    
    # Calculate potential savings (mock calculation)
    msrp = car.price * Decimal('1.15')  # Mock MSRP as 15% higher
    savings = msrp - car.price
    
    # Get seller info
    seller_cars_count = Car.objects.filter(
        seller=car.seller, 
        status='active'
    ).exclude(id=car.id).count()
    
    context = {
        'car': car,
        'images': images,
        'primary_image': primary_image,
        'specifications': specifications,
        'specs_by_category': specs_by_category,
        'reviews': reviews,
        'average_rating': average_rating,
        'total_reviews': total_reviews,
        'is_favorited': is_favorited,
        'inspections': inspections,
        'latest_inspection': latest_inspection,
        'features_list': features_list,
        'similar_cars': similar_cars,
        'msrp': msrp,
        'savings': savings,
        'seller_cars_count': seller_cars_count,
    }
    
    return render(request, 'car_detail.html', context)


@login_required
def send_inquiry(request, slug):
    """Send inquiry about a car"""
    if request.method == 'POST':
        car = get_object_or_404(Car, slug=slug)
        
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        
        inquiry = Inquiry.objects.create(
            car=car,
            sender=request.user,
            recipient=car.seller,
            name=name,
            email=email,
            phone=phone,
            message=message
        )
        
        # Increment inquiry count
        Car.objects.filter(id=car.id).update(inquiries=F('inquiries') + 1)
        
        messages.success(request, 'Your inquiry has been sent successfully!')
        return redirect('car_detail', slug=slug)
    
    return redirect('car_detail', slug=slug)


@login_required
def add_review(request, slug):
    """Add a review for a car"""
    if request.method == 'POST':
        car = get_object_or_404(Car, slug=slug)
        
        # Check if user already reviewed
        if Review.objects.filter(car=car, reviewer=request.user).exists():
            messages.warning(request, 'You have already reviewed this car.')
            return redirect('car_detail', slug=slug)
        
        rating = request.POST.get('rating')
        title = request.POST.get('title')
        comment = request.POST.get('comment')
        
        review = Review.objects.create(
            review_type='car',
            car=car,
            reviewer=request.user,
            rating=rating,
            title=title,
            comment=comment,
            is_approved=False  # Requires admin approval
        )
        
        messages.success(request, 'Your review has been submitted and is awaiting approval.')
        return redirect('car_detail', slug=slug)
    
    return redirect('car_detail', slug=slug)

# ============= CHECKOUT & PAYMENT =============

@login_required
def checkout(request, car_id):
    """Checkout page"""
    car = get_object_or_404(Car, id=car_id, status='active')
    
    if car.seller == request.user:
        messages.error(request, 'You cannot buy your own car')
        return redirect('car_detail', slug=car.slug)
    
    # Calculate fees
    platform_fee = (car.price * Decimal('5.00')) / 100  # 5% platform fee
    total = car.price + platform_fee
    
    context = {
        'car': car,
        'platform_fee': platform_fee,
        'total': total,
    }
    
    return render(request, 'checkout.html', context)


@login_required
def place_order(request, car_id):
    """Place order"""
    if request.method == 'POST':
        try:
            with transaction.atomic():
                car = get_object_or_404(Car, id=car_id, status='active')
                
                if car.seller == request.user:
                    messages.error(request, 'You cannot buy your own car')
                    return redirect('car_detail', slug=car.slug)
                
                # Calculate amounts
                platform_fee = (car.price * Decimal('5.00')) / 100
                total = car.price + platform_fee
                
                # Create order
                order = Order.objects.create(
                    buyer=request.user,
                    seller=car.seller,
                    car=car,
                    car_price=car.price,
                    platform_fee=platform_fee,
                    total_amount=total,
                    status='pending',
                    buyer_note=request.POST.get('note', '')
                )
                
                # Reserve car
                car.status = 'reserved'
                car.save()
                
                messages.success(request, f'Order {order.order_number} created successfully!')
                return redirect('payment_page', order_id=order.id)
                
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('checkout', car_id=car_id)
    
    return redirect('checkout', car_id=car_id)


@login_required
def payment_page(request, order_id):
    """Payment page"""
    order = get_object_or_404(
        Order.objects.select_related('buyer', 'seller', 'car'),
        id=order_id,
        buyer=request.user
    )
    
    # Get or create pending payment
    payment = order.payments.filter(status='pending').first()
    if not payment:
        payment = Payment.objects.create(
            order=order,
            payment_method='mpesa',
            amount=order.total_amount,
            status='pending'
        )
    
    context = {
        'order': order,
        'payment': payment,
        'PAYPAL_CLIENT_ID': settings.PAYPAL_CLIENT_ID,
    }
    
    return render(request, 'payment.html', context)


# ============= M-PESA PAYMENT =============

@login_required
def initiate_mpesa_payment(request, payment_id):
    """Initiate M-Pesa STK Push"""
    if request.method == 'POST':
        try:
            payment = get_object_or_404(
                Payment.objects.select_related('order'),
                id=payment_id,
                order__buyer=request.user
            )
            
            if payment.status == 'completed':
                return JsonResponse({'error': 'Payment already completed'}, status=400)
            
            phone_number = request.POST.get('phone_number', '').strip()
            
            if not phone_number:
                return JsonResponse({'error': 'Phone number is required'}, status=400)
            
            # Format phone number
            phone_number = phone_number.replace('+', '').replace(' ', '')
            if phone_number.startswith('0'):
                phone_number = '254' + phone_number[1:]
            elif not phone_number.startswith('254'):
                phone_number = '254' + phone_number
            
            if not phone_number.isdigit() or len(phone_number) != 12:
                return JsonResponse({
                    'error': 'Invalid phone number. Use 07XXXXXXXX or 2547XXXXXXXX'
                }, status=400)
            
            # Get M-Pesa access token
            access_token = get_mpesa_access_token()
            
            if not access_token:
                return JsonResponse({'error': 'Failed to authenticate with M-Pesa'}, status=500)
            
            # Prepare STK Push
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            business_short_code = settings.MPESA_SHORTCODE
            passkey = settings.MPESA_PASSKEY
            
            password = base64.b64encode(
                (business_short_code + passkey + timestamp).encode()
            ).decode('utf-8')
            
            stk_push_url = settings.MPESA_STK_PUSH_URL
            callback_url = settings.MPESA_CALLBACK_URL
            
            payload = {
                "BusinessShortCode": business_short_code,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(payment.amount),
                "PartyA": phone_number,
                "PartyB": business_short_code,
                "PhoneNumber": phone_number,
                "CallBackURL": callback_url,
                "AccountReference": payment.order.order_number,
                "TransactionDesc": f"Payment for {payment.order.car.title}"
            }
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(stk_push_url, json=payload, headers=headers)
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get('ResponseCode') == '0':
                payment.status = 'processing'
                payment.mpesa_phone = phone_number
                payment.payment_method = 'mpesa'
                payment.response_data = response_data
                payment.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Payment request sent. Check your phone.',
                    'checkout_request_id': response_data.get('CheckoutRequestID')
                })
            else:
                error_message = response_data.get('errorMessage', 'Failed to initiate payment')
                payment.status = 'failed'
                payment.failure_reason = error_message
                payment.response_data = response_data
                payment.save()
                
                return JsonResponse({'error': error_message}, status=400)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


def get_mpesa_access_token():
    """Get M-Pesa OAuth access token"""
    try:
        consumer_key = settings.MPESA_CONSUMER_KEY
        consumer_secret = settings.MPESA_CONSUMER_SECRET
        auth_url = settings.MPESA_AUTH_URL
        
        credentials = base64.b64encode(
            f"{consumer_key}:{consumer_secret}".encode()
        ).decode('utf-8')
        
        headers = {"Authorization": f"Basic {credentials}"}
        response = requests.get(auth_url, headers=headers)
        
        if response.status_code == 200:
            return response.json().get('access_token')
        
        return None
    except Exception as e:
        print(f"Error getting access token: {e}")
        return None


@csrf_exempt
def mpesa_callback(request):
    """M-Pesa callback endpoint"""
    try:
        callback_data = json.loads(request.body)
        body = callback_data.get('Body', {})
        stk_callback = body.get('stkCallback', {})
        
        result_code = stk_callback.get('ResultCode')
        checkout_request_id = stk_callback.get('CheckoutRequestID')
        
        payment = Payment.objects.filter(
            response_data__CheckoutRequestID=checkout_request_id
        ).first()
        
        if not payment:
            return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Payment not found'})
        
        if result_code == 0:
            # Success
            callback_metadata = stk_callback.get('CallbackMetadata', {})
            items = callback_metadata.get('Item', [])
            
            mpesa_receipt = None
            for item in items:
                if item.get('Name') == 'MpesaReceiptNumber':
                    mpesa_receipt = item.get('Value')
                    break
            
            payment.status = 'completed'
            payment.mpesa_receipt = mpesa_receipt
            payment.completed_at = timezone.now()
            payment.response_data = callback_data
            payment.save()
            
            # Update order
            order = payment.order
            order.status = 'completed'
            order.completed_at = timezone.now()
            order.save()
            
            # Update car
            car = order.car
            car.status = 'sold'
            car.sold_at = timezone.now()
            car.save()
            
        else:
            # Failed
            payment.status = 'failed'
            payment.failure_reason = stk_callback.get('ResultDesc')
            payment.response_data = callback_data
            payment.save()
            
            # Release car
            order = payment.order
            car = order.car
            car.status = 'active'
            car.save()
        
        return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Success'})
    except Exception as e:
        print(f"Callback error: {e}")
        return JsonResponse({'ResultCode': 1, 'ResultDesc': str(e)})


# ============= PAYPAL PAYMENT =============

# Configure PayPal
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})


@login_required
def create_paypal_payment(request, payment_id):
    """Create PayPal payment"""
    if request.method == 'POST':
        try:
            payment_obj = get_object_or_404(
                Payment.objects.select_related('order'),
                id=payment_id,
                order__buyer=request.user
            )
            
            if payment_obj.status == 'completed':
                return JsonResponse({'error': 'Payment already completed'}, status=400)
            
            # Create PayPal payment
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "redirect_urls": {
                    "return_url": request.build_absolute_uri(f"/payment/paypal/execute/{payment_obj.id}/"),
                    "cancel_url": request.build_absolute_uri(f"/payment/paypal/cancel/{payment_obj.id}/")
                },
                "transactions": [{
                    "item_list": {
                        "items": [{
                            "name": payment_obj.order.car.title,
                            "sku": str(payment_obj.order.car.id),
                            "price": str(payment_obj.amount),
                            "currency": "USD",
                            "quantity": 1
                        }]
                    },
                    "amount": {
                        "total": str(payment_obj.amount),
                        "currency": "USD"
                    },
                    "description": f"Payment for {payment_obj.order.car.title}"
                }]
            })
            
            if payment.create():
                payment_obj.payment_method = 'paypal'
                payment_obj.paypal_transaction_id = payment.id
                payment_obj.status = 'processing'
                payment_obj.save()
                
                # Get approval URL
                for link in payment.links:
                    if link.rel == "approval_url":
                        return JsonResponse({
                            'success': True,
                            'approval_url': link.href
                        })
            else:
                return JsonResponse({
                    'error': payment.error
                }, status=400)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def execute_paypal_payment(request, payment_id):
    """Execute PayPal payment"""
    payment_obj = get_object_or_404(
        Payment.objects.select_related('order'),
        id=payment_id,
        order__buyer=request.user
    )
    
    payment_id_paypal = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    
    if not payment_id_paypal or not payer_id:
        messages.error(request, 'Invalid PayPal response')
        return redirect('payment_page', order_id=payment_obj.order.id)
    
    try:
        payment = paypalrestsdk.Payment.find(payment_id_paypal)
        
        if payment.execute({"payer_id": payer_id}):
            # Payment successful
            payment_obj.status = 'completed'
            payment_obj.paypal_payer_id = payer_id
            payment_obj.completed_at = timezone.now()
            payment_obj.save()
            
            # Update order
            order = payment_obj.order
            order.status = 'completed'
            order.completed_at = timezone.now()
            order.save()
            
            # Update car
            car = order.car
            car.status = 'sold'
            car.sold_at = timezone.now()
            car.save()
            
            messages.success(request, 'Payment completed successfully!')
            return redirect('payment_success', order_id=order.id)
        else:
            messages.error(request, 'Payment execution failed')
            return redirect('payment_page', order_id=payment_obj.order.id)
            
    except Exception as e:
        messages.error(request, str(e))
        return redirect('payment_page', order_id=payment_obj.order.id)


@login_required
def cancel_paypal_payment(request, payment_id):
    """Cancel PayPal payment"""
    payment_obj = get_object_or_404(
        Payment.objects.select_related('order'),
        id=payment_id,
        order__buyer=request.user
    )
    
    payment_obj.status = 'cancelled'
    payment_obj.save()
    
    # Release car
    car = payment_obj.order.car
    car.status = 'active'
    car.save()
    
    messages.warning(request, 'Payment cancelled')
    return redirect('payment_page', order_id=payment_obj.order.id)


# ============= STRIPE/CARD PAYMENT =============
# Note: You'll need to install stripe: pip install stripe
# import stripe
# stripe.api_key = settings.STRIPE_SECRET_KEY

# @login_required
# def create_stripe_payment(request, payment_id):
#     """Create Stripe payment intent"""
#     pass

# @csrf_exempt
# def stripe_webhook(request):
#     """Stripe webhook for payment confirmation"""
#     pass


# ============= USER ACTIONS =============

@login_required
def toggle_favorite(request, car_id):
    """Add/remove car from favorites"""
    car = get_object_or_404(Car, id=car_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, car=car)
    
    if not created:
        favorite.delete()
        return JsonResponse({'favorited': False})
    
    return JsonResponse({'favorited': True})


@login_required
def send_inquiry(request, car_id):
    """Send inquiry about a car"""
    if request.method == 'POST':
        car = get_object_or_404(Car, id=car_id)
        
        Inquiry.objects.create(
            car=car,
            sender=request.user,
            recipient=car.seller,
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            message=request.POST.get('message')
        )
        
        messages.success(request, 'Inquiry sent successfully!')
        return redirect('car_detail', slug=car.slug)
    
    return redirect('home')


@login_required
def payment_success(request, order_id):
    """Payment success page"""
    order = get_object_or_404(
        Order.objects.select_related('buyer', 'car'),
        id=order_id,
        buyer=request.user
    )
    
    payment = order.payments.filter(status='completed').first()
    
    context = {
        'order': order,
        'payment': payment,
    }
    
    return render(request, 'payment_success.html', context)


@login_required
def my_orders(request):
    """User's orders"""
    orders = Order.objects.filter(
        buyer=request.user
    ).select_related('car', 'seller').order_by('-created_at')
    
    context = {'orders': orders}
    return render(request, 'my_orders.html', context)
