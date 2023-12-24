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

if not username:
   print("please set UI_USERNAME environment variable")
   exit()

if not password:
   print("please set UI_PASSWORD environment variable")
   exit()

url = "http://logout.ui.ac.ir"
extraction_pattern = re.compile("\S*document.sendin.password.value = hexMD5\((.*)\);")
replacement_pattern = re.compile("' \+ document.login.password.value \+ '")

page = requests.get(url)
soup = BeautifulSoup(page.text, "html.parser")
scripts = soup.find_all('script')

for script in scripts:
   search = extraction_pattern.search(str(script.string))
   if search:
      print(f"search: {search.group(1)}")
      pre_hash = replacement_pattern.sub(password, search.group(1))
      hash_str = ""

      with open('./md5.js', 'r') as f:
        print("found pattern")
        content = f.read()
        content += f'var result = hexMD5({pre_hash})'
        ctx = execjs.compile(content)
        hash_str = ctx.eval('result')
        
      data = {
        "username": username,
        "password": hash_str,
        "dst": "",
        "popup": "true",
      }

      headers = {
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1",
        "Origin": "http://logout.ui.ac.ir",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5790.110 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Referer": "http://logout.ui.ac.ir/login",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9",
      }

      # send login request
      response =  requests.post(
         f"{url}/login", 
         data=data, 
         headers=headers,
         proxies=proxies)

      # check status page
      response =  requests.get(
         f"{url}/status",
         headers=headers,
         proxies=proxies)
      print(response.text)