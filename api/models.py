from django.db import models

# Create your models here.

class User(models.Model):
    FirstName = models.CharField(max_length=50)
    LastName = models.CharField(max_length=50)
    Username = models.CharField(max_length=20)
    Password = models.CharField(max_length=50)
    CPassword = models.CharField(max_length=50)
    DateOfBirth= models.DateField()
    Email = models.CharField(max_length=50)
    ContactNo = models.IntegerField()



    def __str__(self):
        return self.FirstName
