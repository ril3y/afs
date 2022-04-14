# afs
Auto File Sender
This is used to monitor when chia plots are created then auto matically query a remote server (over ssh) for mount points (only in the root of the drive ie: / for now) with the most free space available.  It then transfers the files over the network and then removes the plots once the transfer is completed.

## Todo:
Should anyone want to extend this here are things that need work.
1.  Command line arguments to start afs.
2.  Config file that could be used to configure afs.
3.  Password based authentication to remote server. (ssh keys w/o password only now)
4.  Remote filepaths (right now its / root only)
