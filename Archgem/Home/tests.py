from django.test import TestCase

from django.contrib.auth.models import User
import json

from Home.models import Gem

class HomeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        # Create a test gem
        self.gem = Gem.objects.create(
            name="Test Gem",
            latitude=10.0,
            longitude=10.0,
            description="A test gem"
        )

    def test_search_page_status_code(self):
        self.client.force_login(self.user)
        # The view expects a JSON body
        response = self.client.post(
            '/Home/Search/',
            json.dumps({'centerLat': 10.0, 'centerLong': 10.0, 'spanDeltaLat': 1.0, 'spanDeltaLong': 1.0}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # Verify response content
        data = response.json()
        self.assertIn('gems', data)
        self.assertTrue(len(data['gems']) > 0)
        self.assertEqual(data['gems'][0]['name'], "Test Gem")
