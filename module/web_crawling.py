import datetime
import json
import logging
import os
from typing import Union

import requests
from bs4 import BeautifulSoup
from miraelogger import Logger

from module import exception

MODUL_LOGGER = Logger(log_name=__name__, stream_log_level=logging.DEBUG)


class JobAlioCrawling:
    """Job-Alio Web crawling class."""

    def __init__(self, configuration: Union[str, dict]):
        """Initialize the object.

        :param str/dict configuration: Configuration path or Configuration dictionary.
        """
        self.url = "https://job.alio.go.kr/recruit.do"
        self.configuration = None
        self.params = {
            "eduType": "multi",
            "order": "REG_DATE",
            "sort": "DESC"
        }

        if isinstance(configuration, str) and os.path.exists(configuration) and ('.json' in configuration):
            with open(configuration) as _f:
                self.configuration = json.load(_f)["web_crawling"]
        elif isinstance(configuration, dict):
            self.configuration = configuration["web_crawling"]
        else:
            raise TypeError

        MODUL_LOGGER.info("JobAlioCrawling initialize finish.")

    def _create_params(self) -> None:
        """Create params for requests."""
        current_date = datetime.datetime.now()
        start_date = current_date - datetime.timedelta(days=30)

        self.params["s_date"] = start_date.strftime("%Y.%m.%d")
        self.params["e_date"] = current_date.strftime("%Y.%m.%d")

        if "detail_code" in self.configuration.keys():
            self.params["detail_code"] = self.configuration["detail_code"]
            MODUL_LOGGER.debug(f"'채용분야' is selected. [{self.__get_detail_code_info(self.configuration['detail_code'])}]")

        if "location" in self.configuration.keys():
            self.params["location"] = self.configuration["location"]
            MODUL_LOGGER.debug(f"'위치' is selected. [{self.__get_location_info(self.configuration['location'])}]")

        if "work_type" in self.configuration.keys():
            self.params["work_type"] = self.configuration["work_type"]
            MODUL_LOGGER.debug(f"'고용형태' is selected. [{self.__get_work_type_info(self.configuration['work_type'])}]")

        if "career" in self.configuration.keys():
            self.params["career"] = self.configuration["career"]
            MODUL_LOGGER.debug(f"'채용 구분' is selected. [{self.__get_career_info(self.configuration['career'])}]")

        if "education" in self.configuration.keys():
            self.params["education"] = self.configuration["education"]
            MODUL_LOGGER.debug(f"'학력 정보' is selected. [{self.__get_education_info(self.configuration['education'])}]")


    def start(self):
        """Get all page information.

        :raise RequestException: if request is not normal.
        """

        self._create_params()

        _parsing = []
        _pageNo = 1

        while True:
            self.params["pageNo"] = _pageNo
            MODUL_LOGGER.info(f"Get ({_pageNo})th page information...")
            response = requests.get(self.url, params=self.params)

            if response.status_code == 200:
                my_soup = BeautifulSoup(response.content, "html.parser")
                selected_list = my_soup.select("#frm > table > tbody > tr")

                if not selected_list:
                    break

                for _row in selected_list:
                    _column = _row.select("td")
                    _link = _column[2].find('a').get('href')
                    _title = _column[2].text.strip()
                    _org = _column[3].text.strip()
                    _location = _column[4].text.strip().replace("\r","").replace("\t", "").replace("\n","")
                    _work_type = _column[5].text.strip().replace("\r","").replace("\t", "").replace("\n","")
                    _rigister_date = _column[6].text.strip().replace("\r","").replace("\t", "").replace("\n","")
                    _deadline_date = _column[7].text.strip().replace("\r","").replace("\t", "").replace("\n","")[:8]
                    _status = _column[8].text.strip()

                    _parsing.append([_link, _title, _org, _location, _work_type, _rigister_date, _deadline_date, _status])
            else:
                MODUL_LOGGER.error(msg := f"Could not get the webpage. status code is {response.status_code}")
                raise exception.RequestException(msg)

            _pageNo += 1

        MODUL_LOGGER.debug(f"length: {len(_parsing)}")
        for i in _parsing:
            print(i)


    def __get_detail_code_info(self, detail_codes) -> list:
        """Return selected detail code information.

        :param list detail_codes: Detail codes list.
        :return: Detail code information of Korean.
        :rtype: list.
        """
        _korean_info = {
            "600002": "경영·회계·사무",
            "600003": "금융·보험",
            "600004": "교육·자연·사회과학",
            "600005": "법률·경찰·소방·교도·국방",
            "600006": "보건·의료",
            "600007": "사회복지·종교",
            "600008": "문화·예술·디자인·방송",
            "600009": "운전·운송",
            "600010": "영업판매",
            "600011": "경비·청소",
            "600012": "이용·숙박·여행·오락·스포츠",
            "600013": "음식서비스",
            "600014": "건설",
            "600015": "기계",
            "600016": "재료",
            "600017": "화학",
            "600018": "섬유·의복",
            "600019": "전기·전자",
            "600020": "정보통신",
            "600021": "식품가공",
            "600022": "인쇄·목재·가구·공예",
            "600023": "환경·에너지·안전",
            "600024": "농림어업",
            "600025": "연구",
        }
        _result = []

        for i in detail_codes:
            if i in _korean_info.keys():
                _result.append(_korean_info[i])
            else:
                MODUL_LOGGER.warn(f"({i}) is not in detail code.")
        return _result

    def __get_location_info(self, locations) -> list:
        """Return selected location information.

        :param list locations: Locations list.
        :return: Location information of Korean.
        :rtype: list.
        """
        _korean_info = {
            "R3009": "해외",
            "R3010": "서울특별시",
            "R3011": "인천광역시",
            "R3012": "대전광역시",
            "R3013": "대구광역시",
            "R3014": "부산광역시",
            "R3015": "광주광역시",
            "R3016": "울산광역시",
            "R3017": "경기도",
            "R3018": "강원도",
            "R3019": "충청남도",
            "R3020": "충청북도",
            "R3021": "경상북도",
            "R3022": "경상남도",
            "R3023": "전라남도",
            "R3024": "전라북도",
            "R3025": "제주특별자치도",
            "R3026": "세종특별자치시"
        }
        _result = []

        for i in locations:
            if i in _korean_info.keys():
                _result.append(_korean_info[i])
            else:
                MODUL_LOGGER.warn(f"({i}) is not in location.")
        return _result

    def __get_work_type_info(self, work_types) -> list:
        """Return selected work types information.

        :param list work_types: Work types list.
        :return: Work types information of Korean.
        :rtype: list.
        """
        _korean_info = {
            "R1010": "정규직",
            "R1030": "무기계약직",
            "R1040": "비정규직",
            "R1060": "청년인턴(체험형)",
            "R1070": "청년인턴(채용형)"
        }
        _result = []

        for i in work_types:
            if i in _korean_info.keys():
                _result.append(_korean_info[i])
            else:
                MODUL_LOGGER.warn(f"({i}) is not in work types.")
        return _result

    def __get_career_info(self, careers) -> list:
        """Return selected careers information.

        :param list careers: Career list.
        :return: Career information of Korean.
        :rtype: list.
        """
        _korean_info = {
            "R2010": "신입",
            "R2020": "경력",
            "R2030": "신입+경력",
            "R2040": "외국인 전형"
        }
        _result = []

        for i in careers:
            if i in _korean_info.keys():
                _result.append(_korean_info[i])
            else:
                MODUL_LOGGER.warn(f"({i}) is not in work types.")
        return _result

    def __get_education_info(self, educations) -> list:
        """Return selected education information.

        :param list educations: Education list.
        :return: Education information of Korean.
        :rtype: list.
        """
        _korean_info = {
            "R7010": "학력무관",
            "R7020": "중졸이하",
            "R7030": "고졸",
            "R7040": "대졸(2~3년)",
            "R7050": "대졸(4년)",
            "R7060": "석사",
            "R7070": "박사"
        }
        _result = []

        for i in educations:
            if i in _korean_info.keys():
                _result.append(_korean_info[i])
            else:
                MODUL_LOGGER.warn(f"({i}) is not in work types.")
        return _result

