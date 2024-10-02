from django.urls import path
from .views import ReconciliationView


urlpatterns = [
    path('reconcile/', ReconciliationView.as_view(), name='reconcile'),
]
