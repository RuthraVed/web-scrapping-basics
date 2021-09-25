from bs4 import BeautifulSoup
from urllib.request import urlopen


url = "http://olympus.realpython.org/profiles/dionysus"

# Opens the URL http://olympus.realpython.org/profiles/dionysus using urlopen() from the urllib.request module
page = urlopen(url)

# Reads the HTML from the page as a string and assigns it to the html variable
html = page.read().decode("utf-8")

# Creates a BeautifulSoup object and assigns it to the soup variable
soup = BeautifulSoup(html, "html.parser")

# print(soup.get_text())
print(soup.title.text)
print(soup.title.string)

# print(soup.find_all("img"))
image1, image2 = soup.find_all("img")

print(image1.name)
print(image2['src'])

img_list = soup.find_all("img", src="/static/dionysus.jpg")
print(img_list)