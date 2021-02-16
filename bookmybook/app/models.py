from django.db import models



class User(models.Model):

    name = models.CharField(max_length=60, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    mobile = models.IntegerField()
    latitude=models.FloatField()
    longitude=models.FloatField()


class Book(models.Model):

    name = models.CharField(max_length=60)
    author= models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    owner=models.ForeignKey(User, on_delete=models.CASCADE)
    publish_year=models.IntegerField()
    condition=models.CharField(max_length=100)

class Agent(models.Model):

    name = models.CharField(max_length=60)
    address = models.CharField(max_length=100)
    mobile = models.IntegerField()
    ratings=models.FloatField()


class Wishlist(models.Model):
	user=models.ForeignKey(User, on_delete=models.CASCADE)
	books=models.ManyToManyField(Book)


class Order(models.Model):
	user=models.ForeignKey(User, on_delete=models.CASCADE)
	books=models.ManyToManyField(Book)