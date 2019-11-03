# 导入必要的包
import json
import os
import sys
import time
import math
import gc

import elasticsearch
import numpy as np
import paddle.fluid as fluid

dir_path = os.path.dirname(os.path.realpath(__file__))
# 用训练好的模型进行预测并输出预测结果
# 创建执行器
place = fluid.CPUPlace()
exe = fluid.Executor(place)
exe.run(fluid.default_startup_program())

save_path = os.path.join(dir_path, 'infer_model/')

# 从模型中获取预测程序、输入数据名称列表、分类器
[infer_program, feeded_var_names, target_var] = fluid.io.load_inference_model(dirname=save_path, executor=exe)

# 主机
host = "py7hon.com:9200"

# 建立 elasticsearch 连接
try:
    es = elasticsearch.Elasticsearch(hosts=host)
except Exception as e:
    print(e)
    exit()


# 获取数据
def get_data(sentence):
    # 读取数据字典
    with open(os.path.join(dir_path, 'dict_txt.txt'), 'r', encoding='utf-8') as f_data:
        dict_txt = eval(f_data.readlines()[0])
    dict_txt = dict(dict_txt)
    # 把字符串数据转换成列表数据
    keys = dict_txt.keys()
    data = []
    for s in sentence:
        # 判断是否存在未知字符
        if not s in keys:
            s = '<unk>'
        data.append((np.int64)(dict_txt[s]))
    return data

def batch_reader(Json_list,json_path):
    datas = []
    gc.collect()
    json_files = []
    falsefiles = []
    datas.clear()
    falsefiles.clear()
    json_files.clear()
    start = time.perf_counter()
    i=0
    scale = 100
    for file in Json_list:
        if i % 100 == 0:
            a = '=' * int(i / len(Json_list) * 100)
            b = ' ' * (scale - int(i / len(Json_list) * 100))
            c = int(i / len(Json_list) * 100)
            dur = time.perf_counter() - start
            sys.stdout.write("\r{:^3.0f}%[{}=>{}]{:.2f}s".format(c, a, b, dur))
            sys.stdout.flush()
        i+=1
        with open(os.path.join(json_path, file), "r", encoding='utf-8') as f:
            try:
                text = json.load(f)
            except:
                falsefiles.append(file)
                continue
            json_files.append(os.path.join(json_path, file))
            json_text = text['content']
            data = get_data(json_text)
            datas.append(data)
    for file in falsefiles:
        os.remove(os.path.join(dir_path, file))
    file_count = len(Json_list) - len(falsefiles)
    a = '=' * 100
    b = ' ' * 0
    c = 100
    dur = time.perf_counter() - start
    sys.stdout.write("\r{:^3.0f}%[{}=>{}]{:.2f}s".format(c, a, b, dur))
    sys.stdout.flush()
    print('\n文本数据获取完毕，共计{0}条文本数据，有效数据{2}条，无效数据{1}条（已删除）！'.format(len(Json_list),len(falsefiles),file_count))
    print('AI正在加载分类模型...')
    # 获取每句话的单词数量
    base_shape = [[len(c) for c in datas]]

    # 生成预测数据
    tensor_words = fluid.create_lod_tensor(datas, base_shape, place)

    # 执行预测
    result = exe.run(program=infer_program,
                     feed={feeded_var_names[0]: tensor_words},
                     fetch_list=target_var)
    print('模型加载完毕！')
    # 分类名称
    names = ['文化', '娱乐', '体育', '财经', '房产', '汽车', '教育', '科技', '国际', '证券']
    count = np.zeros(10)
    print('AI正在对文本数据进行分类并上传至ES：')
    # 获取结果概率最大的label
    start = time.perf_counter()
    for i in range(file_count):
        if i % 100 == 0:
            a = '=' * int(i / file_count * 100)
            b = ' ' * (scale - int(i / file_count * 100))
            c = int(i / file_count * 100)
            dur = time.perf_counter() - start
            sys.stdout.write("\r{:^3.0f}%[{}=>{}]{:.2f}s".format(c, a, b, dur))
            sys.stdout.flush()
        lab = np.argsort(result)[0][i][-1]
        # print('预测结果标签为：%d，  名称为：%s， 概率为：%f' % (lab, names[lab], result[0][i][lab]))
        count[lab] += 1
        with open(json_files[i], 'r', encoding='utf-8') as load_f:
            try:
                text = json.load(load_f)
            except:
                continue
        text['content_type'] = names[lab]

        id = json_files[i].split('\\')[-1].split('.')[0]
        #try:
        del text['link']
        response = es.index(index='page', doc_type='_doc', id=id, body=text)
        #except Exception:
        # print("\n" + "数据 " + id + " 插入失败，错误信息：" + response)

        # with open(os.path.join(json_path,json_files[i].split('\\')[-1]),'w') as dump_f:
        #     json.dump(text,dump_f)
    a = '=' * 100
    b = ' ' * 0
    c = 100
    dur = time.perf_counter() - start
    sys.stdout.write("\r{:^3.0f}%[{}=>{}]{:.2f}s".format(c, a, b, dur))
    sys.stdout.flush()
    print("\n" + "%d条文本数据分类结束！已全部上传至ES" % (file_count))


def run():
    # 获取图片数据
    print('AI正在获取文本数据...')
    json_path = os.path.realpath(__file__) + '/../../../RawData'
    Json_list = os.listdir(json_path)
    batch_size=500
    if len(Json_list)>batch_size:
        Json_batch=0
        print('当前文本数量为{0}条，正在分批处理...'.format(len(Json_list)))
        for batch_id in range(math.ceil(len(Json_list)/batch_size)):
            a=(batch_size if batch_size<(len(Json_list)-Json_batch) else len(Json_list)-Json_batch)
            print('正在处理第{0}批，数量为{1}...'.format(batch_id+1,a))
            batch_reader(Json_list[Json_batch:Json_batch+a],json_path)
            Json_batch += a
    else:
        batch_reader(Json_list,json_path)


if __name__ == '__main__':
    run()
