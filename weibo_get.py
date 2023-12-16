# -*- coding: utf-8 -*-
 
'''
微博爬虫，爬取一个主题下的博文内容，博主信息，评论等各种信息
'''
 
import requests, random, re
import time
import os
import csv
import sys
import json
import importlib
from fake_useragent import UserAgent
from lxml import etree
import datetime
import pandas as pd
from selenium import webdriver
import urllib.request
 
# 记录起始时间
importlib.reload(sys)
startTime = time.time()
# proxy_addr="122.241.72.191:808"
# --------------------------------------------文件存储-----------------------------------------------------
'''
设置文件储存的路径 
'''
key = '华为Mate60'
path =  key+"/total_content_comments.csv" #总的微博博文与评论的全部信息
path1= key+'/weibo_content.csv'#存取的是微博博文的信息（不包含评论）
path2= key+'/weibo_comments.csv' #只保存评论的信息
 
csvfile = open(path, 'a', newline='', encoding='utf-8-sig')
csvfile1 = open(path1, 'a', newline='', encoding='utf-8-sig')
csvfile2 = open(path2, 'a', newline='', encoding='utf-8-sig')
 
writer = csv.writer(csvfile)
writer_1=csv.writer(csvfile1)
writer_2=csv.writer(csvfile2)
 
# csv头部
writer.writerow(('话题链接', '话题内容', '楼主ID', '楼主昵称', '楼主性别', '发布日期',
                 '发布时间', '转发量', '评论量', '点赞量', '评论者ID', '评论者昵称',
                 '评论者性别', '评论日期', '评论时间', '评论内容'))  #微博博文与评论的全部信息
 
writer_1.writerow(('话题链接',  '楼主ID', '话题内容','楼主昵称', '楼主性别','是否认证','认证类型',
                   '是否认证金v','发博数量','关注人数','粉丝数','微博等级', '发布日期',
                   '发布时间', '转发量', '评论量', '点赞量'))        #微博博文的信息（不包含评论）
 
writer_2.writerow(('楼主ID','评论者ID','话题内容','评论内容','评论者昵称', '评论者性别','是否认证','认证类型',
                   '是否认证金v','发博数量','关注人数','粉丝数','微博等级', '发布日期','评论日期',
                   '评论时间', '回复量', '点赞量'))                   #评论的信息
 
# --------------------------------------------头部信息-----------------------------------------------------
ip_list = [
            {'http': 'http://118.193.47.193:8118'}, # 湖南长沙
            {'http': 'http://58.20.234.243:9091'}, # 湖南湘潭
            {'http': 'http://58.20.235.180:9091'}, # 湖南湘潭
            {"http": "http://112.115.57.20:3128"},
            {'http': 'http://121.41.171.223:3128'},
            {"http": "http://124.88.67.54:80"},
            {"http": "http://61.135.217.7:80"},
            {"http": "http://42.231.165.132:8118"},
            {"http": "http://10.10.1.10:3128"},
            {"https": "http://10.10.1.10:1080"}
        ]
ip = random.choice(ip_list)
 
# 反爬虫
agent = [
            'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
            'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0',
            'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
            'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
            'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
            'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11',
            'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
            'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Mobile Safari/537.36'
        ]
ua = random.choice(agent)
 
cookie_list = [
    # 手机号
    {'cookie':'SINAGLOBAL=1814763918626.8694.1701051057944; XSRF-TOKEN=OrPSQg0qQhQHH7rBgwU2sawn; _s_tentry=-; Apache=4031682277231.468.1701145585224; ULV=1701145585228:3:3:3:4031682277231.468.1701145585224:1701084406457; SSOLoginState=1701145626; WBPSESS=Q8SDBUgQCxl6RtcZy4WpK6Ws3wCtwVEVBljZ0sxpagtBrPOxtY5X0OTFx_-rBzV5xsNHazg97LXyh2qLdrPH31Q_PqAvGlGwgv_nkXEIu8DH1jjBSmonLZhCEnoK0d9WeVN_-LZiYTG3jBjr1e95-A==; SCF=Al7vYFclmq3WBaGCSf3H5_W7DYNGHcFFRJLn8qaOoA4vsWL_TMBy1F9HyPVglVNdoOVseiw7saOcXvm63vcmM5Q.; SUB=_2A25IYRwIDeRhGeBL41ES-SbKyTmIHXVrHxHArDV8PUNbmtANLRPNkW9NRtscGkHsrY5LgwZap--9HD1uhsZ5ekaD; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWkBJPVo8aBrElRsrl.sGIo5JpX5KMhUgL.Foqf1he01Knceo-2dJLoI0qLxKBLBonL12BLxKqL1heLBoeLxK-LB.BL1KeLxKMLB-eLBKnLxKnL1-zL12zLxK-L1KeLBKqt; ALF=1703737687; PC_TOKEN=8cc0db36d4'}
]
 
