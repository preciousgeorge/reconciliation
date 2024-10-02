Reconciliation Application
Overview
This Django-based application provides an API to reconcile two CSV files by comparing their data. The application is designed to accept two CSV files: a source file and a target file. It then checks for discrepancies between the two datasets, such as missing or differing records, and returns a reconciliation report in multiple formats (CSV, JSON, HTML).

Features
File Upload: Accepts two CSV files via a POST request.
Reconciliation Logic: Compares records in the source and target CSVs based on:
Records missing in the source or target.
Records present in both but with differences in certain fields.
Flexible Output: Returns the reconciliation result in CSV, JSON, or HTML format.
Error Handling: Handles missing or invalid files gracefully.
404 Handling: Only the /api/reconcile/ endpoint is accessible. All other URLs return a custom 404 page.
Endpoints
/api/reconcile/ (POST)
This is the main API endpoint for uploading the CSV files and receiving the reconciliation report.

Request:
bash
Copy code
curl -X POST http://127.0.0.1:8000/api/reconcile/ \
  -F "source_file=@/path/to/source.csv" \
  -F "target_file=@/path/to/target.csv"
source_file: The CSV file to use as the source.
target_file: The CSV file to use as the target.
Response:
The response will contain the reconciliation result in the requested format. For example:

CSV format: A downloadable CSV file with discrepancies.
JSON format: A JSON object with missing and differing records.
HTML format: A web page displaying the differences.
Example CSV Structure
Both the source and target CSV files should follow this structure:

csv
Copy code
ID,Name,Date,Amount
1,John Doe,2023-01-01,100
2,Jane Smith,2023-01-04,200.5
How the Reconciliation Works
Upload Two Files: The API accepts two CSV files (source and target).
Comparison: The application compares both files row-by-row based on the ID column.
If a record exists in the source but not the target, it is marked as missing from the target.
If a record exists in the target but not the source, it is marked as missing from the source.
If both source and target contain the same record but with differences (e.g., differing Amount), it is flagged as discrepant.
Report: The differences are returned in a report.
Setup
Prerequisites
Python 3.12 or higher
Django 4.x
Django REST Framework
Installation
Clone the Repository:

bash
Copy code
git clone git@github.com:preciousgeorge/reconciliation.git
cd reconciliation_project
Set Up a Virtual Environment:

bash
Copy code
python -m venv .env
source .env/bin/activate
Install Dependencies:

bash
Copy code
pip install -r requirements.txt
Run Migrations:

bash
Copy code
python manage.py migrate
Start the Development Server:

bash
Copy code
python manage.py runserver
Run Tests (Optional):

bash
Copy code
python manage.py test
File Structure
The project structure is as follows:

bash
Copy code
reconciliation_project/
├── reconciliation/
│   ├── views.py               # Logic for file reconciliation
│   ├── serializers.py         # Serializes the request data
│   ├── urls.py                # URL routing for the API
├── templates/
│   └── 404.html               # Custom 404 error page
├── reconciliation_project/
│   ├── settings.py            # Django settings
│   ├── urls.py                # Project-wide URL configuration
│   └── views.py               # Custom 404 view
API Error Handling
If one or both files are missing in the request, the API will respond with:

json
Copy code
{"error": "Both source_file and target_file are required."}
For any invalid URLs, a custom 404 page will be shown.

Customizing the Application
Changing the CSV Comparison Logic
If you need to customize how the records are compared (e.g., based on different fields), you can modify the logic in reconciliation/views.py under the ReconciliationView.

Adding More Formats
The application currently supports CSV, JSON, and HTML formats. You can add more formats by extending the view logic to handle additional content types.

Conclusion
This reconciliation app is designed to help with file comparison and data integrity checks. It can be customized to suit different reconciliation workflows or data formats. Feel free to extend and enhance its features as needed!
