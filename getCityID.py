
from bs4 import BeautifulSoup
import lxml.html
import urllib.request, urllib.error
from urllib.parse import urlparse
import requests
import csv
import openpyxl
from io import BytesIO


# 全国地方公共団体コード
allCityID_URL = "https://www.soumu.go.jp/main_content/000730858.xlsx"

def doGetCityID(url = allCityID_URL):
    prefNameToID = prefIDtoName={}
    cityNameToID = cityIDtoName={}
    res = requests.get(url)
    wb = openpyxl.load_workbook(filename=BytesIO(res.content))
    ws = wb.worksheets[0]
    for row in ws.rows:
        if row[0].value == "団体コード":
            continue
        if row[2].value == None:  # prefecture
            prefNameToID[row[1].value] = row[0].value
            prefIDToName[row[0].value] = row[1].value
        else:
            cityNameToID[row[1].value+" "+row[2].value] = row[0].value
            cityIDToName[row[0].value] = row[1].value+" "+row[2].value

    return prefNameToID,prefIDToName,cityNameToID,cityIDToName
            
if __name__ == "__main__":
    pn2i,pi2n,cn2i,ci2n = doGetCityID()
