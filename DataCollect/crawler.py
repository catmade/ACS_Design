import sys
import requests
import json
import codecs
import threading
import time
import os
import hashlib
from bs4 import BeautifulSoup

sys.path.extend(['C:\\Users\\Neo\\PycharmProjects\\test', 'C:/Users/Neo/PycharmProjects/test'])

import ACS.DataProcess.PageRank
import ACS.DataProcess.Text_Classification.Classify


abs_dir = os.path.split(os.path.realpath(sys.argv[0]))[0]

# 启动计时器
start_time = time.perf_counter()

# 限定页面个数
total_pages = 20000
# 线程个数
thread_account = 100
# 起始url
initial_url = 'http://jwc.wust.edu.cn'
# 限定域名
restricted_domain = [
    'edu.cn'
]

banned_domain = [
    'www.paper.edu.cn'
]


program_aborted = False
index = 0
url_unvisited = []
url_visited = []

# 未访问url、已访问url以及文件序号锁
url_unvisited_lock = threading.Lock()
url_visited_lock = threading.Lock()
index_lock = threading.Lock()


def init_first_time():
    global index
    result = get_result(initial_url)
    if result['url'] == 'broken_url':
        print('Error:url is broken!Please correct the url and try again.')
        return

    md5 = hashlib.md5()
    md5.update(initial_url.encode('utf-8'))

    url_unvisited.extend(result['link'])

    tmp_list = list()

    while result['link']:
        md5_tmp = hashlib.md5()
        md5_tmp.update(result['link'].pop().encode('utf-8'))
        tmp_list.append(md5_tmp.hexdigest())

    result['link'] = tmp_list

    with codecs.open(abs_dir + '/../RawData/' + md5.hexdigest() + '.json', 'w', encoding="utf-8") as fp:
        index += 1
        json.dump(result, fp=fp, indent=4, ensure_ascii=False)


