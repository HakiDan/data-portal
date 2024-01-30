import socket

smtp_server = 'smtp.gmail.com'

# Get the IP address
ip_address = socket.gethostbyname(smtp_server)

# Write the IP address to smtp_ip.txt
with open('/opt/docker/data-portal/smtp_ip.txt', 'w') as file:
    file.write(ip_address)