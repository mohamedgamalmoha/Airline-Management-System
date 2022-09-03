from django import forms
import django_filters

from .models import Ticket, Flight, TicketStatus


class CreateTicketForm(forms.ModelForm):

    class Meta:
        model = Ticket
        fields = "__all__"


class FlightFilter(django_filters.FilterSet):
    price__gt = django_filters.NumberFilter(field_name='price', lookup_expr='gt')
    price__lt = django_filters.NumberFilter(field_name='price', lookup_expr='lt')

    class Meta:
        model = Flight
        fields = ('company', 'origin', 'destination', 'price', 'departure_time', 'landing_time')


class TicketStatusUpdateForm(forms.ModelForm):
    # status = forms.ChoiceField(choices=TicketStatus.choices, required=True)

    class Meta:
        model = Ticket
        fields = ('status', )
