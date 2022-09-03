from datetime import datetime, timedelta

from django.db import models
from django.utils import timezone


class CompanyManager(models.Manager):

    def get_airline_by_username(self, username: str):
        return self.filter(manager__uername=username)

    def ge_airlines_by_country(self, country_id: int):
        return self.filter(country__id=country_id)

    def get_airline_by_parameters(self, country_name: str):
        return self.filter(name__icontains=country_name)


class FlightManager(models.Manager):

    def get_flights_by_parameters(self, origin_country_id: int, destination_country_id: int, date: datetime):
        return self.filter(origin__id=origin_country_id, destination__id=destination_country_id, departure_time__date=date)

    def get_flights_by_airline_id(self, airline_id: int):
        return self.filter(company__id=airline_id)

    def get_arrival_flights(self, country_id: int):
        data = timezone.now()
        landing = data + timedelta(hours=12)
        return self.filter(country__id=country_id, landing_time__gte=data, landing_time___lte=landing)

    def get_departure_flights(self, country_id: int):
        data = timezone.now()
        landing = data + timedelta(hours=12)
        return self.filter(country__id=country_id, departure_time__gte=data, departure_time___lte=landing)

    def get_flights_by_origin_country_id(self, country_id: int):
        return self.filter(origin__id=country_id)

    def get_flights_by_destination_country_id(self, country_id: int):
        return self.filter(destination__id=country_id)

    def get_flights_by_departure_date(self, date: datetime):
        return self.filter(departure_time__date=date)

    def get_flights_by_landing_date(self, date: datetime):
        return self.filter(landing_time__date=date)

    def get_flights_by_customer(self, customer):
        return self.filter(flight__customer=customer)

    def available(self):
        data = timezone.now()
        return self.filter(departure_time__gte=data)


class TicketsManager(models.Manager):

    def get_tickets_by_customer(self, customer_id: int):
        return self.filter(customer__id=customer_id)
