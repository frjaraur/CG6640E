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
import sys
from contextlib import closing
from selenium.webdriver import Firefox # pip install selenium
from selenium.webdriver.support.ui import WebDriverWait

from bs4 import BeautifulSoup # easy_install beautifulsoup4

from getpass import getpass

# This function shows menu options
def show_menu_options():
    print("\t1 - )   Show all clients")
    print("\t2 - )   Show WiFi clients")
    print("\t3 - )   Show Ethernet clients")
    print("\t4 - )   Show all clients and export to a text file")
    print("\t5 - )   Exit")
    print("\n")
    option = raw_input("   Choose one of this options: ")
    return option

# This function print a client using a pretty format
def print_client(client):
    if client[0] == []: name = 'Unknown PC'
    else: name = str(client[0][0])
    print ""
    print "+---------------------------------------------+"
    print "| New Client:  " + name
    print "+---------------------------------------------+"
    print "|        MAC:  " + str(client[1][0])
    print "|         IP:  " + str(client[2][0])
    print "|     Uptime:  " + str(client[3][0])
    if str(client[4][1]) == ' Ethernet': print "|  Conn Type:  " + 'Ethernet'
    else:
        print "|  Conn Type: " + str(client[4][1])
        print "|      BSSID:  " + str(client[4][4])
        print "|   Protocol:  " + str(client[4][6])
    print "|  Addr Type:  " + str(client[5][0])
    print "+---------------------------------------------+"
    print ""

# This function return a string with all the information using a pretty format
def get_file_content(lan_clients_data):
    text = "LAN CLIENTS INFORMATION\n"
    for client in lan_clients_data:
        if client[0] == []: name = 'Unknown PC'
        else: name = str(client[0][0])
        text += "+---------------------------------------------+\n"
        text += "| New Client:  " + name + '\n'
        text += "+---------------------------------------------+\n"
        text += "|        MAC:  " + str(client[1][0]) + '\n'
        text += "|         IP:  " + str(client[2][0]) + '\n'
        text += "|     Uptime:  " + str(client[3][0]) + '\n'
        if str(client[4][1]) == ' Ethernet': text += "|  Conn Type:  " + 'Ethernet\n'
        else:
            text += "|  Conn Type: " + str(client[4][1]) + '\n'
            text += "|      BSSID:  " + str(client[4][4]) + '\n'
            text += "|   Protocol:  " + str(client[4][6]) + '\n'
        text += "|  Addr Type:  " + str(client[5][0]) + '\n'
        text += "+---------------------------------------------+\n\n"
    return text

# Get user information
user = raw_input('\nEnter username [Left blank for default]: ')
password = getpass('Enter password [Left blank for default]: ')

if not user: user = 'admin'
if not password: password = 'admin'

login_url = "http://192.168.1.1/login/Login.txt?password=" + password + "&user=" + user
target_url = "http://192.168.1.1/basicLanUsers.html"

print "\nGetting information from the router..."
# Use firefox to get page with javascript generated content
with closing(Firefox()) as browser:
    browser.get(login_url)
    browser.get(target_url)
    # button = browser.find_element_by_name('button')
    # button.click()
    # Wait for the page/js to load
    WebDriverWait(browser, timeout=10).until(
        lambda x: x.find_element_by_name('instance'))
    # Store it to string variable
    page_source = browser.page_source
print "Getting info:  [[ OK ]]\n"

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
    print "Clients Found:  [ " + str(len(lan_clients_data)) + " ]"
else: 
    print "Clients Found:  [ 0 ]"
    sys.exit(0)

# Show&Process menu options
option = show_menu_options()
if option == '1':
    for lcd in lan_clients_data:
        print_client(lcd)
elif option == '2':
    for lcd in lan_clients_data:
        if lcd[4][1] != ' Ethernet':
            print_client(lcd)
elif option == '3':
    for lcd in lan_clients_data:
        if lcd[4][1] == ' Ethernet':
            print_client(lcd)
elif option == '4':
    for lcd in lan_clients_data:
        print_client(lcd)
    path = raw_input("WARNING!!! If the file exists, it will be overwrite.\nEnter complete path and name of new text file: ")
    try:
        file = open(path, 'w+')
        print "\nCreating/Open file:  [[ OK ]]"
        file_content = get_file_content(lan_clients_data)
        file.write(file_content)
        print "Writing file:  [[ OK ]]"
        file.close()
        print "Close file:  [[ OK ]]"
        print "You can see the new file on: " + path
    except IOError: 
        print("Creating/Open file:  [[ ERROR ]]")
        print("\tCheck if the path is correct.")
        print("\tCheck if do you have permissions for create files in this folder.")
        print("\tThen, try again.")
        sys.exit(0)
elif option == '5': exit(0)


#https://stackoverflow.com/questions/8960288/get-page-generated-with-javascript-in-python
#https://selenium-python.readthedocs.org/api.html#selenium.webdriver.remote.webdriver.WebDriver
#http://www.crummy.com/software/BeautifulSoup/bs4/doc/index.html#navigating-using-tag-names
