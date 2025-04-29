from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from fire.models import Locations, Incident, FireStation, FireTruck, Firefighters, WeatherConditions
from fire.forms import LocationForm, IncidentForm, FireStationForm, FireFighterForm, FireTruckForm, WeatherConForm
from django.urls import reverse_lazy

from typing import Any
from django.db.models.query import QuerySet
from django.db.models import Q

from django.db import connection
from django.http import JsonResponse
from django.db.models.functions import ExtractMonth

from django.db.models import Count
from datetime import datetime


class HomePageView(ListView):
    model = Locations
    context_object_name = 'home'
    template_name = "home.html"

class ChartView(ListView):
    template_name = 'chart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self, *args, **kwargs):
        pass

def PieCountbySeverity(request):
    query = '''
    SELECT severity_level, COUNT(*) as count
    FROM fire_incident
    GROUP BY severity_level
    '''
    data = {}
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    if rows:
        # Construct the dictionary with severity level as keys and count as values
        data = {severity: count for severity, count in rows}
    else:
        data = {}

    return JsonResponse(data)

def LineCountbyMonth(request):
    current_year = datetime.now().year
    result = {month: 0 for month in range(1, 13)}

    incidents_per_month = Incident.objects.filter(
        date_time__year=current_year
    ).exclude(date_time__isnull=True).values_list('date_time', flat=True)

    for date_time in incidents_per_month:
        if date_time is not None:
            month = date_time.month
            result[month] += 1

    month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
    result_with_month_names = {month_names[int(month)]: count for month, count in result.items()}

    return JsonResponse(result_with_month_names)


def MultilineIncidentTop3Country(request):

    query = '''
        SELECT 
        fl.country,
        strftime('%m', fi.date_time) AS month,
        COUNT(fi.id) AS incident_count
    FROM 
        fire_incident fi
    JOIN 
        fire_locations fl ON fi.location_id = fl.id
    WHERE 
        fl.country IN (
            SELECT 
                fl_top.country
            FROM 
                fire_incident fi_top
            JOIN 
                fire_locations fl_top ON fi_top.location_id = fl_top.id
            WHERE 
                strftime('%Y', fi_top.date_time) = strftime('%Y', 'now')
            GROUP BY 
                fl_top.country
            ORDER BY 
                COUNT(fi_top.id) DESC
            LIMIT 3
        )
        AND strftime('%Y', fi.date_time) = strftime('%Y', 'now')
    GROUP BY 
        fl.country, month
    ORDER BY 
        fl.country, month;
    '''

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    # Initialize a dictionary to store the result
    result = {}

    # Initialize a set of months from January to December
    months = set(str(i).zfill(2) for i in range(1, 13))

    # Loop through the query results
    for row in rows:
        country = row[0]
        month = row[1]
        total_incidents = row[2]

        # If the country is not in the result dictionary, initialize it with all months set to zero
        if country not in result:
            result[country] = {month: 0 for month in months}

        # Update the incident count for the corresponding month
        result[country][month] = total_incidents

    # Ensure there are always 3 countries in the result
    while len(result) < 3:
        # Placeholder name for missing countries
        missing_country = f"Country {len(result) + 1}"
        result[missing_country] = {month: 0 for month in months}

    for country in result:
        result[country] = dict(sorted(result[country].items()))

    return JsonResponse(result)

def multipleBarbySeverity(request):
    query = '''
    SELECT 
        fi.severity_level,
        strftime('%m', fi.date_time) AS month,
        COUNT(fi.id) AS incident_count
    FROM 
        fire_incident fi
    GROUP BY fi.severity_level, month
    '''

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    result = {}
    months = set(str(i).zfill(2) for i in range(1, 13))

    for row in rows:
        level = str(row[0])  # Ensure the severity level is a string
        month = row[1]
        total_incidents = row[2]

        if level not in result:
            result[level] = {month: 0 for month in months}

        result[level][month] = total_incidents

    # Sort months within each severity level
    for level in result:
        result[level] = dict(sorted(result[level].items()))

    return JsonResponse(result)

def map_station(request):
    fireStations = FireStation.objects.values('name', 'latitude', 'longitude')

    for fs in fireStations:
        fs['latitude'] = float(fs['latitude'])
        fs['longitude'] = float(fs['longitude'])

    fireStations_list = list(fireStations)

    context = {
        'fireStations': fireStations_list,
    }

    return render(request, 'map_station.html', context)


def map_Incidents(request):
    # Fetching fire incidents along with their location details
    cities = Locations.objects.values_list('city', flat=True).distinct()
    fireIncidents = Incident.objects.select_related('location').values('location__name', 'location__latitude', 'location__longitude', 'location__city')

 
    for incident in fireIncidents:
        incident['location__latitude'] = float(incident['location__latitude'])
        incident['location__longitude'] = float(incident['location__longitude'])

    fireIncidents_list = list(fireIncidents)

    context = {
        'fireIncidents': fireIncidents_list,  # Pass the list to the template
        'cities': cities,
    }

    return render(request, 'map_incidents.html', context)



#-----------------Location--------------------------------

