import requests


class GrafanaClient():
    def __init__(self, base_url="http://localhost:3000", auth_string="ident:ident", auth_type="basic"):
        self.base_url = base_url
        self.auth_string = auth_string
        self.auth_type = auth_type

    def create_dashboard(self, payload):
        url = self.base_url + "/api/dashboards/db"
        result = self.request("post", url, payload=payload) #json.dumps(payload)? will request method take json string
        return result.json()

    def get_dashboard(self, slug):
        url = self.base_url + "/api/dashboards/db/{}".format(slug)
        result = self.request("get", url)
        return result.json()

    def delete_dashboard(self, slug):
        url = self.base_url + "/api/dashboards/db/:{}".format(slug)
        result = self.request("delete", url)
        return result.json()

    def get_home_dashboard(self):
        url = self.base_url + "/api/dashboards/home"
        result = self.request("get", url)
        return result.json()

    def get_tags(self):
        url = self.base_url + "/api/dashboards/tags"
        result = self.request("get", url)
        return result.json()

    def search_dashboards(self, payload=None):
        url = self.base_url + "/api/search"
        result = self.request("get", url, payload=payload)
        return result.json()

    def get_datasources(self):
        url = self.base_url + "/api/datasources"
        result = self.request("get", url)
        return result.json()

    def get_datasource(self, id):
        url = self.base_url + "/api/datasources/:{}".format(id)
        result = self.request("get", url)
        return result.json()

    def create_datasource(self, payload):
        url = self.base_url + "/api/datasources"
        result = self.request("post", url, payload=payload)
        return result.json()

    def update_datasource(self, id, payload):
        url = self.base_url + "/api/datasources/:{}".format(id)
        result = self.request("put", url, payload=payload)
        return result.json()

    def delete_datasource(self, id):
        url = self.base_url + "/api/datasources/:{}".format(id)
        result = self.request("delete", url)
        return result.json()

    def get_datasource_types(self):
        url = self.base_url + "/api/datasources/plugins"
        result = self.request("get", url)
        return result.json()

    def request(self, method, url, **kwargs):
        if self.auth_type == "basic":
            url = self.basic_auth(url)
            headers = self.basic_headers()
        elif self.auth_type == "token":
            headers = token_headers()
        req_fn = getattr(self, method)
        result = req_fn(url, headers, **kwargs)
        return result

    def basic_auth(self, url):
        u = url.split("://")
        url = "{}://{}@{}".format(u[0], self.auth_string, u[1])
        return url

    def basic_headers(self):
        headers = {
                   #"Accept": "application/json",
                   "Content-Type": "application/json"
                    }
        return headers

    def token_headers(self):
        headers = {"Accept": "application/json",
                   "Content-Type": "application/json",
                   "Authorization": "Bearer {}".format(self.auth_string)}
        return headers

    def get(self, url, headers=None, payload=None):
        """
        :param url: url to get
        :param payload: dictionary of url params
        :return: requests.models.Response object
        """
        result = requests.get(url, params=payload, headers=headers)
        return result

    def post(self, url, headers=None, payload=None, files=None):
        """
        :param url: url to post to
        :param payload: a string or a dict
        :param files: dict. Values can be filehandler, (name, handler, content_type, headers dict), or string
        :return: requests.models.Response object
        """
        result = requests.post(url, data=payload, files=files, headers=headers)
        return result

    def put(self, url, headers=None, payload=None):
        result = requests.put(url, headers=headers, data=payload)

    def delete(self, url, headers=None):
        result = requests.delete(url, headers=headers)
        return result

    def head(self, url, headers=None):
        result = requests.head(url, headers=headers)
        return result

    def options(self, url, headers=None):
        result = requests.options(url, headers=headers)
        return result

#check formatting of ident/auth strings
#unit tests
#end_to_end tests
#site-packagesize
