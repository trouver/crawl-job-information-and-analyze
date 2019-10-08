#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from item_list import data as il_d

def get_standard_salary(salary):
# 将薪资单位标准化为「千/月」，值使用平均值
    if salary == '': return 0
    
    value_interregional = re.search('.*\d\B', salary).group()
    if re.search('-', value_interregional):
        value_min = float(re.search('(.+)-', value_interregional).group(1))
        value_max = float(re.search('-(.+)', value_interregional).group(1))
        value = value_min * 0.4 + value_max * 0.6 # 取区间六分位数
    else:
        value = float(value_interregional)
        
    unit = re.search('[0-9-.]+(.+)/(.+)', salary)
    unit_dict = {'万': 10, '千': 1, '元': 1 / 1000,
                 '小时': 1 / 720, '天': 1 / 30, '月': 1, '年': 12}
    value = value * unit_dict[unit.group(1)[0]] / unit_dict[unit.group(2)]
    
    return round(value, 2) # 保留两位小数

def get_standard_loc(text):
    if re.search('-', text):
        city = re.search('(.+)-', text).group(1)
        area = re.search('-(.+)', text).group(1)
        return city, area
    else:
        return text, ''

def get_index(list, str):
# 返回含有指定字符串的项的索引
    for i, value in enumerate(list):
        if re.search(str, value):
            return i
    return None

def get_standard_exp(text):
# 将工作经历标准化，值使用平均值
    if re.search('\d+', text):
        if re.search('-', text):
            value_min = float(re.search('(.+)-', text).group(1))
            value_max = float(re.search('-(\d+)', text).group(1))
            return round((value_min + value_max) / 2, 2)
        else:
            return int(re.search('\d+', text).group())
    else: return 0

def get_standard_date(date):
# 将发布日期标准化
    date_str = re.search('(.+)发布', date).group(1)
    return datetime.strptime('2019-' + date_str, '%Y-%m-%d')

def get_item_detail(url):
# 获取单条信息
    res = requests.get(url)
    res.encoding = 'gb2312' # 设置编码格式为 gbk
    soup = BeautifulSoup(res.text, features='lxml')

    id = soup.select('.cn input')[0]['value'] # id
    job_name = soup.select('.cn h1')[0]['title'] # 工作名称
    company_name = soup.select('.cname a')[0]['title'] # 公司名称
    
    salary = get_standard_salary(soup.select('.cn strong')[0].text) # 薪资
    
    more_detail = [x.strip() for x in soup.select('.msg')[0].text.split('|')]
    # 更多信息合集
    job_loc_city, job_loc_area = get_standard_loc(more_detail[0]) # 工作地点和区域
    
    job_exp_index = get_index(more_detail, '经验')
    if job_exp_index:
    # 工作经验
        job_exp_text = more_detail[job_exp_index]
        more_detail.remove(job_exp_text) # 移除单项信息
        job_exp = get_standard_exp(job_exp_text)
    else: job_exp = 0
        
    edu_index = get_index(more_detail, '初中及以下|中专|大专|高中|本科|硕士|博士')
    if edu_index:
    # 学历要求
        edu = more_detail[edu_index]
        more_detail.remove(edu)
    else: edu = ''
    
    req_num_index = get_index(more_detail, '^招.+人$')
    if req_num_index:
    # 招聘人数
        req_num_text = more_detail[req_num_index]
        more_detail.remove(req_num_text)
        if re.search('\d+', req_num_text):
            req_num = int(re.search('\d+', req_num_text).group())
        else: req_num = 100
    else: req_num = 0
    
    date_str = more_detail[get_index(more_detail, '发布')]
    release_date = get_standard_date(date_str) # 发布日期
    more_detail.remove(date_str)
    
    other_req = ' '.join(more_detail[1:]) # 其他附加信息
    
    welfare = ' '.join([x.text for x in soup.select('.sp4')]) # 福利信息

    job_detail_all = soup.select('.job_msg')[0].text
    del_index = re.search('职能类别', job_detail_all).start()
    # 返回指定字符在字符串中的位置
    job_detail = re.sub('\s+', '', job_detail_all[:del_index])
    # 职位详细信息
    
    func_cat = ' '.join(soup.select('.mt10 a')[0].text.split('/')) # 职能类别
    
    item_data = pd.DataFrame({'job_name': job_name,
                              'company_name': company_name,
                              'salary(k/m)': salary,
                              'job_loc_city': job_loc_city,
                              'job_loc_area': job_loc_area,
                              'job_exp': job_exp,
                              'edu': edu,
                              'req_num': req_num,
                              'release_date': release_date,
                              'other_req': other_req,
                              'welfare': welfare,
                              'job_detail': job_detail,
                              'func_cat': func_cat},
                             index=[id])
    return item_data

data = pd.DataFrame()
# il_d = pd.read_csv('./item_list.csv', index_col=0)
list = il_d['item_url']

for i, item_url in enumerate(list):
    try:
        item_data = get_item_detail(item_url)
    except IndexError:
        print('Item ' + str(i) + ' detail download fail!' + ' ' * 20)
        continue
    data = pd.concat([data, item_data])
    print('Item detail download progress: ' + str((i + 1) * 100 // len(list))
          + '% (' + str(i + 1) + '/' + str(len(list)) + ')', end='\r')
    
data.index.name = 'id'
all_data = pd.merge(il_d, data, left_index=True, right_index=True)
all_data.to_csv('./item_detail.csv')

print('Item detail download finish!' + ' ' * 20)