#!/usr/bin/env python 
# -*- coding:utf-8 -*-
import math
import random
import time
import requests
import pickle
import hashlib
import json
import os
from lxml import etree
import csv
from utils import CITY_NAME, JOB_NAME, COLUMN, HEADERS, WORK_LIST


def load_progress(old_path):
    try:
        with open(old_path, 'rb') as f:
            tmp = pickle.load(f)
            return tmp
    except Exception as e:
        return set()


def save_progress(old_url_set, url_path):
    try:
        with open(url_path, 'wb+') as f:
            pickle.dump(old_url_set, f)
    except Exception as e:
        print('pickle url failure', e)


def hash_url(url):
    hash =hashlib.md5()
    hash.update(url.encode('utf-8'))
    return hash.hexdigest()[8:-8]


def write_csv_headers(csv_filename):
    with open(csv_filename,'a',newline='',encoding='utf-8') as f:
        f_csv = csv.DictWriter(f, COLUMN)
        f_csv.writeheader()


def get_html(url):
    try:
        response = requests.get(url,headers=HEADERS)
        if response.status_code == 200:
                return response
        else:
            print('get %s failed' % url)
    except Exception as e:
        print('get url failured', e)


def get_page_count(url):
    response = get_html(url)
    json_response = json.loads(response.text)
    numFound = json_response['data']['numFound']
    page_count = math.ceil(numFound / 90)
    return page_count


def save_csv(csv_filename,data):
    with open(csv_filename,'a+',newline='',encoding='utf-8') as f:
        f_csv = csv.DictWriter(f, data.keys())
        f_csv.writerow(data)


def get_work_detail(page_url):
    response = get_html(page_url)
    json_response = json.loads(response.text)
    for result in json_response['data']['results']:
        work_dict = {}
        if result.get('emplType') == '全职':
            work_dict['position_name'] = result.get('jobName')
            work_dict['createDate'] = result.get('createDate')
            work_dict['updateDate'] = result.get('updateDate')
            work_dict['endDate'] = result.get('endDate')
            positionURL = result.get('positionURL')
            work_dict['positionURL'] = positionURL
            WORK_LIST.append(work_dict)
    return WORK_LIST


def get_company_detail(work_list, old_url_set):
    for work_dict in work_list:
        # time.sleep(random.uniform(1,2))
        url = work_dict['positionURL']
        hashed_url = hash_url(url)
        if not url in old_url_set:
            try:
                print('request %s start' % url)
                re = requests.get(url, headers=HEADERS)
                if re.status_code == 200:
                    re.encoding = re.apparent_encoding
                    html = re.text
                    tree = etree.HTML(html)
                    work_dict['job_name'] = tree.xpath('//h3[@class="summary-plane__title"]/text()')[0] # 岗位名称
                    work_dict['salary'] = tree.xpath('//span[@class="summary-plane__salary"]/text()')[0] # 待遇
                    work_dict['jobLight'] = ','.join(tree.xpath('//div[@class="highlights__content"]//span/text()'))  # 职位亮点
                    work_dict['company_name'] = tree.xpath('//a[@class="company__title"]/text()')[0]  # 公司名称
                    work_dict['company_url'] = tree.xpath('//a[@class="company__page-site"]/@href')[0]  # 公司的url
                    work_dict['condition'] = ','.join(tree.xpath('//ul[@class="summary-plane__info"]//li/text()'))  # 基本条件
                    work_dict['duty_and_requirement'] = ''.join(tree.xpath('//div[@class="describtion"]//text()'))  # 工作职责
                    work_dict['work_address'] = tree.xpath('//span[@class="job-address__content-text"]/text()')[0]  # 工作地址

                    old_url_set.add(hashed_url)
                    yield {
                        'job_name': work_dict.get('job_name'),
                        'salary': work_dict.get('salary'),
                        'company_name': work_dict.get('company_name'),
                        'company_url': work_dict.get('company_url'),
                        'condition': work_dict.get('condition'),
                        'duty_and_requirement': work_dict.get('duty_and_requirement'),
                        'work_address': work_dict.get('work_address'),
                        'createDate': work_dict.get('createDate'),
                        'updateDate': work_dict.get('updateDate'),
                        'endDate': work_dict.get('endDate'),
                        'jobLight': work_dict.get('jobLight'),
                        'positionURL': work_dict.get('positionURL'),
                    }

                else:
                    print('get %s failed!' % url)
            except Exception as e:
                print('ERROR %s' % e)


def main():
    original_url = 'https://fe-api.zhaopin.com/c/i/sou?start={0}&pageSize=90&cityId={1}' \
                   '&workExperience=-1&education=-1&companyType=-1&employmentType=-1&jobWelfareTag=' \
                   '-1&kw={2}&kt=3&_v=0.20004152&x-zp-page-request-id=c8fd4ae2ef4d434e81514151c028a7fc-' \
                   '1553497225280-331542'
    output_path = 'output'
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    page_count = get_page_count(original_url.format(0, CITY_NAME, JOB_NAME))
    old_url_set = load_progress('old_url.txt')
    csv_filename = output_path + '/{0}-{1}.csv'.format(JOB_NAME, CITY_NAME)
    if not os.path.exists(csv_filename):
        write_csv_headers(csv_filename)
    for i in range(page_count):
        url = original_url.format(i*90,CITY_NAME, JOB_NAME)
        work_list = get_work_detail(url)
        infos = get_company_detail(work_list, old_url_set)
        for info in infos:
            save_csv(csv_filename, info)
            save_progress(old_url_set, 'old_url.txt')


if __name__ == '__main__':
    start_time = time.time()
    main()
    print('单进程用时：%s' % (time.time() - start_time))



