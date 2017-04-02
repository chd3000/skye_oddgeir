from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField


class LogInfo(models.Model):
    """
    Aktuell noch rudimentär. Können wir gern noch ausbauen.
    Hier stehen die Sachen, die wir für ein vernünftiges Log brauchen.
    """
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT(), editable=False, related_name='created_by')
    modified_at = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, on_delete=models.PROTECT(), editable=False, related_name='modified_by')

    class Meta:
        abstract = True


class Airline(LogInfo):
    """
    Basisdaten über Fluggesellschaften
    https://github.com/SmileyChris/django-countries
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    ICAO = models.CharField(max_length=3)
    IATA = models.CharField(max_length=2)
    country = CountryField()
    start_date = models.DateField(default='1900-01-01') # Wann das Unternehmen gegründet wurde (vllt interessant?)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'airline'
        ordering = ['name', ]


class Airport(LogInfo):
    """
    Basisdaten für Flughäfen
    """
    id = models.AutoField(primary_key=True)
    country = CountryField()
    city = models.CharField(max_length=50)
    IATA = models.CharField(max_length=3)
    ICAO = models.CharField(max_length=4)

    def __str__(self):
        name = self.country + " - " + self.city
        return name

    class Meta:
        db_table = 'airport'
        ordering = ['country', 'city']


class Platform(LogInfo):
    """
    Basisdaten für Buchungsplattform
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    homepage = models.URLField()
    country = CountryField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'platform'
        ordering = ['name', ]


class Flight(LogInfo):
    """
    Basisdaten für Flüge
    """
    id = models.AutoField(primary_key=True)
    flight_number = models.CharField(max_length=5)
    airline = models.ForeignKey(Airline, on_delete=models.PROTECT(), related_name='airline_id')
    start_airport = models.ForeignKey(Airport, on_delete=models.PROTECT(), related_name='start_airport_id')
    end_airport = models.ForeignKey(Airport, on_delete=models.PROTECT(), related_name='end_airport_id')
    start_time = models.DateTimeField()  # planmäßiger Abflug
    end_time = models.DateTimeField()  # planmäßige Landung (hier wirds wohl wichtig sein wie wir die richtige Zeitzone reinbekommen)

    def __str__(self):
        return self.flight_number

    class Meta:
        db_table = 'flight'
        ordering = ['airline', 'flight_number']


class Class(LogInfo):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    level = models.IntegerField()   # Economy 100, Business Class 200, First Class 300... Sowas in der Art?
                                    # So umgehen wir die unterschiedlichen Benennungen und haben 99 Stellen um jede Benennung mit aufzunehmen


class Price(LogInfo):
    """
    Tabelle wo die Preise gespeichert werden. 
    Wird den Batzen der Datenmenge ausmachen.
    Hier ist die Frage, ob wir einen gewissen 'Split' schon mit einplanen oder ober wir einfach die Auswertungen 
    hart speichern und überschreiben lassen.
    """
    id = models.AutoField(primary_key=True)
    platform_id = models.ForeignKey(Platform, on_delete=models.PROTECT(), related_name='platform_id')
    flight_id = models.ForeignKey(Flight, on_delete=models.PROTECT(), related_name='flight_id')
    class_id = models.ForeignKey(Class, on_delete=models.PROTECT(), related_name='class_id')
    price = models.IntegerField()  # Wegen Gleitkommafehlern. Ist das bei uns erheblich oder können wir doch mit Floats rechnen?
