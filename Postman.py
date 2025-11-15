class PostmanRequest(object):
    def __init__(self, Url, Params = None, Headers = None, Cookies = None, Timeout = None, AllowRedirects = True, Verify = None):
        import requests

        self._Pm_Method   = 'POST'
        self._Pm_Url      = Url
        self._Pm_Params   = Params
        self._Pm_Headers  = Headers
        self._Pm_Cookies  = Cookies
        self._Pm_Timeout  = Timeout
        self._Pm_Redirect = AllowRedirects
        self._Pm_Verify   = Verify
        self._Pm_Session  = requests.Session()

    def request(self, method, url, params = None, data = None, headers = None, cookies = None, auth = None, timeout = None, allow_redirects = True, proxies = None, stream = None, verify = None, cert = None):
        import json
        import warnings
        import requests

        # Disable SSL Warning
        Warning_Filters = warnings.filters[:]; requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

        try:
            Response = self._Pm_Session.request(
                method = self._Pm_Method, url = self._Pm_Url, params = self._Pm_Params, headers = self._Pm_Headers, cookies = self._Pm_Cookies, timeout = self._Pm_Timeout, allow_redirects = self._Pm_Redirect, verify = self._Pm_Verify,
                data   = json.dumps({
                    'method' : method.upper(),
                    'url'    : url,
                    'params' : params,
                    'data'   : json.dumps(data),
                    'headers': headers,
                    'cookies': cookies,
                    'auth'   : auth,
                  # 'timeout': timeout,
                  # 'proxies': proxies,
                  # 'stream' : stream,
                  # 'verify' : verify,
                  # 'cert'   : cert,
                    'allow_redirects': allow_redirects
                })
            )
        finally:
        # Recover SSL Warning
            warnings.filters = Warning_Filters

        # Postman Side Error
        if Response.status_code != 200:
            raise requests.exceptions.HTTPError('Error: %s, %s' % (Response.status_code, Response.text))

        # Target Server Side Error
        ResponseJson = Response.json()
        if ResponseJson.get('Ec'.lower()) or not ResponseJson.get('Data'.lower()):
            ResponseEm = ResponseJson.get('Em'.lower()) or ''
            Et, Em = ResponseEm.split(': ', 1) if ': ' in ResponseEm else ('', ResponseEm)
            match Et:
                case 'ValueError': raise ValueError('TargetServer %s@%s' % (Et, Em))
                case 'TypeError' : raise TypeError ('TargetServer %s@%s' % (Et, Em))
                case _           : raise Exception ('TargetServer %s@%s' % (Et, Em))

        return PostmanResponse(self, ResponseJson.get('Data'.lower()))

    def get(self, url, params = None, data = None, headers = None, cookies = None, auth = None, timeout = None, allow_redirects = True, proxies = None, stream = None, verify = None, cert = None):
        return self.request('GET', url, params, data, headers, cookies, auth, timeout, allow_redirects, proxies, stream, verify, cert)

    def put(self, url, params = None, data = None, headers = None, cookies = None, auth = None, timeout = None, allow_redirects = True, proxies = None, stream = None, verify = None, cert = None):
        return self.request('PUT', url, params, data, headers, cookies, auth, timeout, allow_redirects, proxies, stream, verify, cert)

    def head(self, url, params = None, data = None, headers = None, cookies = None, auth = None, timeout = None, allow_redirects = True, proxies = None, stream = None, verify = None, cert = None):
        return self.request('HEAD', url, params, data, headers, cookies, auth, timeout, allow_redirects, proxies, stream, verify, cert)

    def post(self, url, params = None, data = None, headers = None, cookies = None, auth = None, timeout = None, allow_redirects = True, proxies = None, stream = None, verify = None, cert = None):
        return self.request('POST', url, params, data, headers, cookies, auth, timeout, allow_redirects, proxies, stream, verify, cert)

    def patch(self, url, params = None, data = None, headers = None, cookies = None, auth = None, timeout = None, allow_redirects = True, proxies = None, stream = None, verify = None, cert = None):
        return self.request('PATCH', url, params, data, headers, cookies, auth, timeout, allow_redirects, proxies, stream, verify, cert)

    def delete(self, url, params = None, data = None, headers = None, cookies = None, auth = None, timeout = None, allow_redirects = True, proxies = None, stream = None, verify = None, cert = None):
        return self.request('DELETE', url, params, data, headers, cookies, auth, timeout, allow_redirects, proxies, stream, verify, cert)

    def options(self, url, params = None, data = None, headers = None, cookies = None, auth = None, timeout = None, allow_redirects = True, proxies = None, stream = None, verify = None, cert = None):
        return self.request('OPTIONS', url, params, data, headers, cookies, auth, timeout, allow_redirects, proxies, stream, verify, cert)


