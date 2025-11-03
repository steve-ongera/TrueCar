# cars/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'phone_number', 'user_type', 'is_verified', 'created_at']
    list_filter = ['user_type', 'is_verified', 'is_staff']
    search_fields = ['username', 'email', 'phone_number']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'user_type', 'profile_picture', 'date_of_birth', 
                      'address', 'city', 'country', 'is_verified', 'rating')
        }),
    )


@admin.register(Dealer)
class DealerAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'user', 'city', 'is_verified', 'is_premium', 'rating', 'total_listings']
    list_filter = ['is_verified', 'is_premium', 'city']
    search_fields = ['business_name', 'email', 'phone']
    prepopulated_fields = {'slug': ('business_name',)}


@admin.register(CarMake)
class CarMakeAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'is_popular', 'order']
    list_filter = ['is_popular', 'country']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'make', 'is_popular']
    list_filter = ['make', 'is_popular']
    search_fields = ['name', 'make__name']
    prepopulated_fields = {'slug': ('name',)}


class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 1


class CarSpecificationInline(admin.TabularInline):
    model = CarSpecification
    extra = 1


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['title', 'make', 'model', 'year', 'condition', 'price', 'status', 'seller', 'views', 'created_at']
    list_filter = ['status', 'condition', 'body_type', 'fuel_type', 'transmission', 'make', 'is_featured']
    search_fields = ['title', 'vin', 'make__name', 'model__name']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views', 'inquiries', 'created_at', 'updated_at']
    inlines = [CarImageInline, CarSpecificationInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('seller', 'dealer', 'make', 'model', 'year', 'title', 'slug', 'vin')
        }),
        ('Condition & Type', {
            'fields': ('condition', 'body_type')
        }),
        ('Specifications', {
            'fields': ('mileage', 'engine_size', 'fuel_type', 'transmission', 'drive_type',
                      'exterior_color', 'interior_color', 'doors', 'seats')
        }),
        ('Pricing', {
            'fields': ('price', 'negotiable')
        }),
        ('Location', {
            'fields': ('location', 'city', 'country', 'latitude', 'longitude')
        }),
        ('Description & Features', {
            'fields': ('description', 'features')
        }),
        ('Status & Visibility', {
            'fields': ('status', 'is_featured', 'is_urgent')
        }),
        ('Stats', {
            'fields': ('views', 'inquiries', 'created_at', 'updated_at', 'published_at', 'sold_at')
        }),
    )


@admin.register(CarImage)
class CarImageAdmin(admin.ModelAdmin):
    list_display = ['car', 'is_primary', 'order', 'uploaded_at']
    list_filter = ['is_primary', 'uploaded_at']
    search_fields = ['car__title']


@admin.register(InspectionReport)
class InspectionReportAdmin(admin.ModelAdmin):
    list_display = ['car', 'inspector_name', 'inspection_date', 'overall_condition']
    list_filter = ['overall_condition', 'inspection_date']
    search_fields = ['car__title', 'inspector_name']


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ['car', 'sender', 'recipient', 'name', 'is_read', 'replied', 'created_at']
    list_filter = ['is_read', 'replied', 'created_at']
    search_fields = ['car__title', 'name', 'email', 'message']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['review_type', 'car', 'reviewer', 'rating', 'is_approved', 'created_at']
    list_filter = ['review_type', 'rating', 'is_approved', 'is_verified_purchase']
    search_fields = ['title', 'comment', 'reviewer__username']


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'car', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'car__title']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'buyer', 'seller', 'car', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'buyer__username', 'seller__username', 'car__title']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'completed_at']
    
    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'buyer', 'seller', 'car', 'status')
        }),
        ('Pricing', {
            'fields': ('car_price', 'platform_fee', 'delivery_fee', 'total_amount')
        }),
        ('Delivery', {
            'fields': ('delivery_method', 'delivery_address')
        }),
        ('Notes', {
            'fields': ('buyer_note', 'admin_note')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'order', 'payment_method', 'amount', 'status', 'created_at']
    list_filter = ['payment_method', 'status', 'created_at']
    search_fields = ['transaction_id', 'order__order_number', 'mpesa_receipt', 'paypal_transaction_id']
    readonly_fields = ['transaction_id', 'created_at', 'completed_at']
    
    fieldsets = (
        ('Payment Info', {
            'fields': ('transaction_id', 'order', 'payment_method', 'status', 'amount', 'currency')
        }),
        ('M-Pesa Details', {
            'fields': ('mpesa_receipt', 'mpesa_phone', 'mpesa_transaction_id'),
            'classes': ('collapse',)
        }),
        ('PayPal Details', {
            'fields': ('paypal_transaction_id', 'paypal_payer_id', 'paypal_payer_email'),
            'classes': ('collapse',)
        }),
        ('Card Details', {
            'fields': ('card_last4', 'card_brand', 'card_token'),
            'classes': ('collapse',)
        }),
        ('Additional Info', {
            'fields': ('response_data', 'failure_reason', 'created_at', 'completed_at')
        }),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'query', 'results_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['query', 'user__username']


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'is_active', 'start_date', 'end_date']
    list_filter = ['is_active', 'start_date']
    search_fields = ['title', 'subtitle']


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'contact_email', 'contact_phone']
    
    def has_add_permission(self, request):
        # Only allow one settings object
        return not SiteSettings.objects.exists()


# Customize admin site
admin.site.site_header = "TrueCar Admin"
admin.site.site_title = "TrueCar Admin Portal"
admin.site.index_title = "Welcome to TrueCar Admin Portal"