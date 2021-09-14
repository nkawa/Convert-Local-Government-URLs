# Convert-Local-Goverment-URLs
### 2021/09/14 公開 by N.Kawaguchi

日本の自治体の URL を全部取得したい！ということから、URLを取得するコードを作成しました。
総務省と J-Lis のサイトのデータを使っています。

基本的には、 allCityURL.csv をそのまま利用していただくのが良いです。

もし、更新がされている場合は Python3 で getCityID.py を実行すると、

1. J-Lis からの自治体マップ URL から、各自治体のURLを取得

jLIS_map_URL = "https://www.j-lis.go.jp/spd/map-search/cms_1069.html"


2. 総務省の以下のリンクから、団体コードを取得

allCityID_URL = "https://www.soumu.go.jp/main_content/000730858.xlsx"

をおこない、この２つを結合して allCityID.xlsx と allCityURL.csv を作成します。


keywords:
 全自治体URL
 団体コード URL
 