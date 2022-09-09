from django.db import models
from django.urls import reverse
from django.core.validators import ValidationError, MinValueValidator

from accounts.models import User, Customer
from .managers import CompanyManager, FlightManager, TicketsManager


class TicketStatus(models.TextChoices):
    Booked = "Booked", "Booked"
    Canceled = "Canceled", "Canceled"


class Country(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Countries'
        verbose_name_plural = 'Countries'

    def __str__(self):
        return self.name

    def get_single_api_absolut_url(self):
        return reverse('flight:country_by_id', args=[self.id, ])

    def get_all_api_absolut_url(self):
        return reverse('flight:all_countries')


class Company(models.Model):
    name = models.CharField(max_length=200)
    country = models.ForeignKey(Country,  on_delete=models.SET_NULL, null=True)
    manager = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, unique=True, related_name='manager')

    objects = CompanyManager()

    class Meta:
        verbose_name = 'Companies'
        verbose_name_plural = 'Companies'

    def __str__(self):
        return self.name

    def get_single_api_absolut_url(self):
        return reverse('flight:airline_by_id', args=[self.id, ])

    def get_all_api_absolut_url(self):
        return reverse('flight:all_airlines')


class Flight(models.Model):
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True)

    origin = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, related_name='origin')
    destination = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, related_name='destination')

    departure_time = models.DateTimeField()
    landing_time = models.DateTimeField()

    price = models.DecimalField(null=True, decimal_places=2, max_digits=10)
    num_of_tickets = models.PositiveIntegerField(validators=[MinValueValidator(1), ])

    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now_add=True)

    objects = FlightManager()

    def __str__(self):
        return f"From {self.origin.name} to {self.destination.name}"

    class Meta:
        verbose_name = 'Flights'
        verbose_name_plural = 'Flights'

    def save(self, *args, **kwargs):
        if self.num_of_tickets < 1:
            raise ValidationError('Number of tickets cant be negative')
        if self.origin == self.destination:
            raise ValidationError('Origin country cant be same as destination country')
        if self.departure_time >= self.landing_time:
            raise ValidationError('Departure time must be less than landing time')
        super(Flight, self).save(*args, **kwargs)

    def get_single_api_absolut_url(self):
        return reverse('flight:flight_by_id', args=[self.id, ])

    def get_all_api_absolut_url(self):
        return reverse('flight:all_flights')

    def count_receive_rickets(self):
        return Ticket.objects.filter(flight=self).count()

    count_receive_rickets.short_description = 'Received tickets'


class Ticket(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.SET_NULL, null=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, related_name="tickets")
    status = models.CharField(max_length=50, choices=TicketStatus.choices, default=TicketStatus.Booked)

    objects = TicketsManager()

    class Meta:
        verbose_name = 'Tickets'
        verbose_name_plural = 'Tickets'
        unique_together = ('flight', 'customer')

    def save(self, *args, **kwargs):
        max_num_tickets = self.flight.num_of_tickets
        current_num_tickets = Ticket.objects.filter(flight=self.flight).count()
        if current_num_tickets + 1 > max_num_tickets:
            raise ValidationError('Max number of tickets has been reached')
        super(Ticket, self).save(*args, **kwargs)

    # def get_single_api_absolut_url(self):
    #     return reverse('flight:flight_by_id', args=[self.id, ])
    #
    # def get_all_api_absolut_url(self):
    #     return reverse('flight:all_flights')
