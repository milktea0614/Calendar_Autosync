from module.web_crawling import JobAlioCrawling
from module.mobile_automation import NaverCalendar


job_crawling = JobAlioCrawling("./config/init.json")

_notices = job_crawling.start()

mobile = NaverCalendar("./config/init.json")

mobile.go_to_naver_calendar()

_new = mobile.arrange_schedule(_notices)

for _noti in _new:
    mobile.add_schedule(_noti)

mobile.finalize()