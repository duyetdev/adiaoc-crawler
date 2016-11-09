import scrapy

class BatDongSanSpider(scrapy.Spider):
    name = "batdongsan"

    def start_requests(self):
        urls = [
            'http://batdongsan.com.vn/nha-dat-ban',
            'http://batdongsan.com.vn/nha-dat-cho-thue',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_list_and_paging)

    def parse_list_and_paging(self, response):
        for line in response.css('#form1 > div.site-center > div.body-left > div.container-default > div > div.product-list.product-list-page.stat > div.Main > div'):
            item_url = line.css('.p-title a::attr(href)').extract_first()
            yield scrapy.Request(response.urljoin(item_url), callback=self.parse)

        for next_page in response.css('#form1 > div.site-center > div.body-left > div.container-default > div > div.background-pager-controls > div'):
            next_page_url = next_page.css('a::attr(href)').extract_first()
            yield scrapy.Request(response.urljoin(next_page_url), callback=self.parse)

    def parse(self, response):
        title = response.css('#product-detail > div.pm-title > h1::text').extract_first()
        print  ' ===========================', title.encode('utf-8')

        yield {
            'title': title.encode('utf-8'),
        }