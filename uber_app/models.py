from django.db import models

# Create your models here.

class Account(models.Model):
    UserID = models.AutoField(primary_key=True)
    Name = models.TextField()
    Email = models.TextField(unique=True)
    Password = models.TextField()

    def __str__(self):
        return f'UserID:{self.UserID}'

    class Meta:
        db_table = 'Account'

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

class Route(models.Model):
    RouteID = models.AutoField(primary_key=True)
    DriverID = models.IntegerField()
    Status = models.BooleanField(default=True)
    Time = models.DateTimeField()
    Work_Status = models.BooleanField(default=True)

    def __str__(self):
        return f'RouteID:{self.RouteID}'

    class Meta:
        db_table = 'Route'

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
    StationID = models.AutoField(primary_key=True)
    StationName = models.TextField()

    def __str__(self):
        return f'StationID:{self.StationID}'

    class Meta:
        db_table = 'Station'