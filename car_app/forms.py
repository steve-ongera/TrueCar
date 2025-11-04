from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import User
import re


class LoginForm(forms.Form):
    """Login form with username/email and password"""
    username = forms.CharField(
        label='Username or Email',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username or email',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise ValidationError('This field is required.')
        return username.strip()


class RegisterForm(UserCreationForm):
    """Registration form with enhanced password validation"""
    USER_TYPE_CHOICES = [
        ('buyer', 'Buyer'),
        ('seller', 'Private Seller'),
        ('dealer', 'Car Dealer'),
    ]
    
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name',
            'autocomplete': 'given-name'
        })
    )
    
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name',
            'autocomplete': 'family-name'
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address',
            'autocomplete': 'email'
        })
    )
    
    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+254712345678',
            'autocomplete': 'tel'
        })
    )
    
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'user-type-radio'}),
        initial='buyer'
    )
    
    # Dealer-specific fields
    business_name = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Business/Dealership name'
        })
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Brief description of your business',
            'rows': 3
        })
    )
    
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Business address',
            'rows': 2
        })
    )
    
    city = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City'
        })
    )
    
    country = forms.CharField(
        required=False,
        max_length=100,
        initial='Kenya',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Country'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number', 
                  'user_type', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username',
                'autocomplete': 'username'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Update password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a strong password',
            'autocomplete': 'new-password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password'
        })
        
        # Update help texts
        self.fields['password1'].help_text = 'Password must be at least 8 characters with letters and numbers.'
        self.fields['username'].help_text = None
        self.fields['password2'].help_text = None
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise ValidationError('Username is required.')
        
        # Check if username is alphanumeric with optional underscores
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError('Username can only contain letters, numbers, and underscores.')
        
        if len(username) < 3:
            raise ValidationError('Username must be at least 3 characters long.')
        
        if User.objects.filter(username=username).exists():
            raise ValidationError('This username is already taken.')
        
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email already exists.')
        return email.lower()
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        
        # Remove spaces and dashes
        phone_clean = phone_number.replace(' ', '').replace('-', '')
        
        # Basic phone number validation
        if not re.match(r'^\+?[\d]{10,15}$', phone_clean):
            raise ValidationError('Please enter a valid phone number (10-15 digits).')
        
        if User.objects.filter(phone_number=phone_number).exists():
            raise ValidationError('A user with this phone number already exists.')
        
        return phone_number
    
    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        
        # Check for at least one letter and one number
        if not re.search(r'[a-zA-Z]', password):
            raise ValidationError('Password must contain at least one letter.')
        
        if not re.search(r'[0-9]', password):
            raise ValidationError('Password must contain at least one number.')
        
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        business_name = cleaned_data.get('business_name')
        
        # Validate dealer-specific fields
        if user_type == 'dealer':
            if not business_name:
                self.add_error('business_name', 'Business name is required for dealers.')
            if not cleaned_data.get('address'):
                self.add_error('address', 'Business address is required for dealers.')
            if not cleaned_data.get('city'):
                self.add_error('city', 'City is required for dealers.')
        
        return cleaned_data


class UserUpdateForm(forms.ModelForm):
    """Form for updating user profile"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'profile_picture', 
                 'date_of_birth', 'address', 'city', 'country', 'postal_code']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if User.objects.filter(phone_number=phone_number).exclude(pk=self.instance.pk).exists():
            raise ValidationError('A user with this phone number already exists.')
        return phone_number