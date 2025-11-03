# TrueCar - Complete Setup Guide

## 🚗 Project Overview

TrueCar is a comprehensive Django-based car marketplace that allows users to buy and sell:
- Brand new cars
- Used cars (foreign and locally used)
- Crashed/salvage cars

### Features
- ✅ User authentication & profiles
- ✅ Dealer/showroom accounts
- ✅ Advanced car listings with images
- ✅ Search & filtering system
- ✅ Favorites/wishlist
- ✅ Inquiry system
- ✅ Reviews & ratings
- ✅ Complete checkout & ordering
- ✅ **M-Pesa payment integration**
- ✅ **PayPal payment integration**
- ✅ **Credit/Debit card support (Stripe ready)**
- ✅ Admin dashboard
- ✅ Responsive design

---

## 📋 Prerequisites

- Python 3.9+
- PostgreSQL or MySQL (SQLite for development)
- Virtual environment
- Git

---

## 🚀 Installation Steps

### 1. Clone or Create Project

```bash
# Create project directory
mkdir truecar
cd truecar

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 2. Install Django and Create Project

```bash
# Install Django
pip install django

# Create Django project
django-admin startproject truecar_project .

# Create cars app
python manage.py startapp cars
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Setup

```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env with your actual credentials
nano .env  # or use any text editor
```

### 5. Database Configuration

Update `settings.py`:

```python
# For PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# For SQLite (Development)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
```

### 6. Create Database

```bash
# For PostgreSQL
createdb truecar_db

# For MySQL
mysql -u root -p
CREATE DATABASE truecar_db;
```

### 7. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 8. Create Superuser

```bash
python manage.py createsuperuser
```

### 9. Create Media Directories

```bash
mkdir -p media/profiles
mkdir -p media/dealers
mkdir -p media/cars
mkdir -p media/makes
mkdir -p media/banners
mkdir -p media/inspections
```

### 10. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 11. Run Development Server

```bash
python manage.py runserver
```

Visit: `http://localhost:8000`

---

## 💳 Payment Integration Setup

### M-Pesa Configuration

1. **Register for Daraja API**
   - Go to: https://developer.safaricom.co.ke
   - Create an account
   - Create a new app

2. **Get Credentials**
   - Consumer Key
   - Consumer Secret
   - Passkey
   - Shortcode

3. **Update .env**
```env
MPESA_CONSUMER_KEY=your_key
MPESA_CONSUMER_SECRET=your_secret
MPESA_SHORTCODE=your_shortcode
MPESA_PASSKEY=your_passkey
```

4. **Configure Callback URL**
   - Must be publicly accessible (use ngrok for testing)
   - Format: `https://yourdomain.com/payment/mpesa/callback/`

5. **Testing with Ngrok**
```bash
# Install ngrok
npm install -g ngrok
# or download from https://ngrok.com

# Start ngrok
ngrok http 8000

# Copy the https URL and update your .env
MPESA_CALLBACK_URL=https://your-ngrok-url.ngrok.io/payment/mpesa/callback/
```

### PayPal Configuration

1. **Create PayPal Developer Account**
   - Go to: https://developer.paypal.com
   - Sign up/Login

2. **Create App**
   - Go to Dashboard → My Apps & Credentials
   - Create a new app
   - Get Client ID and Secret

3. **Update .env**
```env
PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=your_client_id
PAYPAL_CLIENT_SECRET=your_client_secret
```

4. **For Production**
```env
PAYPAL_MODE=live
# Use live credentials
```

### Stripe Configuration (Optional)

1. **Create Stripe Account**
   - Go to: https://stripe.com
   - Sign up

2. **Get API Keys**
   - Dashboard → Developers → API Keys

3. **Update .env**
```env
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

---

## 📊 Database Schema

### Core Models

1. **User** - Extended user model with profiles
2. **Dealer** - Showroom/dealer information
3. **CarMake** - Car manufacturers (Toyota, Honda, etc.)
4. **CarModel** - Car models (Camry, Accord, etc.)
5. **Car** - Main car listing model
6. **CarImage** - Multiple images per car
7. **CarSpecification** - Detailed specifications
8. **Order** - Purchase orders
9. **Payment** - Payment transactions
10. **Review** - Car/seller reviews
11. **Favorite** - Saved cars
12. **Inquiry** - Contact messages

---

## 🎨 Admin Panel

Access admin at: `http://localhost:8000/admin`