cookie = random.choice(cookie_list)['cookie']
 
#爬微博评论容易遇到反爬，有可能第二页评论就爬不到了，多换几个ip，cookie,Referer试试，或者第二天再试试吧！
headers = {
    'cookie': cookie,
    'user-agent': ua,#UserAgent().chrome,
    'Referer':'https://s.weibo.com/',
    'x-requested-with': 'XMLHttpRequest'
}
 
# # -----------------------------------爬取该主题首页的每个主题的ID------------------------------------------
'''
找出发布者id，并存入列表，用于找每个具体博客的网址
'''
comments_ID = []
index=key
start_time = datetime.datetime(year=2023, month=1, day=1, hour=0)
end_time = datetime.datetime(year=2023, month=11, day=27, hour=0)
def get_title_id():
    time_cur = start_time
    while time_cur < end_time:
        _start_time = time_cur.strftime("%Y-%m-%d-%H")
        _end_time = (time_cur + datetime.timedelta(hours=1)).strftime("%Y-%m-%d-%H")
        print("开始时间：{}   结束时间：{}".format(_start_time, _end_time))
        for page in range(1, 50):  # 每个页面大约有9个话题
            
            time.sleep(random.uniform(0.5,1))
            # 该链接通过抓包获得
            api_url = "https://s.weibo.com/weibo?q=%23{}%23&timescope=custom:{}:{}&Refer=g&page={}".format(
                index, _start_time, _end_time, page) ##月得是两位数,3前面要补0变成03x   
            # print(api_url)
            rep1 = requests.get(url=api_url, headers=headers)
            # rep1.enconding= rep1.apparent_encoding
            try:
                # rep = rep1.text.encode('utf-8').decode('utf8')
                rep=rep1.text # 获取ID值并写入列表comment_ID中
                # print(rep)
                comment_ID=re.findall('(?<=mid=")\d{16}', rep)
                if '<p>抱歉，未找到相关结果。</p>' in rep:
                        print("----------------该段时间遍历完毕-----------------")
                        break
                comments_ID.extend(comment_ID)
                print(page,"页id获取成功！",comment_ID)
            except:
                print(page,"页id获取有误！")
        # print(comment_ID)
        time_cur = time_cur + datetime.timedelta(hours=1)
 
 
# -----------------------------------爬取该主题下每个博客的详情页面 ------------------------------------------
 
