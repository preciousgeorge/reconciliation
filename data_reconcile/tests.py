from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
import io

class ReconciliationTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.source_data = """ID,Name,Date,Amount
1,John Doe,2023-01-01,100
2,Jane Smith,2023-01-02,200.5
3,Robert Brown,2023-01-03,300.75
"""

        self.target_data = """ID,Name,Date,Amount
1,John Doe,2023-01-01,100
2,Jane Smith,2023-01-04,200.5
4,Emily White,2023-01-05,400.9
"""

    def test_reconciliation_json(self):
        source_file = io.StringIO(self.source_data)
        target_file = io.StringIO(self.target_data)

        data = {
            'source_file': source_file,
            'target_file': target_file,
        }

        response = self.client.post(reverse('reconcile') + '?format=json', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.json()
        self.assertEqual(len(response_data['missing_in_target']), 1)
        self.assertEqual(len(response_data['missing_in_source']), 1)
        self.assertEqual(len(response_data['discrepancies']), 1)

        # Check missing in target
        missing_in_target = response_data['missing_in_target'][0]
        self.assertEqual(missing_in_target['record_id'], 3)
        self.assertEqual(missing_in_target['name'], 'Robert Brown')

        # Check missing in source
        missing_in_source = response_data['missing_in_source'][0]
        self.assertEqual(missing_in_source['record_id'], 4)
        self.assertEqual(missing_in_source['name'], 'Emily White')

        # Check discrepancies
        discrepancy = response_data['discrepancies'][0]
        self.assertEqual(discrepancy['record_id'], 2)
        self.assertIn('date', discrepancy['differences'])
        self.assertEqual(discrepancy['differences']['date'][0], '2023-01-02')
        self.assertEqual(discrepancy['differences']['date'][1], '2023-01-04')
