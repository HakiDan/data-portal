from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from core.choices import *
import datetime as dt

mainPath = settings.MAINPATH

# Create your models here.
private_storage = FileSystemStorage(location=settings.PRIVATE_STORAGE_ROOT)
private_storage_std_col = FileSystemStorage(location=settings.PRIVATE_STORAGE_ROOT_STANDARD_COL)

class FileTemplate(models.Model):
    template_name = models.CharField(max_length=200, blank=True, null=True)
    file_template = models.FileField(storage=private_storage_std_col)
    
    class Meta:
        verbose_name = "File template"
        verbose_name_plural = "File templates"
        
    def __str__(self):
        return self.template_name
    

class AgencyList(models.Model):
    agency_fullname = models.CharField(max_length=2000, blank=True, null=True)
    agency_abbr = models.CharField(max_length=100, blank=True, null=True)
    class Meta:
        ordering = ['agency_fullname']
        verbose_name = "Agency list"
        verbose_name_plural = "Agency lists"
    
    def __str__(self):
        return str(self.agency_fullname)
    
class MinistryList(models.Model):
    ministry_fullname = models.CharField(max_length=2000, blank=True, null=True)
    ministry_abbr = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        ordering = ['ministry_fullname']
        verbose_name = "Ministry list"
        verbose_name_plural = "Ministry lists"
    
    def __str__(self):
        return str(self.ministry_fullname)

class MasterlistCommonInfo(models.Model):
    fokus = models.CharField(max_length=10, blank=True, null=True)
    init_id = models.CharField(max_length=15, blank=True, null=True)
    sub_init_id = models.CharField(max_length=15, blank=True, null=True)
    init_name = models.CharField(max_length=1000, blank=True, null=True)
    subinit_name = models.CharField(max_length=1000, blank=True, null=True)
    allocation = models.FloatField(blank=True, null=True,
        help_text=(
            'In million (RM).'
        ),
    )
    fiscal = models.FloatField(blank=True, null=True,
        help_text=(
            'In million (RM).'
        ),
    )
    non_fiscal = models.FloatField(blank=True, null=True,
        help_text=(
            'In million (RM).'
        ),
    )
    ministry = models.ForeignKey(MinistryList, on_delete=models.CASCADE, blank=True, null=True)
    agency = models.ForeignKey(AgencyList, on_delete=models.CASCADE, blank=True, null=True)
    category = models.CharField(max_length=200, choices=CATEGORY, blank=True, null=True)
    status = models.CharField(max_length=100, choices=STATUS, blank=True, null=True)
    is_active = models.BooleanField(('active'), default=False,
        help_text=(
            'Determines whether the initiative is active or not.'
        ),
    )
    class Meta:
        abstract = True
    
class MasterlistBudget(MasterlistCommonInfo):
    stf = models.CharField(max_length=10, choices=STF, blank=True, null=True)
    stf_id = models.CharField(max_length=10, blank=True, null=True)
    category_nec = models.CharField(max_length=50, choices=CATEGORY_NEC, blank=True, null=True)
    category_id = models.CharField(max_length=10, blank=True, null=True)
    program = models.CharField(max_length=50, choices=PROGRAM, blank=True, null=True)
    program_code = models.CharField(max_length=50, choices=PROGRAM_CODE, blank=True, null=True)
    tekad = models.CharField(max_length=15, blank=True, null=True)
    ikhtiar = models.CharField(max_length=15, blank=True, null=True)
    sub_1 = models.IntegerField(blank=True, null=True)
    sub_2 = models.IntegerField(blank=True, null=True)
    nec_id = models.CharField(max_length=15, blank=True, null=True)
    target = models.FloatField(blank=True, null=True,
        help_text=(
            'In million (RM).'
        ),
    )
    sector = models.CharField(max_length=200, choices=SECTOR, blank=True, null=True)
    file_template = models.ForeignKey(FileTemplate, on_delete=models.CASCADE, blank=True, null=True,
        help_text=(
            'Data template for the initiative.'
        ),
    )
    cur_disb = models.FloatField(('disbursement'), blank=True, null=True,
        help_text=(
            'Current disbursement for this initiative in million (RM).'
        ),
    )
    cur_remark = models.CharField(('remark'), max_length=2000, blank=True, null=True,
        help_text=(
            'Current remark for this initiative.'
        ),
    )
    date_modified = models.DateTimeField(blank=True, null=True)
    modified_by = models.CharField(max_length=500, blank=True, null=True,
        help_text=(
            "PID username."
        ),
    )
    
    class Meta:
        verbose_name = "Masterlists & NECs"
        verbose_name_plural = "Masterlists & NECs"
        
    def __str__(self):
        return self.subinit_name
    
class MasterlistNBO(MasterlistCommonInfo):
    has_approved = models.BooleanField(('validate'), default=False,
        help_text=(
            'Determines whether the new initiative has been approved or not.'
        ),
    )
    
    class Meta:
        verbose_name = "NBOs"
        verbose_name_plural = "NBOs"
    
    def __str__(self):
        return self.subinit_name
    
