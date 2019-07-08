import requests
import time
from tqdm import tqdm
import pandas as pd
from bs4 import BeautifulSoup
from string import ascii_lowercase

doctorList = []

def getRowInfo(resultRow):
    try:
        clinic = resultRow.find('span', 'resultCol clinicCol').find('a').text.strip()
        location = resultRow.find('span', 'resultCol locationCol').text[0:-4].strip()
        numbers = resultRow.find('span', 'resultCol phoneCol').text.replace(" ","").replace("\r\n", " ")[1:-2]
        return [clinic, location, numbers]
    except:
        return None

def getDocInfo(doc):
    try:
        rowInfo = []
        for row in doc.find_all('span', 'resultInfoRow'):
            rowInfo.append(getRowInfo(row))
        docImage = doc.contents[1].find('img')['src']
        if docImage == '/findadoctor/images/no_img.jpg':
            docImage = None
        docName = doc.contents[3].find('a', 'results').text.strip()
        return [docImage, docName, rowInfo]
    except:
        raise
        return None

def getDocsOnPage(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    for doctor in soup.find_all('div','resultRow'):
        doctorList.append(getDocInfo(doctor))

def getOtherPages(url):
    try:
        pages = []
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup.find('div', style="padding:5px 0px 5px 10px;margin:5px 0;background:#BEDCEB;").find_all('a'):
            pages.append(tag.contents)
        i = 1
        while i < len(pages):
            getDocsOnPage(('{}&page={}'.format(url, pages[i][0])))
            i+=1
    except:
        pass

def main():
    for letter in tqdm(ascii_lowercase, smoothing = .1, unit = 'Pages'):
        url = ('https://www.uwhealth.org/findadoctor/search/lastname?lastname={}'.format(letter))
        getDocsOnPage(url)
        getOtherPages(url)
    doctorListPD = pd.DataFrame(doctorList, columns = ["Photo URL", "Name", "Location Info"])
    # doctorListPD.to_excel("Doctors@UWHealth.xlsx")
    print(doctorListPD)

main()
