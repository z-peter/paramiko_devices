# kill the script if it still runs. Change path if used elsewhere
kill -9 `pgrep -f slot_info_mattermost`; sleep 10; /usr/bin/python -u /home/pela01/hua_mcast_bug_info_slot_info_mattermost.py  
