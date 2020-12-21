##Script to scrape apartment cost from Irvine Company apartments website
from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import csv
import sys
import pprint
import re
import openpyxl
import datetime


printer = pprint.PrettyPrinter(indent=4)


def main():
    wb = openpyxl.Workbook()
    wb.remove_sheet(wb.get_sheet_by_name("Sheet"))
    
    outfile = build_outfile_name()
    
    url_dict = {}
    populate_url_dict(url_dict)

    for name, url in url_dict.items():
        print("Processing {}".format(name))
        parse_ica_page(name, url, wb)

    
    wb.save(outfile)

def build_outfile_name():
    now = datetime.datetime.now()
    str1 = now.strftime("%a_%b%d_%H_%M")
    fn = "Apartment_Availability_" + str1 + ".xlsx"
    return(fn)

def populate_url_dict(url_dict):
    url_dict["The Village"] = "https://www.irvinecompanyapartments.com/locations/orange-county/irvine/spectrum/village-at-irvine-spectrum/availability.html"
    url_dict["Oak Glen"] = "https://www.irvinecompanyapartments.com/locations/orange-county/irvine/oak-creek/oak-glen/availability.html"
    url_dict["Cypress Village"] = "https://www.irvinecompanyapartments.com/locations/orange-county/irvine/cypress-village/communities/availability.html"
    url_dict["Avella"] = "https://www.irvinecompanyapartments.com/locations/orange-county/irvine/cypress-village/avella/availability.html"
    url_dict["Quail Hill"] = "https://www.irvinecompanyapartments.com/locations/orange-county/irvine/quail-hill/communities/availability.html"
    url_dict["The Park"] = "https://www.irvinecompanyapartments.com/locations/orange-county/irvine/spectrum/the-park/availability.html"

def create_populate_sheet_headers(name, wb):
    wb.create_sheet(title=name)
    sheet = wb.get_sheet_by_name(name)
    sheet.cell(row=1, column=1).value = "Identifier"
    sheet.cell(row=1, column=2).value = "Building No."
    sheet.cell(row=1, column=3).value = "Building Name"

    sheet.cell(row=1, column=4).value = "Floorplan"
    sheet.cell(row=1, column=5).value = "Amenity"
    sheet.cell(row=1, column=6).value = "Beds"
    sheet.cell(row=1, column=7).value = "Baths"
    sheet.cell(row=1, column=8).value = "Size (Sq. Ft.)"
    sheet.cell(row=1, column=9).value = "Price ($)"
    sheet.cell(row=1, column=10).value = "Term (months)"
    sheet.cell(row=1, column=11).value = "Date Available"


def convert_to_int(str1):
    try:
        num = int(str1)
        return num
    except ValueError:
        return str1

def convert_to_float(str1):
    try:
        num = float(str1)
        return num
    except ValueError:
        return str1
        


def parse_ica_page(name, url, wb):
    browser = webdriver.Chrome()
    # url = "https://www.irvinecompanyapartments.com/locations/orange-county/irvine/spectrum/village-at-irvine-spectrum/availability.html"
    browser.get(url)

    # source = requests.get(
    #    "https://www.irvinecompanyapartments.com/locations/orange-county/irvine/spectrum/village-at-irvine-spectrum/availability.html#"
    # ).text


    html_source = browser.page_source
    browser.quit()

    #input = open("source_soup.html", "r")
    soup = BeautifulSoup(html_source, "lxml")
    all_apartments_list = soup.find_all("ul", class_="results-list loaded")
    # printer.pprint(soup)

    # soup_output = open("soup_output.txt", "w")
    # uprint(soup, file=soup_output)
    # individual_apartments = all_apartments_list.find("li")
    # print(all_apartments_list[0], file=soup_output)
    individual_apartments = all_apartments_list[0].find_all("li")
    junk_value = individual_apartments.pop()
    text = junk_value.get_text()
    # text.replace(" ", "")
    # print("Text is *{}*".format(text))
    #if re.match("\n\nNeed More Options.*", text):
    #    pass
    #else:
    #    exit("The last value is not need more options, please recheck!")



    row = 1
    column = 1
    create_populate_sheet_headers(name, wb)
    sheet = wb.get_sheet_by_name(name)

    for apartment in individual_apartments:
        text = apartment.get_text()
        if re.match("\n\nNeed More Options.*", text):
            continue

        name = apartment.find("h5").get_text()
        floorplan_details = name.split(" - ")
        try:
            identifier, building, floorplan = floorplan_details
        except ValueError:
            identifier, building = floorplan_details
            floorplan = "-"
        building_array = building.split(" ")
        building_number = building_array.pop(0)
        building_name = " ".join(building_array)

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
        no_of_baths = convert_to_float(no_of_baths)
        size = convert_to_int(size)
        cost = convert_to_int(cost)
        term_length = convert_to_int(term_length)
        building_number = convert_to_int(building_number)

        row += 1
        sheet.cell(row=row, column=1).value = identifier
        sheet.cell(row=row, column=2).value = building_number
        sheet.cell(row=row, column=3).value = building_name

        sheet.cell(row=row, column=4).value = floorplan

        sheet.cell(row=row, column=5).value = amenity
        sheet.cell(row=row, column=6).value = no_of_beds
        sheet.cell(row=row, column=7).value = no_of_baths
        sheet.cell(row=row, column=8).value = size
        sheet.cell(row=row, column=9).value = cost
        sheet.cell(row=row, column=10).value = term_length
        sheet.cell(row=row, column=11).value = availability

        #print(
        #    "Apartment *{}* Amenity *{}* Bed *{}* Bath *{}* Size *{}* Price *{}* Term *{}* Avail *{}*".format(
        #        name,
        #        amenity,
        #        no_of_beds,
        #        no_of_baths,
        #        size,
        #        cost,
        #        term_length,
        #        availability,
        #    )
        #)
        # print("##############################")

if __name__ == "__main__":
    main()