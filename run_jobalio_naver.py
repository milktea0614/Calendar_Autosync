import os.path

from miraelogger import Logger
from module.web_crawling import JobAlioCrawling
from module.mobile_automation import NaverCalendar


MAIN_LOGGER = Logger(__name__, os.path.realpath("./log/calendar_autosync.log")).logger

job_crawling = JobAlioCrawling("./config/init.json", MAIN_LOGGER)
_notices = job_crawling.start()

mobile = NaverCalendar("./config/init.json", MAIN_LOGGER)

mobile.go_to_naver_calendar()

_new = mobile.arrange_schedule(_notices)

MAIN_LOGGER.info(f"Add {len(_new)} new schedules start...")
for _noti in _new:
    mobile.add_schedule(_noti)
MAIN_LOGGER.info(f"Add {len(_new)} new schedules is finish")

mobile.finalize()