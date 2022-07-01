from django.db.utils import OperationalError
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


User = get_user_model()


class Command(BaseCommand):
    help = "Creating default super user"

    def add_arguments(self, parser):
        parser.add_argument('-u', '--username', default='admin', type=str, help='The username of the account')
        parser.add_argument('-e', '--email', default='admin@gmail.com', type=str, help='The email of the account')
        parser.add_argument('-p', '--password', default='admin',  type=str, help='The password of the account')

    def handle(self, *args, **kwargs):
        username = kwargs.get('username')
        email = kwargs.get('email')
        password = kwargs.get('password')

        self.stdout.write("Creating SuperUser Account ....")
        try:
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS("Creating Account Is Done Successfully !!"))
        except OperationalError:
            raise CommandError(f"Creating Failed, try first to run migrations then migrate")
        except Exception as e:
            raise CommandError(f"Creating Failed Due To: {e}")
