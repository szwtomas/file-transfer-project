File Transfer System Distribuidos

Assumptions:

- Files to upload and download can not be larger than 4gb
- When uploading, it will not overwrite the file if it already exists, it has to be deleted first (for security reasons)

Handshake:

Client first Message:

- operation: 1 byte indicating if the operation is download or upload (0 for download, other for upload)
- path_size: 1 byte indicating the path's size in bytes
- path of size path_size
- file_size: 4 bytes indicating size of the file (if operation is upload)

Server first response Message:

- Response to Download Request:

  - status: 1 byte indicating if there was an error with the request (0 indicating OK, 1 indicating Error)
  - file_size: 4 bytes indicating the file size (only if status == OK)

- Response to Upload Request:
  - status: 1 byte indicating if there was an error with the request (0 indicating OK, 1 indicating Error)

Data messages:

- 4 bytes: Offset of the chunk
- 4 bytes: size of the chunk
- chunk_size bytes: payload
