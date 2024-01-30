from typing import Any
from django.contrib import admin
from django.http.request import HttpRequest
from .models import *
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from apps.masterlist.models import Validation, Note

# Register your models here.

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class AccountsUserAdmin(AuthUserAdmin):
    def add_view(self, *args, **kwargs):
        self.inlines =[]
        return super(AccountsUserAdmin, self).add_view(*args, **kwargs)

    def change_view(self, *args, **kwargs):
        self.inlines =[UserProfileInline]
        return super(AccountsUserAdmin, self).change_view(*args, **kwargs)
    
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        
        if request.user.is_superuser:
            return super().get_fieldsets(request, obj)
        else:
            return [
                        (None, {'fields': ('username', 'password')}),
                        (('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
                        (('Permissions'), {
                            'fields': ('is_active', 'groups',),
                        }),
                        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
                    ]

class MasterlistBudgetAdmin(admin.ModelAdmin):
    ordering = ['sub_init_id']
    list_display = ("sub_init_id", "subinit_name")
    search_fields = ["sub_init_id", "subinit_name"]
    list_filter = ["is_active"]
    
    fieldsets = [
        (
            "Standard Info",
            {
                "fields": [("init_id", "sub_init_id"), ("init_name", "subinit_name"), 
                           ("ministry", "agency", "program_code"), 
                           ("allocation", "is_active"), 
                           ("fiscal", "non_fiscal"), 
                           ("category", "sector", "status"), 
                           ("file_template"), 
                           ("date_modified", "modified_by"),],
            },
        ),
        (
            "B23",
            {
                "classes": ["collapse"],
                "fields": [("fokus", "tekad", "ikhtiar"), 
                           ("sub_1", "sub_2"), 
                           ("cur_disb", "cur_remark")],
            },
        ),
        (
            "NEC",
            {
                "classes": ["collapse"],
                "fields": [("stf", "stf_id", "nec_id"), 
                           ("category_nec", "category_id"), 
                           ("program", "target")],
            },
        ),
    ]

class MinistryAdmin(admin.ModelAdmin):
    list_display = ("ministry_abbr", "ministry_fullname")
    search_fields = ["ministry_abbr", "ministry_fullname"]

class AgencyAdmin(admin.ModelAdmin):
    list_display = ("agency_abbr", "agency_fullname")
    search_fields = ["agency_abbr", "agency_fullname"]

class LogAdmin(admin.ModelAdmin):
    list_display = ("submission_time", "agency_name", "sub_init_id", "full_name")
    search_fields = ["agency_name", "sub_init_id", "full_name"]

class MasterlistLogAdmin(admin.ModelAdmin):
    list_display = ("date_modified", "sub_init_id", "subinit_name", "requestor")
    search_fields = ["sub_init_id", "subinit_name", "requestor"]

class GeneralRemarkAdmin(admin.ModelAdmin):
    list_display = ("date_modified", "sub_init_id", "subinit_name", "requestor")
    search_fields = ["sub_init_id", "subinit_name", "requestor"]

class DisburseMinistryAdmin(admin.ModelAdmin):
    list_display = ("date_modified", "sub_init_id", "subinit_name", "requestor", "disb")
    search_fields = ["sub_init_id", "subinit_name", "requestor"]

class AllocationMinistryAdmin(admin.ModelAdmin):
    list_display = ("date_modified", "sub_init_id", "subinit_name", "requestor", "alct")
    search_fields = ["sub_init_id", "subinit_name", "requestor"]

class ValidationAdmin(admin.ModelAdmin):
    list_display = ("reporting_date", "init_id", "init_name", "validation_date")
    search_fields = ["init_id", "init_name"]

class NoteAdmin(admin.ModelAdmin):
    list_display = ("note_assc_id", "note_assc_name", "text_note")
    search_fields = ["note_assc_id", "note_assc_name"]
    
class MapGender(admin.ModelAdmin):
    ordering = ['gender']
    list_display = ("gender", "std_gender", "sub_init_id")
    search_fields = ["gender", "std_gender", "sub_init_id"]

class MapRace(admin.ModelAdmin):
    ordering = ['race']
    list_display = ("race", "std_race", "sub_init_id")
    search_fields = ["race", "std_race", "sub_init_id"]

class MapState(admin.ModelAdmin):
    ordering = ['state']
    list_display = ("state", "std_state", "sub_init_id")
    search_fields = ["state", "std_state", "sub_init_id"]

class MapBizOwn(admin.ModelAdmin):
    ordering = ['biz_ownership_type']
    list_display = ("biz_ownership_type", "std_biz_ownership_type", "sub_init_id")
    search_fields = ["biz_ownership_type", "std_biz_ownership_type", "sub_init_id"]

class MapBizSector(admin.ModelAdmin):
    ordering = ['biz_sector']
    list_display = ("biz_sector", "std_biz_sector", "sub_init_id")
    search_fields = ["biz_sector", "std_biz_sector", "sub_init_id"]

class MapBumiStatus(admin.ModelAdmin):
    ordering = ['bumi_status']
    list_display = ("bumi_status", "std_bumi_status", "sub_init_id")
    search_fields = ["bumi_status", "std_bumi_status", "sub_init_id"]

admin.site.unregister(User)
admin.site.register(User, AccountsUserAdmin)
admin.site.register(File)
admin.site.register(FileTemplate)
admin.site.register(MasterlistBudget, MasterlistBudgetAdmin)
admin.site.register(MinistryList, MinistryAdmin)
admin.site.register(AgencyList, AgencyAdmin)
admin.site.register(UserLogSubmission, LogAdmin)
admin.site.register(MasterlistBudgetLog, MasterlistLogAdmin)
admin.site.register(GeneralRemark, GeneralRemarkAdmin)
admin.site.register(DisburseMinistry, DisburseMinistryAdmin)
admin.site.register(AllocationMinistry, AllocationMinistryAdmin)
admin.site.register(Validation, ValidationAdmin)
admin.site.register(Note, NoteAdmin)
admin.site.register(MapTableGender, MapGender)
admin.site.register(MapTableRace, MapRace)
admin.site.register(MapTableState, MapState)
admin.site.register(MapTableBizOwnershipType, MapBizOwn)
admin.site.register(MapTableBumiStatus, MapBumiStatus)
admin.site.register(MapTableBizSector, MapBizSector)
admin.site.register(DQUser)

admin.site.site_url = None
admin.site.site_header = "PODS Admin"  
admin.site.site_title = "PODS admin site"
admin.site.index_title = "PODS Admin"