from module.web_crawling import JobAlioCrawling


job_crawling = JobAlioCrawling("./config/init.json")

job_crawling.start()