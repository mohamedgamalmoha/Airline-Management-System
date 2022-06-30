import json
import datetime
import warnings

from django.urls import reverse
from django.test import TestCase, Client
from django.utils.dateparse import parse_datetime
from django.core.validators import ValidationError

from .models import Country, Company, Flight, Ticket
from accounts.tests import BaseTest as AccountsBaseTest
from accounts.models import User, Token, UserRole, Administrator, Customer


warnings.filterwarnings("ignore")


def parse_time_with_replace(t):
    if isinstance(t, str):
        t = parse_datetime(t)
    return t.replace(second=0, microsecond=0)


def parse_str_time(lst):
    for index, dct in enumerate(lst):
        dct.update({'departure_time': parse_time_with_replace(dct.get("departure_time")),
                    'landing_time': parse_time_with_replace(dct.get("landing_time")),
                    'created': parse_time_with_replace(dct.get("created")),
                    'modified': parse_time_with_replace(dct.get("modified"))})
        lst[index] = dct
    return lst


class BaseTest(AccountsBaseTest):

    def setUp(self):
        super().setUp()

        today = datetime.datetime.today()
        tomorrow = today + datetime.timedelta(days=1)

        Country.objects.create(name="Egypt")
        Country.objects.create(name="Morocco")

        Company.objects.create(name="First Airline", country=Country.objects.first(),
                               manager=User.objects.get(username="admin"))

        Flight.objects.create(company=Company.objects.first(),  departure_time=today, landing_time=tomorrow,
                              origin=Country.objects.get(name="Egypt"), destination=Country.objects.get(name="Morocco"),
                              num_of_tickets=10)
        Flight.objects.create(company=Company.objects.first(), departure_time=today, landing_time=tomorrow,
                              origin=Country.objects.get(name="Morocco"), destination=Country.objects.get(name="Egypt"),
                              num_of_tickets=10)


class AnonymousFacadesTest(BaseTest):

    def test_get_all_flights(self):
        client = Client()
        response = client.post(reverse('flight:all_flights'), HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)

    def test_get_flight_by_id(self):
        client = Client()
        response = client.post(reverse('flight:flight_by_id', kwargs={'flight_id': 1}), HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)

    def test_get_flights_by_parameters(self):
        client = Client()
        today = datetime.datetime.today().isoformat()
        kwargs = {'origin_country_id': 1, 'destination_country_id': 2, 'date': today}
        response = client.post(reverse('flight:flight_by_parameters', kwargs=kwargs), HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)

    def test_get_all_airlines(self):
        client = Client()
        response = client.post(reverse('flight:all_airlines'), HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)

    def test_get_airline_by_id(self):
        client = Client()
        response = client.post(reverse('flight:airline_by_id', kwargs={'airline_id': 1}), HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)

    def test_get_airline_by_parameters(self):
        client = Client()
        response = client.post(reverse('flight:airline_by_parameters', kwargs={'company_name': 'First Airline'}),
                               HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)

    def test_get_all_countries(self):
        client = Client()
        response = client.post(reverse('flight:all_countries'), HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)

    def test_get_country_by_id(self):
        client = Client()
        response = client.post(reverse('flight:country_by_id', kwargs={'country_id': 1}), HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)


