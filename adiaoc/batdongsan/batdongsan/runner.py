import scrapy
from scrapy.crawler import CrawlerProcess
from spiders import batdongsan_spider, nhadatso_spider
from scrapy.utils.project import get_project_settings

process = CrawlerProcess(get_project_settings())
process.crawl(batdongsan_spider.BatDongSanSpider)
process.crawl(nhadatso_spider.NhaDatSoSpider)

process.start() # the script will block here until all crawling jobs are finished