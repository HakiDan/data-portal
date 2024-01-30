from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render 
from django.template import loader
from django.conf import settings
from apps.upload.models import *
from django.urls import reverse
from core.tasks import *
from django import template
from apps.home.models import Summary
from django.shortcuts import render
from django.contrib.auth.models import Group

# from collections import Counter
from datetime import datetime
import calendar
import datetime
import requests

mainPath = settings.MAINPATH
SUPRSET_API_URL = 'https://dashboard.laksana.gov.my/api/v1'
# SUPRSET_API_URL = 'http://192.168.100.200:8088/api/v1'

def get_access_token(request):
    SUPRSET_USERNAME = str(request.user.username)
    SUPRSET_PASSWORD = settings.SUPERSET_PASSWORD
    
    data = {
        "password": SUPRSET_PASSWORD,
        "provider": "db",
        "refresh": "true",
        "username": SUPRSET_USERNAME
    }
    
    payload = {
        "resources": [
            {
                "id": "23",
                "type": "dashboard"
            }
        ],
        "rls":[],
        "user": {
            "username": str(request.user.username)
            }
    }
    
    response = requests.post(f'{SUPRSET_API_URL}/security/login', verify = False, json = data)
    access_token = response.json()['access_token']
    api_url_for_guesttoken = f'{SUPRSET_API_URL}/security/guest_token'
    response_token = requests.post(api_url_for_guesttoken, verify = False, json = payload, headers = {'Authorization':f"Bearer {access_token}"})
    return response_token.json().get('token')


@login_required(login_url="/login/")

