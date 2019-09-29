#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import re
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from mpl_toolkits.mplot3d import Axes3D
from pyecharts import options as opts
from pyecharts.charts import Geo
from pyecharts.globals import ChartType
import os
import jieba
import jieba.analyse
# from item_detail import all_data as id_ad

font_path = '/System/Library/Fonts/PingFang.ttc' # 中文字体路径
font_zh = FontProperties(fname=font_path)

id_ad = pd.read_csv('./item_detail.csv', index_col=0)

regex = re.compile('数据分析|data ?analysis|大数据|big ?data', flags=re.I)
bool_arr = pd.Series(index=id_ad.index)
  
for item in id_ad.itertuples():
# 按行遍历数据
    if regex.search(item.job_name):
        bool_arr[item.Index] = True 
    else:
        bool_arr[item.Index] = False
  
data = id_ad[bool_arr]
# 根据职位名称进行数据清洗

# 工资分析
salary_data = data['salary(k/m)'][data['salary(k/m)'] != 0] # 去除未标注工资项
salary_des = salary_data.describe() # 工资基本数据，包括平均数、中位数等
cats = pd.cut(salary_data, 18, precision=2) # 分为 18 个区间
salary_counts = pd.value_counts(cats).sort_index() # 统计每个区间的频率

fig = plt.figure('工资分布统计详情', figsize=[16, 5])
plt.subplots_adjust(left=0.03, bottom=0.3, right=0.97, top=0.9, wspace=0.3)
# 设置画图边框和子图间距

ax1 = fig.add_subplot(141)
plt.title('工资详情描述', fontproperties=font_zh)
for i, v in enumerate(salary_des):
    plt.text(0.05, 1 - (i + 1) * 0.07,
             salary_des.index[i] + ': ' + str(round(v, 2)))
plt.xticks([]) # 设置空坐标轴
plt.yticks([])

ax2 = fig.add_subplot(142)
salary_counts_other = pd.Series({'更高': salary_counts[8:].sum()})
salary_counts_pie = salary_counts_other.append(salary_counts[-11::-1])[::-1]
salary_counts_pie.plot.pie(autopct='%.2f%%', pctdistance=0.7, labeldistance=0.9,
                           startangle=90, counterclock=False, radius=1.2,
                           textprops={'fontproperties': font_zh})
# 自动求百分比，保留两位小数；百分比位置，默认 0.6；标签位置，默认 1.1；
# 十二点钟方向开始，默认九点钟方向开始；顺时针方向画图，默认逆时针；饼图半径，默认 1；字体设置
plt.title('工资分布饼图', fontproperties=font_zh)
plt.ylabel('') # 设置空坐标轴标签

ax3 = fig.add_subplot(122)
salary_counts.plot.bar()
for i, v in enumerate(salary_counts):
    plt.text(i, v, v, ha='center', va='bottom')
plt.title('工资分布柱状图', fontproperties=font_zh)
plt.xlabel('工资区间（千/月）', fontproperties=font_zh)
plt.ylabel('数量', fontproperties=font_zh)

# 地点分析
loc_data = data['job_loc_area'][(data['job_loc_city'] == '成都')
                                & data['job_loc_area'].notnull()]
loc_counts = loc_data.value_counts()

fig = plt.figure('区域分布详情', figsize=[16, 5])
plt.subplots_adjust(left=0.05, bottom=0.2, right=0.99, top=0.9)

ax1 = fig.add_subplot(131)
loc_counts.plot.bar()
for i, v in enumerate(loc_counts):
    plt.text(i, v, v, ha='center', va='bottom')
plt.title('区域分布柱状图', fontproperties=font_zh)
plt.xticks(range(len(loc_counts)), loc_counts.index, fontproperties=font_zh)
plt.xlabel('区域', fontproperties=font_zh)
plt.ylabel('数量', fontproperties=font_zh)

ax2 = fig.add_subplot(132)
loc_counts_other = pd.Series({'其他区域': loc_counts[7:].sum()})
loc_counts_pie = loc_counts_other.append(loc_counts[-6::-1])[::-1]
loc_counts_pie.plot.pie(autopct='%.2f%%', pctdistance=0.7, labeldistance=0.9,
                        startangle=90, counterclock=False, radius=1.2,
                        textprops={'fontproperties': font_zh})
plt.title('区域分布饼图', fontproperties=font_zh)
plt.ylabel('')

