from .TCPClient import TCPClient
from .SaWClient import SaWClient
from .GBNClient import GBNClient
from .constants import TCP_PROTOCOL
from .constants import SAW_PROTOCOL
from .constants import GBN_PROTOCOL
from lib.server.exceptions.ProtocolNotSupportedException import ProtocolNotSupportedException

class ClientFactory:

    def __init__(self):
        self.clients = {
            TCP_PROTOCOL: TCPClient(),
            SAW_PROTOCOL: SaWClient(),
            GBN_PROTOCOL: GBNClient()
        }

    
    def is_supported_protocol(self, protocol: str) -> bool:
        return protocol.lower() in self.clients

    
    def get_client_by_protocol(self, protocol: str):
        if not self.is_supported_protocol(protocol):
            raise ProtocolNotSupportedException(f"Protocol {protocol} is not suported for the client")

        return self.clients.get(protocol.lower(), None)

