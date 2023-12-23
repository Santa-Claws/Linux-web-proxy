from src.server import link_replacinator
from bs4 import BeautifulSoup as bs
from unittest import TestCase


def read_file_as_string(file_name):
    with open(file_name, 'r') as f:
        return "".join(f.readlines())


class LinkReplacinatorTest(TestCase):

    def test_simple(self):
        content = read_file_as_string("test/test.html")
        replaced = link_replacinator(content, "http://apache.org")
        soup = bs(replaced, 'html.parser')
        links = soup.find_all("a")
        assert len(links) > 5
        for link in links:
            print(f"Link: {link.get('href')}")
            assert link.get("href").startswith("http://seanmac.org")
        #assert False, 'it woks'

    def test_script(self):
        content = read_file_as_string("test/slope.html")
        replaced = link_replacinator(content, "https://sites.google.com/site/slopeunblockedgame")
        soup = bs(replaced, 'html.parser')
        links = soup.find_all("a")
        assert len(links) > 5
        for link in links:
            print(f"Link: {link.get('href')}")
            assert link.get("href").startswith("http://seanmac.org")
        # assert False, 'it woks'

    def test_base(self):
        content = read_file_as_string("test/test.html")
        replaced = link_replacinator(content, "https://apache.org")
        soup = bs(replaced, 'html.parser')
        base_header = soup.find_all("base")
        print(f"Link: {link.get('href')}")
        assert base_header.get("href").startswith("http://seanmac.org")
        # assert False, 'it woks'
