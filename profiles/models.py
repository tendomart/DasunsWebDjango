from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Serviceuser(models.Model):
    name = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name


class Daysavailable(models.Model):
    name = models.CharField(max_length=200, null=True)
    
    def __str__(self):
        return self.name

class Serviceprovider(models.Model):
    GENDER = (('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other'),)
    fullname = models.CharField(max_length=200)
    # owner = models.ForeignKey(
    #     User, related_name='serviceProviders', on_delete=models.CASCADE, null=True)
    phone = models.CharField(max_length=200)
    email = models.EmailField(max_length=200, unique=True)
    nin = models.CharField(max_length=200)
    dob = models.CharField(max_length=200)
    gender = models.CharField(max_length=200, choices=GENDER)
    phyadd = models.CharField(max_length=200)
    yearexp = models.CharField(max_length=200)
    notmidman = models.CharField(max_length=200)
    skillset = models.CharField(max_length=200)
    internet = models.CharField(max_length=200)
    qualification = models.CharField(max_length=200)
    portifolio = models.CharField(max_length=200, blank=True)
    profession = models.CharField(max_length=200)
    ref1name = models.CharField(max_length=200)
    ref1title = models.CharField(max_length=200)
    ref1email = models.EmailField(max_length=200)
    ref1phone = models.CharField(max_length=200)
    ref2name = models.CharField(max_length=200)
    ref2title = models.CharField(max_length=200)
    ref2email = models.EmailField(max_length=200)
    ref2phone = models.CharField(max_length=200)
    service = models.CharField(max_length=200)
    availability = models.ManyToManyField(Daysavailable)
    # sunday = models.CharField(max_length=200, blank=True)
    # monday = models.CharField(max_length=200, blank=True)
    # tuesday = models.CharField(max_length=200, blank=True)
    # wednesday = models.CharField(max_length=200, blank=True)
    # thursday = models.CharField(max_length=200, blank=True)
    # friday = models.CharField(max_length=200, blank=True)
    # saturday = models.CharField(max_length=200, blank=True)
    starttime = models.CharField(max_length=200)
    endtime = models.CharField(max_length=200)
    pricevisit = models.CharField(max_length=200, blank=True)
    terms = models.CharField(max_length=200)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.fullname

class Book(models.Model):
    STATUS = (('Available', 'Available'), ('Booked', 'Booked'),
              ('Not available', 'Not available'))
    meetplace = models.CharField(max_length=200)
    meetdate = models.CharField(max_length=200)
    phone = models.CharField(max_length=200)
    starttime = models.CharField(max_length=200)
    endtime = models.CharField(max_length=200)
    # owner = models.ForeignKey(
    #     User, related_name='booking', on_delete=models.CASCADE, null=True)
    serviceuser = models.ForeignKey(Serviceuser, null=True, on_delete=models.SET_NULL)
    serviceprovider = models.ForeignKey(Serviceprovider, null=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    status = models.CharField(max_length=200, null=True, choices=STATUS)

    def __str__(self):
        return self.meetplace