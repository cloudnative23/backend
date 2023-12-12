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
    Passenger_Notification_Count = models.IntegerField(default=0)
    Driver_Notification_Count = models.IntegerField(default=0)

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
    On = models.ForeignKey("RouteStation", db_column="On", on_delete=models.PROTECT, related_name="OnRequests")
    Off = models.ForeignKey("RouteStation", db_column="Off", on_delete=models.PROTECT, related_name="OffRequests")
    Status = models.TextField(default="new")
    Work_Status = models.BooleanField(default=True)
    Date = models.DateField()
    Timestamp = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f'RequestID:{self.RequestID}'

    def update_status(self):
        if self.Route.Status != "available" and self.Status == "new":
            self.Status = "expired"
            return True
        return False

    def to_dict(self):
        return {
            "id": self.RequestID,
            "passenger": self.Passenger.to_dict(),
            "status": self.Status,
            "timestamp": self.Timestamp.isoformat(),
            "date": self.Date.isoformat(),
            "workStatus": self.Work_Status,
            "on-station": self.On.to_dict(passenger=False),
            "off-station": self.Off.to_dict(passenger=False),
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
        if self.Status != "available":
            return False
        if self.Date < date.today():
            self.Status = "expired"
            return True
        for entry in self.RouteStations.exclude(Status="deleted"):
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
            on_passengers[entry.On.Station_id]=entry.Passenger_id
            off_passengers[entry.Off.Station_id]=entry.Passenger_id
            if entry.Passenger_id == uid:
                result.update({
                    'workStatus': entry.Work_Status,
                    'on-station': entry.On.to_dict(passenger=False),
                    'off-station': entry.Off.to_dict(passenger=False)
                })
        result['passengers'] = passengers

        # Populate Stations
        for entry in self.RouteStations.exclude(Status="deleted").order_by("Time"):
            station = entry.Station.to_dict()
            station['datetime'] = entry.Time.isoformat()
            station['on-passengers'] = list(entry.OnPassengers.values_list("Passenger_id", flat=True))
            station['off-passengers'] = list(entry.OffPassengers.values_list("Passenger_id", flat=True))
            stations.append(station)

        result['stations'] = stations
        return result

    def __str__(self):
        return f'RouteID:{self.RouteID}'

    class Meta:
        db_table = 'Route'

class RoutePassenger(models.Model):
    RoutePassengerID = models.BigAutoField(primary_key=True)
    Passenger = models.ForeignKey("Account", db_column="PassengerID", on_delete=models.PROTECT, related_name="RoutePassengers")
    Route = models.ForeignKey("Route", db_column="RouteID", on_delete=models.PROTECT, related_name="RoutePassengers")
    Request = models.ForeignKey("Request", db_column="RequestID", on_delete=models.PROTECT,
                                related_name="+")
    On = models.ForeignKey("RouteStation", db_column="On", on_delete=models.PROTECT, related_name="OnPassengers")
    Off = models.ForeignKey("RouteStation", db_column="Off", on_delete=models.PROTECT, related_name="OffPassengers")
    Work_Status = models.BooleanField(default=True)

    def __str__(self):
        return f'PassengerID:{self.PassengerID} RouteID:{self.RouteID}'

    class Meta:
        db_table = 'RoutePassenger'

class RouteStation(models.Model):
    RouteStationID = models.BigAutoField(primary_key=True)
    Route = models.ForeignKey("Route", db_column="RouteID", on_delete=models.CASCADE, related_name="RouteStations")
    Station = models.ForeignKey("Station", db_column="StationID", on_delete=models.PROTECT, related_name="+")
    Time = models.DateTimeField()
    Status = models.TextField(default="normal")

    def __str__(self):
        return f'RouteID:{self.Route.RouteID}'

    def to_dict(self, passenger=True):
        result = self.Station.to_dict()
        result.update({
            "datetime": self.Time.isoformat()
        })
        if passenger:
            result.update({
                "on-passengers": [entry.Passenger_id for entry in self.OnPassengers.all()],
                "off-passengers": [entry.Passenger_id for entry in self.OffPassengers.all()]
            })
        return result

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

class Notification(models.Model):
    NotificationID = models.BigAutoField(primary_key=True)
    User = models.ForeignKey("Account", db_column="UserID", on_delete=models.PROTECT,related_name="Notification_Users")
    Read = models.BooleanField(default=False)
    For = models.TextField()
    Category = models.TextField()
    Route = models.ForeignKey("Route", db_column="RouteID", on_delete=models.PROTECT, related_name="+", null=True)
    Request = models.ForeignKey("Request", db_column="RequestID", on_delete=models.PROTECT,related_name="+", null=True)
    Timestamp = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f'NotificationID:{self.NotificationID}'

    class Meta:
        db_table = 'Notification'

    def to_dict(self):
        # Currently, we don't implement notifications related to routes
        return {
            "id": self.NotificationID,
            "read": self.Read,
            "for": self.For,
            "category": self.Category,
            "request": self.request.to_dict(),
        }
