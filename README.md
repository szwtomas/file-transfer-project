File Transfer System Distribuidos

Assumptions:

- Files to upload and download can not be larger than 4gb
- When uploading, it will not overwrite the file if it already exists, it has to be deleted first (for security reasons)

Handshake:

Client first Message:

- Sequence Number: 4 bytes indicating the number of the message
- operation: 1 byte indicating if the operation is download or upload (0 for download, other for upload)
- path_size: 1 byte indicating the path's size in bytes
- path of size path_size
- file_size: 4 bytes indicating size of the file (if operation is upload)

Server first response Message:

- Response to Download Request:

  - packet sequence number: 4 bytes
  - status: 1 byte indicating if there was an error with the request (0 indicating OK, 1 indicating Error)
  - file_size: 4 bytes indicating the file size (only if status == OK)

- Response to Upload Request:
  - status: 1 byte indicating if there was an error with the request (0 indicating OK, 1 indicating Error)

**_Data messages_**:

- 4 bytes: Sequence number
- 4 bytes: size of the chunk
- chunk_size bytes: payload

**_ACK_**:

- 4 bytes indicating the sequence number of the acked packet
- 4 bytes indicating total of bytes received overall

**Stop And Wait Protocol**

- The first message interchange is the same as in TCP, because we are already using an ACK response
- Once the file transfer starts, the protcol is almost the same as in TCP but responding with an ACK for every received message
- The ACK consists on the offset received, and for every message both the server and client sends, they must wait for the ACK to be received in order to send the next message
- If a message with a different offset than expected is received, the message is dropped
