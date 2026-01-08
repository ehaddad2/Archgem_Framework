from django.test import TestCase

class LoginTests(TestCase):
    def test_login_page_get_method_not_allowed(self):
        # The view explicitly returns 405 for GET requests
        response = self.client.get('/Login/')
        self.assertEqual(response.status_code, 405)

    def test_login_page_post_invalid_creds(self):
        # POST with invalid credentials should return 401
        response = self.client.post(
            '/Login/',
            {'username': 'wrong', 'password': 'wrong'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)

    def test_login_success(self):
        from django.contrib.auth.models import User
        # Create a user
        User.objects.create_user(username='testuser', password='password')
        
        response = self.client.post(
            '/Login/',
            {'username': 'testuser', 'password': 'password'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('token', data)
