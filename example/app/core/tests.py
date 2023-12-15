from django.test import Client, TestCase
from django.urls import reverse


class ExampleTestCase(TestCase):
    client = Client()

    def test_first_page(self):
        response = self.client.get(reverse("home_page"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('<div class="comments-container">', str(response.content))

    def test_second_page(self):
        response = self.client.get(reverse("second_page"))
        self.assertEqual(response.status_code, 200)
        self.assertIn('<div class="comments-container">', str(response.content))