def index(request):
    get_user = User.objects.get(username=request.user.username)
    pid_group = Group(name='pid_group')
    ia_group = Group(name='ia_group')
    if get_user.groups.filter(name=ia_group).exists():
        try:
            error_values = ['',' ',""," ",'NULL', None, 'N/A', 'n/a', 'NA'] 

            init_id = list(MasterlistBudget.objects.filter(init_id_assc=request.user).values_list('init_id', flat=True))
            allocation = list(Summary.objects.filter(init_id__in=init_id).values_list('allocation', flat=True))
            disbursed = list(Summary.objects.filter(init_id__in=init_id).values_list('disbursed', flat=True))
            status = list(Summary.objects.filter(init_id__in=init_id).values_list('status', flat=True))
            init_name = list(Summary.objects.filter(init_id__in=init_id).values_list('init_name', flat=True))
            beneficiaries = list(Summary.objects.filter(init_id__in=init_id).values_list('bene', flat=True))
            sub_init_name = list(Summary.objects.filter(init_id__in=init_id).values_list('sub_init_name', flat=True))
            bumi_status = list(Summary.objects.filter(init_id__in=init_id).values_list('bumi_status', flat=True))

            dates = list(Summary.objects.filter(init_id__in=init_id).values_list('date', flat=True))

            total_allocation, allocations_array = allocation_sum(sub_init_name, allocation, error_values)
            total_disbursed = disbursement_sum(dates, disbursed, status, error_values)
            total_bene = beneficiary_sum(dates, beneficiaries, status, error_values)
        
            init_name_label = init_name_label_list(init_name)
            sub_init_name_label, sub_init_name_table_label = sub_init_name_label_list(sub_init_name)
            monthly_beneficiaries_values, month_table_value, beneficiaries_array, month_names = monthly_beneficiaries_chart(dates, init_name, init_name_label, status, beneficiaries, error_values)
            disbursed_values, ranged_disbursed_values = date_disbursed_chart(dates, init_name, init_name_label, status, disbursed, error_values)
            state_unique_labels, state_values = state_chart(dates, init_id, init_name, init_name_label, status, disbursed, error_values)
            races, race_beneficiaries = race_chart(dates, init_id, status, beneficiaries, error_values)
            gender, gender_ben = gender_chart(dates, init_id, status, beneficiaries, error_values)
            age_values, age_groups_labels = age_chart(dates, init_id, init_name_label, init_name, status, beneficiaries, error_values) 
            sectors, sector_disbursed = sector_chart(dates, init_id, init_name, init_name_label, status, disbursed, error_values) 
            biz_size_unique_labels, biz_size_values = biz_size_chart(dates, init_id, init_name_label, init_name, status, beneficiaries, error_values)

            items_ia_tables = zip(sub_init_name_table_label, beneficiaries_array, allocations_array, ranged_disbursed_values, month_table_value)

            context = {

                'init_name_label':init_name_label, 
                'init_id':init_id,

                'sub_init_name': sub_init_name,
                'sub_init_name_label':sub_init_name_label,
                
                'bumi_status':bumi_status,

                'races':races,
                'race_beneficiaries':race_beneficiaries,

                'sectors':sectors,
                'sector_disbursed':sector_disbursed,

                'state_unique_labels':state_unique_labels,
                'state_values':state_values,

                'biz_size_unique_labels':biz_size_unique_labels,
                'biz_size_values':biz_size_values,

                'age_values':age_values,
                'age_groups_labels':age_groups_labels,  

                'gender':gender, 
                'gender_ben':gender_ben,

                'status': status,
                'beneficiaries':beneficiaries,
                'monthly_beneficiaries_values':monthly_beneficiaries_values,
                'allocation':allocation,
                
                'month_names':month_names,
                'disbursed':disbursed,
                'disbursed_values':disbursed_values,
                
                'dates':dates,

                'total_disbursed':total_disbursed,
                'total_allocation':total_allocation,
                'total_bene':total_bene,

                'items_ia_tables':items_ia_tables,

                'sub_init_name_table_label':sub_init_name_table_label,
                'beneficiaries_array':beneficiaries_array,
                'allocations_array':allocations_array,
                'range_disbursed_values':ranged_disbursed_values,
                'month_table_value':month_table_value,

            }
        
            html_template = loader.get_template('home/index.html')
            return HttpResponse(html_template.render(context, request,))
            
        except:
            context = {}
            html_template = loader.get_template('home/index.html')
            return HttpResponse(html_template.render(context, request,))
   
    elif get_user.groups.filter(name=pid_group).exists():
        try:
            token = get_access_token(request)
            # superset_url = 'https://dashboard.laksana.gov.my/superset/dashboard/23/?standalone=2&access_token={}/'.format(token)
            superset_url = 'http://192.168.100.200:8088/superset/dashboard/23/?standalone=2&access_token={}/'.format(token)
            context = {'superset_url':superset_url}
            html_template = loader.get_template('home/index.html')
            return HttpResponse(html_template.render(context, request,))
        except:
            context = {}
            html_template = loader.get_template('home/index.html')
            return HttpResponse(html_template.render(context, request,))
    else:
        context = {}
        html_template = loader.get_template('home/index.html')
        return HttpResponse(html_template.render(context, request,))


def allocation_sum(sub_init_name, allocation, error_values): 

    # Initialize a dictionary to store the sum of unique allocation values for each string
    unique_allocation_values = {}

    # Iterate through the zip array of sub_initt_name and allocation
    for sub_init, allocation_value in zip(sub_init_name, allocation):
         
        if sub_init in unique_allocation_values:
            # If it is NULL, change the allocation value into 0.0
            if allocation_value in error_values:
                # Add the value to the existing sum
                unique_allocation_values[sub_init] = 0.0
            else:
                unique_allocation_values[sub_init] = allocation_value

        else:
            # If it's not in the dictionary, create a new entry with the value 
            unique_allocation_values[sub_init] = allocation_value

    # Create a list to store the allocation values
    allocation_values = []

    # Append the sum of unique allocation values to the list
    for total in unique_allocation_values.values():
        allocation_values.append(total)

    # Create a list to store the allocation values array
    allocation_values_array = [] 

    for values in allocation_values:
        # Multiply allocation values 12 times
        allocation_array = [values] * 12
        allocation_values_array.append(allocation_array) 

    # Change the allocation_values_array from a 2D array into a 1D array 
    allocation_array = [element for sublist in allocation_values_array for element in sublist]
 
    total_sum_of_allocation_values = sum(allocation_values)

    return total_sum_of_allocation_values, allocation_array



