#!/bin/sh

#if permission denied error run
#$ chmod +x run_hash_check.sh 
#only env is FILENAME

#prints diff between md5 hashes of client and server files with the same name

cd client_fs_root/
md5sum "$1" > ../md5-client.txt

cd ..
cd server_fs_root/
md5sum "$1" > ../md5-server.txt

cd ..

diff ./md5-client.txt ./md5-server.txt
rm ./md5-client.txt
rm ./md5-server.txt
