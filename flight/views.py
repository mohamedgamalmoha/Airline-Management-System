import json
from datetime import datetime

from django.http.response import JsonResponse
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from django.core.serializers.json import DjangoJSONEncoder

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .forms import UpdateAirlineForm
from .models import Flight, Company, Country, Ticket
from .serializers import UpdateAirlineSerializer, AddFlightSerializer, AddTicketSerializer


# Transfer to customer app
#  create_new_user ( user ) - for internal usage
#  update_customer


# Serializing Data As Json
# - serialize_queryset
# - serialize_model_obj

def serialize_queryset(queryset):
    return json.dumps(list(queryset), cls=DjangoJSONEncoder)


def serialize_model_obj(obj):
    return json.dumps(model_to_dict(obj), cls=DjangoJSONEncoder)


# Anonymous Facade
# - get_all_flight
# - get_flight_by_id
# - get_flights_by_parameters
# - get_all_airlines
# - get_airline_by_id
# - get_airline_by_parameters
# - get_all_countries
# - get_country_by_id

def get_all_flight(request):
    data = serialize_queryset(Flight.objects.all().values())
    return JsonResponse(data, safe=False)


def get_flight_by_id(request, flight_id):
    obj = get_object_or_404(Flight, id=flight_id)
    data = serialize_model_obj(obj)
    return JsonResponse(data, safe=False)


def get_flights_by_parameters(request, origin_country_id, destination_country_id, date):
    d, m, y = date.split('-')
    objects = Flight.objects.get_flights_by_parameters(int(origin_country_id),
                                                       int(destination_country_id),
                                                       datetime(day=int(d), month=int(m), year=int(y))).values()
    data = serialize_queryset(objects)
    return JsonResponse(data, safe=False)


def get_all_airlines(response):
    data = serialize_queryset(Company.objects.all().values())
    return JsonResponse(data, safe=False)


def get_airline_by_id(request, airline_id):
    obj = get_object_or_404(Company, id=airline_id)
    data = serialize_model_obj(obj)
    return JsonResponse(data, safe=False)


def get_airline_by_parameters(request, country_name):
    objects = Company.objects.get_airline_by_parameters(country_name).values()
    data = serialize_queryset(objects)
    return JsonResponse(data, safe=False)


def get_all_countries(request):
    data = serialize_queryset(Country.objects.all().values())
    return JsonResponse(data, safe=False)


def get_country_by_id(request, country_id):
    obj = get_object_or_404(Country, id=country_id)
    data = serialize_model_obj(obj)
    return JsonResponse(data, safe=False)


# Customer Facade
# - update_customer (customer)  ## change to customer app
# - add_ticket (ticket)         ## modify
# - remove_ticket (ticket)      ## modify
# - get_my_tickets ()

# def add_ticket(request, flight_id):
#     obj, created = Ticket.objects.get_or_create(customer=request.user, flight__id=flight_id)
#     ticket = serialize_model_obj(obj)
#     return JsonResponse(ticket, safe=False)


@api_view(['POST'])
def add_ticket(request):
    ticket = AddTicketSerializer(data=request.data)

    if ticket.is_valid():
        ticket.instance.customer = request.user
        ticket.save()
        return Response(ticket.data)

    return Response(status=status.HTTP_404_NOT_FOUND)


def remove_ticket(request, ticket_id):
    obj = get_object_or_404(Ticket, id=ticket_id)
    data = serialize_model_obj(obj)
    obj.delete()
    return JsonResponse(data, safe=False)


def get_my_tickets(request):
    tickets = Ticket.objects.filter(customer=request.user)
    data = serialize_queryset(tickets.values())
    return JsonResponse(data, safe=False)


# Airline Facade
# - get_my_flights ()
# - update_airline (airline)
# - add_flight (flight)
# - update_flight (flight)
# - remove_flight (flight)

def get_my_flights(request):
    flights = Flight.objects.filter(company__manager=request.user)
    data = serialize_queryset(flights.values())
    return JsonResponse(data, safe=False)


def update_airline(request, company_id):
    obj = get_object_or_404(Company, id=company_id)
    form = UpdateAirlineForm(request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return JsonResponse({'is_updated': True}, safe=False, status=200)
    return JsonResponse({'is_updated': True}, safe=False, status=200)


def add_flight(request, flight_id):
    pass


# Admin Facade
# - get_all_customers()
# - add_airline (...)
# - add_customer (...)
# - add_administrator (...)
# - remove_airline (airline)
# - remove_customer (customer)
# - remove_administrator (administrator)
# conda install -c anaconda jupyter
