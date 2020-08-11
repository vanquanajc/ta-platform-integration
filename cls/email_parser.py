import re
from bs4 import BeautifulSoup
from requests_html import HTMLSession

from utils.constants import JOBS_REGEX
from utils.constants import CITY_REGEX
from utils.constants import CODE_REGEX
from utils.constants import PHONE_REGEX
from utils.constants import SOURCE_DICT


class EmailParser:
    def __init__(self, google_service=None):
        self.google_service = google_service

    def parse_email(self, data: dict):
        assert data.get('from_mail') is not None, "Unable to find source in data"
        source = data.get('from_mail')

        if source == 'iappvnco@gmail.com':
            updated_data = self.parse_ahamove_website(data)
        elif source == 'info@tuyendungtopcv.com':
            updated_data = self.parse_topcv(data)
        elif source == 'resumes@mail.careerbuilder.vn':
            updated_data = self.parse_careerbuilder(data)
        else:
            updated_data = self.parse_personal(data)

        return updated_data

    def parse_ahamove_website(self, data):
        body = data.get('body')
        data['source'] = SOURCE_DICT[data['from_mail']]
        data['name'] = re.findall(r'\([\w\s]+\)', body)[0].replace('(', '').replace(')', '').title()
        data['phone'] = self.find_phone(body)
        data['email'] = data.get('reply_to')
        data['city'] = self.find_city(body)
        data['position'] = self.find_job(body)
        data['code'] = self.find_code(body)

        return data

    def parse_topcv(self, data):
        body = data.get('body')
        raw_message = self.google_service.read_email(data['mail_id'], _format='raw')
        url = self.find_topcv_url(raw_message)
        try:
            name, phone, email = self.get_topcv_info(url)
            data['source'] = SOURCE_DICT[data['from_mail']]
            data['name'] = name.title()
            data['phone'] = phone
            data['email'] = email
            data['city'] = self.find_city(body)
            data['position'] = self.find_job(body)
            data['code'] = self.find_code(body)
        except AttributeError:
            data = None

        return data

    def parse_careerbuilder(self, data):
        body = data.get('body')
        title = data.get('subject')
        name = title.split(' vừa')[0].strip().title()
        data['source'] = SOURCE_DICT[data['from_mail']]
        data['name'] = name
        data['phone'] = None
        data['email'] = data.get('reply_to')
        data['city'] = self.find_city(body)
        data['position'] = self.find_job(body)
        data['code'] = self.find_code(body)

        return data

    def parse_careerlink(self, data):
        # TODO: Build careerlink parsing
        pass

    def parse_personal(self, data):
        body = data.get('body')
        data['source'] = 'Personal'
        data['name'] = None
        data['phone'] = self.find_phone(body)
        data['city'] = self.find_city(body)
        data['position'] = self.find_job(body)
        data['code'] = self.find_code(body)

        return data

    @staticmethod
    def find_code(text):
        pattern = re.compile(CODE_REGEX)
        result = pattern.findall(text)
        result = None if len(result) == 0 else result[0]
        return result

    @staticmethod
    def find_phone(text):
        pattern = re.compile(PHONE_REGEX)
        result = pattern.search(text)
        if result:
            result = result.group()
            result = EmailParser.fix_phone_format(result)
        return result

    @staticmethod
    def fix_phone_format(phone: str):
        if not isinstance(phone, str):
            phone = str(phone)
        phone = re.sub(r'\D+', '', phone)
        phone = re.sub(r'^0', '84', phone)
        return phone

    @staticmethod
    def find_job(text):
        pattern = re.compile(JOBS_REGEX)
        result = pattern.findall(text, re.IGNORECASE)
        result = None if len(result) == 0 else result[0]
        return result

    @staticmethod
    def find_city(text):
        pattern = re.compile(CITY_REGEX)
        result = pattern.findall(text, re.IGNORECASE)
        if len(result) > 0:
            result = result[0]
            if result in ['HN', 'HAN']:
                result = 'Hà Nội'
            elif result in ['HCM', 'SG', 'SGN', 'Sài Gòn']:
                result = 'Hồ Chí Minh'
        else:
            result = None
        return result

    @staticmethod
    def find_topcv_url(text):
        pattern = re.compile(r'http://email.tuyendungtopcv.com/c/[\w\r\s=-]*')
        result = pattern.findall(text)[-1].replace('\r', '').replace('=', '').replace('\n', '')
        return result

    @staticmethod
    def get_topcv_info(url):
        session = HTMLSession()
        resp = session.get(url)
        resp.html.render()
        soup = BeautifulSoup(resp.html.html, 'lxml')
        info = soup.find(class_='table-bordered')
        if info:
            info = info.text.replace('Họ tên: ', '').replace('Điện thoại: ', '')\
                .replace('Email: ', '').replace('Vòng: ', '')
            info = re.sub(r'\s{2,}', '\n', info)
            info = [x.strip() for x in info.split('\n')[:3]]
            name = info[0]
            phone = EmailParser.fix_phone_format(info[1])
            email = info[2]
        else:
            name = phone = email = None

        return name, phone, email
