import requests
import re
import json
import time, random
from bs4 import BeautifulSoup
from http.cookies import SimpleCookie
from urllib.parse import urlencode

class A_Course:
    def __init__(self, url, cookie):
        self.course_url = url
        self.session = requests.session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0'
        }
        self.cookie = dict([(c, SimpleCookie(cookie)[c].value) for c in SimpleCookie(cookie)])
        # "/knowledge/cards?clazzid=" + clazzid + "&courseid=" + courseId + "&knowledgeid=" + chapterId + "&num=" + num + "&v=20160407-1"

    def get_utenc(self, url):
        header = self.headers.copy()
        header.update({
            'Host': 'mooc1-2.chaoxing.com',
            'Pragma': 'no-cache',
            'Connection': 'keep-alive',
        })
        response = self.session.get(url, headers=header, cookies=self.cookie)
        utenc = re.search(r'utEnc="([\s\S]*?)";', response.text)
        if utenc:
            return utenc.group(1)

    def get_answer(self, title, url):
        print(title, url)
        header = self.headers.copy()
        header.update({
            'Host':  'mooc1-2.chaoxing.com',
            'Origin': 'https://mooc1-2.chaoxing.com',
            'Pragma': 'no-cache',
            'Referer': url,
            'X - Requested - With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
        })
        courseId = re.search(r'courseId=(\d+)', url).group(1)
        clazzid = re.search(r'clazzid=(\d+)', url).group(1)
        chapterId = re.search(r'chapterId=(\d+)', url).group(1)

        form_data = {
            'courseId': courseId,
            'clazzid': clazzid,
            'chapterId': chapterId
        }

        response = self.session.post('https://mooc1-2.chaoxing.com/mycourse/studentstudyAjax', data=form_data, headers=header, cookies=self.cookie)
        soup = BeautifulSoup(response.text, 'lxml')
        span = soup.find('span', attrs={'title': '章节测验'})
        if span:
            content = span['onclick']
            numbers = re.search(r'changeDisplayContent([\s\S]*?);', content)
            if numbers:
                num_li = numbers.group(1).split(',')
                num_li = [i.replace("'", '').replace('(', '').replace(')', '') for i in num_li]
                num, totalnum, chapterId, courseId, clazzid, knowledgestr = num_li
                src = 'https://mooc1-2.chaoxing.com' + "/knowledge/cards?clazzid=" + clazzid + "&courseid=" + courseId + "&knowledgeid=" + chapterId + "&num=" + str(int(num)-1) + "&v=20160407-1"
                header = self.headers.copy()
                header.update({
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, sdch, br',
                    'Accept-Language': 'zh-CN,zh;q=0.8',
                    'Cache-Control': 'no-cache',
                    'Host': 'mooc1-2.chaoxing.com',
                    'Pragma': 'no-cache',
                    'Referer': url,
                    'Upgrade-Insecure-Requests': '1',
                    'Connection': 'keep-alive',
                })
                response = self.session.get(src, headers=header, cookies=self.cookie)
                marg = re.search(r'try{([\s\S]*?)}catch', response.text)
                if marg:
                    jobid = re.search(r'"jobid":"([\s\S]*?)",', marg.group(1)).group(1)
                    workid = jobid.replace('work-', '')
                    enc = re.search(r'"enc":"([\s\S]*?)",', marg.group(1)).group(1)
                    # utenc = self.get_utenc(url)
                    # print(utenc)
                    utenc = 'd3602109a00822e8bae029084b75065f'
                    data = {
                        'api': '1',
                        'workId': workid,
                        'jobid': jobid,
                        'needRedirect': 'true',
                        'knowledgeid': chapterId,
                        'ut': 's',
                        'clazzId': clazzid,
                        'type': '',
                        'enc': enc,
                        'utenc': utenc,
                        'courseid': courseId
                    }
                    link = 'https://mooc1-2.chaoxing.com/api/work?'+urlencode(data)
                    header = self.headers.copy()
                    header.update({
                        'Host': 'mooc1-2.chaoxing.com',
                        'Pragma': 'no-cache',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                    })
                    response = self.session.get(link, headers=header, cookies=self.cookie, allow_redirects=False)
                    link2 = response.headers['Location']
                    response2 = self.session.get(link2, headers=header, cookies=self.cookie, allow_redirects=False)
                    link3 = response2.headers['Location']
                    response3 = self.session.get(link3, headers=header, cookies=self.cookie, allow_redirects=False)
                    soup = BeautifulSoup(response3.text, 'lxml')
                    question_li = soup.find('div', attrs={'class': 'ZyBottom'})
                    questions = question_li.find_all('div', attrs={'class': 'TiMu'})
                    if questions:
                        for question in questions:
                            answer = question.find('div', attrs={'class': 'Py_answer'}).find_all('i')[-1]['class']
                            if 'dui' in answer:
                                answer = question.find('div', attrs={'class': 'Py_answer'}).find('span').get_text()
                                title_div = question.find('div', attrs={'class': 'Zy_TItle'})
                                title_num = title_div.find('i').get_text()
                                title_word = title_div.find('div').get_text().strip()
                                title = title_num + ' ' + title_word
                                choice_li = question.find('ul')
                                if choice_li:
                                    for i in choice_li.find_all('li'):
                                        title += '\n' + i.get_text()
                                print(title)
                                print(answer)



        else:
            print('Fail2')
            print(response.text)


    def start(self):
        header = self.headers.copy()
        header['Referer'] = 'http://mooc1-2.chaoxing.com/visit/courses'
        response = self.session.get(self.course_url, headers=header, cookies=self.cookie)
        soup = BeautifulSoup(response.text, 'lxml')

        divs = soup.find('div', attrs={'class': 'timeline'}).find_all('div', attrs={'class': 'units'})
        for div in divs:
            title_num = div.find('h2').find('span').find('b').get_text().strip()
            title = div.find('h2').find('a')['title'].strip()
            print(title_num, title)
            if title not in ['阅读', '直播']:
                level_twos = div.find_all('div', attrs={'class': 'leveltwo'})
                for level_two in level_twos:
                    h3_num = len(level_two.find_all('h3'))
                    if h3_num == 1:
                        span1 = level_two.find('span', attrs={'class': 'icon'})
                        span2 = level_two.find('span', attrs={'class': 'articlename'})
                        level_two_title = span1.get_text().strip() + ' ' + span2.find('a')['title'].strip()
                        href = 'https://mooc1-2.chaoxing.com' + span2.find('a')['href']
                        print(level_two_title, href)
                        self.get_answer(level_two_title, href)
                        time.sleep(4)
                    else:
                        span1 = level_two.find('span', attrs={'class': 'icon'})
                        span2 = level_two.find('span', attrs={'class': 'articlename'})
                        level_two_title = span1.get_text().strip() + ' ' + span2.find('a')['title'].strip()
                        href = 'https://mooc1-2.chaoxing.com' + span2.find('a')['href']
                        print(level_two_title, href)
                        span_li = level_two.find_all('span', attrs={'class': 'articlename'})[1:]
                        for span in span_li:
                            level_three_title = ''.join(span.get_text().split())
                            biaohao = re.match(r'\d+.\d+.\d+', level_three_title).group()
                            level_three_title = level_three_title.replace(biaohao, biaohao+' ')
                            href = 'https://mooc1-2.chaoxing.com' + span.find('a')['href']
                            self.get_answer(level_three_title, href)
                            time.sleep(4)



