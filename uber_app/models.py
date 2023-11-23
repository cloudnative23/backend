from django.db import models
from django.contrib.postgres.fields import ArrayField
# Create your models here.

class User(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.TextField()
    avatar = models.URLField(max_length = 200)
    email = models.models.EmailField(max_length = 200)
    phone = models.TextField()

    def __str__(self):
        return f'id:{self.id}'

    class Meta:
        db_table = 'User'

class StationInRoute(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()
    datetime = models.models.DateTimeField()
    on = ArrayField(IntegerField())
    off = ArrayField(IntegerField())

    def __str__(self):
        return f'id:{self.id}'

    class Meta:
        db_table = 'StationInRoute'

class UserSimpleWithContact(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()
    avatar = models.URLField(max_length = 200)
    phone = models.TextField()

    def __str__(self):
        return f'id:{self.id}'

    class Meta:
        db_table = 'UserSimpleWithContact'

class CarInfo(models.Model):
    licensePlateNumber = models.TextField(primary_key=True)
    color = models.TextField()
    capacity = models.IntegerField()

    def __str__(self):
        return f'licensePlateNumber:{self.licensePlateNumber}'

    class Meta:
        db_table = 'CarInfo'


class Route(models.Model):

    id = models.AutoField(primary_key=True)
    date = models.DateTimeField()
    workStatus = models.BooleanField()
    status = models.TextField()

    def __str__(self):
        return f'RouteID:{self.id}'

    class Meta:
        db_table = 'Route'


class Request(models.Model):
    RequestID = models.AutoField(primary_key=True)
    PassengerID = models.IntegerField()
    RouteID = models.IntegerField()
    On = models.IntegerField()
    Off = models.IntegerField()
    Status = models.BooleanField(default=True)
    Work_Status = models.BooleanField(default=True)
    Time = models.DateTimeField()

    def __str__(self):
        return f'RequestID:{self.RequestID}'

    class Meta:
        db_table = 'Request'


class RoutePassenger(models.Model):
    PassengerID = models.IntegerField()
    RouteID = models.IntegerField()
    On = models.IntegerField()
    Off = models.IntegerField()
    Work_Status = models.BooleanField(default=True)

    def __str__(self):
        return f'PassengerID:{self.PassengerID} RouteID:{self.RouteID}'

    class Meta:
        unique_together = (('PassengerID', 'RouteID'),)
        db_table = 'RoutePassenger'

class RouteStation(models.Model):
    RouteID = models.IntegerField()
    StationID = models.IntegerField()
    Time = models.DateTimeField()

    def __str__(self):
        return f'StationID:{self.StationID} RouteID:{self.RouteID}'

    class Meta:
        unique_together = (('StationID', 'RouteID'),)
        db_table = 'RouteStation'

class Station(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()

    def __str__(self):
        return f'StationID:{self.id}'

    class Meta:
        db_table = 'Station'