ax3 = fig.add_subplot(133)
avg_salary_by_loc = salary_data.groupby(loc_data).mean()\
.sort_values(ascending=False)
avg_salary_by_loc.plot.bar()
for i, v in enumerate(avg_salary_by_loc):
    plt.text(i, v, round(v, 2), ha='center', va='bottom')
plt.title('不同区域平均工资柱状图', fontproperties=font_zh)
plt.xticks(range(len(avg_salary_by_loc)), avg_salary_by_loc.index,
           fontproperties=font_zh)
plt.xlabel('区域', fontproperties=font_zh)
plt.ylabel('平均工资（千/年）', fontproperties=font_zh)

loc_list = [[i, loc_counts[i]] for i in loc_counts.index]
geo = Geo().add_schema(maptype='成都')
geo.add('区域分布热度图', loc_list, type_=ChartType.HEATMAP) # 设置名称和数据
geo.set_series_opts(label_opts=opts.LabelOpts(is_show=True)) # 设置标签是否可见
geo.set_global_opts(visualmap_opts=opts.VisualMapOpts()) # 视觉映射配置
geo.render('./loc_heatmap.html') # 保存为网页
os.system('"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"\
 ./loc_heatmap.html') # 打开网页

# 工作经验分析
exp_data = data['job_exp']
exp_des = exp_data.describe() # 工作经验基本数据描述，包括平均数、中位数等
exp_counts = exp_data.value_counts().sort_index() # 按实际值进行频率统计

fig = plt.figure('平均工作经验统计详情', figsize=[16, 5])
plt.subplots_adjust(left=0.03, bottom=0.15, right=0.97, top=0.9, wspace=0.25)

ax1 = fig.add_subplot(161)
plt.title('平均工作经验年限详情描述', fontproperties=font_zh)
for i, v in enumerate(exp_des):
    plt.text(0.05, 1 - (i + 1) * 0.07,
             exp_des.index[i] + ': ' + str(round(v, 2)))
plt.xticks([])
plt.yticks([])

ax2 = fig.add_subplot(162)
exp_counts.plot.pie(autopct='%.2f%%', pctdistance=0.7, labeldistance=0.9,
                    startangle=90, counterclock=False, radius=1.2)
plt.title('平均工作经验年限分布饼图', fontproperties=font_zh)
plt.ylabel('')

ax3 = fig.add_subplot(132)
exp_counts.plot.bar()
for i, v in enumerate(exp_counts):
    plt.text(i, v, v, ha='center', va='bottom')
plt.title('平均工作经验年限分布柱状图', fontproperties=font_zh)
plt.xlabel('工作经验（年）', fontproperties=font_zh)
plt.ylabel('数量', fontproperties=font_zh)

ax4 = fig.add_subplot(133)
avg_salary_by_exp = salary_data.groupby(exp_data).mean()
avg_salary_by_exp.plot.bar()
for i, v in enumerate(avg_salary_by_exp):
    plt.text(i, v, round(v, 2), ha='center', va='bottom')
plt.title('不同工作经验的平均工资柱状图', fontproperties=font_zh)
plt.xlabel('工作经验（年）', fontproperties=font_zh)
plt.ylabel('平均工资（千/月）', fontproperties=font_zh)

# 学历要求分析
edu_data = data['edu'][data['edu'].notnull()]
edu_list = ['初中及以下', '中专', '高中', '大专', '本科', '硕士', '博士']
edu_counts = edu_data.value_counts().reindex(edu_list, fill_value=0)

fig = plt.figure('学历要求详情', figsize=[16, 5])
plt.subplots_adjust(left=0.1, bottom=0.25, right=0.99, top=0.9, wspace=0.1)

ax1 = fig.add_subplot(131)
edu_counts.plot.bar()
for i, v in enumerate(edu_counts):
    plt.text(i, v, v, ha='center', va='bottom')
plt.title('学历要求柱状图', fontproperties=font_zh)
plt.xticks(range(len(edu_counts)), edu_counts.index, fontproperties=font_zh)
plt.xlabel('学历', fontproperties=font_zh)
plt.ylabel('数量', fontproperties=font_zh)

ax2 = fig.add_subplot(132)
edu_counts.sort_values(ascending=False, inplace=True)
edu_counts_other = pd.Series({'其他': edu_counts[3:].sum()})
edu_counts_pie = edu_counts[:3].append(edu_counts_other)
edu_counts_pie.plot.pie(autopct='%.2f%%', labeldistance=0.8, startangle=90,
                        counterclock=False, radius=1.2,
                        textprops={'fontproperties': font_zh})
