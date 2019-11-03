import os
import sys
import json
import numpy as np
import time
import codecs

dir_path = os.path.split(os.path.realpath(sys.argv[0]))[0] + '/../RawData'

print(dir_path)
Vexname = list(os.listdir(dir_path))
Vexnum = len(Vexname)
epoch = 50

# 初始化，去掉所有未在url中出现的link以及错误文件
def init():
    global Vexnum
    falsefiles={}
    idx=0
    start = time.perf_counter()
    for file in Vexname:
        if idx % 100 == 0:
            a = '=' * int(idx / Vexnum * 100)
            b = ' ' * (100 - int(idx / Vexnum * 100))
            c = int(idx / Vexnum * 100)
            dur = time.perf_counter() - start
            sys.stdout.write("\r{:^3.0f}%[{}=>{}]{:.2f}s".format(c, a, b, dur))
            sys.stdout.flush()
        with codecs.open(os.path.join(dir_path, file), 'r', encoding='utf-8') as load_f:
            try:
                text = json.load(load_f)
            except:
                falsefiles[file]=Vexname.index(file)-len(falsefiles)
                continue
            try:
                links = []
                for link in text['link']:
                    if link+'.json' in Vexname:
                        links.append(link)
                text['link'] = links.copy()
            except:
                pass
            finally:
                if 'link' in text:
                    text['link'].clear()
                else:
                    text['link'] = []
        with codecs.open(os.path.join(dir_path, file), 'w', encoding='utf-8') as dump_f:
            json.dump(text, dump_f, ensure_ascii=False,indent=4)
        idx += 1
    print('正在删除错误文件及链接...')
    Vexnum -= len(falsefiles)
    checknum=0
    checkfalse=0
    for file in list(falsefiles.keys()):
        os.remove(os.path.join(dir_path,file))
        Vexname.remove(file)
        for i in range(checknum,falsefiles[file]):
            with codecs.open(os.path.join(dir_path, Vexname[i]), 'r', encoding='utf-8') as load_f:
                text = json.load(load_f)
                try:
                    for falsefile in list(falsefiles.keys())[checkfalse:]:
                        if falsefile in text['link']:
                            text['link'].remove(falsefile)
                except:
                    text['link'].clear()
            with codecs.open(os.path.join(dir_path, Vexname[i]), 'w', encoding='utf-8') as dump_f:
                json.dump(text, dump_f, ensure_ascii=False,indent=4)
        checknum += falsefiles[file]
        checkfalse += 1

# 计算PageRank
def Rank(Value, start):
    NewValue=np.zeros(Vexnum,dtype=np.double)
    for iter in range(1,epoch):
        a = '=' * int(iter / epoch * 100)
        b = ' ' * (100 - int(iter / epoch * 100))
        c = int(iter / epoch * 100)
        dur = time.perf_counter() - start
        sys.stdout.write("\r{:^3.0f}%[{}=>{}]{:.2f}s".format(c, a, b, dur))
        sys.stdout.flush()
        for i in range(Vexnum):
            with open(os.path.join(dir_path, Vexname[i]), 'r', encoding='utf-8') as load_f:
                text = json.load(load_f)

                count = len(text['link'])

                if count == 0:
                    NewValue[i] = Value[i]
                    continue
                for link in text['link']:
                    link += '.json'
                    NewValue[Vexname.index(link)] += Value[i] / count
        for i in range(Vexnum):
            NewValue[i] = NewValue[i] / (iter + 1) + Value[i] * (iter / (iter + 1))
        Value=NewValue.copy()
    return Value


def run():
    print('开始计算PageRank...')
    print('数据初始化...')
    init()
    Value = np.ones(len(Vexname),dtype=np.double)*(1000.0/Vexnum)
    print('错误文件删除完毕！')
    print('正在计算PageRank(迭代次数{})...'.format(epoch))
    start = time.perf_counter()
    Value = Rank(Value, start)
    a = '=' * 100
    b = ' ' * 0
    c = 100
    dur = time.perf_counter() - start
    sys.stdout.write("\r{:^3.0f}%[{}=>{}]{:.2f}s".format(c, a, b, dur))
    sys.stdout.flush()
    print('\nPageRank计算完毕，正在往JSON中写入数据...')
    max = {}
    for file in Vexname:  # 将PageRank写入JSON
        with open(os.path.join(dir_path, file), 'r', encoding='utf-8') as load_f:
            text = json.load(load_f)
        with open(os.path.join(dir_path, file), 'w', encoding='utf-8') as dump_f:
            text['weight'] = Value[Vexname.index(file)]
            max[file] = text['weight']
            json.dump(text, dump_f, ensure_ascii=False,indent=4)
    print('数据写入完毕...')


if __name__ == '__main__':
    run()
