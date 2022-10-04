from ..constants import PAYLOAD_SIZE_BYTES, PACKET_SEQUENCE_BYTES, PACKET_SIZE
from ..exceptions.UDPMessageNotReceivedException import UDPMessageNotReceivedException

def read_until_expected_seq_number(read_message, expected_seq_number):
    retries = 0
    max_retries = 2
    message = read_message()
    print(f"message read {message[:16]}")
    print("expected seq number", expected_seq_number)
    print(f"received seq number {_get_seq_number_from_message(message)}")
    while _get_seq_number_from_message(message) != expected_seq_number and retries < max_retries:
        retries += 1
        message = read_message()
        print("expected seq number", expected_seq_number)
        print(f"received seq number {_get_seq_number_from_message(message)}")
        print(f"message read {message[:16]}, retry number {retries}")
    
    if retries == max_retries:
        raise UDPMessageNotReceivedException(f"Message of sequence number: {expected_seq_number} was not received")

    return message

def _get_seq_number_from_message(data):
    return int.from_bytes(data[:PACKET_SEQUENCE_BYTES], "big")


def send_message_until_acked(read_message, send_message, seq_number, data):
    retry_count = 0
    max_retries = 10
    while retry_count < max_retries:
        print('envio data')
        # for i in range(3):
        send_message(data)
        try:
            data = read_until_expected_seq_number(read_message, seq_number + 1)
            return data
        except UDPMessageNotReceivedException:
            print('no recibí respuesta, vuelvo a enviar')
            retry_count += 1
            continue
    
    print("devuelvo False")
    return False

def get_empty_bytes(amount):
    empty = 0
    return empty.to_bytes(amount, "big")


def build_ack_message(file_size: int, is_error=False):
    data = b""
    seq_number = 0
    data += seq_number.to_bytes(PACKET_SEQUENCE_BYTES, "big")
    if is_error:
        data += b"\x01"
    else:
        data += b"\x00"
    data += file_size.to_bytes(PAYLOAD_SIZE_BYTES, "big")
    data += get_empty_bytes(PACKET_SIZE - len(data))
    return data