plt.title('学历要求饼图', fontproperties=font_zh)
plt.ylabel('')

ax3 = fig.add_subplot(133)
avg_salary_by_edu = salary_data.groupby(edu_data).mean()\
.reindex(edu_list, fill_value=0)
avg_salary_by_edu.plot.bar()
for i, v in enumerate(avg_salary_by_edu):
    plt.text(i, v, round(v, 2), ha='center', va='bottom')
plt.title('不同学历的平均工资柱状图', fontproperties=font_zh)
plt.xticks(range(len(avg_salary_by_edu)), avg_salary_by_edu.index,
           fontproperties=font_zh)
plt.xlabel('学历', fontproperties=font_zh)
plt.ylabel('平均工资（千/月）', fontproperties=font_zh)

# 需求人数分析
num_data = data['req_num'][data['req_num'] != 100]
num_counts = num_data.value_counts().sort_index()

fig = plt.figure('需求人数统计详情', figsize=[10, 5])
plt.subplots_adjust(left=0.1, bottom=0.15, right=0.95, top=0.9, wspace=0.1)

ax1 = fig.add_subplot(121)
num_counts.plot.bar()
for i, v in enumerate(num_counts):
    plt.text(i, v, v, ha='center', va='bottom')
plt.title('需求人数柱状图', fontproperties=font_zh)
plt.xticks(range(len(num_counts)), num_counts.index, fontproperties=font_zh)
plt.xlabel('需求人数', fontproperties=font_zh)
plt.ylabel('数量', fontproperties=font_zh)

ax2 = fig.add_subplot(122)
num_counts_other = pd.Series({'更多': num_counts[5:].sum()})
num_counts_pie = num_counts_other.append(num_counts[-5::-1])[::-1]
num_counts_pie.plot.pie(autopct='%.2f%%', pctdistance=0.9, labeldistance=0.7,
                        startangle=90, counterclock=False, radius=1.2,
                        textprops={'fontproperties': font_zh})
plt.title('需求人数饼图', fontproperties=font_zh)
plt.ylabel('')

# 其他需求分析
other_data = data['other_req'][data['other_req'].notnull()]
other_data_text = ' '.join(other_data)

jieba.analyse.set_stop_words('./stopwords.txt') # 不提取的关键词
other_data_kw = jieba.analyse.extract_tags(other_data_text, topK=10,
                                           withWeight=True)
values = [x[1] for x in other_data_kw]
indexs = [x[0] for x in other_data_kw]
other_data_kw_wt = pd.Series(values, index=indexs)

plt.figure('其他需求关键字统计详情')
plt.subplots_adjust(left=0.1, bottom=0.25, right=0.95, top=0.9)

other_data_kw_wt.plot.bar()
for i, v in enumerate(other_data_kw_wt):
    plt.text(i, v, round(v, 2), ha='center', va='bottom')
plt.title('其他需求关键字统计（前十项）柱状图', fontproperties=font_zh)
plt.xticks(range(len(other_data_kw_wt)), other_data_kw_wt.index,
           fontproperties=font_zh)
plt.xlabel('关键字', fontproperties=font_zh)
plt.ylabel('权重', fontproperties=font_zh)

# 福利分析
wel_data = data['welfare'][data['welfare'].notnull()]
wel_data_text = ' '.join(wel_data).split(' ')
wel_counts_all = pd.Series(wel_data_text).value_counts()
wel_counts_other = pd.Series({'其他福利': wel_counts_all[14:].sum()})
wel_counts = wel_counts_other.append(wel_counts_all[-100::-1])[::-1]

fig = plt.figure('福利信息统计详情', figsize=[12, 5])
plt.subplots_adjust(left=0.1, bottom=0.25, right=0.95, top=0.9, wspace=0.1)

ax1 = fig.add_subplot(121)
wel_counts.plot.bar()
for i, v in enumerate(wel_counts):
    plt.text(i, v, v, ha='center', va='bottom')
plt.title('福利信息统计柱状图', fontproperties=font_zh)
plt.xticks(range(len(wel_counts)), wel_counts.index, fontproperties=font_zh)
plt.xlabel('关键字', fontproperties=font_zh)
plt.ylabel('数量', fontproperties=font_zh)

