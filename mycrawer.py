# -*-coding:utf8-*-

import re
import string
import sys
import os
import urllib
import urllib2
from bs4 import BeautifulSoup
import requests
from lxml import etree

reload(sys)
sys.setdefaultencoding('utf-8')
if (len(sys.argv) >= 2):
    user_id = (int)(sys.argv[1])
else:
    user_id = (int)(raw_input(u"请输入user_id: "))

cookie = {"Cookie": "_T_WM=0d0d8a6602023ef34b7633c2d4c11589; SCF=AhOe3gjy9PoeSldrKzKRg7C6V-QCBmdCYXQngEFbsUDaaL-1C_B0h0Gcfp48kXkI74nwIGUYwMFmtW5vSUx377A.; H5_INDEX=3; H5_INDEX_TITLE=%E5%BE%80%E4%BA%8B%E5%A6%82%E7%83%9Fbody; M_WEIBOCN_PARAMS=featurecode%3D20000320%26luicode%3D10000011%26lfid%3D1005055660460152%252Fhome%26fid%3D1005055660460152%252Fhome%26uicode%3D10000011; SUB=_2A2533tZBDeRhGeNI7VIV9i7Nzj6IHXVVIPoJrDV6PUJbkdANLWbhkW1NSFrJPyZgWViu-YbEIvmg0Jk2kn8Pdgko; SUHB=09P9Qx2bL9wMmP; SSOLoginState=1524278801"}
url = 'https://weibo.cn/u/%d' % user_id

html = requests.get(url, cookies=cookie).content
print(html)
selector = etree.HTML(html)
pageNum = (int)(selector.xpath('//input[@name="mp"]')[0].attrib['value'])

result = ""
urllist_set = set()
word_count = 1
image_count = 1

print u'爬虫准备就绪...'

for page in range(1, 5):

    # 获取lxml页面
    url = 'http://weibo.cn/u/%d?filter=1&page=%d' % (user_id, page)
    lxml = requests.get(url, cookies=cookie).content

    # 文字爬取
    selector = etree.HTML(lxml)
    # content = selector.xpath('//span[@class="ctt"]')
    # for each in content:
    #     text = each.xpath('string(.)')
    #     if word_count >= 4:
    #         text = "%d :" % (word_count - 3) + text + "\n\n"
    #     else:
    #         text = text + "\n\n"
    #     result = result + text
    #     word_count += 1

    # 图片爬取
    soup = BeautifulSoup(lxml, "lxml")
    urllist = soup.find_all('a', re.compile(r'^https://weibo.cn/mblog/oripic', re.I))
    urllist1 = soup.find_all('a', href=re.compile(r'^https://weibo.cn/mblog/pic', re.I))
    first = 0
    for imgurl in urllist:
        imgurl['href'] = re.sub(r"amp;", '', imgurl['href'])
        urllist_set.add(requests.get(imgurl['href'], cookies=cookie).url)
        image_count += 1
    for imgurl_all in urllist1:
        html_content = requests.get(imgurl_all['href'], cookies=cookie).content
        soup = BeautifulSoup(html_content, "lxml")
        urllist2 = soup.find_all('a', href=re.compile(r'^/mblog/oripic', re.I))
        for imgurl in urllist2:
            imgurl['href'] = 'http://weibo.cn' + re.sub(r"amp;", '', imgurl['href'])
        urllist_set.add(requests.get(imgurl['href'], cookies=cookie).url)
        image_count += 1
        image_count -= 1
        print page, 'picurl ok'

# fo = open("/Users/zwd-admin/PycharmProjects/WeboCraw/%s" % user_id+".txt", "wb")
# print(result+"aaaa")
# fo.write(result)
# word_path = os.getcwd() + '/%d' % user_id
# print u'文字微博爬取完毕'
#
link = ""
fo2 = open("/Users/zwd-admin/PycharmProjects/WeboCraw/%s_imageurls" % user_id, "wb")
for eachlink in urllist_set:
    link = link + eachlink + "\n"
fo2.write(link)
print u'图片链接爬取完毕'

if not urllist_set:
    print u'该页面中不存在图片'
else:
    # 下载图片,保存在当前目录的pythonimg文件夹下
    image_path = os.getcwd() + '/weibo_image'
    if os.path.exists(image_path) is False:
        os.mkdir(image_path)
    x = 1
    for imgurl in urllist_set:
        temp = image_path + '/%s.jpg' % x
        print u'正在下载第%s张图片' % x
        try:
            urllib.urlretrieve(urllib2.urlopen(imgurl).geturl(), temp)
        except:
            print u"该图片下载失败:%s" % imgurl
        x += 1

print u'微博图片爬取完毕，共%d张，保存路径%s' % (image_count - 1, image_path)