from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta, date
import random
from faker import Faker

from car_app.models import (
    User, Dealer, CarMake, CarModel, Car, CarImage, CarSpecification,
    InspectionReport, Inquiry, Review, Favorite, Order, Payment,
    Notification, SearchHistory, CompareList, Banner, SiteSettings
)

fake = Faker()
User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with realistic data for Kenyan car marketplace'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()

        self.stdout.write('Starting data seeding...')
        
        # Seed in order of dependencies
        self.seed_users()
        self.seed_dealers()
        self.seed_car_makes_and_models()
        self.seed_cars()
        self.seed_car_images()
        self.seed_car_specifications()
        self.seed_inspection_reports()
        self.seed_inquiries()
        self.seed_reviews()

        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))

    def clear_data(self):
        """Clear all data from tables"""
        models_to_clear = [
            Payment, Order, Notification, SearchHistory, CompareList,
            Favorite, Review, Inquiry, InspectionReport, CarSpecification,
            CarImage, Car, CarModel, CarMake, Dealer, Banner, SiteSettings
        ]
        
        for model in models_to_clear:
            model.objects.all().delete()
        
        # Clear users except superusers
        User.objects.filter(is_superuser=False).delete()
        
        self.stdout.write(self.style.WARNING('Cleared existing data'))

    def seed_users(self):
        """Create sample users"""
        self.stdout.write('Seeding users...')
        
        # Kenyan phone numbers and names
        users_data = [
            {'username': 'john_kamau', 'user_type': 'buyer', 'email': 'john.kamau@gmail.com', 
             'first_name': 'John', 'last_name': 'Kamau', 'phone': '+254712345678'},
            {'username': 'mary_wanjiru', 'user_type': 'buyer', 'email': 'mary.wanjiru@gmail.com',
             'first_name': 'Mary', 'last_name': 'Wanjiru', 'phone': '+254723456789'},
            {'username': 'peter_ochieng', 'user_type': 'buyer', 'email': 'peter.ochieng@gmail.com',
             'first_name': 'Peter', 'last_name': 'Ochieng', 'phone': '+254734567890'},
            {'username': 'grace_akinyi', 'user_type': 'seller', 'email': 'grace.akinyi@gmail.com',
             'first_name': 'Grace', 'last_name': 'Akinyi', 'phone': '+254745678901'},
            {'username': 'david_kipchoge', 'user_type': 'seller', 'email': 'david.kipchoge@gmail.com',
             'first_name': 'David', 'last_name': 'Kipchoge', 'phone': '+254756789012'},
            {'username': 'sarah_muthoni', 'user_type': 'seller', 'email': 'sarah.muthoni@gmail.com',
             'first_name': 'Sarah', 'last_name': 'Muthoni', 'phone': '+254767890123'},
            {'username': 'james_otieno', 'user_type': 'seller', 'email': 'james.otieno@gmail.com',
             'first_name': 'James', 'last_name': 'Otieno', 'phone': '+254778901234'},
            {'username': 'premium_motors', 'user_type': 'dealer', 'email': 'info@premiummotors.co.ke',
             'first_name': 'Premium', 'last_name': 'Motors', 'phone': '+254789012345'},
            {'username': 'elite_cars', 'user_type': 'dealer', 'email': 'sales@elitecars.co.ke',
             'first_name': 'Elite', 'last_name': 'Cars', 'phone': '+254790123456'},
        ]

        kenyan_cities = ['Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret', 'Thika', 'Ruiru', 'Kikuyu']

        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'phone_number': user_data['phone'],
                    'user_type': user_data['user_type'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'city': random.choice(kenyan_cities),
                    'country': 'Kenya',
                    'address': f"{random.randint(1, 999)} {random.choice(['Moi Avenue', 'Kenyatta Avenue', 'Uhuru Highway', 'Kimathi Street', 'Tom Mboya Street'])}",
                    'postal_code': f"{random.randint(100, 900):05d}",
                    'is_verified': True,
                    'id_verified': random.choice([True, False]),
                    'rating': Decimal(str(round(random.uniform(4.0, 5.0), 2))),
                    'total_sales': random.randint(0, 30) if user_data['user_type'] in ['seller', 'dealer'] else 0,
                }
            )
            if created:
                user.set_password('password123')
                user.save()

        self.stdout.write(self.style.SUCCESS(f'Created {len(users_data)} users'))

    def seed_dealers(self):
        """Create sample dealers"""
        self.stdout.write('Seeding dealers...')
        
        dealer_users = User.objects.filter(user_type='dealer')
        
        dealers_info = [
            {
                'business_name': 'Premium Auto Sales Kenya',
                'description': 'Leading car dealership in Nairobi specializing in quality Japanese and European imports. Over 15 years of experience.',
                'city': 'Nairobi',
                'address': 'Mombasa Road, Industrial Area',
                'latitude': Decimal('-1.3161'),
                'longitude': Decimal('36.8516'),
                'established_year': 2008,
            },
            {
                'business_name': 'Elite Motors Limited',
                'description': 'Premium dealership offering certified pre-owned luxury vehicles and brand new cars. Trusted by thousands of Kenyans.',
                'city': 'Nairobi',
                'address': 'Ngong Road, Prestige Plaza',
                'latitude': Decimal('-1.2921'),
                'longitude': Decimal('36.7822'),
                'established_year': 2012,
            },
        ]

        for i, dealer_user in enumerate(dealer_users):
            if not hasattr(dealer_user, 'dealer') and i < len(dealers_info):
                info = dealers_info[i]
                Dealer.objects.create(
                    user=dealer_user,
                    business_name=info['business_name'],
                    description=info['description'],
                    business_license=f"KE{random.randint(100000, 999999)}",
                    tax_id=f"P051{random.randint(100000, 999999)}X",
                    phone=dealer_user.phone_number,
                    email=dealer_user.email,
                    website=f"https://www.{info['business_name'].lower().replace(' ', '')}.co.ke",
                    address=info['address'],
                    city=info['city'],
                    country='Kenya',
                    latitude=info['latitude'],
                    longitude=info['longitude'],
                    is_verified=True,
                    is_premium=True,
                    rating=Decimal(str(round(random.uniform(4.3, 4.9), 2))),
                    total_listings=random.randint(30, 100),
                    established_year=info['established_year'],
                    operating_hours='Monday - Friday: 8:00 AM - 6:00 PM\nSaturday: 9:00 AM - 5:00 PM\nSunday: Closed',
                )

        self.stdout.write(self.style.SUCCESS(f'Created {dealer_users.count()} dealers'))

    def seed_car_makes_and_models(self):
        """Create car makes and models"""
        self.stdout.write('Seeding car makes and models...')
        
        # Popular makes in Kenya
        makes_data = {
            'Toyota': {
                'models': ['Corolla', 'Camry', 'RAV4', 'Land Cruiser', 'Hilux', 'Prado', 'Yaris', 'Fortuner', 'Harrier', 'Mark X', 'Vitz', 'Fielder', 'Axio', 'Premio', 'Allion'],
                'country': 'Japan',
                'description': 'Toyota is the most popular car brand in Kenya, known for reliability and excellent resale value.',
            },
            'Nissan': {
                'models': ['Sylphy', 'Teana', 'X-Trail', 'Patrol', 'Navara', 'Juke', 'Note', 'Tiida', 'Sunny', 'Pathfinder'],
                'country': 'Japan',
                'description': 'Nissan offers a wide range of reliable vehicles popular in the Kenyan market.',
            },
            'Honda': {
                'models': ['Fit', 'Civic', 'Accord', 'CR-V', 'Vezel', 'Stream', 'Insight', 'Airwave'],
                'country': 'Japan',
                'description': 'Honda vehicles are known for fuel efficiency and innovative engineering.',
            },
            'Mazda': {
                'models': ['Demio', 'Axela', 'Atenza', 'CX-5', 'Mazda3', 'Premacy', 'Biante'],
                'country': 'Japan',
                'description': 'Mazda combines Japanese engineering with stylish designs.',
            },
            'Subaru': {
                'models': ['Impreza', 'Forester', 'Outback', 'Legacy', 'XV', 'Levorg'],
                'country': 'Japan',
                'description': 'Subaru is renowned for its AWD systems and boxer engines.',
            },
            'Mercedes-Benz': {
                'models': ['C-Class', 'E-Class', 'S-Class', 'GLE', 'GLC', 'A-Class', 'CLA', 'GLA'],
                'country': 'Germany',
                'description': 'Mercedes-Benz represents luxury and German engineering excellence.',
            },
            'BMW': {
                'models': ['3 Series', '5 Series', '7 Series', 'X1', 'X3', 'X5', 'X6', '1 Series'],
                'country': 'Germany',
                'description': 'BMW is synonymous with performance luxury and driving dynamics.',
            },
            'Volkswagen': {
                'models': ['Golf', 'Passat', 'Polo', 'Tiguan', 'Touareg', 'Jetta'],
                'country': 'Germany',
                'description': 'Volkswagen offers practical and well-engineered vehicles.',
            },
            'Mitsubishi': {
                'models': ['Outlander', 'Pajero', 'RVR', 'Lancer', 'Colt', 'Galant'],
                'country': 'Japan',
                'description': 'Mitsubishi vehicles are popular for their durability and 4WD capabilities.',
            },
            'Audi': {
                'models': ['A3', 'A4', 'A6', 'Q3', 'Q5', 'Q7'],
                'country': 'Germany',
                'description': 'Audi combines luxury with cutting-edge technology.',
            },
            'Land Rover': {
                'models': ['Discovery', 'Range Rover', 'Range Rover Sport', 'Defender', 'Freelander'],
                'country': 'United Kingdom',
                'description': 'Land Rover is the ultimate in luxury off-road capability.',
            },
            'Ford': {
                'models': ['Ranger', 'Explorer', 'Escape', 'Focus', 'Fiesta'],
                'country': 'USA',
                'description': 'Ford offers tough and reliable vehicles for African roads.',
            },
        }

        # Most popular makes in Kenya
        popular_makes = ['Toyota', 'Nissan', 'Honda', 'Mazda', 'Subaru']

        for order, (make_name, make_info) in enumerate(makes_data.items()):
            make, _ = CarMake.objects.get_or_create(
                name=make_name,
                defaults={
                    'country': make_info['country'],
                    'is_popular': make_name in popular_makes,
                    'order': order,
                    'description': make_info['description'],
                }
            )

            # Popular models for each make
            popular_models_map = {
                'Toyota': ['Corolla', 'RAV4', 'Land Cruiser', 'Hilux', 'Prado', 'Harrier'],
                'Nissan': ['X-Trail', 'Sylphy', 'Note'],
                'Honda': ['Fit', 'CR-V'],
                'Mazda': ['Demio', 'CX-5'],
                'Subaru': ['Impreza', 'Forester'],
            }

            for model_name in make_info['models']:
                is_popular = make_name in popular_models_map and model_name in popular_models_map[make_name]
                CarModel.objects.get_or_create(
                    make=make,
                    name=model_name,
                    defaults={
                        'is_popular': is_popular,
                    }
                )

        self.stdout.write(self.style.SUCCESS(f'Created {len(makes_data)} makes with models'))

    def seed_cars(self):
        """Create sample car listings"""
        self.stdout.write('Seeding cars...')
        
        sellers = User.objects.filter(user_type__in=['seller', 'dealer'])
        dealers = Dealer.objects.all()
        makes = CarMake.objects.all()
        
        kenyan_cities = ['Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret', 'Thika', 'Ruiru', 'Kikuyu', 'Machakos', 'Ngong']
        colors = ['White', 'Black', 'Silver', 'Pearl White', 'Grey', 'Blue', 'Red', 'Beige', 'Brown', 'Navy Blue']
        
        # Realistic feature sets
        basic_features = 'Power Steering, Power Windows, Central Locking, Air Conditioning, Radio/CD Player'
        standard_features = 'Power Steering, Power Windows, Central Locking, Air Conditioning, Alloy Wheels, Fog Lights, Electric Mirrors'
        premium_features = 'Leather Seats, Sunroof, Navigation System, Reverse Camera, Keyless Entry, Push Start Button, Climate Control, Cruise Control'
        luxury_features = 'Full Leather Interior, Panoramic Sunroof, Advanced Navigation, 360 Camera, Heated/Ventilated Seats, Premium Sound System, Adaptive Cruise Control, Lane Assist'

        # Realistic price ranges by make and year
        def get_realistic_price(make_name, year, condition):
            base_prices = {
                'Toyota': (800000, 8000000),
                'Nissan': (700000, 5000000),
                'Honda': (750000, 4500000),
                'Mazda': (600000, 3500000),
                'Subaru': (900000, 5500000),
                'Mercedes-Benz': (1500000, 15000000),
                'BMW': (1200000, 12000000),
                'Audi': (1300000, 10000000),
                'Land Rover': (2000000, 20000000),
                'Volkswagen': (800000, 4000000),
                'Mitsubishi': (700000, 4000000),
                'Ford': (900000, 5000000),
            }
            
            min_price, max_price = base_prices.get(make_name, (600000, 5000000))
            
            # Adjust for year
            age = 2024 - year
            depreciation = 1 - (age * 0.08)  # 8% per year
            depreciation = max(depreciation, 0.3)  # Minimum 30% of original value
            
            # Adjust for condition
            condition_multiplier = {
                'brand_new': 1.0,
                'foreign_used': 0.85,
                'locally_used': 0.75,
            }
            
            price = random.randint(int(min_price * depreciation), int(max_price * depreciation))
            price = int(price * condition_multiplier.get(condition, 0.75))
            
            # Round to nearest 50,000
            return (price // 50000) * 50000

        for _ in range(150):
            make = random.choice(makes)
            models = list(make.models.all())
            if not models:
                continue
                
            model = random.choice(models)
            seller = random.choice(sellers)
            year = random.randint(2012, 2024)
            condition = random.choices(
                ['brand_new', 'foreign_used', 'locally_used'],
                weights=[0.1, 0.5, 0.4]
            )[0]
            
            # Determine features based on make and year
            if make.name in ['Mercedes-Benz', 'BMW', 'Audi', 'Land Rover']:
                features = luxury_features if year >= 2018 else premium_features
            elif year >= 2020:
                features = premium_features
            elif year >= 2015:
                features = standard_features
            else:
                features = basic_features

            price = get_realistic_price(make.name, year, condition)
            
            # Realistic mileage
            if condition == 'brand_new':
                mileage = random.randint(0, 50)
            elif condition == 'foreign_used':
                age = 2024 - year
                mileage = random.randint(age * 8000, age * 15000)
            else:  # locally_used
                age = 2024 - year
                mileage = random.randint(age * 15000, age * 25000)

            # Realistic transmission distribution
            if make.name in ['Mercedes-Benz', 'BMW', 'Audi', 'Land Rover']:
                transmission = 'automatic'
            else:
                transmission = random.choices(
                    ['automatic', 'manual'],
                    weights=[0.7, 0.3]
                )[0]

            # Description templates
            descriptions = [
                f"Excellent condition {year} {make.name} {model.name}. Well maintained with full service history. Perfect for Kenyan roads.",
                f"Clean {year} {make.name} {model.name} in pristine condition. One owner, accident-free. Ready for immediate use.",
                f"Superb {year} {make.name} {model.name}. Original paint, no accident history. Very fuel efficient and reliable.",
                f"Fantastic {year} {make.name} {model.name} in excellent mechanical and body condition. Must see to appreciate.",
                f"Beautiful {year} {make.name} {model.name}. Fully loaded with all features. Priced to sell quickly.",
            ]

            car = Car.objects.create(
                seller=seller,
                dealer=random.choice([None, random.choice(dealers)]) if dealers.exists() and seller.user_type == 'dealer' else None,
                make=make,
                model=model,
                year=year,
                condition=condition,
                body_type=random.choice(['sedan', 'suv', 'hatchback', 'pickup', 'wagon']),
                mileage=mileage,
                engine_size=Decimal(str(round(random.uniform(1.3, 4.5), 1))),
                fuel_type=random.choices(
                    ['petrol', 'diesel', 'hybrid'],
                    weights=[0.7, 0.2, 0.1]
                )[0],
                transmission=transmission,
                drive_type=random.choice(['fwd', 'awd', '4wd']) if make.name in ['Subaru', 'Land Rover'] else random.choice(['fwd', 'rwd']),
                exterior_color=random.choice(colors),
                interior_color=random.choice(['Black', 'Beige', 'Grey', 'Brown']),
                doors=4 if random.random() > 0.1 else 2,
                seats=random.choice([5, 5, 5, 7, 8]),
                price=Decimal(str(price)),
                negotiable=True,
                location=random.choice(kenyan_cities),
                city=random.choice(kenyan_cities),
                country='Kenya',
                latitude=Decimal(str(round(random.uniform(-4.0, 1.0), 6))),
                longitude=Decimal(str(round(random.uniform(34.0, 41.0), 6))),
                description=random.choice(descriptions),
                features=features,
                status=random.choices(
                    ['active', 'sold', 'reserved'],
                    weights=[0.8, 0.15, 0.05]
                )[0],
                is_featured=random.choice([True, False, False, False, False]),
                is_urgent=random.choice([True, False, False, False]),
                views=random.randint(5, 500),
                inquiries=random.randint(0, 30),
                published_at=timezone.now() - timedelta(days=random.randint(1, 60)),
            )

        self.stdout.write(self.style.SUCCESS(f'Created 150 cars'))

    def seed_car_images(self):
        """Create sample car images"""
        self.stdout.write('Seeding car images...')
        
        cars = Car.objects.all()
        
        for car in cars:
            num_images = random.randint(4, 10)
            image_types = ['front', 'rear', 'side', 'interior', 'dashboard', 'engine', 'wheels', 'detail']
            
            for i in range(num_images):
                image_type = random.choice(image_types)
                CarImage.objects.create(
                    car=car,
                    image=f'cars/{car.slug}/{image_type}_{i}.jpg',
                    caption=f'{car.year} {car.make.name} {car.model.name} - {image_type.title()} View',
                    is_primary=(i == 0),
                    order=i,
                )

        self.stdout.write(self.style.SUCCESS('Created car images'))

    def seed_car_specifications(self):
        """Create additional car specifications"""
        self.stdout.write('Seeding car specifications...')
        
        cars = Car.objects.all()[:50]
        
        for car in cars:
            specs = [
                ('Engine Type', f'{car.engine_size}L {random.choice(["Inline-4", "V6", "V8"])}', 'Engine'),
                ('Horsepower', f'{random.randint(120, 350)} HP', 'Performance'),
                ('Torque', f'{random.randint(200, 450)} Nm', 'Performance'),
                ('0-100 km/h', f'{random.uniform(6.5, 12.0):.1f} seconds', 'Performance'),
                ('Top Speed', f'{random.randint(170, 250)} km/h', 'Performance'),
                ('Fuel Consumption', f'{random.uniform(6.5, 12.0):.1f}L/100km', 'Efficiency'),
                ('Fuel Tank', f'{random.randint(45, 80)}L', 'Efficiency'),
                ('Boot Space', f'{random.randint(350, 800)}L', 'Interior'),
                ('Warranty', 'Valid until ' + str(2024 + random.randint(1, 3)), 'Additional'),
            ]

            for i, (name, value, category) in enumerate(specs):
                CarSpecification.objects.create(
                    car=car,
                    name=name,
                    value=value,
                    category=category,
                    order=i,
                )

        self.stdout.write(self.style.SUCCESS('Created car specifications'))

    def seed_inspection_reports(self):
        """Create inspection reports"""
        self.stdout.write('Seeding inspection reports...')
        
        cars = Car.objects.filter(condition__in=['foreign_used', 'locally_used'])[:30]
        
        inspection_companies = [
            'AA Kenya Inspection Services',
            'SGS Vehicle Inspection',
            'Kenya Auto Inspections',
            'TruCheck Motors',
        ]
        
        for car in cars:
            InspectionReport.objects.create(
                car=car,
                inspector_name=random.choice(inspection_companies),
                inspection_date=date.today() - timedelta(days=random.randint(1, 45)),
                overall_condition=random.choices(
                    ['excellent', 'good', 'fair'],
                    weights=[0.3, 0.5, 0.2]
                )[0],
                notes=f"Vehicle inspected and found to be in good working condition. All major components checked. Engine runs smoothly. No signs of accident damage. Interior well maintained. Recommended for purchase.",
            )

        self.stdout.write(self.style.SUCCESS('Created inspection reports'))

    def seed_inquiries(self):
        """Create car inquiries"""
        self.stdout.write('Seeding inquiries...')
        
        buyers = User.objects.filter(user_type='buyer')
        cars = Car.objects.filter(status='active')[:40]
        
        inquiry_messages = [
            "Hi, I'm interested in this car. Is it still available?",
            "Can I come for a test drive? When are you available?",
            "What's your best price for this vehicle?",
            "Does the car have a clean logbook?",
            "Can you share more photos of the interior?",
            "Has this car been in any accidents?",
            "Is the price negotiable?",
            "What's included in the sale?",
            "Can I bring my mechanic to inspect it?",
            "Do you accept installment payments?",
        ]
        
        for _ in range(60):
            car = random.choice(cars)
            buyer = random.choice(buyers)
            
            Inquiry.objects.create(
                car=car,
                sender=buyer,
                recipient=car.seller,
                name=f"{buyer.first_name} {buyer.last_name}",
                email=buyer.email,
                phone=buyer.phone_number,
                message=random.choice(inquiry_messages),
                is_read=random.choice([True, False]),
                replied=random.choice([True, False]),
                created_at=timezone.now() - timedelta(days=random.randint(1, 45)),
            )

        self.stdout.write(self.style.SUCCESS('Created inquiries'))

    def seed_reviews(self):
        """Create reviews"""
        self.stdout.write('Seeding reviews...')
        
        buyers = User.objects.filter(user_type='buyer')
        cars = Car.objects.filter(status__in=['active', 'sold'])[:50]
        sellers = User.objects.filter(user_type='seller')
        dealers = Dealer.objects.all()
        
        car_review_comments = [
            "Excellent car! Very fuel efficient and comfortable for long drives.",
            "Great value for money. Exactly as described by the seller.",
            "Smooth transmission and powerful engine. Highly recommend!",
            "Perfect family car. Spacious and reliable.",
            "Love the features and the condition is pristine.",
            "Good car but had some minor issues that were fixed.",
            "Decent vehicle, meets my daily needs perfectly.",
        ]
        
        seller_review_comments = [
            "Very professional and honest seller. Smooth transaction.",
            "Great communication and fair pricing. Would buy again.",
            "Trustworthy seller, car was exactly as described.",
            "Quick response and flexible viewing times. Recommended!",
            "Professional dealer with excellent customer service.",
        ]
        
        # Car reviews
        for _ in range(40):
            Review.objects.create(
                review_type='car',
                car=random.choice(cars),
                reviewer=random.choice(buyers),
                rating=random.choices([3, 4, 5], weights=[0.1, 0.3, 0.6])[0],
                title=f"Great {random.choice(['Purchase', 'Car', 'Vehicle', 'Buy', 'Experience'])}",
                comment=random.choice(car_review_comments),
                is_verified_purchase=random.choice([True, False]),
                is_approved=True,
                created_at=timezone.now() - timedelta(days=random.randint(1, 60)),
            )
        
        # Seller reviews
        for _ in range(25):
            Review.objects.create(
                review_type='seller',
                seller=random.choice(sellers),
                reviewer=random.choice(buyers),
                rating=random.choices([3, 4, 5], weights=[0.1, 0.3, 0.6])[0],
                title=f"Excellent {random.choice(['Seller', 'Service', 'Experience', 'Transaction'])}",
                comment=random.choice(seller_review_comments),
                is_verified_purchase=random.choice([True, False]),
                is_approved=True,
                created_at=timezone.now() - timedelta(days=random.randint(1, 60)),
            )
        self.stdout.write(self.style.SUCCESS('Created reviews'))

        