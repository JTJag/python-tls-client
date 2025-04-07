import http.client
import io
import json
import email
import base64
import ctypes
import http
import urllib3
from requests import Response
from urllib3.util.retry import Retry
from .cffi import request, freeMemory
from .exceptions import TLSClientExeption
from .config import TLSClientAdapterConfig
# from ._compat.http_response import HTTPResponse
from requests.structures import CaseInsensitiveDict
from requests.cookies import extract_cookies_to_jar
from requests.adapters import BaseAdapter, DEFAULT_RETRIES
from requests.utils import get_encoding_from_headers, select_proxy


class TLSClientAdapter(BaseAdapter):

    __attrs__ = [
        "max_retries",
        "config"
    ]

    def __init__(self, config: TLSClientAdapterConfig, max_retries: int = DEFAULT_RETRIES):
        super().__init__()

        self.config = config

        if max_retries == DEFAULT_RETRIES:
            self.max_retries = Retry(0, read=False)
        else:
            self.max_retries = Retry.from_int(max_retries)

    def normalize_headers(self, headers: dict[str, list[str]]) -> dict[str, str]:
        return {k: ", ".join(v) if isinstance(v, list) else str(v) for k, v in headers.items()}

    def build_response(self, req, resp):

        headers = CaseInsensitiveDict(
            {k: ", ".join(v) for k, v in resp["headers"].items()}
        )

        status_code = resp.get("status", 200)
        reason = http.HTTPStatus(status_code).phrase

        version = int(
            resp.get("usedProtocol", "HTTP/1.1").replace("HTTP/", "").replace(".", ""))

        mimetype, encoded_body = resp["body"].split(",")
        body_content = base64.urlsafe_b64decode(encoded_body)
        body = io.BytesIO(body_content)
        body_encoding = get_encoding_from_headers(headers)
        
        headers_msg = email.message.Message()
        for key, value in headers.items():
            headers_msg[key] = value
        
        urllib_response = urllib3.HTTPResponse(
            body,
            headers,
            status_code,
            version,
            reason,
            preload_content=False,
            original_response=type("FakeOriginalResponse", (), {"msg": headers_msg, "headers": headers_msg})()
        )
        
        response = Response()
        response.status_code = status_code
        response.headers = headers
        response.encoding = body_encoding
        response.raw = urllib_response
        response.reason = reason
        response._content = body_content
        response._content_consumed = True
        
        if isinstance(req.url, bytes):
            response.url = req.url.decode("utf-8")
        else:
            response.url = req.url

        # Add new cookies from the server.
        extract_cookies_to_jar(response.cookies, req, urllib_response)

        # Give the Response some context.
        response.request = req

        return response

    def send(self, req, stream=False, timeout=30, verify=True, cert=None, proxies=None):

        if req.body is None:
            encoded_body = ""
        elif isinstance(req.body, str):
            encoded_body = base64.b64encode(req.body.encode('utf-8')).decode('utf-8')
        elif isinstance(req.body, bytes):
            encoded_body = base64.b64encode(req.body).decode('utf-8')
        else:
            raise TypeError(f"req.body must be str or bytes, got {type(req.body).__name__}")

        request_payload = {
            "followRedirects": False,  # requests make redirects with processing cookies
            "insecureSkipVerify": verify,

            # requests prepare cookies for requests and store it in headers
            "withoutCookieJar": True,
            "withDefaultCookieJar": False,

            "isByteRequest": True,  # requests passes an bytes for urllib3
            "isByteResponse": True,
            "additionalDecode": False,  # requests take care about decoding
            "forceHttp1": self.config.force_http1,
            "withDebug": self.config.debug,
            "catchPanics": self.config.catch_panics,
            "withRandomTLSExtensionOrder": self.config.random_tls_extension_order,
            "timeoutSeconds": timeout,
            "timeoutMilliseconds": 0,
            "certificatePinningHosts": self.config.certificate_pinning,
        }

        if self.config.client_identifier:
            request_payload["tlsClientIdentifier"] = self.config.client_identifier
        else:
            request_payload["customTlsClient"] = {
                "ja3String": self.config.ja3_string,
                "h2Settings": self.config.h2_settings,
                "h2SettingsOrder": self.config.h2_settings_order,
                "pseudoHeaderOrder": self.config.pseudo_header_order,
                "connectionFlow": self.config.connection_flow,
                "priorityFrames": self.config.priority_frames,
                "headerPriority": self.config.header_priority,
                "certCompressionAlgo": self.config.cert_compression_algo,
                "supportedVersions": self.config.supported_versions,
                "supportedSignatureAlgorithms": self.config.supported_signature_algorithms,
                "supportedDelegatedCredentialsAlgorithms": self.config.supported_delegated_credentials_algorithms,
                "keyShareCurves": self.config.key_share_curves,
            }

        proxy = select_proxy(req.url, proxies)
        request_payload.update({
            "proxyUrl": proxy,
            "isRotatingProxy": False,
            "sessionId": getattr(req, "_session_id", ""),
            "requestUrl": req.url,
            "headers": dict(req.headers),
            "headerOrder": getattr(req, "_header_order", self.config.header_order),
            "requestMethod": req.method,
            "requestBody": encoded_body,
            "requestCookies": None  # requests prepare cookies for requests and store it in headers
        })

        response = request(json.dumps(request_payload).encode('utf-8'))
        response_bytes = ctypes.string_at(response)
        response_object = json.loads(response_bytes.decode("utf-8"))
        freeMemory(response_object["id"].encode("utf-8"))

        if response_object["status"] == 0:
            raise TLSClientExeption(response_object["body"])

        return self.build_response(req, response_object)

    def close(self):
        pass
