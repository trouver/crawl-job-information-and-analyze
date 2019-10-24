#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

id = []
item_url = []

search_url = 'https://search.51job.com/list/090200,000000,0000,00,9,99,%25E6%2\
595%25B0%25E6%258D%25AE%25E5%2588%2586%25E6%259E%2590,2,1.html?lang=c&stype=&p\
ostchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&\
providesalary=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&di\
biaoid=0&address=&line=&specialarea=00&from=&welfare='
res = requests.get(search_url)  # 获取页面代码
soup = BeautifulSoup(res.text, features='lxml')  # 用 BeautifulSoup 分解页面代码
page_num_text = soup.select('.td')[0].text  # 获取含有页码的文本片段
page_num = int(re.search('\d+', page_num_text).group())  # 获得页码

for i in range(page_num):
    res = requests.get(search_url)
    #     res.encoding = 'gb2312' # 修改页面代码格式为 gb2312
    soup = BeautifulSoup(res.text, features='lxml')

    item_list = soup.select('.t1')  # 选出 class="t1" 下的内容
    for item in item_list:
        item_id_text = item.select('input')
        if len(item_id_text) > 0:  # 去除空值
            item_id = item_id_text[0]['value']
            id.append(item_id)
            item_url.append('https://jobs.51job.com/chengdu/'
                            + item_id + '.html')

    if i == 0:
        search_url = soup.select('.bk a')[0]['href']
    elif i == page_num - 1:
        pass
    else:
        search_url = soup.select('.bk a')[1]['href']

    print('Item list download progress: ' + str((i + 1) * 100 // page_num)
          + '% (' + str(i + 1) + '/' + str(page_num) + ')', end='\r')

data = pd.DataFrame({'item_url': item_url}, index=id)
data.index.name = 'id'
# data.to_csv('./item_list.csv')

print('Item list download finish!' + ' ' * 20)
