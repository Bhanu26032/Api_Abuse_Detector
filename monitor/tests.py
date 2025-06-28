from django.test import TestCase

# Create your tests here.

from django.test import TestCase
from django.urls import reverse

class MonitorUrlsTest(TestCase):
    def test_home_url(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_logs_url(self):
        url = reverse('logs')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_dashboard_url(self):
        url = reverse('dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_settings_url(self):
        url = reverse('settings')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_register_url(self):
        url = reverse('register')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_login_url(self):
        url = reverse('login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_logout_url(self):
        url = reverse('logout')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_sso_login_url(self):
        url = reverse('sso_login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    # Optional: Test proxy URLs if needed
    def test_proxy_url(self):
        url = reverse('proxy')
        response = self.client.get(url)
        # Adjust status code if your view returns a redirect or different response
        self.assertIn(response.status_code, [200, 302, 404])

    def test_proxy_path_url(self):
        url = reverse('proxy_path', kwargs={'path': 'test/path'})
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 302, 404])
