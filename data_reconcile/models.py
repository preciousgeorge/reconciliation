from django.db import models

class Record(models.Model):
    SOURCE_CHOICES = (
        ('source', 'Source'),
        ('target', 'Target'),
    )

    source = models.CharField(max_length=6, choices=SOURCE_CHOICES)
    record_id = models.IntegerField()
    name = models.CharField(max_length=100)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('source', 'record_id')

    def __str__(self):
        return f"{self.source.capitalize()} Record {self.record_id}: {self.name}"
