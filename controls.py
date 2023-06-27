import re
import hashlib
import difflib

from bs4 import BeautifulSoup
import requests

from dotenv import load_dotenv

load_dotenv()


class Controls:
    def __init__(self):
        pass

    def get(self, url):
        req = requests.get(url)
        if req.status_code == 200:
            return req
        else:
            return None

    def parse(self, content, parser=None):
        """
        Parse the content to html object.
        """
        if parser is None:
            self.parsed = BeautifulSoup(content, "html.parser")
        else:
            self.parsed = parser(content)

    @property
    def get_parsed(self):
        return self.parsed

    def convert(self, string):
        """
        Convert and return the hashed string.
        """
        converted = hashlib.md5(string, usedforsecurity=False)

        return converted

    def find_target(self, parsed=None, target="body", multiple=False, _class=None):
        if parsed is None and target:
            return self.get_parsed.find(target)
        else:
            soup = BeautifulSoup(parsed, "html.parser")

            if not multiple and _class:
                return soup.find(target, class_=_class)

        return soup.css.select(target)

    def compare(self, new, old):
        """
        Compare if there's changes to new and old html file and
        returns the list of difference.
        """
        return [difference for difference in difflib.ndiff(new, old)]

    def get_url_id(self, html, selector, parser=None):
        """
        Accepts string-like that will be converted as html object and search through by finding it by using specified selector.
        """
        if html:
            soup = BeautifulSoup(html, "html.parser") or parser(html)
            element = soup.find_all(selector)

    def find(self, html, pattern=None):
        """
        Find the actual id.
        """
        if pattern is None:
            pattern = r"\(\d+\)"

        id = re.search(pattern, html)

        return id

    def build_url(self, base_url, id):
        """
        Builds a url from selector or from specified id.
        """
        if isinstance(id, str):
            id = id.strip("()")

        if base_url.endswith("/"):
            return f"{base_url}{id}"

        else:
            return f"{base_url}/{id}"

    def remove_whitespace(self, string):
        """
        Removes the whitespaces and split them by linebreaks, returns a list of strings.
        """
        return list(map(str.strip, string.splitlines()))
