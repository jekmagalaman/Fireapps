from django.core.management.base import BaseCommand
from faker import Faker
from fire.models import Incident, FireStation, Locations, FireTruck, Firefighters, WeatherConditions

class Command(BaseCommand):
    help = 'Create initial data for the application'
    
    def handle(self, *args, **kwargs):
        self.faker = Faker()
        self.create_location(0)
        self.create_firestation(0)
        self.create_firefighter(0)
        self.create_firetruck(10)
        self.create_incident(0)
        self.create_weather_conditions(0)

    def create_location(self, count):
        for _ in range(count):
            location = Locations.objects.create(
                name=self.faker.company(),
                latitude=self.faker.latitude(),
                longitude=self.faker.longitude(),
                address=self.faker.street_address(),
                city=self.faker.city(),
                country=self.faker.country()
            )
            self.stdout.write(self.style.SUCCESS('Successfully created location'))

    def create_firestation(self, count):
        for _ in range(count):
            fire_station = FireStation.objects.create(
                name=self.faker.company(),
                latitude=self.faker.latitude(),
                longitude=self.faker.longitude(),
                address=self.faker.street_address(),
                city=self.faker.city(),
                country=self.faker.country()
            )
            self.stdout.write(self.style.SUCCESS('Successfully created fire station'))

    def create_firefighter(self, count):
        fire_stations = list(FireStation.objects.all())
        rank_choices= [choice[0] for choice in Firefighters.RANK_CHOICES]
        xp_choices = [choice[0] for choice in Firefighters.XP_CHOICES]

        for _ in range(count):
            firefighter = Firefighters.objects.create(
                name=self.faker.name(),
                rank=self.faker.random_element(rank_choices),
                experience_level=self.faker.random_element(xp_choices),
                station=self.faker.random_element(fire_stations)
            )
            self.stdout.write(self.style.SUCCESS('Successfully created firefighter'))

    def create_firetruck(self, count):
        fire_stations = list(FireStation.objects.all())
        model = ['Toyota fire', 'Tesla', 'Misyubibi fire engine']

        for _ in range(count):
            fire_truck = FireTruck.objects.create(
                truck_number=self.faker.unique.random_int(min=1, max=1000),
                model=self.faker.random_element(model),
                capacity=self.faker.random_int(min=1000, max=5000),
                station=self.faker.random_element(fire_stations)
            )
            self.stdout.write(self.style.SUCCESS('Successfully created fire truck'))

    def create_incident(self, count):
        locations = list(Locations.objects.all())
        severity_choices = [choice[0] for choice in Incident.SEVERITY_CHOICES]

        for _ in range(count):
            incident = Incident.objects.create(
                location=self.faker.random_element(locations),
                date_time=self.faker.date_time_this_year(),
                severity_level=self.faker.random_element(severity_choices),
                description=self.faker.text(max_nb_chars=250)
            )
            self.stdout.write(self.style.SUCCESS('Successfully created incident with severity'))


    def create_weather_conditions(self, count):
        incidents = list(Incident.objects.all())

        for _ in range(count):
            weather = WeatherConditions.objects.create(
                incident=self.faker.random_element(incidents),
                temperature=self.faker.random_number(digits=2, fix_len=True),
                humidity=self.faker.random_number(digits=2, fix_len=True),
                wind_speed=self.faker.random_number(digits=2, fix_len=True),
                weather_description=self.faker.word()
            )
            self.stdout.write(self.style.SUCCESS('Successfully created weather conditions'))
