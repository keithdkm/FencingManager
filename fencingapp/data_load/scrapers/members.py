from bs4 import BeautifulSoup
import requests

from fencingapp.data_load.locators.member_locators import memberLocators

class memberFile:

    def __init__(self,url):
        html_= requests.get(url).content
        self.soup = BeautifulSoup(html_,'lxml')

    @property
    def url_link(self):
        return self.soup.select_one(memberLocators.MEMBER_FILE)['href']