def disbursement_sum(dates, disbursed, status, error_values):

    formatted_dates = [date.strftime("%Y-%m") for date in dates]

    # Find the latest date
    latest_date = max(formatted_dates)

    # Create a dictionary to store the beneficiaries by date
    disbursement_dict = {date: 0 for date in formatted_dates}

    for date, disb_status, disb in zip(formatted_dates, status, disbursed):
        # Check if the date is the latest date, if not append 0 as velues
        if date == latest_date:
            if disb_status == 'DISALURKAN': 
                if disb in error_values:
                    disbursement_dict[date] += 0.0
                else:
                    disbursement_dict[date] += disb
            else:
                pass
        else:
            pass
        
    # Get the sum of disbursements for the latest date from the dictionary
    latest_disbursement_sum = disbursement_dict[latest_date]

    return latest_disbursement_sum
    


def beneficiary_sum(dates, beneficiaries, status, error_values):

    formatted_dates = [date.strftime("%Y-%m") for date in dates]

    # Find the latest date
    latest_date = max(formatted_dates)

    # Create a dictionary to store the beneficiaries by date
    beneficiaries_dict = {date: 0 for date in formatted_dates}

    for date, bene_status, beneficiary in zip(formatted_dates, status, beneficiaries):
        # Check if the date is the latest date, if not append 0 as velues
        if date == latest_date:
            if bene_status == 'DISALURKAN': 
                if beneficiary in error_values:
                    beneficiaries_dict[date] += 0
                else:
                    beneficiaries_dict[date] += beneficiary
            else:
                pass
        else:
            pass
        
    # Get the sum of beneficiaries for the latest date from the dictionary
    latest_beneficiaries_sum = beneficiaries_dict[latest_date]

    return latest_beneficiaries_sum



def init_name_label_list(init_name): 
        
    # Initialize an empty list to store the unique init_name values
    init_name_label = []

    # Append each uniques init_name value in init_unique_labels list
    # For each init in init_name list
    for init in init_name:
        #for init that is not in init_unique_labels list
        if init not in init_name_label:
            #append
            init_name_label.append(init)

    return init_name_label



def sub_init_name_label_list(sub_init_name):
        
    # Initialize an empty list to store the unique init_name values
    sub_init_unique_labels = []

    # Append each uniques init_name value in init_unique_labels list
    # For each init in sub_init_name list
    for sub_init in sub_init_name:
        #for init that is not in init_unique_labels list
        if sub_init not in sub_init_unique_labels:
            #append
            sub_init_unique_labels.append(sub_init)
    
    sub_init_labels = []

    # Iterate through the original list
    for label in sub_init_unique_labels:
        # Create a new list with the current item repeated 12 times
        table_label = [label] * 12
        # Append the repeated item to the 2D array 
        sub_init_labels.append(table_label)

    sub_init_table_labels = [element for sublist in sub_init_labels for element in sublist]

    return sub_init_unique_labels, sub_init_table_labels