if __name__ == "__main__":
    cookie = '__dxca=afa141a9-2194-4259-8745-ac8b5de194bd; KI4SO_SERVER_EC=RERFSWdRQWdsckQ0aGRFcytqcUZFcE5zOTJ6SHVvbUlNTzN6VXNESWtXVmR6ZkJXdjJaY0FxSmNF%0AeFQxSFRzVUNPdGdxMXhwZmNQNApoZEVzK2pxRkVvUUdZU09Db1NIUlhXai9ucDFkbzBMclJ1a0ZW%0AMy9nZ01FRXdUUWt5Q3dmd3hVaDBBUGZuVUQ4SXNXNU1abk83OU5SCjB1am9DcHFRUDFwOXh4MFVC%0AckYybkZGYmNSQ0hwUlRUMkdjeFY0QU1HMjM2VW5lWUo0YkVyRGdybjU1SllYYWo3SndVT3NOTG04%0ASnMKWWREb1NyWlpZWEFUK1dXTkNhbDB0dVVTM1hoOVkza1haZTcvZHAxV0w0TlRmUzFkZUt4Sys3%0AT1I2bk5BQWs2VzZLa1VvZTFEZHJwMwpodWY2aDFZdmcxTjlMVjE0aTh4SDlJSGh4SlFIdURVU3Vq%0AV3FQaVhWMnU1NWZXNzlXOWNRZjRFTHVQaTRnTXd3UWRSWXNNYjVvQWFhCkgvYjVERXFtSk9POU1E%0ARXFvYUc1aCs0SDd3PT0%2FYXBwSWQ9MSZrZXlJZD0x; _tid=43272599; sso_puid=58979822; _industry=6; fid=29669; _uid=58979822; uf=da0883eb5260151eb012152134b41805fbe6049508ba7848b8967459abcbe16b4d4071549cd88ecf78a7cdeaf4309ddc913b662843f1f4ad6d92e371d7fdf6448f82e4ab46d8a7e122d37f0ce2a6151d71e4ef324e83e73c6804b32422da36faf6a4ed1745fdc7f3; _d=1546836209651; UID=58979822; vc=F334EEB67F733E6A625DCC91E8A0BB3B; vc2=1403261D7A04FC8330E01DA4CBFAE2C8; DSSTASH_LOG=C_38-UN_2869-US_58979822-T_1546836209651; thirdRegist=0; rt=-2; tl=0; k8s=6dff42dd063c8508fc24c19ff04fbbff2da8f651; jrose=FFF5AADDA59C8F3DF9A0889366AEAEBB.mooc-4136528608-whkmr; route=f4530fc65c8934baba769156ca67ec88'

    course_url = 'https://mooc1-2.chaoxing.com/mycourse/studentcourse?courseId=202176951&clazzid=5030741&cpi=44418679&enc=b8b3b0dd13531f13f41adc7909bb86fc'
    course = A_Course(course_url, cookie)
    course.start()