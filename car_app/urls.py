# cars/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Home & Listings
    path('', views.home, name='home'),
    path('cars/', views.car_listing, name='car_listings'),
    path('cars/<slug:slug>/', views.car_detail, name='car_detail'),

    # Send inquiry
    path('<slug:slug>/inquiry/', views.send_inquiry, name='send_inquiry'),
    
    # Add review
    path('<slug:slug>/review/', views.add_review, name='add_review'),
    
    # Search & Filters
    path('search/', views.car_listing, name='search'),
    path('brand-new/', views.car_listing, name='brand_new'),
    path('used-cars/', views.car_listing, name='used_cars'),
    path('crashed-cars/', views.car_listing, name='crashed_cars'),
    
    # Checkout & Orders
    path('checkout/<int:car_id>/', views.checkout, name='checkout'),
    path('order/place/<int:car_id>/', views.place_order, name='place_order'),
    path('orders/', views.my_orders, name='my_orders'),
    
    # Payment
    path('payment/<int:order_id>/', views.payment_page, name='payment_page'),
    path('payment/success/<int:order_id>/', views.payment_success, name='payment_success'),
    
    # M-Pesa
    path('payment/mpesa/initiate/<int:payment_id>/', views.initiate_mpesa_payment, name='initiate_mpesa'),
    path('payment/mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
    
    # PayPal
    path('payment/paypal/create/<int:payment_id>/', views.create_paypal_payment, name='create_paypal'),
    path('payment/paypal/execute/<int:payment_id>/', views.execute_paypal_payment, name='execute_paypal'),
    path('payment/paypal/cancel/<int:payment_id>/', views.cancel_paypal_payment, name='cancel_paypal'),
    
    # User Actions
    path('favorite/<int:car_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('inquiry/<int:car_id>/', views.send_inquiry, name='send_inquiry'),
]
