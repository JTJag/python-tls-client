from dataclasses import dataclass
from typing import Optional, Dict, List
from .settings import ClientIdentifiers

@dataclass
class TLSClientAdapterConfig:
    # Examples:
    # Chrome --> chrome_103, chrome_104, chrome_105, chrome_106
    # Firefox --> firefox_102, firefox_104
    # Opera --> opera_89, opera_90
    # Safari --> safari_15_3, safari_15_6_1, safari_16_0
    # iOS --> safari_ios_15_5, safari_ios_15_6, safari_ios_16_0
    # iPadOS --> safari_ios_15_6
    #
    # for all possible client identifiers, check out the settings.py
    client_identifier: ClientIdentifiers = "chrome_120"
    
    # Set JA3 --> TLSVersion, Ciphers, Extensions, EllipticCurves, EllipticCurvePointFormats
    # Example:
    # 771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-5-13-18-51-45-43-27-17513,29-23-24,0
    ja3_string: Optional[str] = None
    
    # HTTP2 Header Frame Settings
    # Possible Settings:
    # HEADER_TABLE_SIZE
    # SETTINGS_ENABLE_PUSH
    # MAX_CONCURRENT_STREAMS
    # INITIAL_WINDOW_SIZE
    # MAX_FRAME_SIZE
    # MAX_HEADER_LIST_SIZE
    #
    # Example:
    # {
    #     "HEADER_TABLE_SIZE": 65536,
    #     "MAX_CONCURRENT_STREAMS": 1000,
    #     "INITIAL_WINDOW_SIZE": 6291456,
    #     "MAX_HEADER_LIST_SIZE": 262144
    # }
    h2_settings: Optional[Dict[str, int]] = None
    
    # HTTP2 Header Frame Settings Order
    # Example:
    # [
    #     "HEADER_TABLE_SIZE",
    #     "MAX_CONCURRENT_STREAMS",
    #     "INITIAL_WINDOW_SIZE",
    #     "MAX_HEADER_LIST_SIZE"
    # ]
    h2_settings_order: Optional[List[str]] = None
    
    # Supported Signature Algorithms
    # Possible Settings:
    # PKCS1WithSHA256
    # PKCS1WithSHA384
    # PKCS1WithSHA512
    # PSSWithSHA256
    # PSSWithSHA384
    # PSSWithSHA512
    # ECDSAWithP256AndSHA256
    # ECDSAWithP384AndSHA384
    # ECDSAWithP521AndSHA512
    # PKCS1WithSHA1
    # ECDSAWithSHA1
    #
    # Example:
    # [
    #     "ECDSAWithP256AndSHA256",
    #     "PSSWithSHA256",
    #     "PKCS1WithSHA256",
    #     "ECDSAWithP384AndSHA384",
    #     "PSSWithSHA384",
    #     "PKCS1WithSHA384",
    #     "PSSWithSHA512",
    #     "PKCS1WithSHA512",
    # ]
    supported_signature_algorithms: Optional[List[str]] = None
    
    # Supported Delegated Credentials Algorithms
    # Possible Settings:
    # PKCS1WithSHA256
    # PKCS1WithSHA384
    # PKCS1WithSHA512
    # PSSWithSHA256
    # PSSWithSHA384
    # PSSWithSHA512
    # ECDSAWithP256AndSHA256
    # ECDSAWithP384AndSHA384
    # ECDSAWithP521AndSHA512
    # PKCS1WithSHA1
    # ECDSAWithSHA1
    #
    # Example:
    # [
    #     "ECDSAWithP256AndSHA256",
    #     "PSSWithSHA256",
    #     "PKCS1WithSHA256",
    #     "ECDSAWithP384AndSHA384",
    #     "PSSWithSHA384",
    #     "PKCS1WithSHA384",
    #     "PSSWithSHA512",
    #     "PKCS1WithSHA512",
    # ]
    supported_delegated_credentials_algorithms: Optional[List[str]] = None
    
    # Supported Versions
    # Possible Settings:
    # GREASE
    # 1.3
    # 1.2
    # 1.1
    # 1.0
    #
    # Example:
    # [
    #     "GREASE",
    #     "1.3",
    #     "1.2"
    # ]
    supported_versions: Optional[List[str]] = None
    
    # Key Share Curves
    # Possible Settings:
    # GREASE
    # P256
    # P384
    # P521
    # X25519
    #
    # Example:
    # [
    #     "GREASE",
    #     "X25519"
    # ]
    key_share_curves: Optional[List[str]] = None
    
    # Cert Compression Algorithm
    # Examples: "zlib", "brotli", "zstd"
    cert_compression_algo: str = None
    
    # Additional Decode
    # Make sure the go code decodes the response body once explicit by provided algorithm.
    # Examples: null, "gzip", "br", "deflate"
    additional_decode: str = None
    
    # Pseudo Header Order (:authority, :method, :path, :scheme)
    # Example:
    # [
    #     ":method",
    #     ":authority",
    #     ":scheme",
    #     ":path"
    # ]
    pseudo_header_order: Optional[List[str]] = None
    
    # Connection Flow / Window Size Increment
    # Example:
    # 15663105
    connection_flow: Optional[int] = None
    
    # Example:
    # [
    #   {
    #     "streamID": 3,
    #     "priorityParam": {
    #       "weight": 201,
    #       "streamDep": 0,
    #       "exclusive": false
    #     }
    #   },
    #   {
    #     "streamID": 5,
    #     "priorityParam": {
    #       "weight": 101,
    #       "streamDep": false,
    #       "exclusive": 0
    #     }
    #   }
    # ]
    priority_frames: Optional[list] = None
    
    # Order of your headers
    # Example:
    # [
    #   "key1",
    #   "key2"
    # ]
    header_order: Optional[List[str]] = None
    
    # Header Priority
    # Example:
    # {
    #   "streamDep": 1,
    #   "exclusive": true,
    #   "weight": 1
    # }
    header_priority: Optional[List[str]] = None
    
    random_tls_extension_order: Optional[bool] = False
    
    force_http1: Optional[bool] = False
    
    # catch panics
    # avoid the tls client to print the whole stacktrace when a panic (critical go error) happens
    catch_panics: Optional[bool] = False
    
    debug: Optional[bool] = False
    
    certificate_pinning: Optional[Dict[str, List[str]]] = None
    
    def __post_init__(self):
        if self.client_identifier:
            custom_client_settings = [
                "ja3_string",
                "h2_settings",
                "h2_settings_order",
                "pseudo_header_order",
                "connection_flow",
                "priority_frames",
                "header_priority",
                "cert_compression_algo",
                "supported_versions",
                "supported_signature_algorithms",
                "supported_delegated_credentials_algorithms",
                "key_share_curves",
            ]
            conflicts = [
                field for field in custom_client_settings
                if getattr(self, field) is not None
            ]

            if conflicts:
                conflict_list = ", ".join(conflicts)
                raise ValueError(
                    f"You can't set 'client_identifier' at the same time as: {conflict_list}"
                )