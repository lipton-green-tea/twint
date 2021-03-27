import re
import time

import requests
import logging as logme


class TokenExpiryException(Exception):
    def __init__(self, msg):
        super().__init__(msg)

        
class RefreshTokenException(Exception):
    def __init__(self, msg):
        super().__init__(msg)
        

class Token:
    def __init__(self, config):
        self._session = requests.Session()
        self._session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0'})
        self.config = config
        self.proxies = self._get_proxies()
        self._retries = 5
        self._timeout = 10
        self.url = 'https://twitter.com'

    def _get_proxies(self) -> dict:
        if self.config.Token_proxy_host == "":
            logme.debug(f"No proxy host in config")
            return {}
        if self.config.Token_proxy_port == 0:
            logme.debug(f"No proxy port in config")
            return {}
        if not self.config.Token_proxy_type:
            logme.debug(f"No proxy type in config")
            return {}
        if self.config.Token_proxy_username and self.config.Token_proxy_password:
            return {
                str(self.config.Token_proxy_type): f"http://{self.config.Token_proxy_username}:{self.config.Token_proxy_password}@{self.config.Token_proxy_host}:{self.config.Token_proxy_port}"
            }
        else:
            return {
                str(self.config.Token_proxy_type): f"http://{self.config.Token_proxy_host}:{self.config.Token_proxy_port}"
            }

    def _request(self):
        for attempt in range(self._retries + 1):
            # The request is newly prepared on each retry because of potential cookie updates.
            req = self._session.prepare_request(requests.Request('GET', self.url))
            logme.debug(f'Retrieving {req.url}')
            print("proxies:", self.proxies)
            try:
                if self.proxies:
                    r = self._session.send(
                        req,
                        allow_redirects=True,
                        timeout=self._timeout,
                        proxies=self.proxies,
                        verify=False
                    )
                else:
                    r = self._session.send(req, allow_redirects=True, timeout=self._timeout)
            except requests.exceptions.RequestException as exc:
                if attempt < self._retries:
                    retrying = ', retrying'
                    level = logme.WARNING
                else:
                    retrying = ''
                    level = logme.ERROR
                print(f'Error retrieving {req.url}: {exc!r}{retrying}')
                logme.log(level, f'Error retrieving {req.url}: {exc!r}{retrying}')
            else:
                success, msg = (True, None)
                msg = f': {msg}' if msg else ''

                if success:
                    logme.debug(f'{req.url} retrieved successfully{msg}')
                    return r
            if attempt < self._retries:
                # TODO : might wanna tweak this back-off timer
                sleep_time = 2.0 * 2 ** attempt
                logme.info(f'Waiting {sleep_time:.0f} seconds')
                time.sleep(sleep_time)
        else:
            msg = f'{self._retries + 1} requests to {self.url} failed, giving up.'
            logme.fatal(msg)
            self.config.Guest_token = None
            raise RefreshTokenException(msg)

    def refresh(self):
        logme.debug('Retrieving guest token')
        res = self._request()
        match = re.search(r'\("gt=(\d+);', res.text)
        if match:
            logme.debug('Found guest token in HTML')
            self.config.Guest_token = str(match.group(1))
        else:
            self.config.Guest_token = None
            raise RefreshTokenException('Could not find the Guest token in HTML')
