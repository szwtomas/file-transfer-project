from .TCPClient import TCPClient
from .SaWClient import SaWClient
from .GBNClient import GBNClient
from .constants import TCP_PROTOCOL, SAW_PROTOCOL, GBN_PROTOCOL
from lib.server.exceptions.ProtocolNotSupportedException import ProtocolNotSupportedException


class ClientFactory:

    def __init__(self):
        
        self.clients = {
            TCP_PROTOCOL: TCPClient(),
            SAW_PROTOCOL: SaWClient(),
            GBN_PROTOCOL: GBNClient()
        }


    def _is_supported_protocol(self, protocol: str) -> bool:
        return protocol.lower() in self.clients


    def _verify_valid_protocol(self, protocol):
        if not self._is_supported_protocol(protocol):
            error_message = f"Protocol {protocol} not supported"
            raise ProtocolNotSupportedException(error_message)


    def get_client_by_protocol(self, protocol: str):
        self._verify_valid_protocol(protocol)
        return self.clients[protocol.lower()]