class CompanyTest(BaseTest):

    def setUp(self):
        super().setUp()
        User.objects.create(username="company_owner", password="company_owner123", email="company_owner@gmail.com",
                            role=UserRole.objects.get(name="admin"))
        Administrator.objects.create(user=User.objects.get(username="company_owner"), first_name="owner_1",
                                     last_name="owner_2")

    def test_company_creation(self):
        Company.objects.all().delete()
        user_token = Token.objects.get(user__username="admin")

        client = Client()
        params = {
            'name': 'First Airline',
            'country': Country.objects.first().id,
            'manager':  User.objects.get(username="company_owner").username,
            'token': user_token.name
        }

        # First Case - data is correct - (Success)
        response = client.post(reverse('flight:add_airline'), params, HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)

        # Second Case - data is incorrect / the country doesn't exist - (Fail)
        params2 = params.copy()
        params2.update({'country': 5})
        response = client.post(reverse('flight:add_airline'), params2, HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 404)

        # Third Case - data is incorrect / the manager doesn't exist - (Fail)
        params3 = params.copy()
        params3.update({'manager': 'any'})
        response = client.post(reverse('flight:add_airline'), params3, HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 404)

    def test_company_removal(self):
        user_token = Token.objects.get(user__username="admin")

        client = Client()
        params = {'token': user_token.name}

        # First Case - the company id exists - (Success)
        response = client.post(reverse('flight:remove_airline', kwargs={'airline': 1}), params,
                               HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)

        # First Case - the company id doesn't  exist - (Fail)
        response = client.post(reverse('flight:remove_airline', kwargs={'airline': 1}), params,
                               HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 404)

    def test_company_update(self):
        user_token = Token.objects.get(user__username="admin")

        client = Client()
        params = {'token': user_token.name, 'country': 1}

        # First Case - the company id exists & data is valid - (Success)
        response = client.post(reverse('flight:update_airline', kwargs={'airline': 1}), params,
                               HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)

        # Second Case - the company id exists & data is not valid- (Fail)
        params2 = params.copy()
        params2.update({'country': 5})
        response = client.post(reverse('flight:update_airline', kwargs={'airline': 1}), params2, HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 404)

        # Third Case - the company id is not exists - (Fail)
        response = client.post(reverse('flight:update_airline', kwargs={'airline': 3}), params,
                               HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 404)


class FlightTest(BaseTest):

    def test_flight_retrieval(self):
        user_token = Token.objects.get(user__username="admin")
        flights = parse_str_time(list(Flight.objects.filter(company__manager=user_token.user).values()))

        client = Client()
        response = client.get(reverse('flight:own_flights'), {'token': user_token.name}, HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.json())
        data = parse_str_time(data)
        for i, j in zip(data, flights):
            self.assertEqual(i, j)

    def test_flight_creation(self):
        today = datetime.datetime.today()
        tomorrow = today + datetime.timedelta(days=1)
        egypt = Country.objects.get(name='Egypt')
        morocco = Country.objects.get(name='Morocco')
        user_token = Token.objects.get(user__username="admin")

        client = Client()
        params = {'token': user_token.name, 'origin': egypt.id, 'destination': morocco.id,  'departure_time': today,
                  'landing_time': tomorrow, 'num_of_tickets': 10}

        # First Case - all data is true - (Success)
        response = client.post(reverse('flight:add_flight'), params, HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)

        # Second Case - number of tickets is negative - (Fail)
        params2 = params.copy()
        params2.update({'num_of_tickets': -10})
        with self.assertRaises(ValidationError):
            client.post(reverse('flight:add_flight'), params2, HTTP_ACCEPT='application/json')

        # Third Case - the origin is same as destination - (Fail)
        params3 = params.copy()
        params3.update({'origin': egypt.id, 'destination': egypt.id})
        with self.assertRaises(ValidationError):
            client.post(reverse('flight:add_flight'), params3, HTTP_ACCEPT='application/json')

        # Fourth Case - the landing time is less than or equal to  departure time -
        params4 = params.copy()
        params4.update({'departure_time': today, 'landing_time': today})
        with self.assertRaises(ValidationError):
            client.post(reverse('flight:add_flight'), params4, HTTP_ACCEPT='application/json')

    def test_flight_removal(self):
        user_token = Token.objects.get(user__username="admin")

        client = Client()
        params = {'token': user_token.name}

        # First Case - the flight id exists - (Success)
        response = client.post(reverse('flight:remove_flight', kwargs={'flight': 1}), params, HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)

        # First Case - the flight id doesn't  exist - (Fail)
        response = client.post(reverse('flight:remove_flight', kwargs={'flight': 3}), params, HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 404)

    def test_flight_update(self):
        user_token = Token.objects.get(user__username="admin")

        client = Client()
        params = {'token': user_token.name,  'num_of_tickets': 15}

        # First Case - the flight id exists & data is valid- (Success)
        response = client.post(reverse('flight:update_flight', kwargs={'flight': 1}), params, HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)

        # Second Case - the flight id exists & data is not valid- (Fail)
        params2 = params.copy()
        params2.update({'num_of_tickets': -15})
        with self.assertRaises(ValidationError):
            client.post(reverse('flight:update_flight', kwargs={'flight': 2}), params2, HTTP_ACCEPT='application/json')

        # Third Case - the flight id is not exists - (Fail)
        response = client.post(reverse('flight:update_flight', kwargs={'flight': 3}), params,
                               HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 404)


