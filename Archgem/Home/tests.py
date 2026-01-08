from django.test import TestCase

class HomeTests(TestCase):
    def test_search_page_status_code(self):
        response = self.client.get('/Home/Search/')
        self.assertEqual(response.status_code, 200)
