
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg
from decimal import Decimal
import uuid


class User(AbstractUser):
    """Extended user model"""
    USER_TYPES = (
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('dealer', 'Dealer'),
        ('admin', 'Admin'),
    )
    
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='buyer')
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(default=False)
    id_verified = models.BooleanField(default=False)
    id_document = models.FileField(upload_to='ids/', null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_sales = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'users'
    
    def __str__(self):
        return self.username


class Dealer(models.Model):
    """Dealer/Showroom information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    logo = models.ImageField(upload_to='dealers/', null=True, blank=True)
    banner = models.ImageField(upload_to='dealers/banners/', null=True, blank=True)
    description = models.TextField()
    business_license = models.CharField(max_length=100)
    tax_id = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    website = models.URLField(blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_listings = models.IntegerField(default=0)
    established_year = models.IntegerField(null=True, blank=True)
    operating_hours = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'dealers'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.business_name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.business_name


class CarMake(models.Model):
    """Car manufacturers/brands"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='makes/', null=True, blank=True)
    country = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_popular = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'car_makes'
        ordering = ['order', 'name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class CarModel(models.Model):
    """Car models"""
    make = models.ForeignKey(CarMake, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    is_popular = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'car_models'
        ordering = ['name']
        unique_together = ['make', 'name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.make.name} {self.name}"


class Car(models.Model):
    """Main car listing model"""
    CONDITION_CHOICES = (
        ('brand_new', 'Brand New'),
        ('foreign_used', 'Foreign Used'),
        ('locally_used', 'Locally Used'),
        ('crashed', 'Crashed/Salvage'),
    )
    
    BODY_TYPE_CHOICES = (
        ('sedan', 'Sedan'),
        ('suv', 'SUV'),
        ('hatchback', 'Hatchback'),
        ('coupe', 'Coupe'),
        ('wagon', 'Station Wagon'),
        ('pickup', 'Pickup Truck'),
        ('van', 'Van'),
        ('minivan', 'Minivan'),
        ('convertible', 'Convertible'),
        ('sports', 'Sports Car'),
    )
    
    FUEL_TYPE_CHOICES = (
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('hybrid', 'Hybrid'),
        ('electric', 'Electric'),
        ('lpg', 'LPG'),
    )
    
    TRANSMISSION_CHOICES = (
        ('manual', 'Manual'),
        ('automatic', 'Automatic'),
        ('cvt', 'CVT'),
    )
    
    DRIVE_TYPE_CHOICES = (
        ('fwd', 'Front Wheel Drive'),
        ('rwd', 'Rear Wheel Drive'),
        ('awd', 'All Wheel Drive'),
        ('4wd', '4 Wheel Drive'),
    )
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('active', 'Active'),
        ('sold', 'Sold'),
        ('reserved', 'Reserved'),
        ('rejected', 'Rejected'),
    )
    
    # Basic Information
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cars')
    dealer = models.ForeignKey(Dealer, on_delete=models.SET_NULL, null=True, blank=True, related_name='cars')
    
    make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    model = models.ForeignKey(CarModel, on_delete=models.CASCADE)
    year = models.IntegerField(validators=[MinValueValidator(1900), MaxValueValidator(2025)])
    
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    vin = models.CharField(max_length=17, unique=True, blank=True, null=True, help_text="Vehicle Identification Number")
    
    # Condition & Type
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    body_type = models.CharField(max_length=20, choices=BODY_TYPE_CHOICES)
    
    # Technical Specifications
    mileage = models.IntegerField(validators=[MinValueValidator(0)], help_text="In kilometers")
    engine_size = models.DecimalField(max_digits=4, decimal_places=1, help_text="In liters (e.g., 2.0)")
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPE_CHOICES)
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES)
    drive_type = models.CharField(max_length=20, choices=DRIVE_TYPE_CHOICES)
    
    exterior_color = models.CharField(max_length=50)
    interior_color = models.CharField(max_length=50)
    
    doors = models.IntegerField(validators=[MinValueValidator(2), MaxValueValidator(5)])
    seats = models.IntegerField(validators=[MinValueValidator(2), MaxValueValidator(9)])
    
    # Pricing
    price = models.DecimalField(max_digits=12, decimal_places=2)
    negotiable = models.BooleanField(default=True)
    
    # Location
    location = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='Kenya')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Description
    description = models.TextField()
    
    # Features & Extras
    features = models.TextField(help_text="Comma-separated features")
    
    # Status & Stats
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    is_urgent = models.BooleanField(default=False)
    views = models.IntegerField(default=0)
    inquiries = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    sold_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'cars'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['make', 'model']),
            models.Index(fields=['price']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.make.name} {self.model.name} {self.year}")
            self.slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"
        if not self.title:
            self.title = f"{self.year} {self.make.name} {self.model.name}"
        super().save(*args, **kwargs)
    
    @property
    def average_rating(self):
        return self.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    def __str__(self):
        return self.title


