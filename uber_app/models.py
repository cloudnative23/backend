from django.db import models

# Create your models here.
class Account(models.Model):
    UserID = models.BigAutoField(primary_key=True)
    Name = models.TextField(default="")
    Email = models.EmailField(unique=True)
    Password = models.TextField(default="")
    Avatar = models.URLField(default="")
    Phone = models.TextField(default="")

    def get_full_name(self) -> str:
        return self.Name

    def get_short_name(self) -> str:
        return self.Name

    def __str__(self):
        return f'UserID:{self.UserID}'

    class Meta:
        db_table = 'Account'

class Request(models.Model):
    RequestID = models.BigAutoField(primary_key=True)
    Passenger = models.ForeignKey("Account", db_column="PassengerID", on_delete=models.PROTECT,
                                  related_name="Requests")
    Route = models.ForeignKey("Route", db_column="RouteID", on_delete=models.PROTECT, related_name="Requests")
    On = models.ForeignKey("Station", db_column="On", on_delete=models.PROTECT, related_name="+")
    Off = models.ForeignKey("Station", db_column="Off", on_delete=models.PROTECT, related_name="+")
    Status = models.BooleanField(default=True)
    Work_Status = models.BooleanField(default=True)
    Time = models.DateTimeField()

    def __str__(self):
        return f'RequestID:{self.RequestID}'

    class Meta:
        db_table = 'Request'

class Route(models.Model):
    RouteID = models.BigAutoField(primary_key=True)
    Driver = models.ForeignKey("Account", db_column="DriverID", on_delete=models.PROTECT,
                               related_name="Driver_Routes")
    Status = models.TextField(default='available')
    Time = models.DateField()
    Work_Status = models.BooleanField(default=True)
    Passengers = models.ManyToManyField(Account,
                                        through="RoutePassenger",
                                        through_fields=("Route", "Passenger"),
                                        related_name="Passenger_Routes")
    Stations = models.ManyToManyField("Station",
                                      through="RouteStation",
                                      through_fields=("Route", "Station"),
                                      related_name="+")
    Car_Color = models.TextField()
    Car_Capacity = models.IntegerField()
    LicensePlateNumber = models.TextField()

    def __str__(self):
        return f'RouteID:{self.RouteID}'

    class Meta:
        db_table = 'Route'

class RoutePassenger(models.Model):
    Passenger = models.ForeignKey("Account", db_column="PassengerID", on_delete=models.PROTECT)
    Route = models.ForeignKey("Route", db_column="RouteID", on_delete=models.PROTECT)
    Request = models.ForeignKey("Request", db_column="RequestID", on_delete=models.PROTECT,
                                related_name="+")
    On = models.ForeignKey("Station", db_column="On", on_delete=models.PROTECT, related_name="+")
    Off = models.ForeignKey("Station", db_column="Off", on_delete=models.PROTECT, related_name="+")
    Work_Status = models.BooleanField(default=True)

    def __str__(self):
        return f'PassengerID:{self.PassengerID} RouteID:{self.RouteID}'

    class Meta:
        db_table = 'RoutePassenger'

class RouteStation(models.Model):
    Route = models.ForeignKey("Route", db_column="RouteID", on_delete=models.CASCADE)
    Station = models.ForeignKey("Station", db_column="StationID", on_delete=models.PROTECT)
    Time = models.DateTimeField()

    def __str__(self):
        return f'RouteID:{self.Route.RouteID}'

    class Meta:
        db_table = 'RouteStation'

class Station(models.Model):
    StationID = models.AutoField(primary_key=True)
    StationName = models.TextField()
    Enable = models.BooleanField(default=True)

    def __str__(self):
        return f'StationID:{self.StationID}'

    class Meta:
        db_table = 'Station'