### Initial Setup Tasks

1. **Create Car Makes**
   - Go to Car Makes
   - Add popular brands (Toyota, Honda, BMW, etc.)

2. **Create Car Models**
   - Link models to makes
   - Add popular models

3. **Create Dealers (Optional)**
   - Set up showroom accounts

4. **Add Banners**
   - Upload homepage banners
   - Set order and active status

5. **Configure Site Settings**
   - Update contact information
   - Set platform fee percentage

---

## 🔧 Management Commands

### Create Sample Data

Create a management command for sample data:

```bash
# cars/management/commands/create_sample_data.py
python manage.py create_sample_data
```

### Clear Cache

```bash
python manage.py clear_cache
```

---

## 🚀 Deployment

### Using Heroku

1. **Install Heroku CLI**
```bash
heroku login
heroku create your-app-name
```

2. **Add Buildpacks**
```bash
heroku buildpacks:set heroku/python
```

3. **Add PostgreSQL**
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

4. **Set Environment Variables**
```bash
heroku config:set SECRET_KEY=your_secret_key
heroku config:set DEBUG=False
heroku config:set MPESA_CONSUMER_KEY=your_key
# ... set all env variables
```

5. **Deploy**
```bash
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### Using AWS/DigitalOcean

1. **Setup Server**
   - Ubuntu 20.04 LTS
   - Python 3.9+
   - PostgreSQL
   - Nginx
   - Gunicorn

2. **Install Dependencies**
```bash
sudo apt update
sudo apt install python3-pip python3-venv postgresql nginx
```

3. **Configure Nginx**
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/user/truecar;
    }
    
    location /media/ {
        root /home/user/truecar;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}
```

4. **Setup Gunicorn**
```bash
gunicorn --workers 3 truecar_project.wsgi:application
```

---

## 🧪 Testing

### Run Tests

```bash
# All tests
python manage.py test

# Specific app
python manage.py test cars

# With coverage
pip install coverage
coverage run manage.py test
coverage report
```

### Test Payments

**M-Pesa Sandbox**
- Use test phone: 254708374149
- PIN: Any 4 digits

**PayPal Sandbox**
- Use sandbox test accounts from PayPal developer dashboard

---

## 📱 API Endpoints (Optional REST API)

If you want to add REST API:

```bash
pip install djangorestframework
```

Create serializers and API views for:
- Car listings
- Search
- Favorites
- Orders
- User profile

---

## 🔒 Security Checklist

- [ ] Use environment variables for secrets
- [ ] Enable HTTPS in production
- [ ] Set `DEBUG=False` in production
- [ ] Configure ALLOWED_HOSTS
- [ ] Use CSRF protection
- [ ] Implement rate limiting
- [ ] Regular security updates
- [ ] Backup database regularly
- [ ] Use strong passwords
- [ ] Enable two-factor authentication

---

## 📞 Support & Documentation

### Useful Links

- Django Docs: https://docs.djangoproject.com
- M-Pesa Daraja: https://developer.safaricom.co.ke/docs
- PayPal API: https://developer.paypal.com/docs
- Stripe Docs: https://stripe.com/docs

### Common Issues

**Issue: M-Pesa callback not working**
- Ensure callback URL is publicly accessible
- Use ngrok for local testing
- Check Daraja portal logs

**Issue: PayPal sandbox not working**
- Verify sandbox credentials
- Check PayPal developer logs
- Ensure correct redirect URLs

**Issue: Images not showing**
- Run `collectstatic`
- Check MEDIA_ROOT and MEDIA_URL settings
- Verify file permissions

---

## 📈 Future Enhancements

- [ ] Real-time chat system
- [ ] Advanced search with AI
- [ ] Car comparison tool
- [ ] Price estimation AI
- [ ] Mobile app (React Native/Flutter)
- [ ] SMS notifications
- [ ] Email newsletters
- [ ] Blog/News section
- [ ] Car financing calculator
- [ ] Insurance integration
- [ ] Delivery tracking
- [ ] Multi-language support

---

## 👨‍💻 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

---

## 📄 License

MIT License - Feel free to use for commercial projects

---

## 🙏 Acknowledgments

- Django Community
- Safaricom Daraja API
- PayPal Developer Platform
- Bootstrap Team

---

**Built with ❤️ for car dealers and buyers in Kenya and beyond!**