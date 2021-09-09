

from bs4 import BeautifulSoup
import lxml.html
import urllib.request, urllib.error
from urllib.parse import urlparse
import requests
import csv

#県毎のURLを取得する関数
def getPrefUrls():
    url =  "http://kikucyt.o.oo7.jp/f/f_jiti/fjiti_left.html"
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')

    names = []
    prefNames = []
    for link in soup.select("body td a"):
        la = (link.get('href') )
        names.append( la)
        prefNames.append(link.text)
        
    names = names[3:-1]   #これで必要な都道府県のみ
    prefNames = prefNames[3:-1]
    return names,prefNames


def getCityTownFromKenUrl(url,prefName):
    urlBase ="http://kikucyt.o.oo7.jp/f/f_jiti/"
    kenUrl = urlBase+url
    res = requests.get(kenUrl)
    kenSp = BeautifulSoup(res.content, 'html.parser')

    trs = kenSp.find_all("tr") # 各行をすべて考える
    kuBase =""
    city = -1
    town = 0
    
#    if len(trs[1].find_all('a')) == 1: #特別区！
#        print('特別:',trs[0].find_all('a')[0].get('href'))
        
    # 各市役所のリンク
    kenchoUrl=trs[0].find_all('a')[0].get('href')
#    kenchoUrl=trs[0].find_all('a')[0].text
    citiesUrl= []
    kuUrl=[]
    townsUrl=[]
    citiesName= []
    townsName=[]
    tokyoFlag = 0

    for idx,lin in enumerate(trs):
        count = len(lin.find_all('a'))
        if count == 1 and idx==0 and lin.find("a").get("href")=='https://www.metro.tokyo.lg.jp/':   #東京都
            tokyoFlag = 1
            kuBase = lin.find('a').get('href')
            kuBaseName = "東京都"
        if idx == 0:# ここは県庁のURL
            continue
#        print(idx,count)
        if count == 1 and len(townsUrl)==0 and lin.find("td").get("colspan")=='4':   #特別市
            kuBase = lin.find('a').get('href')
            kuBaseName =prefName+" "+lin.find('a').text
            citiesUrl.append(kuBase)  # 特別市リンク
            citiesName.append(kuBaseName) #市名称
            
#            print(citiesUrl,len(townsUrl))
            continue
        if kuBase != "":
            if count > 0: #特別市の区
                links = lin.find_all("a")
                for ll in links:
                    kuUrl.append((kuBase, kuBaseName+" "+ll.text, ll.get('href')))  #　区の名前も
            else: #count = 0
                kuBase = ""
                if tokyoFlag == 1:
                    tokyoFlag = 2
            continue
#        if len(kuUrl) >0 and count == 0: # 最初のkuのあとのスペースはパス
#            continue

        if lin.find("td").get("colspan")=='2' and count > 0 and len(townsUrl)==0 :  #都市
            links = lin.find_all("a")
            for ll in links:
                citiesUrl.append(ll.get('href'))
                citiesName.append(prefName+" "+ll.text) #市名称
            continue
        
        if tokyoFlag==2 and count > 0 and len(townsUrl)==0 :  #東京都,　市
            links = lin.find_all("a")
            for ll in links:
                citiesUrl.append(ll.get('href'))
                citiesName.append(prefName+" "+ll.text) #市名称
            continue

        if count == 0 and tokyoFlag == 2:
            tokyoFlag = 3
            continue

#鹿児島県エラー対策            
        if lin.find("td").get("bgcolor")=='#80FF80' and count > 7 :  # 町,村
            links = lin.find_all("a")[:6]
            for ll in links:
                townsUrl.append(ll.get('href'))
                townsName.append(prefName+" "+ll.text)
            continue
    
        
        if lin.find("td").get("bgcolor")=='#80FF80' and count > 0 :  # 町,村
            links = lin.find_all("a")
            for ll in links:
                townsUrl.append(ll.get('href'))
                townsName.append(prefName+" "+ll.text)
            continue
            
        if tokyoFlag==3 and count > 0 and lin.find("td").get('bgcolor')=='#D9FDBB' :  # 町,村
            links = lin.find_all("a")
            for ll in links:
                townsUrl.append(ll.get('href'))
                townsName.append(prefName+" "+ll.text)
            continue
        
        if tokyoFlag == 3 and  count == 1 and lin.find("td").get('bgcolor')=='#80000': #終わり
            print("End")
            break

        if count == 1 and lin.find("td").get('bgcolor')=='#80000': #終わり
            print("End")
            break

        if count == 1 and len(townsUrl)>0:
            if lin.find("td").get("colspan")=='4':
                break
       
            
    return (kenchoUrl,citiesUrl,citiesName,kuUrl,townsUrl,townsName)

def allCityTownFromKenUrls(urls,kenName):
    ks = []
    cs = []
    cns = []
    kus = []
    ts = []
    tns = []
    for i in range(len(urls)):
        (k,c,cn,ku,t,tn) =getCityTownFromKenUrl(urls[i],kenName[i])
#        print(k,len(c),len(ku),len(t))
        ks.append(k)
        cs.extend(c)
        cns.extend(cn)
        kus.extend(ku)
        ts.extend(t)
        tns.extend(tn)
    print(len(ks),len(cs),len(kus),len(ts))
    
    return(ks,kenName,cs,cns,kus,ts,tns)

# 自治体毎の URL を保存！（自治体番号を付けたいな)
def saveAllUrl(allURL):
    with open('allCityURL.csv','w',encoding='utf-8',newline='\n') as csvfile:
        sw = csv.writer(csvfile,delimiter=",", quoting=csv.QUOTE_MINIMAL)
        sw.writerow(["レベル","都道府県名","自治体名","URL"])
        for i in range(len(allURL[0])):  # 県
            sw.writerow(["Pref",allURL[1][i],"",allURL[0][i]])
        for i in range(len(allURL[2])):  # 市
            ss = allURL[3][i].split()
            if len(ss)>2:
                city = ss[1]+" "+ss[2]
            else:
                city = ss[1]
            sw.writerow(["City",ss[0],city,allURL[2][i]])
        for i in range(len(allURL[4])):  # 特別区
            nn = allURL[4][i][1].split()
            if len(nn)>2:
                ward = nn[1]+" "+nn[2]
            else:
                ward = nn[1]
            sw.writerow(["Ward",nn[0],ward,allURL[4][i][2]])

        for i in range(len(allURL[5])):
            nn = allURL[6][i].split()
            sw.writerow(["Town",nn[0],nn[1],allURL[5][i]])

def doitAll():
    kenUrls, kenName = getPrefUrls()
    allUrl = allCityTownFromKenUrls(kenUrls,kenName)
    return allUrl

def saveAll():
    allUrl = doitAll()
    saveAllUrl(allUrl)

if __name__ == "__main__":
    saveAll()


