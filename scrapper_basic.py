"""
One useful package for web scraping in Python’s standard library is urllib, which contains tools for working with URLs.
The urllib.request module contains a function called urlopen() that can be used to open a URL within a program.
"""
import re
from urllib.request import urlopen

# Method 1 - Extract Text From HTML With String Methods
url = "http://olympus.realpython.org/profiles/aphrodite"

page = urlopen(url)
#print(f'pageObject: {page}')
# prints something like "<http.client.HTTPResponse object at 0x0000027959495F70>"

html_bytes = page.read()
#print(f'html_bytes: {html_bytes}')
# prints a html source code of the webpage at url, in one single line

html = html_bytes.decode("utf-8")
#print(f'HTML: {html}')
# prints a html source code of the webpage at url, in a better format

start_index = html.find("<title>") + len("<title>")
end_index = html.find("</title>")
title = html[start_index:end_index]
print(title)


# Method 2 - Extract Text From HTML With Regular Expressions
url = "http://olympus.realpython.org/profiles/dionysus"
page = urlopen(url)
html = page.read().decode("utf-8")

pattern = "<title.*?>.*?</title.*?>"
match_results = re.search(pattern, html, re.IGNORECASE)
title = match_results.group()
title = re.sub("<.*?>", "", title)  # Remove HTML tags

print(title)