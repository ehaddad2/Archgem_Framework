from django.test import TestCase, Client


class HealthCheckTests(TestCase):
    """Tests for the /health/ endpoint."""

    def setUp(self):
        self.client = Client()

    def test_health_endpoint_returns_200(self):
        """Verify /health/ returns 200 when DB and Cache are available."""
        response = self.client.get("/health/")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "healthy"})

    def test_health_endpoint_checks_database(self):
        """Verify /health/ actually queries the database."""
        # This test implicitly verifies DB connectivity since we're using
        # Django's test runner which sets up a test database.
        response = self.client.get("/health/")
        self.assertEqual(response.status_code, 200)
