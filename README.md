# afs
Auto File Sender
This is used to monitor when chia plots are created then auto matically query a remote server (over ssh) for mount points (only in the root of the drive ie: / for now) with the most free space available.  It then transfers the files over the network and then removes the plots once the transfer is completed.


##Example output

>[*] Current #of Pending Jobs: 1
>[*] Processing Job /mnt/output/testing/plot-k32-2022-04-14-01-11-0488a322defe4a442aec1a8d5f880dfc5a63af934c152083d225513c60775cbd.plot`
>[!] Please wait for the remote connection to open
>Opening Connection @ 172.16.10.7:65173 sending file /mnt/output/testing/plot-k32-2022-04-14-01-11-0488a322defe4a442aec1a8d5f880dfc5a63af934c152083d225513c60775cbd.plot >to /mnt/b4602285-f53f-42d5-ac03-b18bbd352c5c/plot-k32-2022-04-14-01-11-0488a322defe4a442aec1a8d5f880dfc5a63af934c152083d225513c60775cbd.plot
>Connecting.... #0 of 5
>[#] Sending File /mnt/output/testing/plot-k32-2022-04-14-01-11-0488a322defe4a442aec1a8d5f880dfc5a63af934c152083d225513c60775cbd.plot to /mnt/b4602285-f53f-42d5-ac03->b18bbd352c5c/plot-k32-2022-04-14-01-11-0488a322defe4a442aec1a8d5f880dfc5a63af934c152083d225513c60775cbd.plot Please wait...
>[#] File has been sent.
>[#] File transfer took 15.965821401278179 minutes!
>[!] Removed: /mnt/output/testing/plot-k32-2022-04-14-01-00-8e90d5b4a0163148ed5c8b092b28cbc6f992c57a199896af056da6c0f305709b.plot successfully


## Todo:
Should anyone want to extend this here are things that need work.
1.  Command line arguments to start afs.
2.  Config file that could be used to configure afs.
3.  Password based authentication to remote server. (ssh keys w/o password only now)
4.  Remote filepaths (right now its / root only)