class TicketTest(BaseTest):

    def setUp(self):
        super().setUp()
        today = datetime.datetime.today()
        tomorrow = today + datetime.timedelta(days=1)

        Country.objects.create(name="Sudan")
        Flight.objects.create(company=Company.objects.first(), departure_time=today, landing_time=tomorrow,
                              origin=Country.objects.get(name="Morocco"), destination=Country.objects.get(name="Sudan"),
                              num_of_tickets=10)

        Flight.objects.filter(id=2).update(num_of_tickets=1)

        Ticket.objects.create(customer=Customer.objects.get(user__username="customer"), flight=Flight.objects.first())
        Ticket.objects.create(customer=Customer.objects.get(user__username="customer"), flight=Flight.objects.last())

    def test_ticket_creation(self):
        customer = Customer.objects.get(user__username="customer")
        customer_token = Token.objects.get(user=customer.user)
        flight = Flight.objects.get(id=2)

        client = Client()
        params = {
            'token': customer_token.name,
            'flight': flight.id,
            'customer': customer.id
        }

        # First Case - all data is true - (Success)
        response = client.post(reverse('flight:add_ticket'), params, HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)

        # Second Case - data is incorrect - (Fail)
        params2 = params.copy()
        params2.update({'customer': 4})
        response = client.post(reverse('flight:add_ticket'), params2, HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 404)

        # Third Case - data is correct & num of tickets exceeds its limit - (Fail)
        with self.assertRaises(ValidationError):
            client.post(reverse('flight:add_ticket'), params, HTTP_ACCEPT='application/json')

    def test_ticket_retrieval(self):
        customer = Customer.objects.get(user__username="customer")
        customer_token = Token.objects.get(user=customer.user)
        tickets = list(Ticket.objects.filter(customer=customer).values())

        client = Client()
        params = {
            'token': customer_token.name,
        }

        response = client.get(reverse('flight:own_tickets'), params, HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.json())
        for i, j in zip(data, tickets):
            self.assertEqual(i, j)

    def test_ticket_removal(self):
        customer = Customer.objects.get(user__username="customer")
        customer_token = Token.objects.get(user=customer.user)

        client = Client()
        params = {'token': customer_token.name}

        # First Case - the flight id exists - (Success)
        response = client.post(reverse('flight:remove_ticket', kwargs={'ticket_id': 1}), params, HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)

        # First Case - the flight id doesn't  exist - (Fail)
        response = client.post(reverse('flight:remove_ticket', kwargs={'ticket_id': 3}), params, HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 404)

        # Third Case - the flight id exists & ticket doesn't belong to same customer - (Fail)
        user = User.objects.create(username="customer_new", password="customer_new123", email="customer_new@gmail.com",
                                   role=UserRole.objects.get(name="customer"))
        customer = Customer.objects.create(user=user, first_name="customer_new_1", last_name="customer_new_2",
                                           address="2end street", phone_number="1234556891",
                                           credit_card="123456784523456")
        ticket = Ticket.objects.create(customer=customer, flight=Flight.objects.first())

        response = client.post(reverse('flight:remove_ticket', kwargs={'ticket_id': ticket.id}), params, HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 403)
