from django.urls import path

from .views import (
    # Anonymous Facade
    get_all_flights, get_flight_by_id, get_flights_by_parameters, get_all_airlines,
    get_airline_by_id, get_airline_by_parameters, get_all_countries, get_country_by_id,

    # Customer Facade
    update_customer,
    add_ticket,
    remove_ticket,
    get_my_tickets,

    # Airline Facade
    get_my_flights,
    update_airline,
    add_flight,
    update_flight,
    remove_flight,

    # Admin Facade
    get_all_customers,
    add_airline,
    add_customer,
    add_administrator,
    remove_airline,
    remove_customer,
    remove_administrator,

    # Custom Views
    SearchFlightView,
    CreateTicketView,
    UpdateTicketStatusView,
    TicketListView
    )


app_name = 'flight'

urlpatterns = [
    # Anonymous Facade
    path('all-flights/', get_all_flights, name='all_flights'),
    path('flight-by-id/<int:flight_id>', get_flight_by_id, name='flight_by_id'),
    path('flight-by-parameters/<int:origin_country_id>/<int:destination_country_id>/<str:date>',
         get_flights_by_parameters, name='flight_by_parameters'),
    path('all-airlines/', get_all_airlines, name='all_airlines'),
    path('airline-by-id/<int:airline_id>', get_airline_by_id, name='airline_by_id'),
    path('airlines-by-parameters/<str:company_name>', get_airline_by_parameters, name='airline_by_parameters'),
    path('all-countries/', get_all_countries, name='all_countries'),
    path('country-by-id/<int:country_id>', get_country_by_id, name='country_by_id'),

    # Customer Facade
    path('update-customer/<int:customer>', update_customer, name='update_customer'),
    path('add-ticket', add_ticket, name='add_ticket'),
    path('remove-ticket/<int:ticket_id>', remove_ticket, name='remove_ticket'),
    path('get-my-tickets', get_my_tickets, name='own_tickets'),

    # Airline Facade
    path('own-flights', get_my_flights, name='own_flights'),
    path('update_airline/<int:airline>', update_airline, name='update_airline'),
    path('add-flight', add_flight, name='add_flight'),
    path('update-flight/<int:flight>', update_flight, name='update_flight'),
    path('remove-flight/<int:flight>', remove_flight, name='remove_flight'),

    # Admin Facade
    path('all-customers', get_all_customers, name='all_customers'),
    path('add-airline', add_airline, name='add_airline'),
    path('add_customer', add_customer, name='add_customer'),
    path('add-administrator', add_administrator, name='add_administrator'),
    path('remove_airline/<int:airline>', remove_airline, name='remove_airline'),
    path('remove_customer/<int:customer>', remove_customer, name='remove_customer'),
    path('remove_administrator/<int:administrator>', remove_administrator, name='remove_administrator'),

    # Views
    path('search/', SearchFlightView.as_view(), name='search_flight'),
    path('ticket/create/<int:pk>', CreateTicketView.as_view(), name='create_ticket'),
    path('ticket/update/<int:pk>', UpdateTicketStatusView.as_view(), name='update_status_ticket'),
    path('ticket/list/', TicketListView.as_view(), name='list_ticket'),
]
