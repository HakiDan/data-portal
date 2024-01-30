from django import template
from django.contrib.auth.models import Group, User
from apps.upload.models import MasterlistBudget, UserProfile

register = template.Library()
    
@register.filter(name='in_group') 
def in_group(user, group_name):
    """_summary_
    Check user in which group he/she belongs to

    Args:
        user (_type_): _description_
        group_name (_type_): _description_

    Returns:
        _type_: _description_
    """
    return user.groups.filter(name=group_name).exists()


@register.filter(name='assc_sub_init_id')
def assc_sub_init_id(sub_init_id):
    """_summary_
    Return queryset of user associate with specified subinitiative

    Args:
        sub_init_id (_type_): _description_

    Returns:
        _type_: _description_
    """
    masterlist = MasterlistBudget.objects.get(sub_init_id=sub_init_id)
    user = masterlist.userprofile_set.all()
    return user


@register.filter(name='is_pic')
def is_pic(userprofile, group_name):
    """_summary_
    Check user in which group he/she belongs to (For assc_sub_init_id filter)

    Args:
        userprofile (_type_): _description_
        group_name (_type_): _description_

    Returns:
        _type_: _description_
    """
    return userprofile.user.groups.filter(name=group_name).exists()