#!/usr/bin/env python 
# -*- coding:utf-8 -*-
from fake_useragent import UserAgent

CITY_NAME = '长沙'
JOB_NAME = '爬虫'
COLUMN = ['职业名', '月薪', '公司名', '公司url', '职位条件', '岗位职责与技能要求', '工作地址',
          '创建日期', '更新日期','截止日期', '职位亮点', '职位url']
HEADERS = {'User-Agent': UserAgent().random}
WORK_LIST = []
