from django.test import TestCase

class LoginTests(TestCase):
    def test_login_page_status_code(self):
        response = self.client.get('/Login/')
        self.assertEqual(response.status_code, 200)