def get_result(url):
    global restricted_domain
    url_list = []
    result = {
        'title': '',
        'url': '',
        'content': '',
        'link': [],
        'update_date': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
    }
    try:
        r = requests.get(url, headers=headers, timeout=8, allow_redirects=False)
        r.raise_for_status()
        if r.status_code != 200:
            raise Exception
    except:
        result['url'] = 'broken_url'
        return result

    listed_link = r.url.split('/')
    if len(listed_link) != 3 and '.' in listed_link[-1]:
        if listed_link[-1].split('.')[1] not in ['html', 'htm', 'php']:
            result['url'] = 'broken_url'
            return result

    r.encoding = r.apparent_encoding
    soup = BeautifulSoup(r.text, 'html.parser')
    links = soup.find_all('a')

    if soup.title is None:
        result['title'] = '无标题'
    else:
        result['title'] = soup.title.text

    result['url'] = r.url
    deleted = [s.extract() for s in soup('script')]
    deleted = [s.extract() for s in soup('style')]
    deleted = [s.extract() for s in soup('title')]
    result['content'] = ' '.join(soup.get_text().replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').split())
    domain = list(filter(None, r.url.split('/')))[1]
    for link in links:
        unhandled_link = link.get('href')
        if unhandled_link is None:
            continue
        if unhandled_link[:1] == '/':
            handled_link = r.url.split('/')[0] + '//' + domain + unhandled_link
        elif unhandled_link[:4] == 'http':
            handled_link = unhandled_link
        else:
            continue

        if handled_link in url_list:
            pass
        else:
            domain = list(filter(None, handled_link.split('/')))[1]
            l_domain = domain.split('.')
            if len(l_domain) <= 3:
                continue
            if domain in banned_domain \
                    or f'{l_domain[-2]}.{l_domain[-1]}' not in restricted_domain:
                # print(spider_thread_info + '(' + url + ') not in restricted domain,skip')
                continue
            url_list.append(handled_link)

    result['link'] = url_list

    return result


def spider_thread():
    global url_unvisited
    global url_visited
    global restricted_domain
    global index
    global start_time
    spider_thread_info = '[' + threading.current_thread().name + ']'

    while True:
        if program_aborted:
            break

        url_unvisited_lock.acquire()
        try:
            if not url_unvisited:
                return
            url = url_unvisited.pop()
        finally:
            url_unvisited_lock.release()

        url_visited_lock.acquire()
        try:
            if url in url_visited:
                # print(spider_thread_info + '(' + url + ') url visited,skip')
                continue

            url_visited.append(url)
        finally:
            url_visited_lock.release()

        result = get_result(url)

        if result['url'] == 'broken_url':
            # print(spider_thread_info + 'broken url,skip')
            continue

        url_unvisited_lock.acquire()
        try:
            url_unvisited.extend(result['link'])
        finally:
            url_unvisited_lock.release()

        # MD5算法处理url作为文件名
        md5 = hashlib.md5()
        md5.update(url.encode('utf-8'))

        tmp_list = list()

        while result['link']:
            md5_tmp = hashlib.md5()
            md5_tmp.update(result['link'].pop().encode('utf-8'))
            tmp_list.append(md5_tmp.hexdigest())

        result['link'] = tmp_list
        continue_flag = 0
        for i in ['页面未找到', '页面无效', '页面不存在', '访问地址无效']:
            if i in result['content']:
                continue_flag = 1
        if continue_flag == 1:
            continue
        with codecs.open(abs_dir + '/../RawData/' + md5.hexdigest() + '.json', 'w', encoding="utf-8") as fp:
            index_lock.acquire()
            try:
                index += 1
                print('\rCrawling data [%d]' % index, end='')
            finally:
                index_lock.release()
            json.dump(result, fp=fp, indent=4, ensure_ascii=False)


def main():
    global program_aborted
    global index
    global url_unvisited
    global url_visited

    if not os.path.exists(abs_dir + '/../RawData/'):
        os.makedirs(abs_dir + '/../RawData/')

    # 打印起始日期时间
    start_date = time.strftime('%Y-%m-%d %H:%M:%S')
    print('Project start at:' + start_date)

    # 创建线程
    thread_list = [threading.Thread(target=spider_thread, name='SpiderThread' + str(i)) for i in range(thread_account)]

    # 启动时检测本地文件url_visited与url_unvisited是否存在
    if os.path.exists(abs_dir + '/progress.json'):
        temp = dict()
        with codecs.open(abs_dir + '/progress.json', 'r', encoding='utf-8') as fp:
            temp = json.load(fp=fp)
        url_unvisited = temp['url_unvisited']
        url_visited = temp['url_visited']
        index = temp['index']
    else:
        print('Running for the first time, launch init function')
        init_first_time()

    for i in thread_list:
        i.start()
    os.system('cls')
    print('Threading initializing complete!')
    try:
        while True:
            # 主线程等待
            if index >= total_pages or not url_unvisited:
                raise KeyboardInterrupt
            time.sleep(1)
    except KeyboardInterrupt:
        print('\nProgram stopped, waiting for threads to join in...')
        program_aborted = True
        wait_time = time.perf_counter()
        for i in thread_list:
            i.join()
        wait_time = time.perf_counter() - wait_time
        print('\nWaiting time %s' % str(wait_time))
        # 打印时间
        print('Crawling complete at %s !' % time.strftime('%Y-%m-%d %H:%M:%S'))
        print('Total %s pages found.' % index)
        print('Using time:%s seconds' % str(time.perf_counter() - start_time))
        save_file = {
            'url_unvisited': url_unvisited,
            'url_visited': url_visited,
            'index': index
        }
        if index <= total_pages:
            with codecs.open(abs_dir + '/progress.json', 'w', encoding='utf-8') as fp:
                json.dump(save_file, fp=fp, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()
    time.sleep(2)
    os.system('cls')
    ACS.DataProcess.PageRank.run()
    time.sleep(2)
    os.system('cls')
    ACS.DataProcess.Text_Classification.Classify.run()
