#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
------------------------------------
# @FileName    :test.py
# @Time        :2024/02/20 12:06
# @Author      :zouxiaobo@corp.netease.com
# @description :
------------------------------------
"""
import akshare as ak
import requests
import time
from datetime import datetime, timedelta
def send_wechat(msg):
    token = '41568f9bd3884c5ebd99623c5e475ae4'#前边复制到那个token
    title = '基金推送'
    content = msg
    template = 'txt'
    url = f"https://www.pushplus.plus/send?token={token}&title={title}&content={content}&template={template}"
    print(url)
    r = requests.post(url=url)
    print(r.text)


info=ak.fund_etf_spot_em()
##ETF池
buy_list={}
codes=['513050','159871','159996','159611','159981','512660','512690','515220','515880',
       '512880','159892','512010','159745','159995','512480','159805',
       '516510','159992','159985','162411','159941','512880','512170','512800','159865',
       '159928','512290','512980','159870','516110'
       ]
code_special=["159819",'159869','515790','516160','515030','159766']
date_format = "%Y%m%d"
sixty_days_ago = datetime.now() - timedelta(days=60)
formatted_date = sixty_days_ago.strftime(date_format)
for code in codes+code_special:

    name=str(info[info['代码']==code]['名称'].values)

    retry_times = 5
    sleep_time = 60  # 设置休眠时间为60秒
    stock_df=[]
    for i in range(retry_times):
        try:
            stock_df = ak.fund_etf_hist_em(symbol=code, period="daily", start_date=formatted_date)
            # 如果上一行代码没有抛出异常，那么代码执行会跳到 break 语句，终止循环
            break
        except Exception as e:  # 处理网络超时、连接失败等可能出现的异常
            print(f"An error happened: {e}. Retrying...")
            # 如果抛出异常，则执行以下语句，
            # 如果没有达到重试次数限制，就暂停一分钟后重新尝试执行请求
            if i < retry_times - 1:  # 检查是否达到了重试次数限制
                time.sleep(sleep_time)
            else:
                print("We've tried several times and failed. Please check the error.")
                raise  # 重新引发异常，通知上层调用者出现了问题


    ## 获取MA指标
    stock_df['MA5'] = stock_df['收盘'].rolling(window=5).mean()
    stock_df['MA10'] = stock_df['收盘'].rolling(window=10).mean()
    stock_df['MA20'] = stock_df['收盘'].rolling(window=20).mean()

    ## 获取最近涨跌幅
    # 确保数据按照日期升序排列
    # stock_df.sort_values(by="日期", inplace=True)


    # 为了使涨跌幅更加直观，可以将其转换为小数形式，例如：1.08 表示 108%
    stock_df['20_day_change_pct']=(stock_df['收盘']-stock_df['收盘'].shift(20))/stock_df['收盘'].shift(20)*100
    stock_df['5_day_change_pct']=(stock_df['收盘']-stock_df['收盘'].shift(5))/stock_df['收盘'].shift(5)*100
    stock_df['10_day_change_pct']=(stock_df['收盘']-stock_df['收盘'].shift(10))/stock_df['收盘'].shift(10)*100

    last_price_ma10=stock_df['MA10'].iloc[-1]
    last_price_ma20=stock_df['MA20'].iloc[-1]
    price=stock_df['收盘'].iloc[-1]

    day_change_pct_20=stock_df['20_day_change_pct'].iloc[-1]
    day_change_pct_10=stock_df['20_day_change_pct'].iloc[-1]


    ##如果最近20个交易日涨幅为正，且最新价>ma10、ma20
    if day_change_pct_20>0 and last_price_ma20<price and day_change_pct_10>0:
        # print(name+code)
        # print(stock_df.iloc[-1])
        buy_list[code+name]=day_change_pct_20
# 对字典的 value 进行降序排序
buy_list = {k: v for k, v in sorted(buy_list.items(), key=lambda item: item[1], reverse=True)}

info=["以下基金为最近技术面强势基金"]

for k,v in buy_list.items():
   info.append(k+"\t最近20日涨幅："+str((v))+"%")

send_wechat('\n'.join(info))
# his=ak.fund_etf_hist_em(symbol=code, period="daily", start_date="20240101", end_date="20240424", adjust="")
    # print(his.columns)
    # print(his.values)
    # break