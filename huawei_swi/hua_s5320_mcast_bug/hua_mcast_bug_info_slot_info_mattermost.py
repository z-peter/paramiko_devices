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



pp = pprint.PrettyPrinter(indent=4)


def get_sp_info(device, device_ip,aaafilename,s5320_file):
    """
    Retrive device info by paramiko and save relevant info to file.
    :param device: Device hostname
    :param device_ip: Device IP address (paramiko requires IP addres)
    :param aaafilename: aaa user/passwd, edit the file with you credentials
    :param s5320_file: The file to store the information
    :return:
    """
    headers = {
        'Content-Type': 'application/json',
    }
    filename = s5320_file
    # Create instance of SSHClient object
    remote_conn_pre = paramiko.SSHClient()

    # Automatically add untrusted hosts (make sure okay for security policy in your environment)
    remote_conn_pre.set_missing_host_key_policy(
        paramiko.AutoAddPolicy())
    # get user credentials from file
    username, password = get_aaa(aaafilename)
    user = str(username)
    passwd = str(password)

    # initiate SSH connection
    print device
    print time.ctime()
    try:
        remote_conn_pre.connect(device_ip, username=user, password=passwd, look_for_keys=False, allow_agent=False)
    except:
        #with open(filename, 'a') as outfile:
            #outfile.write("no connection to " + device)
        return
    else:
        pass

    # Use invoke_shell to establish an 'interactive session'
    remote_conn = remote_conn_pre.invoke_shell()
    # print "Interactive SSH session established"

    # Strip the initial router prompt
    output = remote_conn.recv(1000)

    # See what we have
    #print output


    disable_paging(remote_conn)



    # ssh to the hua switch and go to diagnose cli tree
    remote_conn.send("system-view \n")
    buff = ''
    while not buff.endswith(']'):
        resp = remote_conn.recv(9999)
        buff += resp
    remote_conn.send("diagnose \n")
    buff = ''

    # Find out hpw many slots in the stack
    while not buff.endswith(']'):
        resp = remote_conn.recv(9999)
        buff += resp
    remote_conn.send("display stack \n")
    buff = ''

    while not buff.endswith(']'):
        resp = remote_conn.recv(9999)
        buff += resp
    output = buff.split("\n")
    i = 0
    for lines in output:
        if "S5320" in lines:
            i +=1

    # Time to loop through and get flag info for all included slots
    slot_wrong_flag = []
    with open(filename, 'a') as outfile:
        #outfile.write(device.rstrip() + " number of slots are " + str(i) + "\n")
        k = 0
        while k < i:
            remote_conn.send("display lsw table slot " + str(k) + " l2-table 0 vlan 3980 \n")
            buff = ''
            while not buff.endswith(']'):
                resp = remote_conn.recv(99999)
                buff += resp
            output = buff.split("\n")
            # save slot and device which has flag not correct (=0x0)
            for lines in output:
                if "IPV4_IP_MC_BRIDGING_EN=0x0" in lines:
                    outfile.write("IPV4_IP_MC_BRIDGING_EN=0x0" + " " + device.rstrip() + " slot " + str(k) + "\n")
                    slot_wrong_flag.append(k)
            k += 1

        # loop through slots with wrong flag and set it to 0x1
        #print slot_wrong_flag
        if slot_wrong_flag != None:
            for slot in slot_wrong_flag:
                #print "slot " + str(slot) + " " + device.rstrip() + " is set to 0x1"
                # ssh to the hua switch and go to diagnose cli tree
                remote_conn.send("set lsw table slot " + str(slot) +
                                 " common 0 table-name vlan 3980 1 field-name IPV4_IP_MC_BRIDGING_EN 1 \n")
                buff = ''
                while not buff.endswith(']'):
                    resp = remote_conn.recv(9999)
                    buff += resp


        #print output


    return slot_wrong_flag


def get_aaa(aaafilename):
    with open(aaafilename) as f:
        for line in f:
            parts = line.split(',')
            username = parts[0]
            password = parts[1].rstrip()
        return (username, password)


def disable_paging(remote_conn):
    '''Disable paging on a Cisco router'''

    remote_conn.send("terminal length 0\n")
    time.sleep(0.5)

    # Clear the buffer on the screen
    output = remote_conn.recv(1000)

    return output

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--swi', help="Huawei s5320 hostname, e.g. gnd-f3-as-a, if no argument all s5320 will be searched")
    return parser.parse_args()


def main():
    s5320_file = "s5320_switches_prod"
    aaafilename = "aaa.csv"
    args = parseArgs()
    swi = args.swi

    headers = {
        'Content-Type': 'application/json',
    }
    #data = '{"text": "Hello, this is some text\\nThis is more text. :tada:"}'


    switch_list = []
    filename = "s5320_info_wrong_flag"
    # make sure result file is empty
    open(filename, 'w').close()
    if swi == None:
        with open(s5320_file, 'r') as outfile:
            for device in outfile:
                # print device
                try:
                    device_ip = socket.gethostbyname(device.rstrip())
                    #print device_ip
                except:
                    with open(filename, 'a') as outfile:
                        # outfile.write(device.rstrip() + " no ip address, nslookup failed \n")
                        pass
                else:
                    flag_status = get_sp_info(device, device_ip, aaafilename, filename)
        k = 0
        if len(flag_status) != 0:
            with open(filename,'r') as outfile:
                for device in outfile:

                    print(" test %s " % device)
                    if k == 0:
                        #item = '{"text": "test %s \n"}' % device
                        item = '{"text": "The script has walked through all switches for VLAN 3980 \n' \
                               'The following switches had the flag set to wrong value \n' \
                               'It has been set to the correct value \n %s \n' % device
                        print item
                    else:
                        item = '%s \n' % device
                    switch_list.append(item)
                    k +=1
            switch_list.append('"}')
            data = ''.join(switch_list)
            print data
        else:
            data = '{"text": "The script has walked through all switches for VLAN 3980 \n No wrong flags was found"}'
        response = requests.post('https://mattermost.comhem.com/hooks/zqcsag65c7b75qmrob3rzui59o', headers=headers,data=data)
        print response
    else:
        device_ip = socket.gethostbyname(swi.rstrip())
        flag_status = get_sp_info(swi, device_ip, aaafilename, filename)
        if len(flag_status) != 0:
            with open(filename,'r') as outfile:
                for device in outfile:
                    print(" test %s " % device)
                    data = '{"text": "test %s "}' % device
                    print data
        else:
            data = '{"text": "The script has walked through all switches for VLAN 3980 \n No wrong flags was found"}'
            print data
        response = requests.post('https://mattermost.comhem.com/hooks/zqcsag65c7b75qmrob3rzui59o', headers=headers,data=data)
        print response
    return


main()
