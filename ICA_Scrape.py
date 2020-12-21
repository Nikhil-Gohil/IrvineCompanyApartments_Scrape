##Script to scrape apartment cost from Irvine Company apartments website
from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import csv
import sys
import pprint
import re
import openpyxl


printer = pprint.PrettyPrinter(indent=4)


def populate_sheet_headers(sheet):
    sheet.cell(row=1, column=1).value = "Name"
    sheet.cell(row=1, column=2).value = "Amenity"
    sheet.cell(row=1, column=3).value = "Beds"
    sheet.cell(row=1, column=4).value = "Baths"
    sheet.cell(row=1, column=5).value = "Size (Sq. Ft.)"
    sheet.cell(row=1, column=6).value = "Price ($)"
    sheet.cell(row=1, column=7).value = "Term (months)"
    sheet.cell(row=1, column=8).value = "Date Available"


def convert_to_int(str1):
    try:
        num = int(str1)
        return num
    except ValueError:
        return str1


# def parse_url():
# browser = webdriver.Chrome()
# url = "https://www.irvinecompanyapartments.com/locations/orange-county/irvine/spectrum/village-at-irvine-spectrum/availability.html"
# browser.get(url)

# source = requests.get(
#    "https://www.irvinecompanyapartments.com/locations/orange-county/irvine/spectrum/village-at-irvine-spectrum/availability.html#"
# ).text


# html_source = browser.page_source
# browser.quit()

input = open("source_soup.html", "r")
soup = BeautifulSoup(input.read(), "lxml")
all_apartments_list = soup.find_all("ul", class_="results-list loaded")
# printer.pprint(soup)

soup_output = open("soup_output.txt", "w")
# uprint(soup, file=soup_output)
# individual_apartments = all_apartments_list.find("li")
# print(all_apartments_list[0], file=soup_output)
individual_apartments = all_apartments_list[0].find_all("li")
junk_value = individual_apartments.pop()
text = junk_value.get_text()
text.replace(" ", "")
# print("Text is *{}*".format(text))
if re.match("\n\nNeed More Options.*", text):
    pass
else:
    exit("The last value is not need more options, please recheck!")

wb = openpyxl.Workbook()
wb.remove_sheet(wb.get_sheet_by_name("Sheet"))
wb.create_sheet(title="The Village")
sheet = wb.get_sheet_by_name("The Village")
row = 1
column = 1
populate_sheet_headers(sheet)

for apartment in individual_apartments:

    name = apartment.find("h5").get_text()
    amenity = apartment.find("div", class_="featured-amenity").get_text()
    if not amenity:
        amenity = "None"
    divs = apartment.find_all("div")

    details = divs[1].get_text()
    detail_array = details.split(" / ")
    no_of_beds, no_of_baths, size = detail_array

    no_of_beds = re.sub(" Bed$", "", no_of_beds)
    no_of_baths = re.sub(" Bath$", "", no_of_baths)
    size = re.sub(" Sq\. Ft\.$", "", size)
    size = re.sub(",", "", size)

    pricing = divs[2].get_text()
    price_array = pricing.split(" / ")
    cost, term_length = price_array
    cost = re.sub("^\$", "", cost)
    cost = re.sub(",", "", cost)
    term_length = re.sub(" Months$", "", term_length)

    availability = divs[3].get_text()
    availability = re.sub("^Available ", "", availability)

    no_of_beds = convert_to_int(no_of_beds)
    no_of_baths = convert_to_int(no_of_baths)
    size = convert_to_int(size)
    cost = convert_to_int(cost)
    term_length = convert_to_int(term_length)

    row += 1
    sheet.cell(row=row, column=1).value = name
    sheet.cell(row=row, column=2).value = amenity
    sheet.cell(row=row, column=3).value = no_of_beds
    sheet.cell(row=row, column=4).value = no_of_baths
    sheet.cell(row=row, column=5).value = size
    sheet.cell(row=row, column=6).value = cost
    sheet.cell(row=row, column=7).value = term_length
    sheet.cell(row=row, column=8).value = availability

    print(
        "Apartment *{}* Amenity *{}* Bed *{}* Bath *{}* Size *{}* Price *{}* Term *{}* Avail *{}*".format(
            name,
            amenity,
            no_of_beds,
            no_of_baths,
            size,
            cost,
            term_length,
            availability,
        )
    )
    # print("##############################")
wb.save("example.xlsx")
# print(list(soup.children))
