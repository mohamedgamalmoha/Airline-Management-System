import json
from datetime import datetime

from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from django.core.serializers.json import DjangoJSONEncoder
from django.http.response import JsonResponse, HttpResponseForbidden

from .decorators import auth_view
from .models import Flight, Company, Country, Ticket
from accounts.models import Customer, User, Administrator, Token


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
# - create_new_user

def get_all_flights(request):
    data = serialize_queryset(Flight.objects.all().values())
    return JsonResponse(data, safe=False)


def get_flight_by_id(request, flight_id):
    obj = get_object_or_404(Flight, id=flight_id)
    data = serialize_model_obj(obj)
    return JsonResponse(data, safe=False)


def get_flights_by_parameters(request, origin_country_id: int, destination_country_id: int, date: str):
    d, m, y = date.split('-')
    objects = Flight.objects.get_flights_by_parameters(int(origin_country_id),
                                                       int(destination_country_id),
                                                       datetime(day=int(d), month=int(m), year=int(y))).values()
    data = serialize_queryset(objects)
    return JsonResponse(data, safe=False)


def get_all_airlines(response):
    data = serialize_queryset(Company.objects.all().values())
    return JsonResponse(data, safe=False)


def get_airline_by_id(request, airline_id: int):
    obj = get_object_or_404(Company, id=airline_id)
    data = serialize_model_obj(obj)
    return JsonResponse(data, safe=False)


def get_airline_by_parameters(request, country_name: str):
    objects = Company.objects.get_airline_by_parameters(country_name).values()
    data = serialize_queryset(objects)
    return JsonResponse(data, safe=False)


def get_all_countries(request):
    data = serialize_queryset(Country.objects.all().values())
    return JsonResponse(data, safe=False)


def get_country_by_id(request, country_id: int):
    obj = get_object_or_404(Country, id=country_id)
    data = serialize_model_obj(obj)
    return JsonResponse(data, safe=False)


def create_new_user(user: dict):
    obj, created_user = Customer.objects.update_or_create(**user, defaults={'role': ''})
    return obj, created_user


# Customer Facade
# - update_customer (customer)
# - add_ticket (ticket)
# - remove_ticket (ticket)
# - get_my_tickets ()

@auth_view(method='POST')
def update_customer(request, customer: int):
    cus = get_object_or_404(Customer, id=customer)
    cus.first_name = request.POST.get('first_name', cus.first_name)
    cus.last_name = request.POST.get('last_name', cus.last_name)
    cus.address = request.POST.get('address', cus.address)
    cus.phone_number = request.POST.get('phone_number', cus.phone_number)
    cus.credit_card = request.POST.get('credit_card', cus.phone_number)
    cus.save()
    return JsonResponse({'message': 'Customer has been updated Successfully'})


@auth_view(method='POST')
def add_ticket(request):
    ticket = Ticket()
    ticket.flight = get_object_or_404(Flight, id=int(request.POST.get('flight')))
    ticket.customer = get_object_or_404(Customer, id=int(request.POST.get('customer')))
    ticket.save()
    return JsonResponse({'message': 'Ticket has been created Successfully'})


@auth_view(method='POST')
def remove_ticket(request, ticket_id: int):
    obj = get_object_or_404(Ticket, id=ticket_id)
    obj.delete()
    return JsonResponse({'message': 'Ticket has been deleted Successfully'})


@auth_view(method='GET')
def get_my_tickets(request):
    token = get_object_or_404(Token, name=request.GET.get('token'))
    tickets = Ticket.objects.filter(customer__user=token.user)
    data = serialize_queryset(tickets.values())
    return JsonResponse(data, safe=False)


# Airline Facade
# - get_my_flights ()
# - update_airline (airline)
# - add_flight (flight)
# - update_flight (flight)
# - remove_flight (flight)

@auth_view(method='GET')
def get_my_flights(request):
    token = get_object_or_404(Token, name=request.GET.get('token'))
    flights = Flight.objects.filter(company__manager=token.user)
    data = serialize_queryset(flights.values())
    return JsonResponse(data, safe=False)


@auth_view(method='POST')
def update_airline(request, airline: int):
    obj = get_object_or_404(Company, id=airline)
    token = get_object_or_404(Token, name=request.POST.get('token'))
    if obj.manager != token.user:
        return HttpResponseForbidden('You are not the owner of this company')
    obj.name = request.POST.get('name', obj.name)
    obj.country = get_object_or_404(Country, id=int(request.POST.get('country', obj.country.id)))
    obj.save()
    return JsonResponse({'message': 'Airline Company Has Updated Successfully'}, safe=False)


