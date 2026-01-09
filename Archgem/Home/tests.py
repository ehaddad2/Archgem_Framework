from django.test import TestCase, Client
from django.contrib.auth.models import User
import json

from Home.models import Gem


class HomeTests(TestCase):
    """Tests for Home app endpoints."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        # Create a test gem
        self.gem = Gem.objects.create(
            name="Test Gem",
            latitude=10.0,
            longitude=10.0,
            description="A test gem"
        )

    def test_search_with_force_login(self):
        """Basic test: verify Search works when logged in."""
        self.client.force_login(self.user)
        response = self.client.post(
            '/Home/Search/',
            json.dumps({'centerLat': 10.0, 'centerLong': 10.0, 'spanDeltaLat': 1.0, 'spanDeltaLong': 1.0}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('gems', data)
        self.assertTrue(len(data['gems']) > 0)
        self.assertEqual(data['gems'][0]['name'], "Test Gem")


class EndToEndAuthFlowTests(TestCase):
    """
    E2E tests that simulate frontend behavior:
    1. GET / to grab CSRF token
    2. POST /Login/ with credentials
    3. POST /Home/Search/ with session
    """

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.user = User.objects.create_user(username='e2euser', password='e2epass123')
        # Create a test gem
        Gem.objects.create(
            name="E2E Gem",
            latitude=20.0,
            longitude=20.0,
            description="E2E test gem"
        )

    def test_full_auth_flow_csrf_login_search(self):
        """
        Simulate frontend flow:
        1. GET / to get CSRF token
        2. POST /Login/ with CSRF token + credentials
        3. POST /Home/Search/ with session cookie
        """
        # Step 1: GET / to obtain CSRF token
        init_response = self.client.get('/')
        self.assertEqual(init_response.status_code, 200)
        
        # Extract CSRF token from cookie
        csrf_token = self.client.cookies.get('csrftoken')
        self.assertIsNotNone(csrf_token, "CSRF cookie should be set after GET /")
        
        # Step 2: POST /Login/ with credentials + CSRF
        login_response = self.client.post(
            '/Login/',
            json.dumps({'username': 'e2euser', 'password': 'e2epass123'}),
            content_type='application/json',
            HTTP_X_CSRFTOKEN=csrf_token.value
        )
        self.assertEqual(login_response.status_code, 200)
        login_data = login_response.json()
        self.assertIn('token', login_data, "Login should return a token")
        
        # Step 3: POST /Home/Search/ with session (automatically maintained by Client)
        search_response = self.client.post(
            '/Home/Search/',
            json.dumps({'centerLat': 20.0, 'centerLong': 20.0, 'spanDeltaLat': 5.0, 'spanDeltaLong': 5.0}),
            content_type='application/json',
            HTTP_X_CSRFTOKEN=csrf_token.value
        )
        self.assertEqual(search_response.status_code, 200, 
                         f"Search should return 200, got {search_response.status_code}: {search_response.content}")
        
        search_data = search_response.json()
        self.assertIn('gems', search_data)
        self.assertTrue(len(search_data['gems']) > 0, "Should find the E2E gem")
        self.assertEqual(search_data['gems'][0]['name'], "E2E Gem")

    def test_search_without_login_fails(self):
        """Verify that Search fails with 302 redirect when not logged in."""
        # GET CSRF first
        self.client.get('/')
        csrf_token = self.client.cookies.get('csrftoken')
        
        # Try to search without logging in
        response = self.client.post(
            '/Home/Search/',
            json.dumps({'centerLat': 20.0, 'centerLong': 20.0, 'spanDeltaLat': 5.0, 'spanDeltaLong': 5.0}),
            content_type='application/json',
            HTTP_X_CSRFTOKEN=csrf_token.value
        )
        # @login_required redirects to login page (302) when not authenticated
        self.assertEqual(response.status_code, 302)

    def test_search_without_csrf_fails(self):
        """Verify that Search fails with 403 when CSRF token is missing."""
        # Login first (using force_login to bypass CSRF for login step)
        self.client.force_login(User.objects.get(username='e2euser'))
        
        # Try to search WITHOUT CSRF token
        response = self.client.post(
            '/Home/Search/',
            json.dumps({'centerLat': 20.0, 'centerLong': 20.0, 'spanDeltaLat': 5.0, 'spanDeltaLong': 5.0}),
            content_type='application/json'
            # No HTTP_X_CSRFTOKEN!
        )
        self.assertEqual(response.status_code, 403, "Should get 403 Forbidden without CSRF")
