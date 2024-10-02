from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RecordSerializer
from .models import Record
import csv
import io

class ReconciliationView(APIView):
    def post(self, request):
        print(request.FILES)
        source_file = request.FILES.get('source_file')
        target_file = request.FILES.get('target_file')

        if not source_file or not target_file:
            return Response({'error': 'Both source_file and target_file are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Clear previous records (optional)
        Record.objects.all().delete()

        # Process and save source data
        source_errors = self.process_csv_file(source_file, 'source')
        # Process and save target data
        target_errors = self.process_csv_file(target_file, 'target')

        if source_errors or target_errors:
            return Response({'error': 'Invalid CSV data.'}, status=status.HTTP_400_BAD_REQUEST)

        # Perform reconciliation
        missing_in_target, missing_in_source, discrepancies = self.reconcile_records()

        # Generate report
        report_format = request.query_params.get('format', 'json')
        return self.generate_report(missing_in_target, missing_in_source, discrepancies, report_format)

    def process_csv_file(self, file, source_label):
        """Reads CSV file, normalizes data, and saves records to the database."""
        try:
            file_data = file.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(file_data))
        except Exception as e:
            return str(e)

        for row in reader:
            normalized_row = self.normalize_data(row)
            serializer = RecordSerializer(data={
                'source': source_label,
                'record_id': normalized_row['ID'],
                'name': normalized_row['Name'],
                'date': normalized_row['Date'],
                'amount': normalized_row['Amount'],
            })
            if serializer.is_valid():
                serializer.save()
            else:
                return serializer.errors
        return None

    def normalize_data(self, row):
        """Normalize data (e.g., trim spaces, standardize cases, parse dates)."""
        normalized_row = {
            'ID': int(row['ID'].strip()),
            'Name': row['Name'].strip(),
            'Date': row['Date'].strip(),
            'Amount': float(row['Amount'].strip()),
        }
        return normalized_row

    def reconcile_records(self):
        """Perform reconciliation between source and target records."""
        source_records = Record.objects.filter(source='source')
        target_records = Record.objects.filter(source='target')

        source_ids = set(source_records.values_list('record_id', flat=True))
        target_ids = set(target_records.values_list('record_id', flat=True))

        # Missing records
        missing_in_target_ids = source_ids - target_ids
        missing_in_source_ids = target_ids - source_ids

        missing_in_target = source_records.filter(record_id__in=missing_in_target_ids)
        missing_in_source = target_records.filter(record_id__in=missing_in_source_ids)

        # Discrepancies in common records
        common_ids = source_ids & target_ids
        discrepancies = []

        for record_id in common_ids:
            source_record = source_records.get(record_id=record_id)
            target_record = target_records.get(record_id=record_id)

            differences = {}
            if source_record.name != target_record.name:
                differences['name'] = (source_record.name, target_record.name)
            if source_record.date != target_record.date:
                differences['date'] = (source_record.date, target_record.date)
            if source_record.amount != target_record.amount:
                differences['amount'] = (source_record.amount, target_record.amount)

            if differences:
                discrepancies.append({
                    'record_id': record_id,
                    'differences': differences
                })

        return missing_in_target, missing_in_source, discrepancies

    def generate_report(self, missing_in_target, missing_in_source, discrepancies, report_format):
        """Generate reconciliation report in the desired format."""
        if report_format == 'csv':
            return self.generate_csv_report(missing_in_target, missing_in_source, discrepancies)
        elif report_format == 'html':
            return self.generate_html_report(missing_in_target, missing_in_source, discrepancies)
        else:
            # Default to JSON
            missing_in_target_data = RecordSerializer(missing_in_target, many=True).data
            missing_in_source_data = RecordSerializer(missing_in_source, many=True).data
            return Response({
                'missing_in_target': missing_in_target_data,
                'missing_in_source': missing_in_source_data,
                'discrepancies': discrepancies
            })

    def generate_csv_report(self, missing_in_target, missing_in_source, discrepancies):
        """Generate CSV report."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Missing in Target
        writer.writerow(['Missing in Target'])
        writer.writerow(['ID', 'Name', 'Date', 'Amount'])
        for record in missing_in_target:
            writer.writerow([record.record_id, record.name, record.date, record.amount])

        # Missing in Source
        writer.writerow([])
        writer.writerow(['Missing in Source'])
        writer.writerow(['ID', 'Name', 'Date', 'Amount'])
        for record in missing_in_source:
            writer.writerow([record.record_id, record.name, record.date, record.amount])

        # Discrepancies
        writer.writerow([])
        writer.writerow(['Discrepancies'])
        writer.writerow(['Record ID', 'Differences'])
        for discrepancy in discrepancies:
            writer.writerow([discrepancy['record_id'], discrepancy['differences']])

        response = Response(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reconciliation_report.csv"'
        return response

    def generate_html_report(self, missing_in_target, missing_in_source, discrepancies):
        """Generate HTML report."""
        html_content = '<h1>Reconciliation Report</h1>'

        # Missing in Target
        html_content += '<h2>Records Missing in Target</h2><ul>'
        for record in missing_in_target:
            html_content += f"<li>ID: {record.record_id}, Name: {record.name}, Date: {record.date}, Amount: {record.amount}</li>"
        html_content += '</ul>'

        # Missing in Source
        html_content += '<h2>Records Missing in Source</h2><ul>'
        for record in missing_in_source:
            html_content += f"<li>ID: {record.record_id}, Name: {record.name}, Date: {record.date}, Amount: {record.amount}</li>"
        html_content += '</ul>'

        # Discrepancies
        html_content += '<h2>Records with Discrepancies</h2><ul>'
        for discrepancy in discrepancies:
            differences = discrepancy['differences']
            diff_str = ', '.join([f"{field}: {values[0]} vs {values[1]}" for field, values in differences.items()])
            html_content += f"<li>Record ID {discrepancy['record_id']}: {diff_str}</li>"
        html_content += '</ul>'

        return Response(html_content, content_type='text/html')