@auth_view(method='POST')
def add_flight(request):
    token = get_object_or_404(Token, name=request.POST.get('token'))
    customer = token.user
    flight = Flight()
    flight.company = customer.manager
    flight.origin = get_object_or_404(Country, id=int(request.POST.get('origin')))
    flight.destination = get_object_or_404(Country, id=int(request.POST.get('destination')))
    flight.departure_time = datetime.fromisoformat(request.POST.get('departure_time'))
    flight.landing_time = datetime.fromisoformat(request.POST.get('landing_time'))
    flight.num_of_tickets = request.POST.get('num_of_tickets', 10)
    flight.save()
    return JsonResponse({'message': 'Airline Company Has Updated Successfully'}, safe=False)


@auth_view(method='POST')
def update_flight(request, flight: int):
    token = get_object_or_404(Token, name=request.POST.get('token'))
    flight = get_object_or_404(Flight, id=flight)
    if flight.company.manager != token.user:
        return HttpResponseForbidden('Your company is not the owner of this flight')
    flight.origin = get_object_or_404(Country, id=int(request.POST.get('origin', flight.origin.id)))
    flight.destination = get_object_or_404(Country, id=int(request.POST.get('destination', flight.destination.id)))
    flight.departure_time = datetime.fromisoformat(request.POST.get('departure_time', str(flight.departure_time)))
    flight.landing_time = datetime.fromisoformat(request.POST.get('landing_time', str(flight.landing_time)))
    flight.save()
    return JsonResponse({'message': 'Flight Has Updated Successfully'}, safe=False)


@auth_view(method='POST')
def remove_flight(request, flight: int):
    token = get_object_or_404(Token, name=request.POST.get('token'))
    obj = get_object_or_404(Flight, id=flight)
    if obj.company.manager != token.user:
        return HttpResponseForbidden('Your company is not the owner of this flight')
    obj.delete()
    return JsonResponse({'message': 'Flight has been deleted Successfully'})


# Admin Facade
# - get_all_customers()
# - add_airline (...)
# - add_customer (...)
# - add_administrator (...)
# - remove_airline (airline)
# - remove_customer (customer)
# - remove_administrator (administrator)

@auth_view(method='GET', allow_admin_only=True)
def get_all_customers(request):
    data = serialize_queryset(Customer.objects.all().values())
    return JsonResponse(data, safe=False)


@auth_view(method='POST', allow_admin_only=True)
def add_airline(request):
    airline = Company()
    airline.name = request.POST.get('name')
    airline.manager = get_object_or_404(User, username=request.POST.get('manger'))
    airline.country = get_object_or_404(Country, id=request.POST.get('country'))
    airline.save()
    return JsonResponse({'message': 'Airline Has Been Added Successfully'}, safe=False)


@auth_view(method='POST', allow_admin_only=True)
def add_customer(request):
    customer = Customer()
    customer.user = get_object_or_404(User, username=request.POST.get('user'))
    customer.first_name = request.POST.get('first_name')
    customer.last_name = request.POST.get('last_name')
    customer.address = request.POST.get('address')
    customer.phone_number = request.POST.get('phone_number')
    customer.credit_card = request.POST.get('credit_card')
    customer.save()
    return JsonResponse({'message': 'Customer Has Been Added Successfully'}, safe=False)


@auth_view(method='POST', allow_admin_only=True)
def add_administrator(request):
    administrator = Administrator()
    administrator.user = get_object_or_404(User, username=request.POST.get('user'))
    administrator.first_name = request.POST.get('first_name')
    administrator.last_name = request.POST.get('last_name')
    return JsonResponse({'message': 'Administrator Has Been Added Successfully'}, safe=False)


@auth_view(method='POST', allow_admin_only=True)
def remove_airline(request, airline: int):
    obj = get_object_or_404(Company, id=airline)
    obj.delete()
    return JsonResponse({'message': 'Airline has been deleted Successfully'})


@auth_view(method='POST', allow_admin_only=True)
def remove_customer(request, customer: int):
    obj = get_object_or_404(Customer, id=customer)
    obj.delete()
    return JsonResponse({'message': 'Customer has been deleted Successfully'})


@auth_view(method='POST', allow_admin_only=True)
def remove_administrator(request, administrator: int):
    obj = get_object_or_404(Administrator, id=administrator)
    obj.delete()
    return JsonResponse({'message': 'Administrator has been deleted Successfully'})
