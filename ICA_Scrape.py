##Script to scrape apartment cost from Irvine Company apartments website
from bs4 import BeautifulSoup
import requests
import csv
import sys
import pprint

printer  = pprint.PrettyPrinter(indent=4)
soup_output = open("source_soup.txt", "w")


source = requests.get('https://www.irvinecompanyapartments.com/locations/orange-county/irvine/spectrum/village-at-irvine-spectrum/availability.html#').text

soup = BeautifulSoup(source, 'lxml')
#printer.pprint(soup)
print(source, file=soup_output)
print("Hello World!")