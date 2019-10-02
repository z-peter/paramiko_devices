# Huawei S53xx capture-packet parser

This script log into a Huawei s53xx/s63xx and perform capture packet. 
It then parse the data to be compliant with Wireshark import.
Wireshark usage:
file -> Import from hex dump
browse to the file from the script and import it -> Done! 

NB! The acl must be created manually in the switch 

On the srv-netscript-2 server virtualenv is used. To start the virtualenv do:

```bash
# Go to the following directory
cd /home/tech-shared/hua_optical_level
# Activate virtualenv
source venv/bin/activate
# When done running the script below, close virtualenv
deactivate
```

The script use argparse, i.e type:

```bash
cd ../get_hua_capture_packet
python hua_packet_capture.py --h
#Example, cpature packets 
python hua_packet_capture.py -s ksd-dsw-01 -u pela01 -i XGigabitEthernet0/0/17 -a 4099 -n 3 -t 10
```

Default your username on linux is filled in as username. When prompted for password, use your tacacs password.

 