class DQUser(models.Model):
    dq_user = models.CharField(('username'), max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.dq_user

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    validation_perm = models.BooleanField(('validation PIC'), default=False,
        help_text=(
            'Designates whether this user is the person in charge of validation or not.'
        ),
    )
    is_lead = models.BooleanField(('lead'), default=False,
        help_text=(
            'Designates whether this user should be treated as leader for their initiative.'
        ),
    )
    agency_name = models.ForeignKey(AgencyList, on_delete=models.CASCADE, blank=True, null=True)
    phone_number = models.CharField(('phone number'), max_length=50, blank=True, null=True)
    last_update_password = models.DateTimeField(('last update password'), blank=True, null=True)
    dq_name = models.ForeignKey(DQUser, on_delete=models.CASCADE, blank=True, null=True,
        help_text=(
            '*Only applicable for IAs.'
        ),
    )
    init_id_assc = models.ManyToManyField(MasterlistBudget, blank=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    
    
class LogInfo(models.Model):
    subinit_name = models.CharField(max_length=1000, blank=True, null=True,
        help_text=(
            'Subinitiative name.'
        ),
    )
    date_modified = models.DateTimeField(blank=True, null=True,
        help_text=(
            'Date modified/created by PID.'
        ),
    )
    sub_init_id = models.CharField(max_length=15, blank=True, null=True)
    requestor = models.CharField(max_length=200, blank=True, null=True,
        help_text=(
            'Requestor PID name.'
        ),
    )
    
    class Meta:
        abstract = True
    
class MasterlistBudgetLog(LogInfo):
    class Meta:
        verbose_name = "Masterlist log"
        verbose_name_plural = "Masterlist logs"
    
class DisburseMinistry(LogInfo):
    disb = models.FloatField(('disbursement'), blank=True, null=True,
        help_text=(
            'Disbursement amount.'
        ),
    )
    
    class Meta:
        verbose_name = "Disbursement log"
        verbose_name_plural = "Disbursement logs"
    
class AllocationMinistry(LogInfo):
    alct = models.FloatField(('allocation'), blank=True, null=True,
        help_text=(
            'Allocation amount.'
        ),
    )
    
    class Meta:
        verbose_name = "Allocation log"
        verbose_name_plural = "Allocation logs"
    
class GeneralRemark(LogInfo):
    remark = models.CharField(('remark'), max_length=2000, blank=True, null=True,
        help_text=(
            'General remark.'
        ),
    )
    
    class Meta:
        verbose_name = "Remark log"
        verbose_name_plural = "Remark logs"
    
class UserLogSubmission(models.Model):
    full_name = models.CharField(max_length=200, blank=True, null=True)
    agency_name = models.CharField(max_length=300, blank=True, null=True)
    initiative = models.CharField(max_length=1000, blank=True, null=True)
    sub_init_id = models.CharField(max_length=15, blank=True, null=True)
    filename = models.CharField(max_length=300, blank=True, null=True)
    submission_time = models.DateTimeField(blank=True, null=True)
    rejected_filename = models.CharField(max_length=1000, blank=True, null=True)
    accepted_filename = models.CharField(max_length=1000, blank=True, null=True)
    accepted_rows = models.IntegerField(blank=True, null=True)
    rejected_rows = models.IntegerField(blank=True, null=True)
    sum_accepted = models.CharField(max_length=50, blank=True, null=True)
    sum_rejected = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        verbose_name = "Submission log"
        verbose_name_plural = "Submission logs"
        
    def __str__(self):
        return str(self.submission_time)


class File(models.Model):
    Inisiatif = models.ForeignKey(MasterlistBudget, on_delete=models.CASCADE, blank=True, null=True)
    Fail = models.FileField(storage=private_storage, 
                            validators=[FileExtensionValidator(allowed_extensions=['csv', 'xlsx', 'xls', 'txt'])])
    Helaian = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = "File"
        verbose_name_plural = "Files"
    
    def __str__ (self):
        return str(self.Inisiatif)
    
class MapTableInitID(models.Model):
    sub_init_id = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        abstract = True
    
class MapTableRace(MapTableInitID):
    race = models.CharField(max_length=200, blank=True, null=True)
    std_race = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        verbose_name = "Mapping Table (Race)"
        verbose_name_plural = "Mapping Table (Race)"
    
class MapTableGender(MapTableInitID):
    gender = models.CharField(max_length=200, blank=True, null=True)
    std_gender = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        verbose_name = "Mapping Table (Gender)"
        verbose_name_plural = "Mapping Table (Gender)"
    
class MapTableState(MapTableInitID):
    state = models.CharField(max_length=200, blank=True, null=True)
    std_state = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        verbose_name = "Mapping Table (State)"
        verbose_name_plural = "Mapping Table (State)"
    
class MapTableBumiStatus(MapTableInitID):
    bumi_status = models.CharField(max_length=200, blank=True, null=True)
    std_bumi_status = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        verbose_name = "Mapping Table (Bumi Status)"
        verbose_name_plural = "Mapping Table (Bumi Status)"
    
class MapTableBizSector(MapTableInitID):
    biz_sector = models.CharField(max_length=1000, blank=True, null=True)
    std_biz_sector = models.CharField(max_length=1000, blank=True, null=True)
    
    class Meta:
        verbose_name = "Mapping Table (Biz Sector)"
        verbose_name_plural = "Mapping Table (Biz Sector)"
    
class MapTableBizOwnershipType(MapTableInitID):
    biz_ownership_type = models.CharField(max_length=200, blank=True, null=True)
    std_biz_ownership_type = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        verbose_name = "Mapping Table (Biz Ownership Type)"
        verbose_name_plural = "Mapping Table (Biz Ownership Type)"
    
class StandardRace(models.Model):
    race = models.CharField(max_length=200)
    
class StandardGender(models.Model):
    gender = models.CharField(max_length=200)
    
class StandardState(models.Model):
    state = models.CharField(max_length=200)
    
class StandardBumiStatus(models.Model):
    bumi_status = models.CharField(max_length=200)
    
class StandardBizSector(models.Model):
    biz_sector = models.CharField(max_length=1000)
    
class StandardBizOwnershipType(models.Model):
    biz_ownership_type = models.CharField(max_length=200)
