from django.contrib import admin

from .models import Country, Company, Flight, Ticket


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'manager')


class TicketInlineAdmin(admin.TabularInline):
    model = Ticket
    readonly_fields = ('customer', )


class FlightAdmin(admin.ModelAdmin):
    list_display = ('company', 'origin', 'destination', 'departure_time', 'landing_time', 'num_of_tickets', 'price',
                    'count_receive_rickets')
    readonly_fields = ('count_receive_rickets', )
    search_fields = ('company__name', 'origin__name', 'destination__name')
    search_help_text = 'You can search by company name, origin country and destination country'
    list_per_page = 10
    list_filter = ('origin', 'destination')
    inlines = (TicketInlineAdmin, )


class TicketAdmin(admin.ModelAdmin):
    list_display = ('flight', 'customer', 'status')


admin.site.register(Country)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Flight, FlightAdmin)
admin.site.register(Ticket, TicketAdmin)
