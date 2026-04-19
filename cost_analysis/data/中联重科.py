import re
import json
import requests

headers = {
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Referer": "https://data.eastmoney.com/bbsj/yjbb/000157.html",
    "Sec-Fetch-Dest": "script",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\""
}
cookies = {
    "qgqp_b_id": "9fc3a7519a24ab23e662c4025ba69cfd",
    "st_si": "80908079383975",
    "xsb_history": "874380%7C%u5353%u6D77%u79D1%u6280%2C873924%7C%u5343%u5E74%u821F",
    "HAList": "ty-1-600031-%u4E09%u4E00%u91CD%u5DE5%2Cty-1-600078-%u6F84%u661F%u80A1%u4EFD",
    "st_asi": "delete",
    "st_pvi": "38932402311656",
    "st_sp": "2023-08-28%2022%3A05%3A35",
    "st_inirUrl": "https%3A%2F%2Fdata.eastmoney.com%2Fcjsj%2Fgdp.html",
    "st_sn": "35",
    "st_psi": "20241202162900191-113300301075-1250182183",
    "JSESSIONID": "289E2FC1D240FAB8050B47253B4B8985"
}
url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
params = {
    "callback": "jQuery1123013912870956472_1733128095884",
    "sortColumns": "REPORTDATE",
    "sortTypes": "-1",
    "pageSize": "50",
    "pageNumber": "1",
    "columns": "ALL",
    "filter": "(SECURITY_CODE=\"000157\")",
    "reportName": "RPT_LICO_FN_CPD"
}
response = requests.get(url, headers=headers, cookies=cookies, params=params)
Target_data_json = re.search('.*?"data":(.*?),"count".*?', response.text,re.S).group(1)
# print(Target_data_json,type(Target_data_json))

Target_data_dict = json.loads(Target_data_json)
print(len(Target_data_dict),type(Target_data_dict))

# 写入JSON数据
with open('中联重科.json', 'w', encoding='utf-8') as f:
    # 确保中文能正确写入，设置ensure_ascii=False
    json.dump(Target_data_dict[:20], f, ensure_ascii=False, indent=4)

