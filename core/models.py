from django.db import models

# Create your models here.



class Project(models.Model):
    name=models.CharField(max_length=250)
    features=models.TextField(max_length=1000)
    email=models.EmailField()
    
    
    def __str__(self):
        return f"project name : {self.name} _ email : {self.email}"
