#!/bin/sh

#if permission denied error run
#$ chmod +x run_hash_check.sh 
#only env is FILENAME

#prints diff between sha1 hashes of client and server files with the same name

cd client_fs_root/
sha1sum "$1" > ../sha-client.txt

cd ..
cd server_fs_root/
sha1sum "$1" > ../sha-server.txt

cd ..

diff ./sha-client.txt ./sha-server.txt
rm ./sha-client.txt
rm ./sha-server.txt
