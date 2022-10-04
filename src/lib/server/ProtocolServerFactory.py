from .TCPServer import TCPServer
from .SAWServer import SAWServer
from .GBNServer import GBNServer
from .exceptions.ProtocolNotSupportedException import ProtocolNotSupportedException
from .constants import TCP_PROTOCOL, SAW_PROTOCOL, GBN_PROTOCOL
from lib.server.logger import log_tcp, log_saw, log_gbn


class ProtocolServerFactory:

    def __init__(self):
        self.protocols = {
            TCP_PROTOCOL: TCPServer(),
            SAW_PROTOCOL: SAWServer(),
            GBN_PROTOCOL: GBNServer()
        }
        
        self.loggers = {
            TCP_PROTOCOL: log_tcp,
            SAW_PROTOCOL: log_saw,
            GBN_PROTOCOL: log_gbn
        }


    def is_supported_protocol(self, protocol: str):
        return protocol.lower() in self.protocols


    def get_server_from_selected_protocol(self, protocol: str):
        if not self.is_supported_protocol(protocol):
            raise ProtocolNotSupportedException(f"Protocol {protocol} is not suported")

        return self.protocols.get(protocol.lower(), None)


    def get_protocol_logger(self, protocol: str):
        if not self.is_supported_protocol(protocol):
            raise ProtocolNotSupportedException(f"Protocol {protocol} is not suported")

        return self.loggers.get(protocol.lower(), None)    