class LocationList(ListView):
    model = Locations
    context_object_name = 'locations'
    template_name = 'locations/location_list.html'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        qs = super(LocationList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get('q')
            qs = qs.filter(Q(name__icontains=query) | 
                        Q(city__icontains=query) |
                        Q(address__icontains=query) |
                        Q(country__icontains=query))
        return qs

class LocationCreateView(CreateView):
    model = Locations
    form_class = LocationForm
    template_name = 'locations/location_add.html'
    success_url = reverse_lazy('location-list')

class LocationUpdateView(UpdateView):
    model = Locations
    form_class = LocationForm
    template_name = 'locations/location_edit.html'
    success_url = reverse_lazy('location-list')

class LocationDeleteView(DeleteView):
    model = Locations
    template_name = 'locations/location_del.html'
    success_url = reverse_lazy('location-list')

#-----------------FireStation--------------------------------


class FirestationList(ListView):
    model = FireStation
    context_object_name = 'firestation'
    template_name = 'firestation/firestation_list.html'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        qs = super(FirestationList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get('q')
            qs = qs.filter(Q(name__icontains=query) | 
                        Q(city__icontains=query) |
                        Q(address__icontains=query) |
                        Q(country__icontains=query))
        return qs

class FirestationCreateView(CreateView):
    model = FireStation
    form_class = FireStationForm
    template_name = 'firestation/firestation_add.html'
    success_url = reverse_lazy('firestation-list')

class FirestationUpdateView(UpdateView):
    model = FireStation
    form_class = FireStationForm
    template_name = 'firestation/firestation_edit.html'
    success_url = reverse_lazy('firestation-list')

class FirestationDeleteView(DeleteView):
    model = FireStation
    template_name = 'firestation/firestation_del.html'
    success_url = reverse_lazy('firestation-list')


#-----------------FireIncident--------------------------------


class FireincidentList(ListView):
    model = Incident
    context_object_name = 'fireincident'
    template_name = 'fireincident/fireincident_list.html'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        qs = super(FireincidentList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get('q')
            qs = qs.filter(Q(location__name__icontains=query) | 
                           Q(location__city__icontains=query) |
                           Q(location__country__icontains=query) |
                           Q(severity_level__icontains=query))
        return qs

class FireincidentCreateView(CreateView):
    model = Incident
    form_class = IncidentForm
    template_name = 'fireincident/fireincident_add.html'
    success_url = reverse_lazy('fireincident-list')

class FireincidentUpdateView(UpdateView):
    model = Incident
    form_class = IncidentForm
    template_name = 'fireincident/fireincident_edit.html'
    success_url = reverse_lazy('fireincident-list')

class FireincidentDeleteView(DeleteView):
    model = Incident
    template_name = 'fireincident/fireincident_del.html'
    success_url = reverse_lazy('fireincident-list')


#-----------------Firetruckss--------------------------------


class FiretrucksList(ListView):
    model = FireTruck
    context_object_name = 'firetruck'
    template_name = 'firetruck/firetruck_list.html'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        qs = super(FiretrucksList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get('q')
            qs = qs.filter(Q(truck_number__icontains=query) | 
                           Q(model__icontains=query) |
                           Q(capacity__icontains=query) |
                           Q(station__name__icontains=query))
        return qs

class FiretrucksCreateView(CreateView):
    model = FireTruck
    form_class = FireTruckForm
    template_name = 'firetruck/firetruck_add.html'
    success_url = reverse_lazy('firetruck-list')

class FiretrucksUpdateView(UpdateView):
    model = FireTruck
    form_class = FireTruckForm
    template_name = 'firetruck/firetruck_edit.html'
    success_url = reverse_lazy('firetruck-list')

class FiretrucksDeleteView(DeleteView):
    model = FireTruck
    template_name = 'firetruck/firetruck_del.html'
    success_url = reverse_lazy('firetruck-list')



#-----------------Firefighterssss--------------------------------


class FireFightersList(ListView):
    model = Firefighters
    context_object_name = 'firefighter'
    template_name = 'firefighter/firefighter_list.html'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        qs = super(FireFightersList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get('q')
            qs = qs.filter(Q(name__icontains=query) | 
                           Q(rank__icontains=query) |
                           Q(experience_level__icontains=query) |
                           Q(station__name__icontains=query)|
                           Q(station__country__icontains=query))
        return qs

class FireFightersCreateView(CreateView):
    model = Firefighters
    form_class = FireFighterForm
    template_name = 'firefighter/firefighter_add.html'
    success_url = reverse_lazy('firefighter-list')

class FireFightersUpdateView(UpdateView):
    model = Firefighters
    form_class = FireFighterForm
    template_name = 'firefighter/firefighter_edit.html'
    success_url = reverse_lazy('firefighter-list')

class FireFightersDeleteView(DeleteView):
    model = Firefighters
    template_name = 'firefighter/firefighter_del.html'
    success_url = reverse_lazy('firefighter-list')



#-----------------weathercondtions--------------------------------


class WeatherConditionList(ListView):
    model = WeatherConditions
    context_object_name = 'weathercondition'
    template_name = 'weathercon/weathercon_list.html'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        qs = super(WeatherConditionList, self).get_queryset(*args, **kwargs)
        if self.request.GET.get("q") != None:
            query = self.request.GET.get('q')
            qs = qs.filter(Q(incident__location__name__icontains=query) | 
                           Q(temperature__icontains=query) |
                           Q(humidity__icontains=query) |
                           Q(wind_speed__icontains=query))
        return qs

class WeatherConditionCreateView(CreateView):
    model = WeatherConditions
    form_class = WeatherConForm
    template_name = 'weathercon/weathercon_add.html'
    success_url = reverse_lazy('weathercon-list')

class WeatherConditionUpdateView(UpdateView):
    model = WeatherConditions
    form_class = WeatherConForm
    template_name = 'weathercon/weathercon_edit.html'
    success_url = reverse_lazy('weathercon-list')

class WeatherConditionDeleteView(DeleteView):
    model = WeatherConditions
    template_name = 'weathercon/weathercon_del.html'
    success_url = reverse_lazy('weathercon-list')
