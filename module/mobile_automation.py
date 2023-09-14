"""Control the Naver Calendar mobile app."""
import json
import logging
import os
import time

import urllib3.exceptions
import selenium.common.exceptions

import appium.webdriver.appium_service

from appium import webdriver
from typing import Union

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.common.touch_action import TouchAction
from miraelogger import Logger
from module import exception

MODUL_LOGGER = Logger(log_name=__name__, stream_log_level=logging.DEBUG)


class NaverCalendar:
    """Naver Calendar control class."""

    def __init__(self, configuration: Union[str, dict]):
        """Initialize the object.

        :param str/dict configuration: Configuration path or Configuration dictionary.
        """
        self._configuration = None

        if isinstance(configuration, str) and os.path.exists(configuration) and ('.json' in configuration):
            with open(configuration, encoding="utf-8") as _f:
                self._configuration = json.load(_f)["mobile"]
        elif isinstance(configuration, dict):
            self._configuration = configuration["mobile"]
        else:
            raise TypeError

        try:
            self._appium_service = appium.webdriver.appium_service.AppiumService()
            self._appium_service.start(args=["--relaxed-security", "--log-timestamp"])
            MODUL_LOGGER.info(f"Appium service is started.")
        except appium.webdriver.appium_service.AppiumServiceError as e:
            raise exception.AppiumException(e)

        try:
            self._driver = webdriver.Remote(r"http://localhost:4723", self._configuration["capabilities"])
            MODUL_LOGGER.info(f"{self._configuration['capabilities']['deviceName']} is connected.")
        except urllib3.exceptions.MaxRetryError as e:
            raise exception.AppiumException(e)

        MODUL_LOGGER.info("NaverCalendar initialize finish.")

    def go_to_naver_calendar(self):
        """Open the Naver calendar."""

        MODUL_LOGGER.debug("Go to Home")
        self._driver.press_keycode(3)

        self._touch('//*[@content-desc="네이버 캘린더"]')

        self._scroll("down", 2)
        self._scroll("up", 1)

    def arrange_schedule(self, notice_list) -> list:
        """Check the old notice and get the new notice list.

        :param list notice_list: Notice list.
        :return: New notice list.
        :rtype: list.
        """
        _exist = []
        _new = []

        self._touch("//*[contains(@resource-id, 'id/menu_search')]")
        time.sleep(0.5)

        MODUL_LOGGER.info("Setup the search filter.")
        self._touch("//*[contains(@resource-id, 'id/search_filter')]")
        self._touch("//*[contains(@resource-id, 'id/searchFilterInit')]")
        self._touch("//*[contains(@resource-id, 'id/calendarFilter')]")
        self._touch(f"//*[contains(@text, '{self._configuration['calendar']}')]")
        self._driver.back()
        self._driver.back()

        _search_editor = self._driver.find_element(by=AppiumBy.XPATH, value="//*[contains(@resource-id, 'id/search_keyword_editor')]")
        for _noti in notice_list:
            MODUL_LOGGER.debug(f"Target title: {_noti['title']}")
            _search_editor.clear()
            _search_editor.send_keys(_noti['title'])

            if self._driver.is_keyboard_shown():
                self._driver.hide_keyboard()

            # 1st confirmation - empty text
            _empty_view = None
            try:
                _empty_view = self._driver.find_elements(by=AppiumBy.XPATH,value="//*[contains(@resource-id, 'id/empty_view')]")
            except (selenium.common.exceptions.NoSuchElementException, RuntimeError, TimeoutError):
                pass

            if isinstance(_empty_view, list) and (len(_empty_view) > 0):
                _new.append(_noti)
                continue

            # Second confirmation - start date comparison for title duplication situations
            self._scroll_to_bottom()

            try:
                _schedule_list = self._driver.find_elements(by=AppiumBy.XPATH, value=f"//*[contains(@resource-id, 'id/content') and @text='{_noti['title']}']")
            except (selenium.common.exceptions.NoSuchElementException, RuntimeError, TimeoutError):
                _new.append(_noti)
                continue

            TouchAction(self._driver).tap(_schedule_list[-1]).perform()

            _start_date = self._driver.find_element(by=AppiumBy.XPATH, value="//*[contains(@resource-id, 'id/startDate')]").text

            if _noti['rigister_date'] not in _start_date:
                _new.append(_noti)
            self._driver.back()

        self._driver.back()
        MODUL_LOGGER.info(f"New notice: {len(_new)}, Exists notice: {len(notice_list) - len(_new)}")
        return _new

    def add_schedule(self, notice) -> None:
        """Add schedule

        :param list notice: Notice.
        """
        self._touch('//*[contains(@resource-id, "id/floating_write_button")]')
        self._touch('//*[contains(@resource-id, "id/floating_action_menu_schedule")]')
        MODUL_LOGGER.info("Open the adding schedule screen.")

        _search_editor = self._driver.find_element(by=AppiumBy.XPATH, value="//*[@resource-id='com.nhn.android.calendar:id/content']")
        _search_editor.clear()
        _search_editor.send_keys(notice['title'])
        MODUL_LOGGER.debug(f"Input title: {notice['title']}")

        _all_day_btn = self._driver.find_element(by=AppiumBy.XPATH, value="//*[contains(@resource-id, 'id/allday')]")
        if _all_day_btn.is_selected() is False:
            TouchAction(self._driver).tap(_all_day_btn).perform()
            MODUL_LOGGER.debug("Change the time option to all-day")

        self._control_date(notice['rigister_date'], notice['deadline_date'])

        _memo = self._driver.find_element(by=AppiumBy.XPATH, value="//*[contains(@resource-id, 'id/memoEdit')]")
        _memo.send_keys(notice['memo'])
        MODUL_LOGGER.debug(f"Input memo: {notice['memo']}")

        _calendar_name = self._driver.find_element(by=AppiumBy.XPATH, value="//*[contains(@resource-id, 'id/calendarName')]")
        if _calendar_name.text != self._configuration["calendar"]:
            TouchAction(self._driver).tap(_calendar_name).perform()
            self._touch(f"//*[contains(@resource-id, 'id/calendarText') and @text='{self._configuration['calendar']}']")
        MODUL_LOGGER.debug(f"Selected Calendar name: {self._configuration['calendar']}")

        try:
            self._touch("//*[contains(@resource-id, 'id/reminder_chip_view_remove')]")
        except exception.AppiumException:
            pass
        MODUL_LOGGER.debug(f"Remove the reminder")

        self._touch("//*[contains(@resource-id, 'id/toolbarConfirm')]")
        MODUL_LOGGER.info(f"{notice['title']} is add.")

    def _control_date(self, start_date, end_date):
        """Control the date as target_date

        :param str start_date: The YYYY.MM.DD format string.
        :param str end_date: The YYYY.MM.DD format string.
        """
        self._touch("//*[contains(@resource-id, 'id/startDate')]")

        _year_x, _year_y, _year_distance = self.__get_center_position("//*[contains(@resource-id, 'id/year')]")
        _month_x, _month_y, _month_distance = self.__get_center_position("//*[contains(@resource-id, 'id/month')]")
        _day_x, _day_y, _day_distance = self.__get_center_position("//*[contains(@resource-id, 'id/day')]")
        _scroll_info = [
            [_year_x, _year_y, _year_distance, "Year"],
            [_month_x, _month_y, _month_distance, "Month"],
            [_day_x, _day_y, _day_distance, "Day"]
        ]
        MODUL_LOGGER.debug("Get Date scroll position and distance for scroll.")

        self.__set_date(start_date.split("."), "//*[contains(@resource-id, 'id/startDate')]", _scroll_info)
        MODUL_LOGGER.debug("Change the start date.")

        self._touch("//*[contains(@resource-id, 'id/endDate')]")
        self.__set_date(end_date.split("."), "//*[contains(@resource-id, 'id/endDate')]", _scroll_info)
        self._touch("//*[contains(@resource-id, 'id/endDate')]")
        MODUL_LOGGER.debug("Change the end date.")

    def __set_date(self, target, xpath, info_list):
        """

        :param list target: Target date information list.
        :param str xpath:
        :param info_list:
        :return:
        """
        for i in range(3):
            try:
                _current = self._driver.find_element(by=AppiumBy.XPATH, value=xpath).text.split("(")[0].split(".")
            except (selenium.common.exceptions.NoSuchElementException, RuntimeError, TimeoutError):
                MODUL_LOGGER.exception(msg := f"Could not find the {xpath} elements.")
                raise exception.AppiumException(msg)

            if target[i] != _current[i]:
                _differ = int(target[i]) - int(_current[i])
                _x = info_list[i][0]
                _y_start = info_list[i][1]
                if _differ > 0:
                    _y_end = info_list[i][1] - info_list[i][2]
                else:
                    _y_end = info_list[i][1] + info_list[i][2]

                for _ in range(abs(_differ)):
                    TouchAction(self._driver).press(x=_x, y=_y_start).wait(100).move_to(x=_x, y=_y_end).release().wait(100).perform()

            _current = self._driver.find_element(by=AppiumBy.XPATH, value=xpath).text.split("(")[0].split(".")
            if target[i] != _current[i]:
                MODUL_LOGGER.error(f"Set {info_list[i][-1]} value to {target[i]} failed.")

    def __get_center_position(self, xpath, division=5):
        """Get center position of element. And get distance for scroll.

        :param str xpath: Target Xpath expression.
        :param int division: Division value.
        :return: x position, y position, distance
        :rtype: int, int, int
        """
        self._driver.implicitly_wait(0.5)
        try:
            _target_ele = self._driver.find_element(by=AppiumBy.XPATH, value=xpath)
        except (selenium.common.exceptions.NoSuchElementException, RuntimeError, TimeoutError):
            MODUL_LOGGER.exception(msg := f"Could not find the '{xpath}' within 0.5 sec.")
            raise exception.AppiumException(msg)

        _x_position = _target_ele.location["x"] + (_target_ele.size["width"] / 2)
        _y_position = _target_ele.location["y"] + (_target_ele.size["height"] / 2)
        _distance = _target_ele.size["height"] / division / 4 * 3
        return _x_position, _y_position, _distance


    def finalize(self):
        """Finalize."""
        MODUL_LOGGER.debug("Go to Home")
        self._driver.press_keycode(3)

        self._driver.quit()
        self._appium_service.stop()

    def _touch(self, xpath, timeout=1.0) -> None:
        """Touch element.

        :param str xpath: Xpath expression.
        :param float timeout: Timeout for waiting (default=1.0).
        :raise: exception.AppiumException: if exception occurs.
        """
        self._driver.implicitly_wait(timeout)
        try:
            _target = self._driver.find_element(by=AppiumBy.XPATH, value=xpath)
            TouchAction(self._driver).tap(_target).perform()
            MODUL_LOGGER.debug(f"Touch the '{xpath}' is success.")
        except (selenium.common.exceptions.NoSuchElementException, RuntimeError):
            MODUL_LOGGER.exception(msg := f"Touch the '{xpath}' is failed")
            raise exception.AppiumException(msg)
        except TimeoutError:
            MODUL_LOGGER.exception(msg := f"Could not find the '{xpath}' within {timeout} sec.")
            raise exception.AppiumException(msg)

    def _scroll_to_bottom(self) -> None:
        """Scroll to bottom."""
        _previous_page = self._driver.page_source

        for _ in range(100):
            self._scroll()
            _current_page = self._driver.page_source
            if _previous_page == _current_page:
                break
            _previous_page = _current_page

    def _scroll(self, direction="up", times=1, x_position=None) -> None:
        """Scroll the screen.

        :param str direction: Scroll direction string. (up, down)
        :param int times: Scroll repeat times. (default=1)
        :param int x_position: Standard X position. (default=None)
        """
        if direction.lower() not in ["up", "down"]:
            MODUL_LOGGER.exception(
                msg := "Please check the 'direction' value. The 'direction' value must be in ['up', 'down']")
            raise ValueError(msg)

        _window_size = self._driver.get_window_size()
        _width = _window_size['width']
        _height = _window_size['height']

        if x_position is None:
            x_position = int(_width / 2)

        try:
            for _ in range(times):
                if direction.lower() == "up":
                    TouchAction(self._driver).press(x=x_position, y=int(_height / 2)).wait(100).move_to(x=x_position, y=int(
                        _height / 4)).release().perform()
                elif direction.lower() == "down":
                    TouchAction(self._driver).press(x=x_position, y=int(_height / 2)).wait(100).move_to(x=x_position, y=int(
                        _height / 4 * 3)).release().perform()
            MODUL_LOGGER.debug(f"Scroll to {direction} is finish.")
        except Exception:
            MODUL_LOGGER.exception(msg := f"Could not scroll to {direction}.")
            raise Exception(msg)