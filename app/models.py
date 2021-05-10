from django.db import models

# Create your models here.


class Statistic(models.Model):
	words = models.IntegerField(default=0)
	type = models.CharField(max_length=30)
	document_type = models.CharField(max_length=30)
	date = models.DateTimeField(auto_now_add=True)