def monthly_beneficiaries_chart(dates, init_name, init_name_label, status, beneficiaries, error_values):  

    date_beneficiaries_sum_count = {init_name: {"January": 0, "February": 0, "March": 0, "April": 0, "May": 0,"June": 0,"July": 0,"August": 0,"September": 0,"October": 0,"November": 0,"December": 0} for init_name in init_name_label}

    month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November","December"]

    name_bulan = ["Januari", "Februari", "Mac", "April", "Mei", "Jun", "Julai", "Ogos", "September", "Oktober", "November","Disember"]

    label_bulan = ['JANUARI', 'FEBRUARI', 'MAC', 'APRIL', 'MEI', 'JUN', 'JULAI' , 'OGOS' , 'SEPTEMBER', 'OKTOBER', 'NOVEMBER' , 'DISEMBER']

    month_array = []

    # Done to generate alist of month names in bottom table
    # Loop through each 'init' value
    for init in init_name_label:
        # Use a nested list comprehension to extract only the month values
        month_values = [month for month in name_bulan]
        
        # Extend the one_d_array with the month values
        month_array.extend(month_values)

    months = []

    # To convert the dates to get month values only and convert it into a name of the month
    for date in dates:
        months.append(date.strftime("%B")) 

    # Calculate the total number of beneficiaries for each month
    for init, month, bene_status, total_beneficiaries in zip(init_name, months, status, beneficiaries):
        # Loop through all the values in the month_names array
        for month_name in month_names:
            # Only choose the one with condiotion that match bene_status == "DISALURKAN"
            if bene_status == "DISALURKAN":
                if month == month_name:
                    if total_beneficiaries in error_values:
                        date_beneficiaries_sum_count[init][month_name] += 0
                    else:
                        date_beneficiaries_sum_count[init][month_name] += total_beneficiaries
                else:
                    pass
            else:
                pass
                
    # Initialize an array to store the monthly_beneficiaries values
    monthly_beneficiaries = []

    # Append only the count values for each program to the final_count_values_2d 2D array
    for init in init_name_label:
        disbursed_sum = date_beneficiaries_sum_count[init]
        disbursed_values = list(disbursed_sum.values())
        monthly_beneficiaries.append(disbursed_values)

    beneficiaries_array = []

    # Iterate through the rows and columns of the array
    for row in monthly_beneficiaries:
        for element in row:
            beneficiaries_array.append(element)

    return monthly_beneficiaries, month_array, beneficiaries_array, label_bulan


def date_disbursed_chart(dates, init_name, init_name_label, status, disbursed, error_values):

    date_disbursed_sum_count = {date_group: {"January": 0, "February": 0, "March": 0, "April": 0, "May": 0,"June": 0,"July": 0,"August": 0,"September": 0,"October": 0,"November": 0,"December": 0} for date_group in init_name_label}

    month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November","December"]

    months = []

    for date in dates:
        months.append(date.strftime("%B"))

    # Calculate the age group counts for each target program based on program_num_people
    for init, month, month_status, total_disbursed in zip(init_name, months, status, disbursed):
        for month_name in month_names:
            if month in month_name:
                if month_status == "DISALURKAN":
                    if total_disbursed in error_values:
                        date_disbursed_sum_count[init][month_name] += 0.0
                    else:
                        date_disbursed_sum_count[init][month_name] += total_disbursed
                else:
                    pass
            else:
                pass

    # Initialize a 2D array to store the final count values without labeling
    monthly_disbursed = []

    # Append only the count values for each program to the final_count_values_2d 2D array
    for init in init_name_label:
        disbursed_sum = date_disbursed_sum_count[init]
        disbursed_values = list(disbursed_sum.values())
        monthly_disbursed.append(disbursed_values)

    disbursed_list = [item for sublist in monthly_disbursed for item in sublist] 

    return monthly_disbursed, disbursed_list


