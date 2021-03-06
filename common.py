import base64
import os
import re
import time
from urllib.parse import urlencode
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
import openpyxl
import xlrd
import requests
from flashtext import KeywordProcessor

'''
公共库
'''


# @description: txt记录
# @Author: Hengyi
# @Date: 2021/8/6
# @Param: location:相对或者绝对位置
# @Param: text:记录的内容
def log(location, text):
    with open(location, "a+", encoding='utf-8') as f:
        f.write(text)


# @description: 读取excel文件内容
# @Author: Hengyi
# @Date: 2021/8/6
# @Param: file:相对或者绝对的excel文件
# @Param: col:列
# @Return: res:array
def get_info_excel(file, col):
    res = []
    wb = xlrd.open_workbook(filename=file)  # 打开文件
    sheet = wb.sheet_by_index(0)  # 通过索引获取表格
    col = sheet.col(col)[1:]  # 获取到目标
    for one in col:
        res.append(one.value)
    return res


# @description: 匹配网站
# @Author: Hengyi
# @Date: 2021/8/6
# @Param: info:文本
# @Return: str
def match_url(info):
    try:
        match = '.*?(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)./?'
        return re.match(match, info, re.M | re.I).group(1)
    except Exception as e:
        return ''


# @description: 获取文本某一倍数行的内容
# @Author: Hengyi
# @Date: 2021/8/6
# @Param: location:文本相对位置或者绝对位置
# @Param: multiple:例如所有的3的倍数
# @Return: array
def get_multiple_num(location, multiple):
    res = []
    with open(location, 'r', encoding='utf-8') as f:
        for num, line in enumerate(f):
            if (num - 1) % multiple == 0:
                line = line.replace('\n', '')
                res.append(line)
    return res


# @description: 获取图片的base编码
# @Author: Hengyi
# @Date: 2021/8/6
# @Param: location:相对或者绝对位置
# @Return:
def base(location):
    f = open(location, 'rb')
    image_base = base64.b64encode(f.read())
    f.close()
    image_str = str(image_base)
    real_image_str = image_str[2:len(image_str) - 1]
    os.remove(location)  # 可以注释，为了释放空间，获取了就删除了
    return 'data:image/jpg;base64,' + real_image_str


# @description: 写入excel文件中
# @Author: Hengyi
# @Date: 2021/8/6
# @Param: index: 编号（写入是从1开始）
# @Param: res: 内容
# @Param: col: 第几行
def write_excel(index, res, col):
    workbook = openpyxl.load_workbook("aim_test.xlsx")
    worksheet = workbook.worksheets[0]
    worksheet.cell(index + 2, col, res)
    workbook.save(filename="aim_test.xlsx")


# @description: 定位某字符串在数组中的下标
# @Author: Hengyi
# @Date: 2021/8/6
# @Param: arr:目标数组 item:元素
# @Return: int
def location_index(arr, item):
    index = [i for i, a in enumerate(arr) if a == item]
    if not index:
        return -1
    else:
        return index[0]


# @description: 处理每一行字数（防止记录一行字数过多）
# @Author: Hengyi
# @Date: 2021/8/6
# @Param: text:内容
# @Return: string
def handleNum(text):
    text = str(text)
    a = 0
    res = []
    container = ''
    for x in text:
        container += x
        a += 1
        if a == 100:
            res.append(container)
            a = 0
            container = ''
    res = '\n'.join(res)
    return res


# @description: 处理标注
# @Author: Hengyi
# @Date: 2021/8/6
# @Param: text:内容
# @Return: string
def handleAnnotation(text):
    text = text.replace('[1]', '')
    text = text.replace('[2]', '')
    text = text.replace('[3]', '')
    text = text.replace('[4]', '')
    text = text.replace('[5]', '')
    text = text.replace('[6]', '')
    text = text.replace('[7]', '')
    text = text.replace('[8]', '')
    text = text.replace('[9]', '')
    text = text.replace('[10]', '')
    text = text.replace('[11]', '')
    return text


# @description: 谷歌请求某页面中含有的链接
# @Author: Hengyi
# @Date: 2021/8/7
# @Param: want:搜索内容
# @return array
def get_info(want):
    browser = webdriver.Chrome()
    wait = WebDriverWait(browser, 10)
    res = []
    data = {'keyword': want}
    one = str(urlencode(data)).split('=')[1]
    browser.get('https://www.google.com.hk/search?q=' + one)
    time.sleep(2)  # 2秒的休眠给网络一个缓冲时间
    text = browser.find_elements_by_xpath("//a")
    for each in text:
        url = each.get_attribute("href")
        if not bool(re.search('google', str(url))) and url is not None:
            res.append(url)
    return res


# @description: 在该网页的源码中寻找是否存在关键字
# @Author: Hengyi
# @Date: 2021/8/7
# @Param: page:网页内容
# @Param: key:关键字
# @Return: array
def parse_page(page, key):
    keyword_processor = KeywordProcessor()
    keyword_processor.add_keyword(key)
    keywords_found = keyword_processor.extract_keywords(str(page))
    return keywords_found


# @description: 请求链接保存为指定图片
# @Author: Hengyi
# @Date: 2021/8/11
# @Param: url:请求链接
# @Param: name:想保存的名字
def urllib_download(url, name):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
        }
        if bool(re.search('https', str(url))):  # 则是https请求
            proxies = {'https': 'http://127.0.0.1:7890'}
        else:
            proxies = {'http': 'http://127.0.0.1:7890'}
        r = requests.get(url, proxies=proxies, headers=headers, timeout=4)
        if r.status_code == 200:
            with open(f"./img/{name}.jpg", 'wb') as f:
                f.write(r.content)
        else:
            log('./error.txt', f"{url}\n")
    except Exception as e:
        log('./error.txt', f"{url}\n")


# @description: 分析页面是不是js渲染
# @Author: Hengyi
# @Date: 2021/8/7
# @Param: text:网页内容
# @Return: boolean
def judge_js(text):
    judge_fun = bool(re.search('function', str(text)))
    judge_p = bool(re.search('<p>', str(text)))
    if judge_fun and not judge_p:
        return True
    else:
        return False


# @description: 文件转为字节流
# @Author: Hengyi
# @Date: 2021-08-26
# @Param: filename：位置
# @Return: binaryData：二进制
def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData
    

# @description: 数组切片
# @Author: Hengyi
# @Date: 2021-09-04
# @Param: items 数组
# @Param: n 倍数
# @Return: array：数组
def list_split(items, n):
    return [items[i:i+n] for i in range(0, len(items), n)]


banner = """
  ___  _____ ____        _     _           
 / _ \|  ___/ ___| _ __ (_) __| | ___ _ __ 
| | | | |_  \___ \| '_ \| |/ _` |/ _ \ '__|
| |_| |  _|  ___) | |_) | | (_| |  __/ |   
 \__\_\_|   |____/| .__/|_|\__,_|\___|_|   
                  |_|                      
"""