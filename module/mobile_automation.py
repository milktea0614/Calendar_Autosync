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
            MODUL_LOGGER.debug(f"Target title: {_noti[1]}")
            _search_editor.clear()
            _search_editor.send_keys(_noti[1])

            if self._driver.is_keyboard_shown():
                self._driver.hide_keyboard()

            _empty_view = None
            try:
                _empty_view = self._driver.find_elements(by=AppiumBy.XPATH,value="//*[contains(@resource-id, 'id/empty_view')]")
            except (selenium.common.exceptions.NoSuchElementException, RuntimeError, TimeoutError):
                pass

            if _empty_view is not None:
                _new.append(_noti)
                continue

            self._scroll(times=10)

            try:
                _schedule_list = self._driver.find_elements(by=AppiumBy.XPATH, value=f"//*[contains(@resource-id, 'id/content') and @text='{_noti[1]}']")
            except (selenium.common.exceptions.NoSuchElementException, RuntimeError, TimeoutError):
                _new.append(_noti)
                continue

            TouchAction(self._driver).tap(_schedule_list[-1]).perform()

            _current_status_switch = self._driver.find_element(by=AppiumBy.XPATH, value="//*[contains(@resource-id, 'id/completeSwitch')]")
            _update_status = True if "마감" in _noti[-1] else False
            _schedule_status = True if _current_status_switch.get_attribute("checked").lower() == "true" else False

            if _update_status != _schedule_status:
                self._touch("//*[contains(@resource-id, 'id/completeSwitch')]")
                MODUL_LOGGER.info(f"{_noti[1]} status is changed from {_schedule_status} to {_update_status}.")
            self._driver.back()

        self._driver.back()
        MODUL_LOGGER.info(f"New notice: {len(_new)}, Exists notice: {len(notice_list) - len(_new)}")
        return _new

    def add_schedule(self, notice) -> None:
        """Add schedule

        :param list notice: Notice.
        """
        self._touch('//*[contains(@resource-id, "id/floating_write_button"]')
        self._touch('//*[contains(@resource-id, "id/floating_action_menu_schedule"]')
        MODUL_LOGGER.info("Open the adding schedule screen.")

        _search_editor = self._driver.find_element(by=AppiumBy.XPATH, value="//*[contains(@resource-id, 'id/content')]")
        _search_editor.send_keys(notice[1])
        MODUL_LOGGER.debug(f"Input title: {notice[1]}")

        _all_day_button = self._driver.find_element(by=AppiumBy.XPATH, value="//*[contains(@resource-id, 'id/allday')]")
        TouchAction(self._driver).tap(_all_day_button).perform()
        MODUL_LOGGER.debug("Change the time option to all-day")
        
        # todo


    def finalize(self):
        """Finalize."""
        self._driver.quit()
        self._appium_service.stop()

    def _touch(self, xpath, timeout=1.0) -> None:
        """Touch element.

        :param str xpath: Xpath expression.
        :param float timeout: Timeout for waiting (default=1.0).
        :raise
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