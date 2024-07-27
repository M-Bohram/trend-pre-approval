'''
Custom User Model Documentation

This module defines a custom user model tailored specifically for our project's authentication needs. It extends the AbstractBaseUser and PermissionsMixin classes provided by Django.

Attributes:
    username (CharField): A unique field representing the username of the user.
    phone_number (CharField): A field representing the phone number of the user. Optional, can be null and blank.
    email (EmailField): A unique field representing the email address of the user.
    is_staff (BooleanField): A boolean field indicating whether the user is part of our staff or not. Default is False.
    is_active (BooleanField): A boolean field indicating whether the user account is currently active. Default is True.
    date_joined (DateTimeField): A field representing the date and time when the user account was created.
    avatar (ImageField): An image field representing the user's avatar. It's optional, with the default image being 'avatar.png'.
    created_data (DateTimeField): A field representing the date and time when the user instance was created.
    updated_data (DateTimeField): A field representing the date and time when the user instance was last updated.
    objects (CustomUserManager): The manager for this custom user model.

Methods:
    __str__(): Returns the string representation of the user instance, which is the username.
    save(*args, **kwargs): Overrides the save method to hash the password before saving it to the database.

Usage:
    To implement this custom user model in the project,the following steps have been implimented:
    
    1. Imported this CustomUser class into the relevant modules of our Django project.
    2. Configured the AUTH_USER_MODEL setting in our settings.py file to point to this custom user model:
    
        AUTH_USER_MODEL = 'authentication.CustomUser'
'''

import random
from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import CustomUserManager
from django.core.mail import send_mail


class CustomUser(AbstractBaseUser, PermissionsMixin):
    '''
    Custom User Model

    This is our project's custom user model that extends the AbstractBaseUser class provided by Django. It provides tailored fields and methods for user authentication and management.
    '''

    username = models.CharField(max_length=35, unique=True)
    phone_number = models.CharField(max_length=13, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    avatar = models.ImageField(upload_to='images/', default='images/avatar.jpeg', blank=True, null=True)
    last_otp = models.CharField(max_length=6, blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)
    created_data = models.DateTimeField(auto_now_add=True)
    updated_data = models.DateTimeField(auto_now=True)
    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        '''
        String Representation
       
        Returns the username of the user instance.
        '''
        return self.username
  
    def save(self, *args, **kwargs):
        '''
        Save Method      
        The save method is overridden to incorporate password hashing using Django's make_password function. This is implemented to ensure hashing even in scenarios where it could otherwise fail.
        '''
        if self.password and not self.password.startswith('pbkdf2_sha256'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    # reset password methods
    def generate_otp(self):
        self.last_otp = f'{random.randint(100000, 999999):06}'
        self.otp_expiry = timezone.now() + timedelta(minutes=10)
        self.save()

    def send_password_reset_email(self):

        mail_subject = 'Reset your password'
        # create the message as a string
        message = f"""
        Hi {self.email},

        We received a request to reset your password. Your OTP code is:

        {self.last_otp}

        This code is valid for 10 minutes. If you didn't request a password reset, you can ignore this email.

        Thanks,
        Your team
        """
        send_mail(mail_subject, message, 'admin@mywebsite.com', [self.email])


class Block(models.Model):
    """
    Block Model

    Represents a blocking relationship between two users.
    """
    blocker = models.ForeignKey(CustomUser, related_name='blocking', on_delete=models.CASCADE)
    blocked = models.ForeignKey(CustomUser, related_name='blocked_by', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blocker', 'blocked')  # ensures that a user cannot block the same user more than once
        indexes = [
            models.Index(fields=['blocker']),
            models.Index(fields=['blocked']),
        ]

    def save(self, *args, **kwargs):
        from profile_app.models import Follow
        # Handle unfollow on block
        Follow.objects.filter(follower=self.blocker, following=self.blocked).delete()
        Follow.objects.filter(follower=self.blocked, following=self.blocker).delete()
        super().save(*args, **kwargs)
