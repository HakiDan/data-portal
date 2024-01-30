from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from apps.upload.models import AgencyList
from core.choices import STATUS, STATUS_VAL

private_storage = FileSystemStorage(location=settings.PRIVATE_STORAGE_ROOT_MASTERLIST)

class FileMasterlist(models.Model):
    Fail = models.FileField(storage=private_storage, validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls', 'csv'])])
    
    def __str__ (self):
        return str(self.Fail)

class Validation(models.Model):
    reporting_date = models.DateTimeField(null=True, blank=True)
    agency = models.CharField(max_length=50, null=True, blank=True)
    init_id = models.CharField(max_length=15, null=True, blank=True)
    init_name = models.CharField(max_length=1000, null=True, blank=True)
    bene_last_month = models.IntegerField(null=True, blank=True)
    bene_this_month = models.IntegerField(null=True, blank=True)
    disb_last_month = models.FloatField(null=True, blank=True)
    disb_this_month = models.FloatField(null=True, blank=True)
    applied_amount = models.FloatField(null=True, blank=True)
    approved_amount = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=100, choices=STATUS, null=True, blank=True)
    failed_reason_user =  models.CharField(max_length=1000, null=True, blank=True)
    edit_note_by = models.CharField(max_length=100, null=True, blank=True)
    date_modified_note = models.DateTimeField(null=True, blank=True)
    is_validate = models.CharField(max_length=100, choices=STATUS_VAL, null=True, blank=True)
    is_push = models.BooleanField(default=False, null=True, blank=True)
    cur_note = models.TextField(null=True, blank=True)
    validate_by = models.CharField(max_length=200, null=True, blank=True)
    push_by = models.CharField(max_length=200, null=True, blank=True)
    validation_date = models.DateTimeField(null=True, blank=True)
    push_date = models.DateTimeField(null=True, blank=True)
    date_modified = models.DateTimeField(null=True, blank=True)
            
    class Meta:
        verbose_name = "Validation"
        verbose_name_plural = "Validation"

class Note(models.Model):
    date_modified = models.DateTimeField(null=True, blank=True)
    note_assc_id = models.CharField(max_length=15, blank=True, null=True)
    note_assc_name = models.CharField(max_length=500, blank=True, null=True)
    editor = models.CharField(max_length=200, blank=True, null=True)
    text_note = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Validation note"
        verbose_name_plural = "Validation notes"
