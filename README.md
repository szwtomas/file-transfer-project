File Transfer System Distribuidos

Assumptions:

- Files to upload and download can not be larger than 4gb

Client first Message:

- operation: 1 byte indicating if the operation is download or upload (0 for download, other for upload)
- path_size: 1 byte indicating the path's size in bytes
- path of size path_size
- if operation is upload, size of the file (max 4gb)
