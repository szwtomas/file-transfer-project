from ..exceptions.UDPMessageNotReceivedException import UDPMessageNotReceivedException

def read_until_expected_seq_number(read_message, expected_seq_number):
    retries = 0
    max_retries = 10
    message = read_message()
    while _get_seq_number_from_message(message) != expected_seq_number and retries < max_retries:
        retries += 1
        message = read_message()
    
    if retries == max_retries:
        raise UDPMessageNotReceivedException(f"Message of sequence number: {expected_seq_number} was not received")

    return message

def _get_seq_number_from_message(data):
    return int.from_bytes(data[0:4])


def send_message_until_acked(read_message, send_message, seq_number, data):
    retry_count = 0
    max_retries = 10
    while retry_count < max_retries:
        send_message(data)
        try:
            data = read_until_expected_seq_number(read_message, seq_number)
            return data
        except UDPMessageNotReceivedException:
            retry_count += 1
            continue
    
    return False

