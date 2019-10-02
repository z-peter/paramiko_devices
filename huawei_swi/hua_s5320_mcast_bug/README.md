# Huawei mcast bug fix script

This script is used to check if the mcast bug for Huawei S5320 is present. If the script finds that the bridge-table contains the wrong flag it corrects it.

The switches that are checked are stored in the  file s5320_switches_prod. When new S5320 switches are installed in the production network, the switchnames must be added to the file. 

There are two scripts running. One for each mcast VLAN (3980 and 3981). The scripts are scheduled by crontab. See  crontab_info for how to set up crontab. the crontab starts two bash scripts which in turn starts the python scripts.

Finally the aaa.csv must be updated with your tacacs credentials to be able to log into the switches.

All files must be stored under the same directory. If not you need to change the path in the two python scripts.

