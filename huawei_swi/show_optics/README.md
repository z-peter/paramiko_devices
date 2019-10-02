# Huawei S53xx optical level 

This script log into a Huawei s5300 script and outputs all optical levels. 

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
python3 hua_optical_levels.py -h
#Example, view all optical interfaces for the switch
python hua_optical_levels.py -s GSL-F24-AS-A -a y
#Example, only view optical interfaces with levels below threashold values for the switch
python hua_optical_levels.py -s GRI-F10-AS-A -a
# Store the output to a file named test
python hua_optical_levels.py -s GRI-F10-AS-A > test
```

Default your username on linux is filled in as username. When prompted for password, use your tacacs password.

 