#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Peter Larsson IP Network
# 20190513
'''
The purpose of this program is to parse huawei switch capture-packet to a wireshark compatible format
    - Paramiko is used to logging into devices.
    - Capture packets are stored in a filename to be copied to your PC to be opened by wireshark
    - Open the file from wireshark by File -> Import from hex dump (browse to the filename)
'''
import json
import pprint
import argparse
import paramiko
import time
import socket
import re
import sys
import getpass



pp = pprint.PrettyPrinter(indent=4)


def get_hua_info(device, device_ip,username, password, interface, filename, acl, num_packets, timeout):
    """
    Parameters required to capture packets. It stores the result in the filename.
    :param device:
    :param device_ip:
    :param username:
    :param password:
    :param interface:
    :param filename:
    :param acl:
    :param num_packets:
    :param timeout:
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
    #paramiko.util.log_to_file("filename.log")

    try:
        remote_conn_pre.connect(device_ip, username=user, password=passwd, look_for_keys=False, allow_agent=False)
    except:
        print('ssh error')
        print(time.ctime())
        return


    # Use invoke_shell to establish an 'interactive session'
    remote_conn = remote_conn_pre.invoke_shell()
    print("Interactive SSH session established")

    # Strip the initial router prompt
    output = remote_conn.recv(1000)

    disable_paging(remote_conn)
    remote_conn.send("screen-length 0 temporary \n")
    buff = ''
    while not buff.endswith('>'):
        resp = remote_conn.recv(9999)
        buff += resp

    remote_conn.send("system-view \n")
    buff = ''
    while not buff.endswith(']'):
        resp = remote_conn.recv(9999)
        buff += resp
    remote_conn.send("capture-packet interface " + interface + " acl " + acl +
                     " destination terminal packet-len 64 packet-num " + str(num_packets) + " time-out " + str(timeout) + "\n")
    buff = ''

    # Stop receiving data based on hua output
    while not 'length: 64 (expected)' in buff:
        resp = remote_conn.recv(99999)
        buff += resp
        # catch input capture-packet parameter error and send it to terminal
        if 'Error' in buff:
            print(buff)
            return
    output = buff.split("\n")

    # A few parameters to keep track of relevant data
    packet_list = list(range(0,250,10))
    i = 0
    k = 0

    # Time to parse the data
    with open(filename, 'a') as outfile:
        for lines in output:
            if '----' in lines:
                i += 1
                k = 0
            # Match on hex data
            m = re.match('^[0-9a-f ]+$', lines.rstrip())
            if m and (i % 2 != 0):
                if k == 0:
                    print('# packet 1')
                    print('0000' + lines.rstrip())
                    outfile.write('0000' + lines.rstrip() + "\n")
                    k += 1
                else:
                    print('# packet ' + str(k+1))
                    print('00' + str(packet_list[k]) + lines.rstrip())
                    outfile.write('00' + str(packet_list[k]) + lines.rstrip() + "\n")
                    k += 1
    return

    return


def disable_paging(remote_conn):
    '''Disable paging on a device'''
    remote_conn.send("terminal length 0\n")
    time.sleep(0.5)
    # Clear the buffer on the screen
    output = remote_conn.recv(1000)

    return output

def parseArgs():
    timestr = time.strftime("%Y%m%d-%H%M%S")
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    pparser = argparse.ArgumentParser(formatter_class=argparse.HelpFormatter)
    parser.add_argument('-s', '--swi', help="switch host name")
    parser.add_argument('-u', '--username', help="your tacacs username", default=getpass.getuser())
    parser.add_argument('-i', '--interface', help="Type interface, e.g. XGigabitEthernet0/0/17 or Eth-Trunk 17",
                        type=str)
    parser.add_argument('-a', '--access_list', help="acl used to filter packet")
    parser.add_argument('-f', '--filename', help="filename where packets are stored",
                        default='-packet_cap-' + timestr + '.txt')
    parser.add_argument('-n', '--number_of_packets', help="nmber of packets to capture",
                        default='5')
    parser.add_argument('-t', '--timeout', help="capture timeout (if number of packets is not reached",
                        default='20')
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
    #filename = 'test_hua.txt'
    args = parseArgs()
    swi = args.swi
    username = args.username
    password = args.password
    interface = args.interface
    filename = swi + args.filename
    acl = args.access_list
    num_packets = args.number_of_packets
    timeout = args.timeout
    open(filename, 'w').close()
    try:
        device_ip = socket.gethostbyname(swi.rstrip())
    except:
        print("Swicth hostname not found")
        return
    get_hua_info(swi, device_ip, username, password, interface, filename, acl, num_packets, timeout)

    return


main()
