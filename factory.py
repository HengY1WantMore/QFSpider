import json
# import threading
# import queue
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException
from config import *
from common import *


class Selenium:
    def __init__(self, page, record, key: str, want: list):
        self.key = key  # 搜索语法
        self.want = want  # 搜索语法
        self.page = page  # 查看页数
        self.record = record  # 记录位置
        self.start = 0  # 拼凑翻页参数
        self.option = webdriver.ChromeOptions()
        self.option.add_experimental_option("excludeSwitches", ["enable-logging"])
        # self.option.add_argument('headless')  # 设置option
        self.browser = webdriver.Chrome(options=self.option)
        self.wait = WebDriverWait(self.browser, 10)

    def get_url_info(self, page):
        self.start = page * 10
        data = {'keyword': self.key}
        one = str(str(urlencode(data)).split('=')[1]).replace('%3A', ':') + (
            f'&start={str(self.start)}' if self.start != 0 else '')
        url = f"https://www.google.com.hk/search?q={one}"
        self.browser.get(url)
        text = self.browser.find_elements_by_xpath("//a")  # 拿到该页所有的链接
        effective_link = list(filter(
            lambda x: not bool(re.search('google', str(x.get_attribute("href")))) and x.get_attribute(
                "href") is not None, text))
        effective_link = list(map(lambda x: x.get_attribute("href"), effective_link))
        domain_list = list(
            set(list(map(lambda x: re.match(r'http.*?//(.*?)/.*?', x, re.M | re.I).group(), effective_link))))
        filter_repeat_list = list(
            filter(lambda x: re.match(r'http.*?//(.*?)/.*?', x, re.M | re.I).group() in domain_list,
                   effective_link))
        final_list = list(filter(lambda x: filter_url(x), filter_repeat_list))
        return final_list

    def get_each_page(self, url_want, times=1):  # 获取每一页的源码
        if times >= MaxTimes:
            log('./record/error.txt', f"{url_want} 无法请求\n")
            return False
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        }
        try:
            if IsOpen:
                proxies = {
                    'http': f'http://{Ip}:{Port}',
                    'https': f'https://{Ip}:{Port}'
                }
                response = requests.get(url_want, proxies=proxies, headers=header, timeout=5)  # 使用代理
            else:
                response = requests.get(url_want, headers=header, timeout=5)
            if response.status_code == 200 or str(response.status_code)[0] == '3':
                response.encoding = 'utf-8'
                if judge_js(response.text):
                    return self.get_page_info(url_want)
                else:
                    return parse_page(response.text, self.want) and parse_page(response.text, Black_want)
            else:
                return False
        except Exception as e:
            times += 1
            self.get_each_page(url_want, times)

    def get_page_info(self, page_url):  # 处理js渲染的链接
        try:
            self.browser.get(page_url)
            text = self.browser.page_source
            return parse_page(text, self.key)
        except Exception as e:
            log('./record/error.txt', f"处理js渲染的链接错误：{page_url}\n")
            return False

    def want_operation(self):  # 单线程主程序
        info = dict()
        info['source'] = self.key
        all_url = []
        for num in range(self.page):
            url_array = self.get_url_info(num)
            sort_res = list(filter(lambda x: self.get_each_page(x), url_array))
            all_url.append(sort_res)
            print(f"The Mission {info['source']} page: {num + 1} is done")
        info['url'] = dict(enumerate(all_url)) if all_url else {}
        if info['url'] != {}:
            log(self.record, str(json.dumps(info, ensure_ascii=False) + ',\n'))
        self.browser.quit()


def filter_url(url):
    domain = re.match(r'http.*?//(.*?)/.*?', url, re.M | re.I).group()
    if Black_domain:
        for one_black in Black_domain:
            if one_black in domain:
                return False
    return True


def parse_page(page, filter_list):
    keyword_processor = KeywordProcessor()
    if filter_list:
        for each in filter_list:
            keyword_processor.add_keyword(each)
        keywords_found = keyword_processor.extract_keywords(str(page))
        keywords_found = list(set(keywords_found))
        if len(keywords_found):
            return True
        else:
            return False
    else:
        return True


def judge_js(text):
    judge_fun = bool(re.search('function', str(text)))
    judge_p = bool(re.search('<p>', str(text)))
    if judge_fun and not judge_p:
        return True
    else:
        return False


def handleOnlyOne(search, record_path, pages_num):
    search = ' '.join(search[0])
    want = [] if search[1] == '' else search[1]
    Selenium(pages_num, record_path, search, want).want_operation()


def main(search, threads_num, record_path, pages_num, flag):
    if flag == 0:
        handleOnlyOne(search, record_path, pages_num)
    else:
        print(1)

    # class Signal(object):
    #     flag = False
    #
    # class Broser(object):
    #     def __init__(self):
    #         self.driver = webdriver.Chrome("E://chromedriver.exe")
    #
    #     def worker(self, uid):
    #         '''任务'''
    #         url = f"https://space.bilibili.com/{uid}"
    #         self.driver.get(url)
    #         try:
    #             # 显示等待，只等3秒
    #             name = WebDriverWait(self.driver, 3).until(
    #                 EC.presence_of_element_located((By.ID, "h-name"))
    #             )
    #         except TimeoutException:
    #             return (None, uid)
    #
    #         else:
    #             return (name.text, uid)
    #
    #     def __getattr__(self, item):
    #         if hasattr(self.driver, item):
    #             return getattr(self.driver, item)
    #         return getattr(self, item)
    #
    # class BroserThread(threading.Thread):
    #     def __init__(self, signal, dataQueue, broser):
    #         super(BroserThread, self).__init__()
    #         self.signal = signal
    #         self.dataQueue = dataQueue
    #         self.broser = broser
    #
    #     def run(self):
    #         while True:
    #             if self.signal.flag == False:
    #                 break
    #             try:
    #                 uid = self.dataQueue.get(block=False)
    #             except queue.Empty:
    #                 pass
    #             else:
    #                 datas = self.broser.worker(uid)
    #                 print(datas)
    #
    #                 self.dataQueue.task_done()

    # # 信号对象
    # signal = Signal()
    #
    # # 队列集
    # dataQueue = queue.Queue()
    #
    # # 生产者
    # offset = 125526
    # for i in range(10):
    #     offset += i
    #     dataQueue.put(offset)
    #
    # # 消费者
    # thread_num = 5
    # brosers = [Broser() for i in range(thread_num)]
    # signal.flag = True
    # for i in range(thread_num):
    #     thread = BroserThread(signal, dataQueue, brosers[i])
    #     thread.daemon = True
    #     thread.start()
    #
    # # 等待队列
    # dataQueue.join()
    #
    # signal.flag = False
    #
    # tuple(map(
    #     lambda b: b.quit(), brosers
    # ))


if __name__ == '__main__':
    main([['华为'], ''], 1, './record/record.json', 1, 0)