class PostmanResponse(object):
    def __init__(self, request, response):
        import base64
        import requests

        self._content = base64.b64decode(response['_content'])
        self._content_consumed = True
        self._next = response['next']

        #: Integer Code of responded HTTP Status, e.g. 404 or 200.
        self.status_code = response['status_code']

        #: Case-insensitive Dictionary of Response Headers.
        #: For example, ``headers['content-encoding']`` will return the
        #: value of a ``'Content-Encoding'`` response header.
        self.headers = requests.structures.CaseInsensitiveDict(response['headers'])

        #: File-like object representation of response (for advanced usage).
        #: Use of ``raw`` requires that ``stream=True`` be set on the request.
        #: This requirement does not apply for use internally to Requests.
        self.raw = request

        #: Final URL location of Response.
        self.url = response['url']

        #: Encoding to decode with when accessing r.text.
        self.encoding = response['encoding']
        self.apparent_encoding = response['apparent_encoding']

        #: A list of :class:`Response <Response>` objects from
        #: the history of the Request. Any redirect responses will end
        #: up here. The list is sorted from the oldest to the most recent request.
        self.history = []

        #: Textual reason of responded HTTP Status, e.g. "Not Found" or "OK".
        self.reason = response['reason']

        #: A CookieJar of Cookies the server sent back.
        self.cookies = response['cookies']

        #: The amount of time elapsed between sending the request
        #: and the arrival of the response (as a timedelta).
        #: This property specifically measures the time taken between sending
        #: the first byte of the request and finishing parsing the headers. It
        #: is therefore unaffected by consuming the response content or the
        #: value of the ``stream`` keyword argument.
        self.elapsed = response['elapsed']

        #: The :class:`PreparedRequest <PreparedRequest>` object to which this
        #: is a response.
        self.request = None

        #: Other details of the response.
        try:
            self.content = self._content
            self.text = str(self.content, self.encoding, errors = 'replace')
        except (LookupError, TypeError):
            self.content = self._content
            self.text = str(self.content, errors = 'replace')

        self.ok = response['ok']
        self.next = response['next']
        self.links = response['links']
        self.is_redirect = response['is_redirect']
        self.is_permanent_redirect = response['is_permanent_redirect']

    def __repr__(self):
        return f"<Response [{self.status_code}]>"

    def __bool__(self):
        return self.ok

    def __nonzero__(self):
        return self.ok

    def __iter__(self):
        return self.iter_content(128)

    def json(self, **kwargs):
        import json
        from requests.utils import guess_json_utf
        from requests.compat import JSONDecodeError
        from requests.exceptions import JSONDecodeError as RequestsJSONDecodeError

        if not self.encoding and self.content and len(self.content) > 3:
            # No encoding set. JSON RFC 4627 section 3 states we should expect
            # UTF-8, -16 or -32. Detect which one to use; If the detection or
            # decoding fails, fall back to `self.text` (using charset_normalizer to make
            # a best guess).
            encoding = guess_json_utf(self.content)
            if encoding is not None:
                try:
                    return json.loads(self.content.decode(encoding), **kwargs)
                except UnicodeDecodeError:
                    # Wrong UTF codec detected; usually because it's not UTF-8
                    # but some other 8-bit codec.  This is an RFC violation,
                    # and the server didn't bother to tell us what codec *was*
                    # used.
                    pass
                except JSONDecodeError as e:
                    raise RequestsJSONDecodeError(e.msg, e.doc, e.pos)

        try:
            return json.loads(self.text, **kwargs)
        except JSONDecodeError as e:
            # Catch JSON-related errors and raise as requests.JSONDecodeError
            # This aliases json.JSONDecodeError and simplejson.JSONDecodeError
            raise RequestsJSONDecodeError(e.msg, e.doc, e.pos)

    def close(self):
        release_conn = getattr(self.raw, 'release_conn', None)
        if release_conn is not None:
            release_conn()
