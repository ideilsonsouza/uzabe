class ZDCConsts:
    class MODBusResponse:
        READ = 200

    class HTTPResponse:
        # 1xx: Informacional
        CONTINUE = 100
        SWITCHING_PROTOCOLS = 101
        PROCESSING = 102  # WebDAV

        # 2xx: Sucesso
        OK = 200
        CREATED = 201
        ACCEPTED = 202
        NON_AUTHORITATIVE_INFORMATION = 203
        NO_CONTENT = 204
        RESET_CONTENT = 205
        PARTIAL_CONTENT = 206
        MULTI_STATUS = 207  # WebDAV
        ALREADY_REPORTED = 208  # WebDAV
        IM_USED = 226

        # 3xx: Redirecionamento
        MULTIPLE_CHOICES = 300
        MOVED_PERMANENTLY = 301
        FOUND = 302
        SEE_OTHER = 303
        NOT_MODIFIED = 304
        USE_PROXY = 305
        TEMPORARY_REDIRECT = 307
        PERMANENT_REDIRECT = 308  # RFC 7538

        # 4xx: Erros do cliente
        BAD_REQUEST = 400
        UNAUTHORIZED = 401
        PAYMENT_REQUIRED = 402
        FORBIDDEN = 403
        NOT_FOUND = 404
        METHOD_NOT_ALLOWED = 405
        NOT_ACCEPTABLE = 406
        PROXY_AUTHENTICATION_REQUIRED = 407
        REQUEST_TIMEOUT = 408
        CONFLICT = 409
        GONE = 410
        LENGTH_REQUIRED = 411
        PRECONDITION_FAILED = 412
        PAYLOAD_TOO_LARGE = 413
        URI_TOO_LONG = 414
        UNSUPPORTED_MEDIA_TYPE = 415
        RANGE_NOT_SATISFIABLE = 416
        EXPECTATION_FAILED = 417
        IM_A_TEAPOT = 418  # joke
        MISDIRECTED_REQUEST = 421
        UNPROCESSABLE_ENTITY = 422  # WebDAV
        LOCKED = 423  # WebDAV
        FAILED_DEPENDENCY = 424  # WebDAV
        TOO_EARLY = 425
        UPGRADE_REQUIRED = 426
        PRECONDITION_REQUIRED = 428
        TOO_MANY_REQUESTS = 429
        REQUEST_HEADER_FIELDS_TOO_LARGE = 431
        UNAVAILABLE_FOR_LEGAL_REASONS = 451

        # 5xx: Erros do servidor
        INTERNAL_SERVER_ERROR = 500
        NOT_IMPLEMENTED = 501
        BAD_GATEWAY = 502
        SERVICE_UNAVAILABLE = 503
        GATEWAY_TIMEOUT = 504
        HTTP_VERSION_NOT_SUPPORTED = 505
        VARIANT_ALSO_NEGOTIATES = 506
        INSUFFICIENT_STORAGE = 507  # WebDAV
        LOOP_DETECTED = 508  # WebDAV
        NOT_EXTENDED = 510
        NETWORK_AUTHENTICATION_REQUIRED = 511

    class HTTPMessage:
        @staticmethod
        def get_message(status_code):
            messages = {
                ZDCConsts.HTTPResponse.OK: "OK",
                ZDCConsts.HTTPResponse.CREATED: "Created",
                ZDCConsts.HTTPResponse.ACCEPTED: "Accepted",
                ZDCConsts.HTTPResponse.NON_AUTHORITATIVE_INFORMATION: "Non-Authoritative Information",
                ZDCConsts.HTTPResponse.NO_CONTENT: "No Content",
                ZDCConsts.HTTPResponse.INTERNAL_SERVER_ERROR: "Internal Server Error",
                ZDCConsts.HTTPResponse.NOT_IMPLEMENTED: "Not Implemented",
                ZDCConsts.HTTPResponse.BAD_GATEWAY: "Bad Gateway",
                ZDCConsts.HTTPResponse.SERVICE_UNAVAILABLE: "Service Unavailable",
                ZDCConsts.HTTPResponse.GATEWAY_TIMEOUT: "Gateway Timeout",
                ZDCConsts.HTTPResponse.HTTP_VERSION_NOT_SUPPORTED: "HTTP Version Not Supported"
            }

            message = messages.get(status_code, "Unknown Status Code")
            print(message)
            return message