#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# A simple python script to get active IPs on LAN managed 
# with a CBN CG6640E router model. This script has been 
# optimizated to firmware CG6640-3.5.1.10a-SH therefore
# using a different firmware version can cause errors.
#
# gNrg(at)tuta.io
#
import os
from contextlib import closing
from selenium.webdriver import Firefox # pip install selenium
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup # easy_install beautifulsoup4
from getpass import getpass

# This function prints the script banner
def print_header():
    os.system("clear")
    print "+--------------------------------------------------+"
    print "|                                                  |"
    print "|                    CG6640E.py                    |"
    print "|                     by  gNrg                     |"
    print "|                                                  |"
    print "+--------------------------------------------------+"
    print ""

# This function shows menu options
def show_menu_options():
    print("\t1 - )   Show all clients")
    print("\t2 - )   Show WiFi clients")
    print("\t3 - )   Show Ethernet clients")
    print("\t4 - )   Show clients and save")
    print("\t5 - )   Exit")
    print("\n")
    option = raw_input("   Choose one of this options: ")
    return option

# This function print a client using a pretty format
def print_client(client, known_macs):
    n = get_known_MAC_name(str(client[1][0]), known_macs)
    if n: name = n
    else: name = 'UNKNOWN HOST!'
    if client[0] != []: name += ' - ' + str(client[0][0])
    print ""
    print "+--------------------------------------------------+"
    print "|     Client:  " + name
    print "+--------------------------------------------------+"
    print "|        MAC:  " + str(client[1][0])
    print "|         IP:  " + str(client[2][0])
    print "|     Uptime:  " + str(client[3][0])
    if str(client[4][1]) == ' Ethernet': print "|  Conn Type:  " + 'Ethernet'
    else:
        print "|  Conn Type: " + str(client[4][1])
        print "|      BSSID:  " + str(client[4][4])
        print "|   Protocol:  " + str(client[4][6])
    print "|  Addr Type:  " + str(client[5][0])
    print "+--------------------------------------------------+"
    print ""

# This function return a string with a machine name if the MAC given exists into KnownMACs file
def get_known_MAC_name(MAC, known_macs):
    name = ''
    for m in known_macs:
        if m[0] == MAC:
            name = m[1]
    return name

# This function return a string with all the information using a pretty format
def get_file_content(lan_clients_data, known_macs):
    text = "LAN CLIENTS INFORMATION\n"
    for client in lan_clients_data:
        n = get_known_MAC_name(str(client[1][0]), known_macs)
        if n: name = n
        else: name = 'UNKNOWN HOST!'
        if client[0] != []: name += ' - ' + str(client[0][0])
        text += "+--------------------------------------------------+\n"
        text += "|     Client:  " + name + '\n'
        text += "+--------------------------------------------------+\n"
        text += "|        MAC:  " + str(client[1][0]) + '\n'
        text += "|         IP:  " + str(client[2][0]) + '\n'
        text += "|     Uptime:  " + str(client[3][0]) + '\n'
        if str(client[4][1]) == ' Ethernet': text += "|  Conn Type:  " + 'Ethernet\n'
        else:
            text += "|  Conn Type: " + str(client[4][1]) + '\n'
            text += "|      BSSID:  " + str(client[4][4]) + '\n'
            text += "|   Protocol:  " + str(client[4][6]) + '\n'
        text += "|  Addr Type:  " + str(client[5][0]) + '\n'
        text += "+--------------------------------------------------+\n\n"
    return text

# This function reads a KnownMACs file and return the values on a list
def get_known_macs():
    known_macs = []
    path = raw_input("Enter complete path of KnownMACs text file: ")
    try:
        file = open(path, 'r')
        print "\nOpen file:\t\t\t[[ OK ]]"
        file_content = file.read()
        file_lines = []
        i = 0
        for line in file_content.split("\n"):
            a, b = line.split(" ")
            known_macs.append([])
            known_macs[i].append(a)
            known_macs[i].append(b)
            i += 1
        print "Getting file information:\t[[ OK ]]"
        file.close()
        print "Close file:\t\t\t[[ OK ]]"
        return known_macs
    except IOError: 
        print("Open/Read file:  [[ ERROR ]]")
        print("\tCheck if the path is correct.")
        print("\tCheck if do you have permissions for read the file.")
        print("\tThen, try again.")
        sys.exit(0)

print_header()
# Get user information
user = raw_input('\nEnter username [Left blank for default]: ')
password = getpass('Enter password [Left blank for default]: ')
ip = raw_input('Router IP [Left blank for 192.168.1.1]: ')

if not user: user = 'admin'
if not password: password = 'admin'
if not ip: ip = '192.168.1.1'

# Get KnownMACs file content
known_macs = []
load_mac_file = raw_input('\nDo you want to load KnownMACs file?[y/N]: ')
if load_mac_file == 'y' or load_mac_file == 'Y': 
    known_macs = get_known_macs() # MAC [0] - Name [1]

print_header()

login_url = "http://" + ip + "/login/Login.txt?password=" + password + "&user=" + user
target_url = "http://" + ip + "/basicLanUsers.html"

print "\nGetting information from the router..."
# Use firefox to get page with javascript generated content
with closing(Firefox()) as browser:
    browser.get(login_url)
    browser.get(target_url)
    # button = browser.find_element_by_name('button')
    # button.click()
    # Wait for the page/js to load
    try:
        WebDriverWait(browser, timeout=10).until(
            lambda x: x.find_element_by_name('instance'))
    except: 
        print "Getting info:\t\t[[ ERROR ]]\n"
        exit(-1)
    # Store it to string variable
    page_source = browser.page_source
print "Getting info:\t\t[[ OK ]]\n"

# Format the string to navigate it using BeautifulSoup
soup = BeautifulSoup(page_source, 'lxml')
lan_clients = soup.find_all(attrs={"name": "instance"})
lan_clients_data = []
client_data = []
# Remove blanks from list
for client in lan_clients:
    unformatted_client_data = client.contents
    for data in unformatted_client_data:
        if data != u' ':
            client_data.append(data.contents)
    lan_clients_data.append(client_data)
    client_data = []

if len(lan_clients_data) > 0:
    print "Clients Found:\t\t[ " + str(len(lan_clients_data)) + " ]\n"
else: 
    print "Clients Found:\t\t[ 0 ]\n"
    exit(0)

# Show&Process menu options
option = show_menu_options()
print_header()
if option == '1':
    for lcd in lan_clients_data:
        print_client(lcd, known_macs)
elif option == '2':
    for lcd in lan_clients_data:
        if lcd[4][1] != ' Ethernet':
            print_client(lcd, known_macs)
elif option == '3':
    for lcd in lan_clients_data:
        if lcd[4][1] == ' Ethernet':
            print_client(lcd, known_macs)
elif option == '4':
    for lcd in lan_clients_data:
        print_client(lcd, known_macs)
    path = raw_input("WARNING!!! If the file exists, it will be overwrite.\nEnter complete path and name of new text file: ")
    try:
        file = open(path, 'w')
        print "\nCreating/Open file:\t[[ OK ]]"
        file_content = get_file_content(lan_clients_data, known_macs)
        file.write(file_content)
        print "Writing file:\t\t[[ OK ]]"
        file.close()
        print "Close file:\t\t[[ OK ]]"
        print "You can see the new file on: " + path
    except IOError: 
        print("Creating/Open file:  [[ ERROR ]]")
        print("\tCheck if the path is correct.")
        print("\tCheck if do you have permissions for create files in this folder.")
        print("\tThen, try again.")
        sys.exit(0)
elif option == '5': exit(0)