from django.db import models
from datetime import date, datetime

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

    def to_dict(self, contact=False):
        result = {
            "id": self.UserID,
            "name": self.Name,
            "avatar": self.Avatar
        }
        if contact:
            result.update({
                "email": self.Email,
                "phone": self.Phone
            })
        return result

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
    Status = models.TextField(default="new")
    Work_Status = models.BooleanField(default=True)
    Date = models.DateField()

    def __str__(self):
        return f'RequestID:{self.RequestID}'

    def to_dict(self):
        return {
            "id": self.RequestID,
            "status": self.Status,
            "date": self.Date,
            "workStatus": self.Work_Status,
            "passenger": self.Passenger.to_dict(),
            "route": self.Route.to_dict()
        }

    class Meta:
        db_table = 'Request'

class Route(models.Model):
    RouteID = models.BigAutoField(primary_key=True)
    Driver = models.ForeignKey("Account", db_column="DriverID", on_delete=models.PROTECT,
                               related_name="Driver_Routes")
    Status = models.TextField(default='available')
    Date = models.DateField()
    Work_Status = models.BooleanField(default=True)
    Passengers = models.ManyToManyField(Account,
                                        through="RoutePassenger",
                                        through_fields=("Route", "Passenger"),
                                        related_name="Passenger_Routes")
    Stations = models.ManyToManyField("Station",
                                      through="RouteStation",
                                      through_fields=("Route", "Station"),
                                      related_name="+")
    Car_Model = models.TextField(default="")
    Car_Color = models.TextField(default="")
    Car_Capacity = models.IntegerField(default="")
    LicensePlateNumber = models.TextField(default="")

    def update_status(self):
        if self.Status == "deleted":
            return False
        if self.Date < date.today():
            self.Status = "expired"
            return True
        # Check each stations
        for entry in self.RouteStations.all():
            if entry.Time < datetime.now():
                self.Status = "expired"
                return True
        return False

    def to_dict(self, uid=None):
        result = {
            "id": self.RouteID,
            "status": self.Status,
            "date": self.Date,
            "driver": self.Driver.to_dict(contact=True),
            "n-passengers": self.RoutePassengers.count(),
            "carInfo": {
                "model": self.Car_Model,
                "color": self.Car_Color,
                "capacity": self.Car_Capacity,
                "licensePlateNumber": self.LicensePlateNumber
            }
        }

        if self.Driver.UserID == uid:
            result['workStatus'] = self.Work_Status

        # Populate Passengers
        passengers = list()
        stations = list()
        on_passengers = dict()
        off_passengers = dict()

        for entry in self.RoutePassengers.all():
            passengers.append(entry.Passenger.to_dict())
            on_passengers[entry.On.StationID]=entry.Passenger.UserID
            off_passengers[entry.Off.StationID]=entry.Passenger.UserID
            if entry.Passenger.UserID == uid:
                result.update({
                    'workStatus': entry.Work_Status,
                    'on-station': entry.On.to_dict(),
                    'off-station': entry.Off.to_dict()
                })
        result['passengers'] = passengers

        # Populate Stations
        for entry in self.RouteStations.all():
            station = entry.Station.to_dict()
            station['datetime'] = entry.Time.isoformat()
            station['on-passengers'] = on_passengers.get(entry.Station.StationID, [])
            station['off-passengers'] = off_passengers.get(entry.Station.StationID, [])
            stations.append(station)

        result['stations'] = stations
        return result

    def __str__(self):
        return f'RouteID:{self.RouteID}'

    class Meta:
        db_table = 'Route'

class RoutePassenger(models.Model):
    Passenger = models.ForeignKey("Account", db_column="PassengerID", on_delete=models.PROTECT, related_name="RoutePassengers")
    Route = models.ForeignKey("Route", db_column="RouteID", on_delete=models.PROTECT, related_name="RoutePassengers")
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
    Route = models.ForeignKey("Route", db_column="RouteID", on_delete=models.CASCADE, related_name="RouteStations")
    Station = models.ForeignKey("Station", db_column="StationID", on_delete=models.PROTECT, related_name="+")
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

    def to_dict(self):
        return {
            "id": self.StationID,
            "name": self.StationName
        }

    class Meta:
        db_table = 'Station'
