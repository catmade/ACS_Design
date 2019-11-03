# ACS_Deasign
《信息内容安全》课程设计——搜索引擎

## 项目目录结构
```
ACS_Design          // 主目录
    RawData
        *.json      // 数据
    DataCollection  // 数据收集
        *.py
    DataProcess     // 数据处理
        *.py
    WebApp          // 网站
        *.jar
```

## ElasticSearch
安装IK分词器，针对中文分词
创建索引
```
PUT 127.0.0.1:9200/page
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