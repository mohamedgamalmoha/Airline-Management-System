import json
from datetime import datetime

from django.contrib import messages
from django.urls import reverse_lazy
from django.forms.models import model_to_dict
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.views.generic.detail import DetailView
from django.shortcuts import redirect, get_object_or_404
from django.core.serializers.json import DjangoJSONEncoder
from django.http.response import JsonResponse, HttpResponseForbidden

from .decorators import auth_view, CustomerRequired
from .forms import FlightFilter, TicketStatusUpdateForm
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
    d = datetime.fromisoformat(date)
    objects = Flight.objects.get_flights_by_parameters(int(origin_country_id), int(destination_country_id), d).values()
    data = serialize_queryset(objects)
    return JsonResponse(data, safe=False)


def get_all_airlines(response):
    data = serialize_queryset(Company.objects.all().values())
    return JsonResponse(data, safe=False)


def get_airline_by_id(request, airline_id: int):
    obj = get_object_or_404(Company, id=airline_id)
    data = serialize_model_obj(obj)
    return JsonResponse(data, safe=False)


def get_airline_by_parameters(request, company_name: str):
    objects = Company.objects.get_airline_by_parameters(company_name).values()
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
    Ticket.objects.create(
        flight=get_object_or_404(Flight, id=int(request.POST.get('flight'))),
        customer=get_object_or_404(Customer, id=int(request.POST.get('customer')))
    )
    return JsonResponse({'message': 'Ticket has been created Successfully'})


@auth_view(method='POST')
def remove_ticket(request, ticket_id: int):
    obj = get_object_or_404(Ticket, id=ticket_id)
    token = get_object_or_404(Token, name=request.POST.get('token'))
    if obj.customer.user != token.user:
        return HttpResponseForbidden('You are not the owner of this company')
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
    Flight.objects.create(
        company=customer.manager,
        origin=get_object_or_404(Country, id=int(request.POST.get('origin'))),
        destination=get_object_or_404(Country, id=int(request.POST.get('destination'))),
        departure_time=datetime.fromisoformat(request.POST.get('departure_time')),
        landing_time=datetime.fromisoformat(request.POST.get('landing_time')),
        num_of_tickets=int(request.POST.get('num_of_tickets', 10))
    )
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
    flight.num_of_tickets = int(request.POST.get('num_of_tickets', flight.num_of_tickets))
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
    Company.objects.create(
        name=request.POST.get('name'),
        manager=get_object_or_404(User, username=request.POST.get('manager')),
        country=get_object_or_404(Country, id=request.POST.get('country'))
    )
    return JsonResponse({'message': 'Airline Has Been Added Successfully'}, safe=False)


@auth_view(method='POST', allow_admin_only=True)
def add_customer(request):
    Customer.objects.create(
        user=get_object_or_404(User, username=request.POST.get('user')),
        first_name=request.POST.get('first_name'),
        last_name=request.POST.get('last_name'),
        address=request.POST.get('address'),
        phone_number=request.POST.get('phone_number'),
        credit_card=request.POST.get('credit_card')
    )
    return JsonResponse({'message': 'Customer Has Been Added Successfully'}, safe=False)


@auth_view(method='POST', allow_admin_only=True)
def add_administrator(request):
    Administrator.objects.create(
        user=get_object_or_404(User, username=request.POST.get('user')),
        first_name=request.POST.get('first_name'),
        last_name=request.POST.get('last_name')
    )
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


class SearchFlightView(ListView):
    model = Flight
    filterset_class = FlightFilter
    template_name = "flight/search.html"

    def get_filterset_class(self):
        return self.filterset_class

    def get_queryset(self):
        queryset = super().get_queryset()
        filterset = self.get_filterset_class()
        self.filterset = filterset(self.request.GET, queryset=queryset)
        return self.filterset.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class CreateTicketView(CustomerRequired, DetailView):
    model = Flight
    context_object_name = "flight"
    template_name = "flight/create.html"
    success_url = reverse_lazy("flight:list_ticket")
    success_message = "Ticket has been booked Successfully "

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        customer_ticket = Ticket.objects.filter(customer__user=request.user, flight=obj)
        if customer_ticket.exists():
            messages.error(request, "You have already booked this ticket")
            return redirect("flight:search_flight")
        return super(CreateTicketView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user = request.user
        customer = Customer.objects.get(user=user)
        customer.credit_card = request.POST.get('credit_card')
        customer.save()

        flight = self.get_object()
        count = flight.ticket_set.count()
        if flight.num_of_tickets > count:
            Ticket.objects.create(
                customer=user.customer,
                flight=flight
            )
            success_message = self.get_success_message()
            messages.success(self.request, success_message)
        else:
            messages.error(request, "Number of tickets exceed the limit")
            return redirect("flight:search_flight")

        return redirect(self.success_url)

    def get_success_message(self):
        return self.success_message


class UpdateTicketStatusView(CustomerRequired, UpdateView):
    model = Ticket
    form_class = TicketStatusUpdateForm
    template_name = "flight/update.html"
    success_url = reverse_lazy("flight:list_ticket")
    success_message = "Ticket has been updated successfully"
    extra_context = {
        "title": "Update Ticket"
    }


class TicketListView(CustomerRequired, ListView):
    model = Ticket
    context_object_name = "tickets"
    template_name = "flight/list.html"

    def get_queryset(self):
        return self.model.objects.filter(customer=self.request.user.customer)
