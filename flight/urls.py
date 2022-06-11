from django.urls import path

from .views import (
    # Anonymous Facade
    get_all_flight, get_flight_by_id, get_flights_by_parameters, get_all_airlines,
    get_airline_by_id, get_airline_by_parameters, get_all_countries, get_country_by_id,

    # Customer Facade
    add_ticket,
    remove_ticket,
    get_my_tickets,

    # Airline Facade
    get_my_flights,
    update_airline,

    # Admin Facade
    )


app_name = 'flight'

urlpatterns = [
    path('all-flights/', get_all_flight, name='all_flights'),
    path('flight-by-id/<int:flight_id>', get_flight_by_id, name='flight_by_id'),
    path('flight-by-parameters/<int:origin_country_id>/<int:destination_country_id>/<str:date>',
         get_flights_by_parameters, name='flight_by_id'),

    path('all-airlines/', get_all_airlines, name='all_airlines'),
    path('airline-by-id/<int:airline_id>', get_airline_by_id, name='airline_by_id'),
    path('airlines-by-parameters/<str:company_name>', get_airline_by_parameters, name='airline_by_parameters'),

    path('all-countries/', get_all_countries, name='all_countries'),
    path('country-by-id/<int:country_id>', get_country_by_id, name='country_by_id'),

    path('add-ticket', add_ticket, name='add_ticket'),
    path('remove--ticket', remove_ticket, name='remove_ticket'),
    path('get-my-tickets', get_my_tickets, name='own_tickets'),

    path('own-flights', get_my_flights, name='own_flights'),
    path('update_airline', update_airline, name='update_airline'),
]