ax2 = fig.add_subplot(122)
wel_counts.plot.pie(autopct='%.2f%%', pctdistance=0.7, labeldistance=0.9,
                    startangle=90, counterclock=False, radius=1.2,
                    textprops={'fontproperties': font_zh})
plt.title('福利信息统计饼图', fontproperties=font_zh)
plt.ylabel('')

# 工作详情分析
dtl_data = ''.join(data['job_detail'])
dtl_data_kw = jieba.analyse.extract_tags(dtl_data, topK=18, withWeight=True)
values = [x[1] for x in dtl_data_kw]
indexs = [x[0] for x in dtl_data_kw]
dtl_data_kw_wt = pd.Series(values, index=indexs)

plt.figure('详细信息关键字统计详情')
plt.subplots_adjust(left=0.1, bottom=0.25, right=0.95, top=0.95)

dtl_data_kw_wt.plot.bar()
for i, v in enumerate(dtl_data_kw_wt):
    plt.text(i, v, round(v, 2), ha='center', va='bottom')
plt.title('详细信息关键字统计（前 18 项）柱状图', fontproperties=font_zh)
plt.xticks(range(len(dtl_data_kw_wt)), dtl_data_kw_wt.index,
           fontproperties=font_zh)
plt.xlabel('关键字', fontproperties=font_zh)
plt.ylabel('权重', fontproperties=font_zh)

# 职能分类分析
func_data = ' '.join(data['func_cat']).split(' ')
func_counts_all = pd.Series(func_data).value_counts()
func_counts_other = pd.Series({'其他分类': func_counts_all[11:].sum()})
func_counts = func_counts_other.append(func_counts_all[-73::-1])[::-1]

fig = plt.figure('职能分类统计详情', figsize=[12, 5])
plt.subplots_adjust(left=0.1, bottom=0.3, right=0.95, top=0.9, wspace=0.1)

ax1 = fig.add_subplot(121)
func_counts.plot.bar()
for i, v in enumerate(func_counts):
    plt.text(i, v, v, ha='center', va='bottom')
plt.title('职能分类统计柱状图', fontproperties=font_zh)
plt.xticks(range(len(func_counts)), func_counts.index, fontproperties=font_zh)
plt.xlabel('分类', fontproperties=font_zh)
plt.ylabel('数量', fontproperties=font_zh)

ax2 = fig.add_subplot(122)
func_counts.plot.pie(autopct='%.2f%%', pctdistance=0.7, labeldistance=0.9,
                     startangle=90, counterclock=False, radius=1.2,
                     textprops={'fontproperties': font_zh})
plt.title('职能分类统计饼图', fontproperties=font_zh)
plt.ylabel('')

# 分析平均工资、工作经验和学历的相关性
reg_data0 = pd.merge(salary_data, exp_data, left_index=True, right_index=True)
reg_data = pd.merge(reg_data0, edu_data, left_index=True, right_index=True)
edu_dict = {v: i for i, v in enumerate(edu_list)}
reg_data['edu'] = reg_data['edu'].map(edu_dict)
reg_data.rename(columns={'salary(k/m)': 'salary', 'job_exp': 'exp'},
                inplace=True)

fig = plt.figure('平均工资与工作经验和学历的相关性', figsize=[12, 5])

ax1 = fig.add_subplot(121, projection='3d')
ax1.scatter(reg_data['exp'], reg_data['edu'], reg_data['salary'])
plt.yticks(range(len(edu_list)), edu_list, fontproperties=font_zh)
plt.title('平均工资、工作经验和学历的散点图', fontproperties=font_zh)
plt.xlabel('工作经验（年）', fontproperties=font_zh)
plt.ylabel('学历', fontproperties=font_zh)
ax1.set_zlabel('平均工资（千/月）', fontproperties=font_zh)

ax2 = fig.add_subplot(122)
corr1 = reg_data['salary'].corr(reg_data['exp']) # 工资与工作经验的相关系数
corr2 = reg_data['salary'].corr(reg_data['edu']) # 工资与学历的相关系数
plt.title('平均工资与工作经验和学历的相关系数', fontproperties=font_zh)
plt.text(0.05, 0.93, '平均工资与工作经验的相关系数：' + str(round(corr1, 3)),
         fontproperties=font_zh)
plt.text(0.05, 0.86, '平均工资与学历的相关系数：' + str(round(corr2, 3)),
         fontproperties=font_zh)
plt.xticks([]) # 设置空坐标轴
plt.yticks([])

plt.show()
# plt.close()