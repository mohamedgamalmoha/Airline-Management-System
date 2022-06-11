from rest_framework import serializers

from .models import Country, Company, Flight, Ticket


class UpdateAirlineSerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = ('name', 'country')


class AddFlightSerializer(serializers.ModelSerializer):

    class Meta:
        model = Flight
        fields = ('company', 'origin', 'destination', 'departure_time', 'landing_time', 'num_of_tickets')


class AddTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ('flight', )
