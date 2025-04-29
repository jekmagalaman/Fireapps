from django.contrib import admin
from django.urls import path

from fire.views import HomePageView, ChartView, PieCountbySeverity, LineCountbyMonth, MultilineIncidentTop3Country, multipleBarbySeverity, map_station, map_Incidents, LocationList,LocationCreateView, LocationUpdateView, LocationDeleteView, FirestationList, FirestationCreateView, FirestationUpdateView, FirestationDeleteView, FireincidentList, FireincidentCreateView, FireincidentUpdateView, FireincidentDeleteView, FiretrucksList, FiretrucksCreateView, FiretrucksUpdateView,FiretrucksDeleteView, FireFightersList, FireFightersCreateView, FireFightersUpdateView, FireFightersDeleteView, WeatherConditionList, WeatherConditionUpdateView, WeatherConditionCreateView, WeatherConditionDeleteView

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', HomePageView.as_view(), name='home'),
    path('dashboard_chart', ChartView.as_view(), name='dashboard-chart'),
    path('chart/', PieCountbySeverity, name='chart'),
    path('multilineChart/', MultilineIncidentTop3Country, name='chart'),
    path('lineChart/', LineCountbyMonth, name='chart'),
    path('multiBarChart/', multipleBarbySeverity, name='chart'),
    path('stations', map_station, name='map-station'),
    path('Incidents', map_Incidents, name='map-incidents'),

    path('location_list', LocationList.as_view(), name='location-list'),
    path('location_list/add', LocationCreateView.as_view(), name='location-add'),
    path('location_list/<pk>',LocationUpdateView.as_view(), name='location-update'),
    path('location_list/<pk>/delete',LocationDeleteView.as_view(), name='location-delete'),

    path('firestation_list', FirestationList.as_view(), name='firestation-list'),
    path('firestation_list/add', FirestationCreateView.as_view(), name='firestation-add'),
    path('firestation_list/<pk>',FirestationUpdateView.as_view(), name='firestation-update'),
    path('firestation_list/<pk>/delete',FirestationDeleteView.as_view(), name='firestation-delete'),

    path('fireincident_list', FireincidentList.as_view(), name='fireincident-list'),
    path('fireincident_list/add', FireincidentCreateView.as_view(), name='fireincident-add'),
    path('fireincident_list/<pk>',FireincidentUpdateView.as_view(), name='fireincident-update'),
    path('fireincident_list/<pk>/delete',FireincidentDeleteView.as_view(), name='fireincident-delete'),

    path('firetruck_list', FiretrucksList.as_view(), name='firetruck-list'),
    path('firetruck_list/add', FiretrucksCreateView.as_view(), name='firetruck-add'),
    path('firetruck_list/<pk>',FiretrucksUpdateView.as_view(), name='firetruck-update'),
    path('firetruck_list/<pk>/delete',FiretrucksDeleteView.as_view(), name='firetruck-delete'),

    path('firefighter_list', FireFightersList.as_view(), name='firefighter-list'),
    path('firefighter_list/add', FireFightersCreateView.as_view(), name='firefighter-add'),
    path('firefighter_list/<pk>',FireFightersUpdateView.as_view(), name='firefighter-update'),
    path('firefighter_list/<pk>/delete',FireFightersDeleteView.as_view(), name='firefighter-delete'),

    path('weathercon_list', WeatherConditionList.as_view(), name='weathercondition-list'),
    path('weathercon_list/add', WeatherConditionCreateView.as_view(), name='weathercondition-add'),
    path('weathercon_list/<pk>',WeatherConditionUpdateView.as_view(), name='weathercondition-update'),
    path('weathercon_list/<pk>/delete',WeatherConditionDeleteView.as_view(), name='weathercondition-delete'),


]
