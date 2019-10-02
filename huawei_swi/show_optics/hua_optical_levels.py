# -*- coding: utf-8 -*-
# 
# Peter Larsson IP Network
# 20180615
'''
The purpose of this program is to perform an inventory of Huawei switch info regarding MC flag per slot.
    - Paramiko is used to logg in to devices.
    - The aaa.csv needs to be filled in with your tacacs credentials
    - Switch info is stored in file
'''
import json
import pprint
import argparse
import paramiko
import time
import socket
import re
import requests
import sys
import time
import getpass



pp = pprint.PrettyPrinter(indent=4)


def get_hua_info(device, device_ip,username, password, allinfo):
    """
    Retrive device info by paramiko and save relevant info to file.
    :param device: Device hostname
    :param device_ip: Device IP address (paramiko requires IP addres)
    :param aaafilename: aaa user/passwd, edit the file with you credentials
    :param s5320_file: The file to store the information
    :return:
    """

    # Create instance of SSHClient object
    remote_conn_pre = paramiko.SSHClient()

    # Automatically add untrusted hosts (make sure okay for security policy in your environment)
    remote_conn_pre.set_missing_host_key_policy(
        paramiko.AutoAddPolicy())
    # get user credentials from file

    # initiate SSH connection
    print(device)
    print(time.ctime())
    user = str(username)
    passwd = str(password)

    try:
        remote_conn_pre.connect(device_ip, username=user, password=passwd, look_for_keys=False, allow_agent=False)
    except:
        #with open(filename, 'a') as outfile:
            #outfile.write("no connection to " + device)
        print('ssh error')
        print(time.ctime())
        return
    else:
        pass

    # Use invoke_shell to establish an 'interactive session'
    remote_conn = remote_conn_pre.invoke_shell()
    print("Interactive SSH session established")

    # Strip the initial router prompt
    output = remote_conn.recv(1000)

    # See what we have
    #print output

    optical_val ={}
    optical_list = []
    disable_paging(remote_conn)
    slot_wrong_flag = []
    remote_conn.send("screen-length 0 temporary \n")
    buff = ''
    while not buff.endswith('>'):
        resp = remote_conn.recv(9999)
        buff += resp

    remote_conn.send("display transceiver verbose \n")
    buff = ''
    while not buff.endswith('>'):
        resp = remote_conn.recv(99999)
        buff += resp
    output = buff.split("\n")
    for lines in output:
        if "GigabitEthernet" in lines:
            if "absent" not in lines:
                parts = lines.split()
                interface = parts[0]
        if "RX Power(dBM)" in lines:
            parts = lines.split(":")
            values = [parts[1].rstrip()]
            optical_val = {}
            optical_val[interface] = values
            optical_list.append(optical_val)
        if "RX Power Low  Threshold(dBM)" in lines:
            parts = lines.split(":")
            values.append(parts[1].rstrip())
            if float(values[0]) <= float(values[1]):
                values.append("optical level not ok")
            else:
                values.append("optical level ok")
    print("Number of interfaces: " + str(len(optical_list)))
    #print optical_list
    print("%21s %10s %8s %22s" % ("Optical Interface", "Value", "Threshold", "Status"))
    for interface in optical_list:
        for key, value in interface.items():
            if allinfo == "no":
                if "optical level not ok" in value[2]:
                    output = "%8s %10s %22s" % (value[0],value[1],value[2])
                    print("%21s" % (''.join(interface.keys())) + ', ' + output)
            else:
                output = "%8s %10s %22s" % (value[0], value[1], value[2])
                print("%21s" % (''.join(interface.keys())) + ', ' + output)
    return


def disable_paging(remote_conn):
    '''Disable paging on a device'''
    remote_conn.send("terminal length 0\n")
    time.sleep(0.5)
    # Clear the buffer on the screen
    output = remote_conn.recv(1000)

    return output

def parseArgs():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    pparser = argparse.ArgumentParser(formatter_class=argparse.HelpFormatter)
    parser.add_argument('-s', '--swi', help="switch host name")
    parser.add_argument('-u', '--username', help="your tacacs username", default=getpass.getuser())
    parser.add_argument('-a', '--allinfo', help="Type yes if all interface values shall be displayed",
                        type=str, default='no')
    parser.add_argument('-p', '--password', help='Specify password', type=Password, default=Password.DEFAULT)
    return parser.parse_args()


class Password:
    DEFAULT = 'Prompt if not specified'
    def __init__(self, value):
        if value == self.DEFAULT:
            value = getpass.getpass('Tacacs Password: ')
        self.value = value

    def __str__(self):
        return self.value


def main():
    args = parseArgs()
    swi = args.swi
    username = args.username
    password = args.password
    allinfo = args.allinfo
    try:
        device_ip = socket.gethostbyname(swi.rstrip())
    except:
        print("Swicth hostname not found")
        return
    get_hua_info(swi, device_ip, username, password, allinfo)

    return


main()