'''
该主题下每个博客主的详情（包括话题内容、楼主id、楼主昵称、楼主性别、发布时间、日期、
发布时间、转发量、评论量、点赞量）
（利用正则表达式抓取）
'''
is_continue='y'
start_date = pd.to_datetime('2023/1/1')
end_date = pd.to_datetime('2023/11/27')
def spider_title(comment_ID):
 
    article_url = 'https://m.weibo.cn/detail/' + comment_ID
    print("article_url = ", article_url)
    time.sleep(random.uniform(0.5,1))
 
    try:
        html_text = requests.get(url=article_url).text
        # 发布日期
        created_title_time = re.findall('.*?"created_at": "(.*?)".*?', html_text)[0].split(' ')
        # print(created_title_time)
        # 日期
        if 'Jan' in created_title_time:
            title_created_YMD = "{}/{}/{}".format(created_title_time[-1], '01', created_title_time[2])
        elif 'Feb' in created_title_time:
            title_created_YMD = "{}/{}/{}".format(created_title_time[-1], '02', created_title_time[2])
        elif 'Mar' in created_title_time:
            title_created_YMD = "{}/{}/{}".format(created_title_time[-1], '03', created_title_time[2])
        elif 'Apr' in created_title_time:
            title_created_YMD = "{}/{}/{}".format(created_title_time[-1], '04', created_title_time[2])
        elif 'May' in created_title_time:
            title_created_YMD = "{}/{}/{}".format(created_title_time[-1], '05', created_title_time[2])
        elif 'Jun' in created_title_time:
            title_created_YMD = "{}/{}/{}".format(created_title_time[-1], '06', created_title_time[2])
        elif 'July' in created_title_time:
            title_created_YMD = "{}/{}/{}".format(created_title_time[-1], '07', created_title_time[2])
        elif 'Aug' in created_title_time:
            title_created_YMD = "{}/{}/{}".format(created_title_time[-1], '08', created_title_time[2])
        elif 'Sep' in created_title_time:
            title_created_YMD = "{}/{}/{}".format(created_title_time[-1], '09', created_title_time[2])
        elif 'Oct' in created_title_time:
            title_created_YMD = "{}/{}/{}".format(created_title_time[-1], '10', created_title_time[2])
        elif 'Nov' in created_title_time:
            title_created_YMD = "{}/{}/{}".format(created_title_time[-1], '11', created_title_time[2])
        elif 'Dec' in created_title_time:
            title_created_YMD = "{}/{}/{}".format(created_title_time[-1], '12', created_title_time[2])
        # print("title_created_YMD = ", title_created_YMD)
 
        print('发布日期：',title_created_YMD)
        time2 = pd.to_datetime(title_created_YMD)
 
        if start_date<= time2 <= end_date:
            # 话题内容
            find_title = re.findall('.*?"text": "(.*?)",.*?', html_text)[0]
            title_text = re.sub('<(S*?)[^>]*>.*?|<.*? />', '', find_title)  # 正则匹配掉html标签
            # print("title_text = ", title_text)
 
            # 楼主ID
            title_user_id = re.findall('.*?"id": (.*?),.*?', html_text)[1]
            # print("title_user_id = ", title_user_id)
 
            # 楼主昵称
            title_user_NicName = re.findall('.*?"screen_name": "(.*?)",.*?', html_text)[0]
            # print("title_user_NicName = ", title_user_NicName)
 
            # 楼主性别
            title_user_gender = re.findall('.*?"gender": "(.*?)",.*?', html_text)[0]
            # print("title_user_gender = ", title_user_gender)
 
            verified=re.findall('.*?"verified": (.*?),.*?', html_text)[0]#楼主是否认证
            if verified=='true':
                verified_type_ext = re.findall('.*?"verified_type_ext": (.*?),.*?', html_text)[0] # 楼主是否金v
            else:
                verified_type_ext=0
            # print(verified_type_ext)
            content_num=re.findall('.*?"statuses_count": (.*?),.*?', html_text)[0] #楼主发博数量
            verified_type=re.findall('.*?"verified_type": (.*?),.*?', html_text)[0]#楼主认证类型
            urank=re.findall('.*?"urank": (.*?),.*?', html_text)[0]#楼主微博等级
            guanzhu=re.findall('.*?"follow_count": (.*?),.*?', html_text)[0]#楼主关注数
            fensi=eval(re.findall('.*?"followers_count": (.*?),.*?', html_text)[0])#楼主粉丝数
 
            # 发布时间
            add_title_time = created_title_time[3]
            print("add_title_time = ", add_title_time)
            #当该条微博是是转发微博时，会有一个原微博的转发评论点赞量，以及本条微博的转发评论点赞量，此时需要的是第2个元素
            if len(re.findall('.*?"reposts_count": (.*?),.*?', html_text))>1:
                # 转发量
                reposts_count = re.findall('.*?"reposts_count": (.*?),.*?', html_text)[1]
                # print("reposts_count = ", reposts_count)
 
                # 评论量
                comments_count = re.findall('.*?"comments_count": (.*?),.*?', html_text)[1]
                print("comments_count = ", comments_count)
 
                # 点赞量
                attitudes_count = re.findall('.*?"attitudes_count": (.*?),.*?', html_text)[1]
                # print("attitudes_count = ", attitudes_count)
 
                # 每个ajax一次加载20条数据
                comment_count = int(int(comments_count) / 20)
            else:
                # 转发量
                reposts_count = re.findall('.*?"reposts_count": (.*?),.*?', html_text)[0]
                # print("reposts_count = ", reposts_count)
 
                # 评论量
                comments_count = re.findall('.*?"comments_count": (.*?),.*?', html_text)[0]
                print("comments_count = ", comments_count)
 
                # 点赞量
                attitudes_count = re.findall('.*?"attitudes_count": (.*?),.*?', html_text)[0]
                # print("attitudes_count = ", attitudes_count)
 
                # 每个ajax一次加载20条数据
                comment_count = int(int(comments_count) / 20)
 
            # position1是记录
            position1 = (article_url, title_text, title_user_id, title_user_NicName, title_user_gender, title_created_YMD,
                         add_title_time, reposts_count, comments_count, attitudes_count, " ", " ", " ", " ", " ", " ")
            position11 = (article_url, title_user_id, title_text, title_user_NicName, title_user_gender, verified, verified_type,
            verified_type_ext, content_num, guanzhu, fensi, urank, title_created_YMD, add_title_time,reposts_count, comments_count, attitudes_count)
 
            # 写入数据
            writer.writerow((position1))
            writer_1.writerow(position11)
            print('写入博文信息数据成功！')
            return comment_count, title_user_id, title_created_YMD,title_text
 
            global is_continue
        else:
            is_continue = 'y'#input('日期超出范围,是否继续爬取博文信息?(y/n, 默认: y) ——> ')#输入是否继续爬取
            if is_continue == 'y' or is_continue == 'yes' or not is_continue:
                pass
            else:
                print('日期超出范围，停止爬取博文信息！')
                # 计算使用时间
                endTime = time.time()
                useTime = (endTime - startTime) / 60
                print("该次所获的信息一共使用%s分钟" % useTime)
                sys.exit(0)
            return is_continue
    except:
        print('博文网页解析错误，或微博不存在或暂无查看权限！')
        pass
 
 
