import os
import re
import requests

from bs4 import BeautifulSoup
import execjs

# https://www.scrapingbee.com/blog/python-requests-proxy/
proxies = {
   'http': 'http://127.0.0.1:8080',
   'https': 'http://127.0.0.1:8090',
}

username = os.environ.get("UI_USERNAME")
password = os.environ.get("UI_PASSWORD")
url = "http://logout.ui.ac.ir"
extraction_pattern = re.compile("\S*document.sendin.password.value = hexMD5\((.*)\);")
replacement_pattern = re.compile("' \+ document.login.password.value \+ '")

page = requests.get(url)
soup = BeautifulSoup(page.text, "html.parser")
scripts = soup.find_all('script')

for script in scripts:
   search = extraction_pattern.search(str(script.string))
   if search:
      pre_hash = replacement_pattern.sub(password, search.group(1))
      hash_str = ""

      with open('./md5.js', 'r') as f:
        content = f.read()
        content += f'var result = hexMD5({pre_hash})'
        ctx = execjs.compile(content)
        hash_str = ctx.eval('result')
        
      data = {
        "username": username,
        "password": hash_str,
        "dst": "",
        "popup": False,
      }

      response =  requests.post(url, json=data)      
      print(response.text)
