from django.urls import reverse
from django.test import TestCase, Client

from .models import User, UserRole, Customer, Administrator, Token


class BaseTest(TestCase):
    def setUp(self):
        UserRole.objects.create(name="admin")
        UserRole.objects.create(name="customer")

        User.objects.create(username="admin", password="admin123", email="admin@gmail.com",
                            role=UserRole.objects.get(name="admin"))
        Administrator.objects.create(user=User.objects.get(username="admin"), first_name="admin_1", last_name="admin_2")

        User.objects.create(username="customer", password="customer123", email="customer@gmail.com",
                            role=UserRole.objects.get(name="customer"))
        Customer.objects.create(user=User.objects.get(username="customer"), first_name="customer_1",  last_name="customer_2",
                                address="2end street", phone_number="1234556891", credit_card="123456784523456")

        Token.objects.create(user=User.objects.get(username="admin"))
        Token.objects.create(user=User.objects.get(username="customer"))


class TokenTest(BaseTest):

    def test_token_creation(self):
        admin = User.objects.get(username="admin")
        customer = User.objects.get(username="customer")

        admin_token = Token.objects.get(user=admin)
        customer_token = Token.objects.get(user=customer)

        client = Client()

        admin_response = client.get(reverse('accounts:user_token'), {'username': admin.username, 'password': admin.password},
                                    HTTP_ACCEPT='application/json')
        self.assertEqual(admin_response.status_code, 200)
        self.assertEqual(admin_token.name, str(admin_response.json()['token']))

        customer_response = client.get(reverse('accounts:user_token'),
                                       {'username': customer.username, 'password': customer.password},
                                       HTTP_ACCEPT='application/json')
        self.assertEqual(customer_response.status_code, 200)
        self.assertEqual(customer_token.name, str(customer_response.json()['token']))