class CarImage(models.Model):
    """Car images"""
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='cars/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'car_images'
        ordering = ['order', '-is_primary']
    
    def __str__(self):
        return f"Image for {self.car.title}"


class CarSpecification(models.Model):
    """Additional car specifications"""
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='specifications')
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=200)
    category = models.CharField(max_length=50, blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'car_specifications'
        ordering = ['category', 'order']
    
    def __str__(self):
        return f"{self.name}: {self.value}"


class InspectionReport(models.Model):
    """Vehicle inspection reports"""
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='inspections')
    inspector_name = models.CharField(max_length=200)
    inspection_date = models.DateField()
    overall_condition = models.CharField(max_length=20, choices=[
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ])
    report_file = models.FileField(upload_to='inspections/', null=True, blank=True)
    notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'inspection_reports'
    
    def __str__(self):
        return f"Inspection for {self.car.title}"


class Inquiry(models.Model):
    """Car inquiries/messages"""
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='car_inquiries')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_inquiries')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_inquiries')
    
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    message = models.TextField()
    
    is_read = models.BooleanField(default=False)
    replied = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'inquiries'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Inquiry for {self.car.title} from {self.name}"


class Review(models.Model):
    """Car/Seller reviews"""
    REVIEW_TYPE = (
        ('car', 'Car Review'),
        ('seller', 'Seller Review'),
        ('dealer', 'Dealer Review'),
    )
    
    review_type = models.CharField(max_length=20, choices=REVIEW_TYPE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_reviews', null=True, blank=True)
    dealer = models.ForeignKey(Dealer, on_delete=models.CASCADE, related_name='dealer_reviews', null=True, blank=True)
    
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200)
    comment = models.TextField()
    
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.rating}★ review by {self.reviewer.username}"


class Favorite(models.Model):
    """User favorites/saved cars"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'favorites'
        unique_together = ['user', 'car']
    
    def __str__(self):
        return f"{self.user.username} saved {self.car.title}"


class Order(models.Model):
    """Car purchase orders"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )
    
    order_number = models.CharField(max_length=50, unique=True)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales')
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    
    # Pricing
    car_price = models.DecimalField(max_digits=12, decimal_places=2)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Delivery info
    delivery_method = models.CharField(max_length=50, blank=True)
    delivery_address = models.TextField(blank=True)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Notes
    buyer_note = models.TextField(blank=True)
    admin_note = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.order_number


class Payment(models.Model):
    """Payment transactions"""
    PAYMENT_METHOD = (
        ('mpesa', 'M-Pesa'),
        ('paypal', 'PayPal'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
    )
    
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='KES')
    
    # M-Pesa specific
    mpesa_receipt = models.CharField(max_length=100, blank=True)
    mpesa_phone = models.CharField(max_length=15, blank=True)
    mpesa_transaction_id = models.CharField(max_length=100, blank=True)
    
    # PayPal specific
    paypal_transaction_id = models.CharField(max_length=100, blank=True)
    paypal_payer_id = models.CharField(max_length=100, blank=True)
    paypal_payer_email = models.EmailField(blank=True)
    
    # Card specific
    card_last4 = models.CharField(max_length=4, blank=True)
    card_brand = models.CharField(max_length=20, blank=True)
    card_token = models.CharField(max_length=200, blank=True)
    
    # Additional info
    response_data = models.JSONField(null=True, blank=True)
    failure_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.transaction_id} - {self.payment_method}"


class Notification(models.Model):
    """User notifications"""
    NOTIFICATION_TYPE = (
        ('inquiry', 'New Inquiry'),
        ('order', 'Order Update'),
        ('payment', 'Payment'),
        ('review', 'New Review'),
        ('system', 'System'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=200, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class SearchHistory(models.Model):
    """User search history"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='searches', null=True, blank=True)
    session_key = models.CharField(max_length=100, blank=True)
    query = models.CharField(max_length=200)
    filters = models.JSONField(null=True, blank=True)
    results_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'search_history'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.query


class CompareList(models.Model):
    """Car comparison lists"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='compare_lists')
    cars = models.ManyToManyField(Car, related_name='in_comparisons')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'compare_lists'
    
    def __str__(self):
        return f"Compare list by {self.user.username}"


class Banner(models.Model):
    """Homepage banners"""
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='banners/')
    mobile_image = models.ImageField(upload_to='banners/mobile/', null=True, blank=True)
    link = models.CharField(max_length=200, blank=True)
    button_text = models.CharField(max_length=50, blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'banners'
        ordering = ['order']
    
    def __str__(self):
        return self.title


class SiteSettings(models.Model):
    """Site configuration"""
    site_name = models.CharField(max_length=200, default='TrueCar')
    site_logo = models.ImageField(upload_to='site/', null=True, blank=True)
    site_favicon = models.ImageField(upload_to='site/', null=True, blank=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15)
    address = models.TextField()
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    platform_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    
    class Meta:
        db_table = 'site_settings'
        verbose_name_plural = 'Site Settings'
    
    def __str__(self):
        return self.site_name