from django import forms

from .models import Country, Company, Flight, Ticket


class UpdateAirlineForm(forms.ModelForm):

    class Meta:
        model = Company
        fields = ('name', 'country')


class AddFlightForm(forms.ModelForm):

    class Meta:
        model = Flight
        fields = ('company', 'origin', 'destination', 'departure_time', 'landing_time', 'num_of_tickets')
