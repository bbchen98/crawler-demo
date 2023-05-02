#!/usr/bin/python
# -*- coding:utf-8 -*-

import time
import re
import requests
from my_email import Email
import sys
import importlib as imp

imp.reload(sys)


class OfO(object):
    def __init__(self, uid, account, password, receivers):
        """
        初始化
        :param uid: uid
        :param account: 邮箱账号
        :param password: 邮箱密码
        :param receivers: 收信者
        """
        self.uid = uid
        self.email_info = {
            'account': account,
            'password': password,
            'receivers': receivers
        }
        self.main_flag = 0  # 0：非新动态；1：新动态；2：已发邮件
        self.time_set = {
            'new': 180,      # 30s内->新动态
            'waiting': 2,   # 发现新动态后，每2s刷新一次
            'old': 5,      # 非新动态，5s刷新一次
            'sleep': 300    # 发送过邮件后，休息300s
        }
        self.table = {
            "n0": ['零', '宁', '灵', '领', '另', '令', '玲', '凌', '岭', '伶', '龄', '凝', '拧'],
            "n1": ['一', '亿', '以', '已', '易', '艺', '乙', '要', '腰', '姚', '药', '咬', '妖', '摇', '瑶', '邀', '耀', '幺', '夭', '曜'],
            "n2": ['二', '爱', '哎', '而', '矮', '霭', '艾', '挨', '哀', '唉', '耳', '碍', '儿', '尔', '埃', '额', '鹅', '饿', '呃', '俄', '娥', '厄', '碍'],
            "n3": ['三', '山', '闪', '伞', '散', '删', '善', '扇', '衫', '珊'],
            "n4": ['四', '似', '是', '斯', '撕', '司', '私', '思', '丝', '寺', '肆', '厮', '时', '事', '使', '式', '市', '试', '师', '实', '士', '似'],
            "n5": ['五', '吴', '雾', '无', '误', '物', '舞', '屋', '午', '武', '务', '勿', '吾', '乌', '呜', '悟', '捂', '巫', '污'],
            "n6": ['六', '刘', '流', '留', '溜', '柳', '榴'],
            "n7": ['七', '期', '起', '骑', '气', '其', '器', '棋', '弃', '齐', '奇', '琪', '崎', '启', '旗', '漆', '汽', '妻'],
            "n8": ['八', '把', '罢', '吧', '巴', '拔', '霸', '扒', '爸'],
            "n9": ['九', '就', '救', '旧', '久', '韭', '酒', '舅', '揪']
        }

    def __trans(self, ori_str):
        """
        将汉字转为数字
        :param ori_str: 原始字符串（str)
        :return: 一串数字（str）
        """
        final_str = ''
        success_flag = 0
        # 取n0-n9，放在列表中
        table_keys = list(self.table.keys())
        # 逐个处理字符
        for sigle_str in ori_str:
            for table_n in table_keys:
                if sigle_str in self.table[table_n]:
                    final_str += table_n[-1:]
                    success_flag = 1
                    break
            # 无匹配，保留原字符
            if success_flag == 0:
                final_str += sigle_str
            # 匹配，重置success_flag
            else:
                success_flag = 0
        return final_str

    def __send_email(self, title, text):
        """
        发送邮件
        :param title: 邮件名
        :param text: 内容
        :return:
        """
        # print(title, text)
        my_email = Email(self.email_info['account'], self.email_info['password'])
        if my_email.send_email(self.email_info['receivers'], title, text):
            print("成功发送邮件：" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    def __process_str(self, ori_str):
        """
        处理字符串，如果有代码，提取代码
        :param ori_str: 可能含有代码的字符串(str)
        :return: true/false, str/''
        """
        flag = False
        final_str = ''
        sum = 0
        # 提取出所有的【】
        all = re.findall(u'\u3010.*?\u3011', ori_str)
        # for st in all:
        #     stt = st[1:-1]       # 去除【】
        #     stt = stt.strip()    # 去除首尾空格
        #     if len(stt) == 8:    # 有代码
        #         flag = True
        #         if sum < 1:
        #             final_str = final_str + self.__trans(stt)
        #         else:
        #             final_str = final_str + '、' + self.__trans(stt)
        #         sum += 1

        # 【】存在，直接发送邮件
        if len(all) > 0:
            flag = True
            final_str = ''.join(all)
        return flag, final_str

    def __get_html_src(self, url):
        """
        从url获取源码
        :param url: URL
        :return: 源码
        """
        # 爬取首页
        headers = {
            'Cookie': 'l=v; _uuid=AEF47032-A43C-46D2-5A3A-F717F2DBA70791057infoc; buvid3=1E5CEA50-B7FD-4571-904D-46589D4AEFFA143088infoc; sid=j2bdba3z; DedeUserID=435408620; DedeUserID__ckMd5=053adfa053858233; SESSDATA=34a07e04%2C1621062412%2C7037a*b1; bili_jct=7925adca3b451ef1e8954bfa7f1e610b; bp_video_offset_435408620=441204599996697805; dy_spec_agreed=1; CURRENT_FNVAL=80; blackside_state=1; PVID=2; bp_t_offset_435408620=458153034866998414',
            'user-agent': 'Mozilla/5.0'
        }
        try:
            r = requests.get(url, headers=headers, timeout=2)
            r.encoding = 'utf-8'
        except Exception:
            print("抓取页面异常：" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            return -1
        # 返回网页源码
        return r.text

    def get_zfb_pwd(self):
        """
        获取支付宝红包口令
        :return:
        """
        # 启动
        print('爬虫已启动...')
        # 开始监视
        while True:
            # 获取最新动态状态源码
            url = 'http://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid=' \
                  + str(self.uid) + ''
            dt_src = self.__get_html_src(url)
            while dt_src == -1:
                dt_src = self.__get_html_src(url)
            # 用正则表达式提取出时间
            dt_time = 0
            search_r = re.search(r'\"timestamp\":.*?,', dt_src)
            if search_r:
                dt_time = int(search_r.group(0)[12:-1])
            self.main_flag = 0
            # 如果是新动态
            if int(time.time()) - dt_time < self.time_set['new']:
                print("新动态：" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                self.main_flag = 1
                # 获取最新动态ID
                dt_id_str = ''
                search_r = re.search(r'\"dynamic_id\":.*?,', dt_src)
                if search_r:
                    r_str = search_r.group(0)
                    mh = r_str.find(':')
                    if mh != -1:
                        dt_id_str = r_str[mh + 1:-1]
                # 首先检查动态文字中是否有代码
                rec = re.compile('"dynamic_id_str":"' + dt_id_str + '.*?"card".*?reply')
                search_r = re.search(rec, dt_src)
                if search_r:
                    r_str = search_r.group(0)
                    flag, result = self.__process_str(r_str)
                    # 有代码，发送邮件
                    if flag:
                        email_title = '代码：' + result
                        # 邮件内容
                        sindex = r_str.find('content')
                        email_text = r_str[sindex+13:]
                        eindex = email_text.find('"')
                        email_text = email_text[:eindex-1]
                        # 发送
                        self.__send_email(email_title, email_text)
                        self.main_flag = 2
                    # 动态文字中无代码，检查评论
                    else:
                        # 获取该动态源码
                        url = 'http://api.bilibili.com/x/v2/reply?&jsonp=jsonp&pn=1&type=17&oid=' + dt_id_str + '&sort=2'
                        cmt_src = self.__get_html_src(url)
                        while cmt_src == -1:
                            cmt_src = self.__get_html_src(url)
                        # 如果有置顶评论，处理
                        search_r = re.search(r'"top":{"r.*?"plat"', cmt_src)
                        if search_r:
                            # 获取到评论
                            cmt_str = search_r.group(0)
                            cmt_i = cmt_str.rfind('sage":"')
                            cmt_str = cmt_str[cmt_i + 7:-8]
                            # 对代码进行检测
                            flag, result = self.__process_str(cmt_str)
                            if flag:
                                # 有代码
                                email_title = '代码：' + result
                                email_text = cmt_str
                                self.__send_email(email_title, email_text)
                                self.main_flag = 2

            # 休息
            if self.main_flag == 0:
                time.sleep(self.time_set['old'])
            elif self.main_flag == 1:
                time.sleep(self.time_set['waiting'])
            elif self.main_flag == 2:
                time.sleep(self.time_set['sleep'])


if __name__ == "__main__":
    ID = 651039864
    email_account = 'xiaobingbao2020@163.com'
    email_pwd = 'FQIBPADQMMGEMSCS'
    email_receiver = ['chenbingbing0110@vip.qq.com', 'xiaozhao010@qq.com', 'lostyearling@qq.com']
    # email_receiver = ['chenbingbing0110@vip.qq.com']
    ofo = OfO(ID, email_account, email_pwd, email_receiver)
    ofo.get_zfb_pwd()