def state_chart(dates, init_id, init_name, init_name_label, status, disbursed, error_values):

    states = list(Summary.objects.filter(init_id__in=init_id).values_list('state', flat=True))

    # Format the dates from the dates cloumn to be in yyyy-mm format
    formatted_dates = [date.strftime("%Y-%m") for date in dates]

    # Get the latest date
    latest_date = max(formatted_dates)

    # Inititalize the list of the possible state name for the data we could receive
    # state_groups = ["WP PUTRAJAYA","NEGERI SEMBILAN","SELANGOR","WP LABUAN","SABAH","PAHANG","WP KUALA LUMPUR","PERLIS","MELAKA","TERENGGANU","SARAWAK","PULAU PINANG","JOHOR","PERAK","KELANTAN","KEDAH","TIDAK DIKENALPASTI"]

    state_groups = []

    for state, date in zip(states, formatted_dates):
        if date == latest_date:
            if state not in state_groups:
                if state in error_values:
                    if "TIDAK DIKENALPASTI" not in state_groups:
                        state_groups.append("TIDAK DIKENALPASTI")
                    else:
                        pass
                else:
                    state_groups.append(state)
            else:
                pass
        else:
            pass

    # Inititalize the States dictionary for each intitiatives
    # states_list_counts = {init_name: {"WP PUTRAJAYA": 0,"NEGERI SEMBILAN": 0,"SELANGOR": 0,"WP LABUAN": 0,"SABAH": 0,"PAHANG": 0,"WP KUALA LUMPUR": 0,"PERLIS": 0,"MELAKA": 0,"TERENGGANU": 0,"SARAWAK": 0,"PULAU PINANG": 0,"JOHOR": 0,"PERAK": 0,"KELANTAN": 0,"KEDAH": 0,"TIDAK DIKENALPASTI": 0} for init_name in init_name_label}
    states_list_counts = {init_name: {state: 0 for state in state_groups} for init_name in init_name_label}

    # Calculate the disbursement for each state of each initiatives for the latest date
    for init, state, state_status, disb, date in zip(init_name, states, status, disbursed, formatted_dates):
        # Check whether it is the latest date
        if date == latest_date:
            if state_status == "DISALURKAN":
            # Check whether the state is in the  state_groups list
                if state in state_groups:
                    # Check for error values
                    if disb in error_values:
                        states_list_counts[init][state] += 0.0
                    else:
                        states_list_counts[init][state] += disb
                elif state in error_values:
                    if disb in error_values:
                        states_list_counts[init]["TIDAK DIKENALPASTI"] += 0.0
                    else:
                        states_list_counts[init]["TIDAK DIKENALPASTI"] += disb
            else:
                pass
        else:
            pass
            
    # Initialize a 2D array to store the final count values
    state_values = []

    # Append only the count values for each program to the final_count_values_2d 2D array
    for init in init_name_label:
        state_list_count = states_list_counts[init]
        count_values = list(state_list_count.values())
        state_values.append(count_values)

    return state_groups, state_values



def race_chart(dates, init_id, status, beneficiaries, error_values):

    races = list(Summary.objects.filter(init_id__in=init_id).values_list('race', flat=True))

    race_unique_labels = ['MELAYU','CINA','INDIA','ORANG ASLI','BUMIPUTERA SARAWAK','BUMIPUTERA SABAH','LAIN-LAIN','TIDAK DIKENALPASTI']

    formatted_dates = [date.strftime("%Y-%m") for date in dates]

    latest_date = max(formatted_dates)

    # Initialize a dictionary to store the counts for each race label
    sums = {race: 0 for race in race_unique_labels}

    # Iterate through the lists using zip and update the counts and latest dates
    for race, race_status, beneficiary_sum, date in zip(races, status, beneficiaries, formatted_dates):
        # Check if the current date is later than the latest date for the same race label
        if date == latest_date:
            if race_status == "DISALURKAN":
                if race in race_unique_labels:
                    if beneficiary_sum in error_values:
                        sums[race] += 0
                    else:
                        sums[race] += beneficiary_sum 
                else:
                    if beneficiary_sum in error_values:
                        sums["TIDAK DIKENALPASTI"] += 0
                    else:
                        sums["TIDAK DIKENALPASTI"] += beneficiary_sum
            else:
                pass
        else:
            pass

    # Create a list to store the total beneficiaries values
    total_race_beneficiaries_values = []

    # Append the total values to the list
    for total in sums.items():
        total_race_beneficiaries_values.append(total)

    races = race_unique_labels
    race_beneficiaries = total_race_beneficiaries_values

    return races, race_beneficiaries


