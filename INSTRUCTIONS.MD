**Execution instructions**

**Server**:
To run the server, go to 'src' folder and run
```
python3 start-server.py <protocol> <options>
```
Supported protocols options are:
- gbn (Go Back N)
- saw (Stop and Wait)

To display options run
```
python3 start-server.py -h
```

**Client**:

To run a client, go to 'src' folder and run:

If you want to start a downloading client:
```
python3 download-file.py <protocol> <options> <filename>
```

If you want to start an uploading client:
```
python3 upload-file.py <protocol> <options> <filename>
```
Supported protocols options are:
- gbn (Go Back N)
- saw (Stop and Wait)

To display options run any of these two lines
```
python3 download-file.py -h
python3 upload-file.py -h
```

Filename is the name of the file you want to download or upload. This file should either be in "server_fs_root" or "client_fs_root", depending on the operation, and will be saved in the corresponding folder between those two.