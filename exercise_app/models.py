from collections.abc import Iterable
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.contrib.auth.hashers import make_password
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email field must required")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        hashed_password = make_password(password)
        user.set_password(hashed_password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)
    
class CustomUser(AbstractUser):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    
    groups = models.ManyToManyField(Group, blank=True, related_name='custom_user_groups')
    user_permissions = models.ManyToManyField(Permission, blank=True, related_name="custom_user_permission")
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class Country(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    country_code = models.CharField(max_length=10, unique=True)
    curr_symbol = models.CharField(max_length=10)
    phone_code = models.CharField(max_length=10, unique=True)
    my_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

class State(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    state_code = models.CharField(max_length=10, unique=True)
    gst_code = models.CharField(max_length=10, unique=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

class City(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    city_code = models.CharField(max_length=10, unique=True)
    phone_code = models.CharField(max_length=10, unique=True)
    population = models.IntegerField()
    avg_age = models.FloatField()
    num_of_adult_males = models.IntegerField()
    num_of_adult_females = models.IntegerField()
    state = models.ForeignKey(State, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.population < (self.num_of_adult_males + self.num_of_adult_females):
            raise ValueError("City population must be greater than the sum of num of adult males and females")
        return super().save(*args, **kwargs)
