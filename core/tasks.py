from django.template.loader import get_template
from background_task import background
from django.conf import settings
from apps.upload.models import *
import logging
from email.mime.text import MIMEText
import smtplib
from decouple import config
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from pyzabbix import ZabbixMetric, ZabbixSender

mainPath = settings.MAINPATH
logger = logging.getLogger('main')
zabbix_sender = ZabbixSender(settings.ZABBIX_SERVER, settings.ZABBIX_PORT)

@background(schedule=20)
def notify_IAs(information):
    """_summary_
    Notify IAs and IAs lead about submission of the file from PIC 

    Args:
        information (_type_): _description_
    """
    for email_list in information['email_IA']:
        # with open('/app/smtp_ip.txt', 'r') as file:
        #     ip_address = file.read().strip()
        email = "SALAM SEJAHTERA"
        if information['result_msg'] == 'Success':
            html_tpl_path = 'email/email_IA_success.html'
        else:
            html_tpl_path = 'email/email_IA_failed.html'
        content = {
            "email":email,
            "filename":information['file_name'],
            "initiative":information['initiative'].upper(),
            "count_row_accepted":information['count_row_accepted'],
            "count_row_rejected":information['count_row_rejected'],
            "user_full_name":information['user_full_name'],
            "msg":information['msg'],
            "date":information['date'],
            "agency_name":(information['agency_name']),
            "file_ext":information['file_ext'],
            "sumaccepted":information['sumaccepted'],
            "sumrejected":information['sumrejected'],
            }
        email_html_template = get_template(html_tpl_path).render(content)
        msg = MIMEText(email_html_template, 'html')
        msg['Subject'] = 'PENGESAHAN PENERIMAAN DATA OLEH LAKSANA BERHUBUNG DENGAN INISIATIF ' + information['initiative'].upper()
        msg['From'] = settings.EMAIL_HOST_USER
        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as smtp_conn:
            try:
                smtp_conn.starttls()
                # smtp_conn.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                smtp_conn.sendmail(settings.EMAIL_HOST_USER, email_list, msg.as_string())
                logger.info('Email for file ' + information['file_name'] + '.' + information['file_ext'] 
                            + ' Initiative: ' + information['initiative'] + ' has been sent to ' + email_list 
                            + " - " + information['username'])
                try:
                    packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                           'Email for file ' + information['file_name'] + '.' + information['file_ext'] 
                                           + ' Initiative: ' + information['initiative'] + ' has been sent to ' + email_list 
                                           + " - " + information['username'])]
                    zabbix_sender.send(packet)
                except:
                    pass
            except:
                logger.info('Failed sent email for file ' + information['file_name'] + '.' + information['file_ext'] 
                            + ' Initiative: ' + information['initiative'] + ' to ' + email_list 
                            + " - " + information['username'])
                try:
                    packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                           'Failed sent email for file ' + information['file_name'] + '.' + information['file_ext'] 
                                           + ' Initiative: ' + information['initiative'] + ' to ' + email_list 
                                           + " - " + information['username'])]
                    zabbix_sender.send(packet)
                except:
                    pass
    

def notify_password_request(user):
    """_summary_
    Reset password request for all users

    Args:
        user (_type_): _description_
    """
    # with open('/app/smtp_ip.txt', 'r') as file:
    #     ip_address = file.read().strip()
    html_tpl_path = 'email/password_email.html'
    content = {
        'domain':config('DOMAIN_NAME'),
        'site_name':'Website',
        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
        'user':user,
        'token':default_token_generator.make_token(user),
        'protocol':config('PROTOCOL'),
        }
    email_html_template = get_template(html_tpl_path).render(content)
    msg = MIMEText(email_html_template, 'html')
    msg['Subject'] = 'PENERIMAAN PERMOHONAN UNTUK KEMAS KINI KATA LALUAN'
    msg['From'] = settings.EMAIL_HOST_USER
    # context = ssl.create_default_context()
    with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as smtp_conn:
        try:
            # smtp_conn.starttls(context = context)
            smtp_conn.starttls()
            # smtp_conn.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            smtp_conn.sendmail(settings.EMAIL_HOST_USER, user.email, msg.as_string())
            logger.info("Success request change password - " + str(user))
            try:
                packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                       "Success request change password - " + str(user))]
                zabbix_sender.send(packet)
            except:
                pass
        except:
            logger.info("Failed request change password - " + str(user))
            try:
                packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                       "Failed request change password - " + str(user))]
                zabbix_sender.send(packet)
            except:
                pass
      
            