# -------------------------------------------------抓取评论信息---------------------------------------------------
# comment_ID话题编号（找出max_id,id_type）
def get_page(comment_ID, max_id, id_type):
    params = {
        'max_id': max_id,
        'max_id_type': id_type
    }
    url = 'https://m.weibo.cn/comments/hotflow?id={}&mid={}&max_id={}&max_id_type={}'.format(comment_ID, comment_ID,max_id,id_type)
    try:
        time.sleep(2)
        # r = requests.get(url, params=params, headers=headers)
        r = requests.get(url,headers=headers)
        if r.status_code==200:
            print('评论页面解析成功！')
            a=r.json()
            return r.json() #新浪有反爬虫，第二页评论就获取不到了，哭哭
    except requests.ConnectionError as e:
        print('评论页面解析错误!', e.args)
        pass
 
# -------------------------------------------------抓取评论item最大值---------------------------------------------------
def parse_page(jsondata):
    if jsondata:
        items = jsondata.get('data')
        item_max_id = {}
        item_max_id['max_id'] = items['max_id']
        item_max_id['max_id_type'] = items['max_id_type']
        print('评论页面max_id和max_id_type获取成功！')
        return item_max_id
 
# -------------------------------------------------抓取评论信息---------------------------------------------------
 
def write_csv(jsondata,title_user_id,title_created_YMD,title_text):
    #当没有评论时，jsondata为空
    try:
        for json in jsondata['data']['data']:
            # 评论者ID
            user_id = json['user']['id']
            # 评论者昵称
            user_name = json['user']['screen_name']
            # 评论者性别,m表示男性，表示女性
            user_gender = json['user']['gender']
            user_statuses_count = json['user']['statuses_count']#评论者发博数量
            user_verified = json['user']['verified']  # 评论者是否认证
            user_verified_type = json['user']['verified_type']  # 评论者认证类型
            if user_verified=='true':
                user_verified_type_ext = json['user']['verified_type_ext']  # 评论者是否金v
            else:
                user_verified_type_ext = 0
            user_follow_count = json['user']['follow_count']  # 评论者关注数
            user_followers_count = json['user']['followers_count']  # 评论者发博数
            user_urank = json['user']['urank']  # 评论者微博等级
            # 获取评论
            comments_text = json['text']
            comment_text = re.sub('<(S*?)[^>]*>.*?|<.*? />', '', comments_text)  # 正则匹配掉html标签
            # print('评论内容：',comment_text)
            # 评论时间
            created_times = json['created_at'].split(' ')
            comment_total_number=json["total_number"]#评论的回复数量
            comment_like_count = json["like_count"]  # 评论的点赞数量
 
            if 'Jan' in created_times:
                created_YMD = "{}/{}/{}".format(created_times[-1], '1', created_times[2])
            elif 'Feb' in created_times:
                created_YMD = "{}/{}/{}".format(created_times[-1], '2', created_times[2])
            elif 'Mar' in created_times:
                created_YMD = "{}/{}/{}".format(created_times[-1], '3', created_times[2])
            elif 'Apr' in created_times:
                created_YMD = "{}/{}/{}".format(created_times[-1], '4', created_times[2])
            elif 'May' in created_times:
                created_YMD = "{}/{}/{}".format(created_times[-1], '5', created_times[2])
            elif 'Jun' in created_times:
                created_YMD = "{}/{}/{}".format(created_times[-1], '6', created_times[2])
            elif 'July' in created_times:
                created_YMD = "{}/{}/{}".format(created_times[-1], '7', created_times[2])
            elif 'Aug' in created_times:
                created_YMD = "{}/{}/{}".format(created_times[-1], '8', created_times[2])
            elif 'Sep' in created_times:
                created_YMD = "{}/{}/{}".format(created_times[-1], '9', created_times[2])
            elif 'Oct' in created_times:
                created_YMD = "{}/{}/{}".format(created_times[-1], '10', created_times[2])
            elif 'Nov' in created_times:
                created_YMD = "{}/{}/{}".format(created_times[-1], '11', created_times[2])
            elif 'Dec' in created_times:
                created_YMD = "{}/{}/{}".format(created_times[-1], '12', created_times[2])
            else:
                print('评论时间获取有误')
            created_time = created_times[3]  # 评论时间时分秒
 
            position2 = (
            " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", user_id, user_name, user_gender, created_YMD, created_time,
            comment_text)
 
            position22 = (title_user_id,user_id,title_text, comment_text,user_name, user_gender,user_verified,user_verified_type,user_verified_type_ext,user_statuses_count,user_follow_count,
                          user_followers_count,user_urank,title_created_YMD,created_YMD,created_time,comment_total_number,comment_like_count)
            # 写入数据
            writer.writerow((position2))
            writer_2.writerow(position22)
            print('写入评论信息数据成功！')
    except:
        print('评论为空，没有写入文件！')
        pass
 