def gender_chart(dates, init_id, status, beneficiaries, error_values):

    genders = list(Summary.objects.filter(init_id__in=init_id).values_list('gender', flat=True))

    # Initiate list for Unique Race value in Race Column
    gender_unique_labels = ["LELAKI", "PEREMPUAN", "TIDAK DIKENALPASTI"]

    formatted_dates = [date.strftime("%Y-%m") for date in dates]

    latest_date = max(formatted_dates)

    # Initialize a dictionary to store the sums for each value in race_unique_labels
    sums = {gender: 0 for gender in gender_unique_labels}

    # Iterate through race and beneficiaries and update sums based on race_unique_labels
    for gender, gender_status, beneficiary_sum, date in zip(genders, status, beneficiaries, formatted_dates):
        if date == latest_date:
            if gender_status == "DISALURKAN":
                if gender in gender_unique_labels:
                    if beneficiary_sum in error_values:
                        sums[gender] += 0
                    else:
                        sums[gender] += beneficiary_sum
                else:
                    if beneficiary_sum in error_values:
                        sums["TIDAK DIKENALPASTI"] += 0
                    else:
                        sums["TIDAK DIKENALPASTI"] += beneficiary_sum
            else:
                pass
        else:
            pass

    # Create a list to store the total beneficiaries values
    total_gender_beneficiaries_values = []

    # Append the total values to the list
    for total in sums.items():
        total_gender_beneficiaries_values.append(total)

    return gender_unique_labels, total_gender_beneficiaries_values


def age_chart(dates, init_id, init_name_label, init_name, status, beneficiaries, error_values):

    beneficiaries_age = list(Summary.objects.filter(init_id__in=init_id).values_list('age', flat=True))

    # age_groups_labels = ["<20","20-29","30-39","40-49","50-59","60>","TIDAK DIKENALPASTI"]

    formatted_dates = [date.strftime("%Y-%m") for date in dates]

    latest_date = max(formatted_dates)

    age_groups_labels = []

    for age, date in zip(beneficiaries_age, formatted_dates):
        if date == latest_date:
            if age not in age_groups_labels:
                if age in error_values:
                    if "TIDAK DIKENALPASTI" not in age_groups_labels:
                        age_groups_labels.append("TIDAK DIKENALPASTI")
                    else:
                        pass
                else:
                    age_groups_labels.append(age)
            else:
                pass
        else:
            pass

    # Initialize dictionaries to store age group counts for each initiatives
    # age_groups = {init_name: {"<20": 0, "20-29": 0, "30-39": 0, "40-49": 0, "50-59": 0, "60>": 0, "TIDAK DIKENALPASTI": 0} for init_name in init_name_label}
    age_groups = {init_name: {age: 0 for age in age_groups_labels} for init_name in init_name_label}

    # Calculate the age group counts for each target program based on program_num_people
    for init, age, age_status, beneficiary, date in zip(init_name, beneficiaries_age, status, beneficiaries, formatted_dates):
        if date == latest_date:
            if age_status == "DISALURKAN":
                if age in age_groups_labels:
                    if beneficiary in error_values:
                        age_groups[init][age] += 0
                    else:
                        age_groups[init][age] += beneficiary

                elif age not in age_groups_labels:
                    if beneficiary in error_values:
                        age_groups[init]["TIDAK DIKENALPASTI"] += 0
                    else:
                        age_groups[init]["TIDAK DIKENALPASTI"] += beneficiary
                    
                elif age in error_values:
                    if beneficiary in error_values:
                        age_groups[init]["TIDAK DIKENALPASTI"] += 0
                    else:
                        age_groups[init]["TIDAK DIKENALPASTI"] += beneficiary
            else:
                pass
        else:
            pass

    # Initialize a 2D array to store the final count values without labeling
    age_values = []

    # Append only the count values for each program to the final_count_values_2d 2D array
    for init in init_name_label:
        age_group_count = age_groups[init]
        count_values = list(age_group_count.values())
        age_values.append(count_values)

    return age_values, age_groups_labels


