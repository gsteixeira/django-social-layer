from django.test import TestCase, Client
from django.urls import reverse

# Create your tests here.
class ExampleTestCase(TestCase):
    client = Client()

    def test_first_page(self):
        response = self.client.get(reverse('home_page'))
        self.assertEqual(response.status_code, 200)

    def test_second_page(self):
        response = self.client.get(reverse('second_page'))
        self.assertEqual(response.status_code, 200)
