from datetime import timedelta

from django.apps import apps
from django.utils import timezone
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand, CommandError


# Accounts Models
User = apps.get_model("accounts", "User")
Token = apps.get_model("accounts", "Token")
UserRole = apps.get_model("accounts", "UserRole")
Customer = apps.get_model("accounts", "Customer")
Administrator = apps.get_model("accounts", "Administrator")

# Flight Models
Country = apps.get_model("flight", "Country")
Company = apps.get_model("flight", "Company")
Flight = apps.get_model("flight", "Flight")
Ticket = apps.get_model("flight", "Ticket")


class Command(BaseCommand):
    help = 'Upload Dummy Data To The DataBase'

    @staticmethod
    def default_data():
        today = timezone.now()
        tomorrow = today + timedelta(days=1)

        # Accounts Data
        UserRole.objects.create(name="admin")
        UserRole.objects.create(name="customer")

        User.objects.create(username="admin", password="admin123", email="admin@gmail.com",
                            role=UserRole.objects.get(name="admin"))
        Administrator.objects.create(user=User.objects.get(username="admin"), first_name="admin_1", last_name="admin_2")

        User.objects.create(username="customer", password="customer123", email="customer@gmail.com",
                            role=UserRole.objects.get(name="customer"))
        Customer.objects.create(user=User.objects.get(username="customer"), first_name="customer_1",
                                last_name="customer_2", address="2end street", phone_number="1234556891",
                                credit_card="123456784523456")

        Token.objects.create(user=User.objects.get(username="admin"))
        Token.objects.create(user=User.objects.get(username="customer"))

        # Flight Data
        Country.objects.create(name="Egypt")
        Country.objects.create(name="Sudan")
        Country.objects.create(name="Morocco")

        Company.objects.create(name="First Airline", country=Country.objects.first(),
                               manager=User.objects.get(username="admin"))

        Flight.objects.create(company=Company.objects.first(), departure_time=today, landing_time=tomorrow,
                              origin=Country.objects.get(name="Egypt"), destination=Country.objects.get(name="Morocco"),
                              num_of_tickets=10)
        Flight.objects.create(company=Company.objects.first(), departure_time=today, landing_time=tomorrow,
                              origin=Country.objects.get(name="Morocco"), destination=Country.objects.get(name="Egypt"),
                              num_of_tickets=10)
        Flight.objects.create(company=Company.objects.first(), departure_time=today, landing_time=tomorrow,
                              origin=Country.objects.get(name="Morocco"), destination=Country.objects.get(name="Sudan"),
                              num_of_tickets=10)

        Ticket.objects.create(customer=Customer.objects.get(user__username="customer"), flight=Flight.objects.first())
        Ticket.objects.create(customer=Customer.objects.get(user__username="customer"), flight=Flight.objects.last())

    def handle(self, *args, **kwargs):
        self.stdout.write("Uploading data ....")
        try:
            self.default_data()
            self.stdout.write(self.style.SUCCESS("Uploading Is Done Successfully !!"))
        except OperationalError:
            raise CommandError(f"Creating Failed, try first to run migrations then migrate")
        except Exception as e:
            raise CommandError(f"Uploading Failed Due To: {e}")