def sector_chart(dates, init_id, init_name, init_name_label, status, disbursed, error_values):

    sectors = list(Summary.objects.filter(init_id__in=init_id).values_list('sector', flat=True))

    formatted_dates = [date.strftime("%Y-%m") for date in dates]

    # Find the latest date
    latest_date = max(formatted_dates)

    # Initialize a list to store unique sector values
    sector_labels = []

    for sector, date in zip(sectors, formatted_dates):
        if date == latest_date:
            if sector not in sector_labels:
                if sector in error_values:
                    if "TIDAK DIKENALPASTI" not in sector_labels:
                        sector_labels.append("TIDAK DIKENALPASTI")
                    else:
                        pass
                else:
                    sector_labels.append(sector)
            else:
                pass
        else:
            pass

    # Initialize a dictionary to store the sums
    sector_groups = {init_name: {sector: 0 for sector in sector_labels} for init_name in init_name_label}

    # Calculate the age group counts for each target program based on program_num_people
    for init, sector, sector_status, disb, date in zip(init_name, sectors, status, disbursed, formatted_dates):
        if date == latest_date:
            if sector_status == "DISALURKAN":
                if sector in sector_labels:
                    if disb in error_values:
                        sector_groups[init][sector] += 0.0
                    else:
                        sector_groups[init][sector] += disb
                elif sector in error_values:
                    if disb in error_values:
                        sector_groups[init]["TIDAK DIKENALPASTI"] += 0.0
                    else:
                        sector_groups[init]["TIDAK DIKENALPASTI"] += disb
            else:
                pass
        else:
            pass   

    # Initialize a 2D array to store the final count values without labeling
    sector_values = []

    # Append only the count values for each program to the final_count_values_2d 2D array
    for init in init_name_label:
        sector_count = sector_groups[init]
        count_values = list(sector_count.values())
        sector_values.append(count_values)

    return sector_labels, sector_values



def biz_size_chart(dates, init_id, init_name_label, init_name, status, beneficiaries, error_values):

    biz_sizes = list(Summary.objects.filter(init_id__in=init_id).values_list('biz_size', flat=True))

    # Initiate list for Unique biz_size value in biz_size Column
    # biz_size_labels = ["MIKRO", "KECIL", "SEDERHANA", "BESAR", "TIDAK DIKENALPASTI"]

    biz_size_labels = []

    formatted_dates = [date.strftime("%Y-%m") for date in dates]

    latest_date = max(formatted_dates)

    for biz_size, date in zip(biz_sizes, formatted_dates):
        if date == latest_date:
            if biz_size not in biz_size_labels:
                if biz_size in error_values:
                    if "TIDAK DIKENALPASTI" not in biz_size_labels:
                        biz_size_labels.append("TIDAK DIKENALPASTI")
                    else:
                        pass
                else:
                    biz_size_labels.append(biz_size)
            else:
                pass
        else:
            pass

    # Initialize dictionaries to store age group counts for each initiatives
    # biz_size_groups = {init_name: {"MIKRO": 0, "KECIL": 0, "SEDERHANA": 0, "BESAR": 0, "TIDAK DIKENALPASTI": 0} for init_name in init_name_label}
    biz_size_groups = {init_name: {sector: 0 for sector in biz_size_labels} for init_name in init_name_label}

    # Calculate the age group counts for each target program based on program_num_people
    for init, biz_size, biz_status, beneficiary, date in zip(init_name, biz_sizes, status, beneficiaries, formatted_dates):
        if date == latest_date:
            if biz_status == "DISALURKAN":
                if biz_size in biz_size_labels:
                    if beneficiary in error_values:
                        biz_size_groups[init][biz_size] += 0
                    else:
                        biz_size_groups[init][biz_size] += beneficiary

                elif biz_size not in biz_size_labels:
                    if beneficiary in error_values:
                        biz_size_groups[init]["TIDAK DIKENALPASTI"] += 0
                    else:
                        biz_size_groups[init]["TIDAK DIKENALPASTI"] += beneficiary

                elif biz_size in error_values:
                    if beneficiary in error_values:
                        biz_size_groups[init]["TIDAK DIKENALPASTI"] += 0
                    else:
                        biz_size_groups[init]["TIDAK DIKENALPASTI"] += beneficiary 
            else:
                pass
        else: 
            pass

    # Initialize a 2D array to store the values only without the keys
    biz_size_values = []

    # Append only the count values for each program to the final_count_values_2d 2D array
    for init in init_name_label:
        biz_size_groups_count = biz_size_groups[init]
        count_values = list(biz_size_groups_count.values())
        biz_size_values.append(count_values)

    return biz_size_labels, biz_size_values



@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))

#register = template.Library() 

@login_required(login_url="/login/")
def profile(request):
    """_summary_
    Render profile page

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """    
    return render(request, 'home/profile.html')