@background(schedule=20)
def notify_validation_failed(information):
    """_summary_
    Send an email notification (failed validation) to PIDs

    Args:
        pid_users (_type_): _description_
    """
    for email_list in information['pid_users']:
        # with open('/app/smtp_ip.txt', 'r') as file:
        #     ip_address = file.read().strip()
        email = "Greetings"
        html_tpl_path = 'email/email_failed_validation.html'
        content = {
            "email":email,
            "init_name":information['init_name'].upper(),
            "init_id":information['init_id'],
            "date":information['date'],
            "rejection_note":information['rejection_note'],
            "current_note":information['current_note'],
            }
        email_html_template = get_template(html_tpl_path).render(content)
        msg = MIMEText(email_html_template, 'html')
        msg['Subject'] = 'REJECTED VALIDATION FOR INITIATIVE ' + information['init_name'].upper()
        msg['From'] = settings.EMAIL_HOST_USER
        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as smtp_conn:
            try:
                smtp_conn.starttls()
                # smtp_conn.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                smtp_conn.sendmail(settings.EMAIL_HOST_USER, email_list, msg.as_string())
                logger.info('Email for failed validation Initiative: ' + information['init_name'] 
                            + ' has been sent to ' + email_list)
                try:
                    packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                           'Email for failed validation Initiative: ' + information['init_name'] 
                                           + ' has been sent to ' + email_list)]
                    zabbix_sender.send(packet)
                except:
                    pass
            except:
                logger.info('Failed email for failed validation Initiative: ' + information['init_name'] 
                            + ' has been sent to ' + email_list)
                try:
                    packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                           'Failed email for failed validation Initiative: ' + information['init_name'] 
                                           + ' has been sent to ' + email_list)]
                    zabbix_sender.send(packet)
                except:
                    pass
       
                
@background(schedule=20)               
def notify_register_user(user_info):
    """_summary_
    Send email to user (IA) for registration

    Args:
        user (_type_): _description_
    """
    # with open('/app/smtp_ip.txt', 'r') as file:
    #     ip_address = file.read().strip()
    html_tpl_path = 'email/notify_registration.html'
    content = {
        'email': user_info['user_email'],
        'password': user_info['user_password'],
        'requestor': user_info['requestor'],
        }
    email_html_template = get_template(html_tpl_path).render(content)
    msg = MIMEText(email_html_template, 'html')
    msg['Subject'] = 'PENDAFTARAN PENGGUNA ' + str(user_info['user_email'])
    msg['From'] = settings.EMAIL_HOST_USER
    # context = ssl.create_default_context()
    with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as smtp_conn:
        try:
            # smtp_conn.starttls(context = context)
            smtp_conn.starttls()
            # smtp_conn.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            smtp_conn.sendmail(settings.EMAIL_HOST_USER, user_info['user_email'], msg.as_string())
            logger.info("Success register user " + str(user_info['user_email'] + 
                        " - " + str(user_info['requestor'])))
            try:
                packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                       "Success register user " + str(user_info['user_email'] + 
                                        " - " + str(user_info['requestor'])))]
                zabbix_sender.send(packet)
            except:
                pass
        except:
            logger.info("Failed register user " + str(user_info['user_email'] + 
                        " - " + str(user_info['requestor'])))
            try:
                packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                       "Failed register user " + str(user_info['user_email'] + 
                                        " - " + str(user_info['requestor'])))]
                zabbix_sender.send(packet)
            except:
                pass
            
            
@background(schedule=20)               
def notify_register_pid(user_info):
    """_summary_
    Send email to user (PID) for registration report

    Args:
        user (_type_): _description_
    """
    # with open('/app/smtp_ip.txt', 'r') as file:
    #     ip_address = file.read().strip()
    html_tpl_path = 'email/notify_registration_pid.html'
    content = {
        'email': user_info['user_email'],
        'agency': user_info['user_agency'],
        'phone_number': user_info['user_phone_number'],
        'subinit_name': user_info['user_subinit_name'],
        'requestor': user_info['requestor'],
        'requestor_email': user_info['requestor_email'],
        }
    email_html_template = get_template(html_tpl_path).render(content)
    msg = MIMEText(email_html_template, 'html')
    msg['Subject'] = 'PENDAFTARAN PENGGUNA ' + str(user_info['user_email'])
    msg['From'] = settings.EMAIL_HOST_USER
    # context = ssl.create_default_context()
    with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as smtp_conn:
        try:
            # smtp_conn.starttls(context = context)
            smtp_conn.starttls()
            # smtp_conn.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            smtp_conn.sendmail(settings.EMAIL_HOST_USER, user_info['requestor_email'], msg.as_string())
            logger.info("Success send email for user registration " + str(user_info['user_email'] + 
                        " - " + str(user_info['requestor'])))
            try:
                packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                       "Success send email for user registration " + str(user_info['user_email'] + 
                                        " - " + str(user_info['requestor'])))]
                zabbix_sender.send(packet)
            except:
                pass
        except:
            logger.info("Failed send email for user registration " + str(user_info['user_email'] + 
                        " - " + str(user_info['requestor'])))
            try:
                packet = [ZabbixMetric('CentOS PODS Dev Master', 'django.log.user_activity', 
                                       "Failed send email for user registration " + str(user_info['user_email'] + 
                                        " - " + str(user_info['requestor'])))]
                zabbix_sender.send(packet)
            except:
                pass