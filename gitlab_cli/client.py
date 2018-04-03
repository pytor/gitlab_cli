import os
from urllib.parse import urljoin
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class APIClient(object):

    def __init__(self, config):
        self.config = config
        self.header = {'PRIVATE-TOKEN': config["token"]}
        self.url = "{}/api/v{}/projects".format(
            config["server"].strip("/"), config["api_version"])

    def _request(self, path, method, **params):
        url = self.url + path
        resp = method(url, headers=self.header,
                      params=params, verify=False, timeout=10)

        if resp.status_code != requests.status_codes.codes.ok:
            return {
                "message": "Response code is %s" % resp.status_code,
                "kind": "error"
            }
        if resp.headers["content-type"] == "text/plain":
            return {"raw_data": resp.text}
        else:
            return resp.json()

    def get(self, path, **params):
        return self._request(path, requests.get, **params)

    def post(self, path, **params):
        return self._request(path, requests.post, **params)
