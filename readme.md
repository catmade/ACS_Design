# 通用小规模搜索引擎 

<img src="./images/logo.png" width="300px" alt="logo" align="">

《信息内容安全》课程设计——搜索引擎

## 目录

- [背景](#背景)
- [运行环境](#运行环境)
- [运行步骤](#运行步骤)
    - [安装、配置ElasticSearch并启动](#安装、配置ElasticSearch并启动)
    - [启动Web服务](#启动Web服务)
    - [数据的爬取与预处理](#数据的爬取与预处理)
    - [计算PageRank值](#计算PageRank值)
    - [利用AI进行文本分类并上传至ES](#利用AI进行文本分类并上传至ES)
    - [Enjoy](#Enjoy)
- [相关项目](#相关项目)
- [主要项目负责人](#主要项目负责人)
- [参考资料](#参考资料)

## 背景

《信息内容安全》网络信息内容获取技术课程项目设计
- 一个至少能支持10个以上网站的爬虫程序，且支持增量式数据采集;并至少采集10000个实际网页;
- 针对采集回来的网页内容， 能够实现网页文本的分类;
- 可进行重复或冗余网页的去重过滤;
- 对经去冗以后的内容建立倒排索引;
- 采用PageRank算法实现搜索结果的排序;
- 支持自然语言的模糊检索;
- 可实现搜索结果的可视化呈现。
- 可以在线记录每次检索的日志，井可对日志数据进统计分析和关联挖掘。

## 运行环境

- 平台：全平台

- jdk 1.8.0

- ElasticSearch 7.4.0

- Python 3.6 及以上

    - 安装依赖模块
        - PageRank算法、AI文本分类与上传
            ```
            > pip install paddlepaddle numpy elasticsearch
            ```
        - 数据的爬取与预处理
            ```
            > pip install requests bs4
            ```

## 运行步骤

### 安装、配置 ElasticSearch 并启动
- [下载](https://www.elastic.co/cn/downloads/elasticsearch) 并解压Elasticsearch，详细步骤自行搜索
    - 可以从 apt 和 yum 的软件仓库安装，也可以使用 Windows MSI 安装包安装
- [安装](https://github.com/medcl/elasticsearch-analysis-ik/releases) IK 中文分词器，详细步骤自行搜索
- 创建索引
    ```
    PUT http://127.0.0.1/page
    {
        "settings": {
            "number_of_shards": "5",
            "number_of_replicas": "0"
        },
        "mappings": {
            "properties": {
                "title": {
                    "type": "text",
                    "analyzer": "ik_max_word"
                },
                "weight": {
                    "type": "double"
                },
                "content" : {
                    "type" : "text",
                    "analyzer": "ik_max_word"
                },
                "content_type": {
                    "type": "text"
                },
                "url": {
                    "type": "text",
                    "analyzer": "ik_max_word"
                },
                "update_date": {
                    "type": "date",
                    "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
                }
            }
        }
    }
    ```
- 启动 ElasticSearch ，在 bash 中执行 `bin/elasticsearch` 或者在 Windows 的 cmd、powershell 执行 `bin\elasticsearch.bat`

### 启动Web服务

```
> cd WebApp
> java -jar *.jar
```

![启动Web服务](./images/launchWeb.gif)

### 数据的爬取与预处理

```
> cd DataCrawler
> python crawler.py
```

![网络爬虫](./images/crawler.gif)

### 计算PageRank值

```
> cd DataProcess
> python PageRank.py
```

![PageRank算法](./images/PageRank.gif)

### 利用AI进行文本分类并上传至ES

```
> cd DataProcess/Text_Classification
> python Classify.py
```

![AI文本分类](./images/AI.gif)

### Enjoy

访问[http://127.0.0.1:80](http://127.0.0.1:80)

![访问主页](./images/homePage.png)

## 相关项目

- web服务
    - [Searcher](https://github.com/1811455433/Searcher)

## 主要项目负责人

|<a href="https://github.com/1811455433"><img src="https://avatars1.githubusercontent.com/u/38749472?s=460&v=4" width="64" height="64" alt="WangWei Github头像"></a>|<a href="https://github.com/AgentAnderson" ><img src="https://avatars2.githubusercontent.com/u/48425922?s=460&v=4" width="64" height="64" alt="AgentAnderson Github头像"></a>|<a href="https://github.com/Shelly111111"><img src="https://avatars0.githubusercontent.com/u/50294940?s=460&v=4" width="64" height="64" alt="Shelly111111 Github头像"></a>|
|:--:|:--:|:--:|
|[@WangWei](https://github.com/1811455433) |[@AgentAnderson](https://github.com/AgentAnderson)|[@Shelly111111](https://github.com/Shelly111111)|
|[Web服务](https://github.com/1811455433/Searcher)|[数据爬取](https://github.com/1811455433/ACS_Design/tree/master/DataCollect)|[数据处理](https://github.com/1811455433/ACS_Design/tree/master/DataProcess)|

## 参考资料

[1]  [SpringBoot项目实战 视频教程全集 | 35小时](https://www.bilibili.com/video/av62800055)

[2]  [从入门到摔门【Java】ElasticSearch6入门教程（62集）](https://www.bilibili.com/video/av54116325)