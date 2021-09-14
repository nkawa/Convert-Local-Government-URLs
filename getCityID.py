
from bs4 import BeautifulSoup
import lxml.html
import urllib.request, urllib.error
from urllib.parse import urlparse
import requests
import csv
import openpyxl
from io import BytesIO

# 自治体向けの団体コード＋URLの取得
# 2021/09/14 確認 
# Coded by Nobuo Kawaguchi

# 全国地方公共団体コード
# 総務省ページからダウンロード
allCityID_URL = "https://www.soumu.go.jp/main_content/000730858.xlsx"

# J-Lis からの自治体マップ URL
jLIS_map_URL = "https://www.j-lis.go.jp/spd/map-search/cms_1069.html"

# 自治体IDのリストから dict を作成
def doGetCityIDdicts(url = allCityID_URL):
    prefNameToID = {}
    prefIDToName = {}
    cityNameToID = {}
    cityIDToName = {}
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

# J-Lisから県毎のマップを取り出す
def getPrefUrls(url = jLIS_map_URL):
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')
    urls = []
    prefNames = []
    allLinks = soup.find_all('a')
    for a in allLinks:
        ltxt = a.text
        if ltxt.endswith("県") or ltxt.endswith("都") or  ltxt.endswith("道") or ltxt.endswith("府"):
            prefNames.append(a.text)
            urls.append("https://www.j-lis.go.jp"+a.get('href'))
    return urls,prefNames

# J-Lisの県毎のマップから、各自治体へのリンクを取り出す
def getCityTownFromKenUrl(url,prefName):
    res = requests.get(url)
    s = urlparse(url)
    kenSp = BeautifulSoup(res.content, 'html.parser')
    dd = kenSp.find_all("div",{"class": "wb-contents"})
    allLinks = dd[0].find_all("a")
    baseLinks= []
    if len(allLinks) < 5:  #only for Hokkaido
        for lk in allLinks:
            rres = requests.get(s.scheme+"://"+s.netloc+lk.get('href'))
            ssp = BeautifulSoup(rres.content, 'html.parser')
            dd = ssp.find_all("div",{"class": "wb-contents"})
            baseLinks.extend(dd[0].find_all("a"))
    else:
        baseLinks.extend(allLinks)

    lgUrls= []
    lgNames=[]
    for lk in baseLinks:
        ltxt = lk.text
        if ltxt == prefName:
            prefUrl = lk.get('href')
            continue
        if ltxt.endswith("市") or ltxt.endswith("町") or ltxt.endswith("村"):
            lgNames.append(prefName+" "+ltxt)
            lgUrls.append(lk.get('href')) 
        elif ltxt.endswith("区") and prefName=="東京都": # for Tokyo Wards
            lgNames.append(prefName+" "+ltxt)
            lgUrls.append(lk.get('href')) 
    return (prefUrl, lgUrls, lgNames)

# J-Lisから、全自治体へのリンクを取り出す
def allLGUrls():
    urls,kenNames = getPrefUrls()
    lgUrls = []
    lgNames = []
    prefUrls = {}
    for i in range(len(urls)):
        prefUrl, lgUrl,lgName =getCityTownFromKenUrl(urls[i],kenNames[i])
        prefUrls[kenNames[i]]= prefUrl
        lgUrls.extend(lgUrl)
        lgNames.extend(lgName)
        print("Get URLS for",kenNames[i],"count:",len(lgUrl))
     
    return(prefUrls, lgUrls,lgNames)

# 自治体毎の URL を保存！（自治体番号を付けたいな)
def saveAllLocalGovUrl(allURL):
    with open('allLocalGovURL.csv','w',encoding='utf-8',newline='\n') as csvfile:
        sw = csv.writer(csvfile,delimiter=",", quoting=csv.QUOTE_MINIMAL)
        sw.writerow(["都道府県名","自治体名","URL"])
        for i in range(len(allURL[0])):
            s = allURL[1][i].split()
            sw.writerow([s[0],s[1],allURL[0][i]])

# 総務省の自治体コードのworksheet に URL を追加、保存
def saveCityURLxlsx(url = allCityID_URL, xlsxName = "allCityID.xlsx", csvName= 'allCityURL.csv'):
    prefUrls, lgUrls,lgNames = allLGUrls()
    res = requests.get(url)
    wb = openpyxl.load_workbook(filename=BytesIO(res.content))
    ws = wb.worksheets[0]
    cityNameToID = {}
    for row in ws.rows:
        if row[0].value == "団体コード":
            row[5].value = "URL" # add URL for topline
            continue
        if row[2].value == None:  # prefecture
            row[5].value = prefUrls[row[1].value]  #prefURL
        else:
            cname = row[1].value+" "+row[2].value
            # J-LISと総務省での細かな違い
            if row[2].value == "梼原町":
                cname = "高知県 檮原町"
            elif row[2].value == "七ヶ宿町":
                cname = "宮城県 七ケ宿町"
            try:
                row[5].value = lgUrls[lgNames.index(cname)]  #cityName -> URL
                cityNameToID[cname] = row[0].value
            except ValueError:
                print("can't find URL for :",cname, row[4].value)
    # xslxファイルの保存
    try:
        wb.save(xlsxName)
    except PermissionError:
        print("Permission error")
    # csvファイルの保存
    print("Writing city URLs into ", csvName)
    with open(csvName,'w',encoding='utf-8',newline='\n') as csvfile:
        sw = csv.writer(csvfile,delimiter=",", quoting=csv.QUOTE_MINIMAL)
        sw.writerow(["団体コード", "都道府県名","自治体名","URL"])
        for i in range(len(lgUrls)):
            s = lgNames[i].split()
            sw.writerow([cityNameToID[lgNames[i]],s[0],s[1],lgUrls[i]])

            
if __name__ == "__main__":
 #   pn2i,pi2n,cn2i,ci2n = doGetCityID()
   saveCityURLxlsx()
 
