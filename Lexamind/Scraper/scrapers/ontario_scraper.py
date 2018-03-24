#! python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 15:45:54 2018
@author: Sacha Perry-Fagant
"""

import urllib.request as urllib2
from bs4 import BeautifulSoup
import requests
from .scraper_api import Scraper, Bill
import csv
import chardet

class Ontario( Scraper ):

    def __init__(self):
        super(Scraper, self).__init__()
        self.legislature="Ontario"

    # Gets all the text from the detailed info page
    def Extract_Info_Ontario(url):
        try:
            response = requests.get(url)
        except:
            print("There was an issue connecting to the internet")
            return

        if response.status_code != 200:
            print("There was an error finding the detailed page")
            return

        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page, "html.parser")
        text = ""
        wordSection = ""
        i = 1
        # check all the word sections starting at 1
        while wordSection != None:
            section = "WordSection" + str(i)
            wordSection = soup.find("div", attrs = {'class' : section})
            if wordSection == None:
                break
            # Finds all the text in the word section
            all_text = wordSection.find_all("span")
            for txt in all_text:
                text += txt.text
                text = text.replace('\\xa0', ' ')
                text = text.replace('\\xc2', ' ')
                text = text.replace('\\n', '\n')
                text = text.replace('"','')
                text = text.replace('"','')
                text = text.replace("b'", "")
                text += "\n"
            i += 1
        return text


    # Transform the dictionary to CSV
    def Convert_to_csv(data, fileName = "test.csv"):
        csvfile = open(fileName, 'w', newline='')
        file = csv.writer(csvfile)
        labels = ['identifier', 'title', 'date', 'stage', 'activity', 'committee', 'details']
        file.writerow(labels)
        for row in data:
            text = []
            text.append(row.identifier)
            text.append(row.title)
            text.append(row.events[0]['date'])
            text.append(row.events[0]['stage'])
            text.append(row.events[0]['activity'])
            text.append(row.events[0]['committee'])
            text.append(str(row.details.encode('utf-8')))
            file.writerow(text)
            # if there are multiple rows
            if len(row.events) > 1:
                for i in range(1, len(row.events)):
                    text = ["",""]
                    text.append((row.events[i]['date']))
                    text.append((row.events[i]['stage']))
                    text.append(row.events[i]['activity'])
                    text.append(row.events[i]['committee'])
                    file.writerow(text)

        csvfile.close()

    # Reads in the lines from the file and cleans them up
    def test_csv(filename = "Legislative_Assembly_of_Ontario.csv"):
        file = open(filename, mode = 'r')
        lines = file.readlines()
        file.close()
        clean_lines = []
        for line in lines:
            clean = line.replace('\\xa0', ' ')
            clean = clean.replace('\\xc2', ' ')
            clean = clean.replace('\\n', '\n')
            clean = clean.replace('"','')
            clean = clean.replace('"','')
            clean = clean.replace("b'", "")
            clean_lines.append(clean)
        return clean_lines

    # the main function that scrapes the Legislative Assembly of Ontario
    # it will be saved as Legislative_Assembly_of_Ontario.csv
    def retrieve_bills(self,  filename = None):
        url = "http://www.ontla.on.ca/web/bills/bills_current.do?locale=fr"
        url_base = "http://www.ontla.on.ca/web/bills/"

        # Where all the data from the bills will be stored
        data = []

        # Checking internet connection and webpage
        try:
            response = requests.get(url)
        except:
            print("There was an issue connecting to the internet")
            return

        if response.status_code != 200:
            print("There was an error finding the first page")
            return

        page = urllib2.urlopen(url)
        soup = BeautifulSoup(page, "html.parser")
        bills = soup.find_all("div", attrs = {"class": "billstatus"})

        counter = 1
        for bill in bills:
            if counter > 3:
                continue

            if counter % 10 == 0:
                print("Currently at bill " + str(counter))
            counter += 1

            # Data is separated by commas in the CSV so the commas are removed

            # the id is bill73 for example
            identifier = self.legislature + bill.get("id").replace(","," ")

            # has the title and the url for the detailed data
            title_url = bill.find('a', href=True)

            title = title_url.text.strip().replace(","," ")

            bill_info = Bill(identifier, title)

            # If there is more than one row in the table, save all rows
            # Each attribute is saved in a list for that attribute
            current_row = bill.findNext('tbody').find('tr')
            while current_row != None:
                date = current_row.find('td', attrs = {'class' : "date"}).text.strip().replace(","," ")
                stage = current_row.find('td', attrs = {'class' : "stage"}).text.strip().replace(","," ")
                activity = current_row.find('td', attrs = {'class' : "activity"}).text.strip().replace(","," ")
                committee = current_row.find('td', attrs = {'class' : "committee"}).text.strip().replace(","," ")
                bill_info.addEvent(stage, date, activity, committee)

                current_row = current_row.findNextSibling('tr')

            # Getting the url of the detailed info
            info_url = url_base + title_url['href']
            bill_info.setDetails(Ontario.Extract_Info_Ontario(info_url))

            #print(bill_info.details)

            data.append(bill_info)

        if filename == None:
            # it will be saved as Legislative_Assembly_of_Ontario.csv
            filename = soup.find("meta", attrs = {'name' : "dc:publisher"})['content']
            filename = filename.replace(" ", "_")
            filename += ".csv"
        Ontario.Convert_to_csv(data, filename)

        self.bills=data

        return data