# -------------------------------------------------主函数---------------------------------------------------
def main():
    # comments_ID=['4708577132940142'] #测试该id
    count_title = len(comments_ID)
    for count, comment_ID in enumerate(comments_ID):
        print("正在爬取第%s条微博，一共找到个%s条微博需要爬取" % (count + 1, count_title))
 
        try:
            # maxPage获取返回的最大评论数量/20 再取整 （即评论数量的页数）
            maxPage,title_user_id,title_created_YMD,title_text = spider_title(comment_ID)
            # print('maxPage = ', maxPage)
            m_id = 0
            id_type = 0
            if maxPage != 0:  # 小于18条评论的不需要循环
                # 用评论数量控制循环
                for page in range(0, maxPage):
                    # 自定义函数-抓取网页评论信息
                    jsondata = get_page(comment_ID, m_id, id_type)
 
                    # 评论信息写入CSV文件
                    write_csv(jsondata,title_user_id,title_created_YMD,title_text)
 
                    # 自定义函数-获取评论item最大值
                    results = parse_page(jsondata)
                    time.sleep(1)
                    m_id = results['max_id']
                    id_type = results['max_id_type']
            else:
                jsondata = get_page(comment_ID, m_id, id_type)
                # 自定义函数-写入CSV文件
                write_csv(jsondata,title_user_id,title_created_YMD,title_text)
        except:
            if is_continue == 'y' or is_continue == 'yes' or not is_continue:
                print("--------------------------分隔符---------------------------")
                pass
            else:
                sys.exit(0)
        print("--------------------------分隔符---------------------------")
    csvfile.close()
    csvfile1.close()
    csvfile2.close()
 
 
if __name__ == '__main__':
    # 获取话题ID
    get_title_id()
 
    # 主函数操作
    main()
 
    # 计算使用时间
    endTime = time.time()
    useTime = (endTime - startTime) / 60
    print("该次所获的信息一共使用%s分钟" % useTime)
    # print('错误页面:',error_page_list)