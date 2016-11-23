# -*- coding: utf-8 -*-

import scrapy
from scrapy_redis.spiders import RedisSpider
from datetime import datetime
import re
from HTMLParser import HTMLParser
h = HTMLParser()


class BatDongSanSpider(RedisSpider):
    name = "batdongsan"
    allowed_domains = ['batdongsan.com.vn']

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

        for next_page in response.css('#form1 > div.site-center > div.body-left > div.container-default  div.background-pager-controls a'):
            next_page_url = next_page.css('::attr(href)').extract_first()
            print '=======================> next ', next_page_url
            yield scrapy.Request(response.urljoin(next_page_url), callback=self.parse_list_and_paging)

    def parse(self, response):
        url = response.url

        title = response.css('title::text').extract_first()
        description = response.css('#product-detail > div.pm-content.stat').extract_first()

        area_text = response.css('#product-detail > div.kqchitiet > span:nth-child(2) > span:nth-child(2) > strong::text').extract_first()
        area = self.parse_area(area_text)

        price_text = response.css('#product-detail > div.kqchitiet > span:nth-child(2) > span.gia-title.mar-right-15 > strong::text').extract_first()
        price = self.parse_price_from_text(price_text)
        unit = self.parse_unit_from_price(price_text)
        property_type = response.css('#product-detail > div.pm-content-detail > table > tbody > tr > td:nth-child(1) > div > div.left-detail > div:nth-child(4) > div.right::text').extract_first()
        
        # address = response.css('#product-detail > div.pm-content-detail > table > tbody > tr > td:nth-child(1) > div > div.left-detail > div:nth-child(2) > div.right::text').extract_first()
        # district = response.css('#product-detail > div.kqchitiet > span.diadiem-title.mar-right-15::text').extract_first()
        address_label = u'Địa chỉ'
        address = response.xpath('//*[@class="left-detail"]/div[contains(., \''+ address_label +'\')]/div[2]//text()').extract_first()
        provincial_city, district = self.parse_province_district_from_address(address)

        project = ''
        
        end_date_label = u'Ngày hết hạn'
        end_date = response.xpath('//*[@class="left-detail"]/div[contains(., \''+ end_date_label +'\')]/div[2]//text()').extract_first()

        contact_name_label = u'Tên liên lạc'
        contact_name = response.xpath('//*[@id="divCustomerInfo"]/div[contains(., \''+ contact_name_label +'\')]/div[2]//text()').extract_first()
        
        post_type_label = u'Loại tin rao'
        post_type_text = response.xpath('//*[@class="left-detail"]/div[contains(., \''+ post_type_label +'\')]/div[2]//text()').extract_first()
        post_type = self.parse_post_type(post_type_text)
        post_cat = self.parse_post_cat(post_type_text)

        email_raw = response.xpath('//*[@id="LeftMainContent__productDetail_contactEmail"]/div[2]/script//text()').extract_first()
        email = self.parse_email_from_raw(email_raw)

        phone_label = u'Mobile'
        phone = response.xpath('//*[@id="divCustomerInfo"]/div[contains(., \''+ phone_label +'\')]/div[2]//text()').extract_first()
        phone = self.parse_result_item(phone, 'phone')
        if not phone:
            phone_label = u'Điện thoại'
            phone = response.xpath('//*[@id="divCustomerInfo"]/div[contains(., \''+ phone_label +'\')]/div[2]//text()').extract_first()
            phone = self.parse_result_item(phone, 'phone')

        images = response.css('#photoSlide > div.list-img ul > li > img::attr(src)').extract()
        images = self.parse_real_image_url(images)

        youtube_url = []

        yield {
            'url': url,
            'title': self.parse_result_item(title),
            'description': self.parse_result_item(description, 'description'),
            'area': self.parse_result_item(area, 'int'),
            'area_text': self.parse_result_item(area_text),
            'price': self.parse_result_item(price, 'money'),
            'price_text': self.parse_result_item(price_text),
            'unit': unit,
            'property_type': self.parse_result_item(property_type),
            'provincial_city': self.parse_result_item(provincial_city),
            'district': self.parse_result_item(district),
            'address': self.parse_result_item(address),
            'post_type': self.parse_result_item(post_type),
            'post_cat': self.parse_result_item(post_cat),
            'project': self.parse_result_item(project),
            'end_date': self.parse_result_item(end_date, 'date'),
            'contact_name': self.parse_result_item(contact_name),
            'email': self.parse_result_item(email),
            'phone': phone,
            'images': images,
        }

    def parse_result_item(self, text, data_type='str'):
        if text == None:
            return ''

        if data_type == 'number':
            return text

        if data_type == 'int':
            try:
                result = int(text)
                return result
            except:
                return 0

        if data_type == 'money':
            return text

        if data_type == 'date':
            try: 
                date = datetime.strptime(text)
                return date
            except:
                return None

        text = str(text.encode('utf-8'))

        if data_type == 'description':
            pass
        else:
            text = text.strip()

        return text

    def parse_unit_from_price(self, price_text):
        _dict = { '1': u'Triệu VNĐ', '1000': u'Tỷ VNĐ', '10': u'Triệu VNĐ/m2', 'thang': u'Triệu VNĐ/tháng', 'tt': u'Thỏa thuận' }
        _default = 'tt'

        if price_text == None:
            return _default

        if price_text.find(u'triệu/tháng') > -1 or price_text.find(u'Triệu/tháng') > -1:
            return 'thang'
        if price_text.find(u'triệu/m2') > -1 or price_text.find(u'Triệu/m2')> -1 or price_text.find(u'triệu/m²') > -1:
            return '10'
        if price_text.find(u'triệu') > -1 or price_text.find(u'Triệu') > -1:
            return '1'
        if price_text.find(u'Tỷ') > -1 or price_text.find(u'tỷ') > -1:
            return '1000'

        return _default

    def parse_price_from_text(self, price_text):
        if price_text == None:
            return 0

        price_text = price_text.encode('utf8')
        re_search = re.search(r'[+-]?([0-9]*[.])?[0-9]+', price_text)
        
        if re_search:
            price = float(re_search.group())
            if price:
                return price
        return 0

    def parse_area(self, price_text):
        if price_text == None:
            return 0

        price_text = price_text.encode('utf8')
        re_search = re.search(r'[+-]?([0-9]*[.])?[0-9]+', price_text)
        
        if re_search:
            price = float(re_search.group())
            if price:
                return price
        return 0

    def parse_province_district_from_address(self, text):
        province_list = [u"Cần Thơ", u"Đà Nẵng", u"Hà Nội", u"Hải Phòng", u"Hồ Chí Minh", u"An Giang", u"Bà Rịa-Vũng Tàu", u"Bắc Giang", u"Bắc Kạn", u"Bạc Liêu", u"Bắc Ninh", u"Bến Tre", u"Bình Định", u"Bình Dương", u"Bình Phước", u"Bình Thuận", u"Cà Mau", u"Cao Bằng", u"Đắk Lắk", u"Đắk Nông", u"Điện Biên", u"Đồng Nai", u"Đồng Tháp", u"Gia Lai", u"Hà Giang", u"Hà Nam", u"Hà Tĩnh", u"Hải Dương", u"Hậu Giang", u"Hòa Bình", u"Hưng Yên", u"Khánh Hòa", u"Kiên Giang", u"Kon Tum", u"Lai Châu", u"Lâm Đồng", u"Lạng Sơn", u"Lào Cai", u"Long An", u"Nam Định", u"Nghệ An", u"Ninh Bình", u"Ninh Thuận", u"Phú Thọ", u"Phú Yên", u"Quảng Bình", u"Quảng Nam", u"Quảng Ngãi", u"Quảng Ninh", u"Quảng Trị", u"Sóc Trăng", u"Sơn La", u"Tây Ninh", u"Thái Bình", u"Thái Nguyên", u"Thanh Hóa", u"Thừa Thiên Huế", u"Tiền Giang", u"Trà Vinh", u"Tuyên Quang", u"Vĩnh Long", u"Vĩnh Phúc", u"Yên Bái", ]
        province_district_list = { u"Cần Thơ": [ u"Cờ Đỏ", u"Phong Điền", u"Thới Lai", u"Vĩnh Thạnh", u"Bình Thủy", u"Cái Răng", u"Ninh Kiều", u"Ô Môn", u"Thốt Nốt" ], u"Đà Nẵng": [ u"Hòa Vang", u"Hoàng Sa", u"Cẩm Lệ", u"Hải Châu", u"Liên Chiểu", u"Ngũ Hành Sơn", u"Sơn Trà", u"Thanh Khê" ], u"Hà Nội": [ u"Ba Vì", u"Chương Mỹ", u"Đan Phượng", u"Đông Anh", u"Gia Lâm", u"Hoài Đức", u"Mê Linh", u"Mỹ Đức", u"Phú Xuyên", u"Phúc Thọ", u"Quốc Oai", u"Sóc Sơn", u"Thạch Thất", u"Thanh Oai", u"Thanh Trì", u"Thường Tín", u"Từ Liêm", u"ứng Hòa", u"Ba Đình", u"Cầu Giấy", u"Đống Đa", u"Hà Đông", u"Hai Bà Trưng", u"Hoàn Kiếm", u"Hoàng Mai", u"Long Biên", u"Tây Hồ", u"Thanh Xuân", u"Thị xã Sơn Tây" ], u"Hải Phòng": [ u"An Dương", u"An Lão", u"Bạch Long Vĩ", u"Cát Hải", u"Kiến Thụy", u"Thủy Nguyên", u"Tiên Lãng", u"Vĩnh Bảo", u"Đồ Sơn", u"Dương Kinh", u"Hải An", u"Hồng Bàng", u"Kiến An", u"Lê Chân", u"Ngô Quyền" ], u"Hồ Chí Minh": [ u"Bình Chánh", u"Cần Giờ", u"Củ Chi", u"Hóc Môn", u"Nhà Bè", u"Quận 1", u"Quận 10", u"Quận 11", u"Quận 12", u"Quận 2", u"Quận 3", u"Quận 4", u"Quận 5", u"Quận 6", u"Quận 7", u"Quận 8", u"Quận 9", u"Bình Tân", u"Bình Thạnh", u"Gò Vấp", u"Phú Nhuận", u"Tân Bình", u"Tân Phú", u"Thủ Đức" ], u"An Giang": [ u"An Phú", u"Châu Phú", u"Châu Thành", u"Chợ Mới", u"Phú Tân", u"Thoại Sơn", u"Tịnh Biên", u"Tri Tôn", u"Long Xuyên", u"Thị xã Châu Đốc", u"Thị xã Tân Châu" ], u"Bà Rịa-Vũng Tàu": [ u"Châu Đức", u"Côn Đảo", u"Đất Đỏ", u"Long Điền", u"Tân Thành", u"Xuyên Mộc", u"Vũng Tàu", u"Thị xã Bà Rịa" ], u"Bắc Giang": [ u"Hiệp Hòa", u"Lạng Giang", u"Lục Nam", u"Lục Ngạn", u"Sơn Động", u"Tân Yên", u"Việt Yên", u"Yên Dũng", u"Yên Thế", u"Bắc Giang" ], u"Bắc Kạn": [ u"Ba Bể", u"Bạch Thông", u"Chợ Đồn", u"Chợ Mới", u"Na Rì", u"Ngân Sơn", u"Pác Nặm", u"Thị xã Bắc Kạn" ], u"Bạc Liêu": [ u"Đông Hải", u"Giá Rai", u"Hòa Bình", u"Hồng Dân", u"Phước Long", u"Vĩnh Lợi", u"Thành Phố Bạc Liêu" ], u"Bắc Ninh": [ u"Gia Bình", u"Lương Tài", u"Quế Võ", u"Thuận Thành", u"Tiên Du", u"Yên Phong", u"Bắc Ninh", u"Thị xã Từ Sơn" ], u"Bến Tre": [ u"Ba Tri", u"Bình Đại", u"Châu Thành", u"Chợ Lách", u"Giồng Trôm", u"Mỏ Cày Bắc", u"Mỏ Cày Nam", u"Thạnh Phú", u"Bến Tre" ], u"Bình Định": [ u"An Lão", u"An Nhơn", u"Hoài  Ân", u"Hoài Nhơn", u"Phù Mỹ", u"Phù cát", u"Tây Sơn", u"Tuy Phước", u"Vân Canh", u"Vĩnh Thạnh", u"Quy Nhơn" ], u"Bình Dương": [ u"Bến Cát", u"Dầu Tiếng", u"Dĩ An", u"Phú Giáo", u"Tân Uyên", u"Thuận An", u"Thị xã Thủ Dầu Một" ], u"Bình Phước": [ u"Bù Đăng", u"Bù Đốp", u"Bù Gia Mập", u"Chơn Thành", u"Đồng Phú", u"Hớn Quản", u"Lộc Ninh", u"Thị xã Bình Long", u"Thị xã Đồng Xoài", u"Thị xã Phước Long" ], u"Bình Thuận": [ u" Đức Linh", u"Bắc Bình", u"Hàm Tân", u"Hàm Thuận Bắc", u"Hàm Thuận Nam", u"Phú Qúi", u"Tánh Linh", u"Tuy Phong", u"Phan Thiết", u"Thị xã La Gi" ], u"Cà Mau": [ u"Cái Nước", u"Đầm Dơi", u"Năm Căn", u"Ngọc Hiển", u"Phú Tân", u"Thới Bình", u"Trần Văn Thời", u"U Minh", u"Cà Mau" ], u"Cao Bằng": [ u"Bảo Lạc", u"Bảo Lâm", u"Hạ Lang", u"Hà Quảng", u"Hòa An", u"Nguyên Bình", u"Phục Hòa", u"Quảng Uyên", u"Thạch An", u"Thông Nông", u"Trà Lĩnh", u"Trùng Khánh", u"Thị xã Cao Bằng" ], u"Đắk Lắk": [ u"Buôn Đôn", u"Cư Kuin", u"Cư MGar", u"Ea Kar", u"Ea Súp", u"EaHLeo", u"Krông Ana", u"Krông Bông", u"Krông Búk", u"Krông Năng", u"Krông Pắc", u"Lắk", u"MDrắk", u"Buôn Ma Thuột", u"Thị xã Buôn Hồ" ], u"Đắk Nông": [ u"Cư Jút", u"Đắk GLong", u"Đắk Mil", u"Đắk RLấp", u"Đắk Song", u"KRông Nô", u"Tuy Đức", u"Thị xã Gia Nghĩa" ], u"Điện Biên": [ u"Điện Biên", u"Điện Biên Đông", u"Mường Chà", u"Mương Nhé", u"Mường ảng", u"Tủa Chùa", u"Tuần Giáo", u"Điện Biên phủ", u"Thị xã Mường Lay" ], u"Đồng Nai": [ u"Cẩm Mỹ", u"Định Quán", u"Long Thành", u"Nhơn Trạch", u"Tân Phú", u"Thống Nhất", u"Trảng Bom", u"Vĩnh Cửu", u"Xuân Lộc", u"Biên Hòa", u"Thị xã Long Khánh" ], u"Đồng Tháp": [ u"Cao Lãnh", u"Châu Thành", u"Hồng Ngự", u"Lai Vung", u"Lấp Vò", u"Tam Nông", u"Tân Hồng", u"Thanh Bình", u"Tháp Mười", u"Cao Lãnh", u"Thị xã Hồng Ngự", u"Thị xã Sa Đéc" ], u"Gia Lai": [ u"Chư Păh", u"Chư Pưh", u"Chư Sê", u"ChưPRông", u"Đăk Đoa", u"Đăk Pơ", u"Đức Cơ", u"Ia Grai", u"Ia Pa", u"KBang", u"KBang", u"Kông Chro", u"Krông Pa", u"Mang Yang", u"Phú Thiện", u"Plei Ku", u"Thị xã AYun Pa", u"Thị xã An Khê" ], u"Hà Giang": [ u"Bắc Mê", u"Bắc Quang", u"Đồng Văn", u"Hoàng Su Phì", u"Mèo Vạc", u"Quản Bạ", u"Quang Bình", u"Vị Xuyên", u"Xín Mần", u"Yên Minh", u"Thành Phố Hà Giang" ], u"Hà Nam": [ u"Bình Lục", u"Duy Tiên", u"Kim Bảng", u"Lý Nhân", u"Thanh Liêm", u"Phủ Lý" ], u"Hà Tĩnh": [ u"Cẩm Xuyên", u"Can Lộc", u"Đức Thọ", u"Hương Khê", u"Hương Sơn", u"Kỳ Anh", u"Lộc Hà", u"Nghi Xuân", u"Thạch Hà", u"Vũ Quang", u"Hà Tĩnh", u"Thị xã Hồng Lĩnh" ], u"Hải Dương": [ u"Bình Giang", u"Cẩm Giàng", u"Gia Lộc", u"Kim Thành", u"Kinh Môn", u"Nam Sách", u"Ninh Giang", u"Thanh Hà", u"Thanh Miện", u"Tứ Kỳ", u"Hải Dương", u"Thị xã Chí Linh" ], u"Hậu Giang": [ u"Châu Thành", u"Châu Thành A", u"Long Mỹ", u"Phụng Hiệp", u"Vị Thủy", u"Thành Phố Vị Thanh", u"Thị xã Ngã Bảy" ], u"Hòa Bình": [ u"Cao Phong", u"Đà Bắc", u"Kim Bôi", u"Kỳ Sơn", u"Lạc Sơn", u"Lạc Thủy", u"Lương Sơn", u"Mai Châu", u"Tân Lạc", u"Yên Thủy", u"Hòa Bình" ], u"Hưng Yên": [ u"Ân Thi", u"Khoái Châu", u"Kim Động", u"Mỹ Hào", u"Phù Cừ", u"Tiên Lữ", u"Văn Giang", u"Văn Lâm", u"Yên Mỹ", u"Hưng Yên" ], u"Khánh Hòa": [ u"Cam Lâm", u"Diên Khánh", u"Khánh Sơn", u"Khánh Vĩnh", u"Ninh Hòa", u"Trường Sa", u"Vạn Ninh", u"Nha Trang", u"Thị xã Cam Ranh" ], u"Kiên Giang": [ u"An Biên", u"An Minh", u"Châu Thành", u"Giang Thành", u"Giồng Riềng", u"Gò Quao", u"Hòn Đất", u"Kiên Hải", u"Kiên Lương", u"Phú Quốc", u"Tân Hiệp", u"U Minh Thượng", u"Vĩnh Thuận", u"Rạch Giá", u"Thị xã Hà Tiên" ], u"Kon Tum": [ u"Đắk Glei", u"Đắk Hà", u"Đắk Tô", u"Kon Plông", u"Kon Rẫy", u"Ngọc Hồi", u"Sa Thầy", u"Tu Mơ Rông", u"Kon Tum" ], u"Lai Châu": [ u"Mường Tè", u"Phong Thổ", u"Sìn Hồ", u"Tam Đường", u"Tân Uyên", u"Than Uyên", u"Thị xã Lai Châu" ], u"Lâm Đồng": [ u"Bảo Lâm", u"Cát Tiên", u"Đạ Huoai", u"Đạ Tẻh", u"Đam Rông", u"Di Linh", u"Đơn Dương", u"Đức Trọng", u"Lạc Dương", u"Lâm Hà", u"Bảo Lộc", u"Đà Lạt" ], u"Lạng Sơn": [ u"Bắc Sơn", u"Bình Gia", u"Cao Lộc", u"Chi Lăng", u"Đình Lập", u"Hữu Lũng", u"Lộc Bình", u"Tràng Định", u"Văn Lãng", u"Văn Quan", u"Lạng Sơn" ], u"Lào Cai": [ u"Bắc Hà", u"Bảo Thắng", u"Bảo Yên", u"Bát Xát", u"Mường Khương", u"Sa Pa", u"Si Ma Cai", u"Văn Bàn", u"Lào Cai" ], u"Long An": [ u"Bến Lức", u"Cần Đước", u"Cần Giuộc", u"Châu Thành", u"Đức Hòa", u"Đức Huệ", u"Mộc Hóa", u"Tân Hưng", u"Tân Thạnh", u"Tân Trụ", u"Thạnh Hóa", u"Thủ Thừa", u"Vĩnh Hưng", u"Tân An" ], u"Nam Định": [ u"Giao Thủy", u"Hải Hậu", u"Mỹ Lộc", u"Nam Trực", u"Nghĩa Hưng", u"Trực Ninh", u"Vụ Bản", u"Xuân Trường", u"ý Yên", u"Nam Định" ], u"Nghệ An": [ u"Anh Sơn", u"Con Cuông", u"Diễn Châu", u"Đô Lương", u"Hưng Nguyên", u"Kỳ Sơn", u"Nam Đàn", u"Nghi Lộc", u"Nghĩa Đàn", u"Quế Phong", u"Quỳ Châu", u"Quỳ Hợp", u"Quỳnh Lưu", u"Tân Kỳ", u"Thanh Chương", u"Tương Dương", u"Yên Thành", u"Vinh", u"Thị xã Cửa Lò", u"Thị xã Thái Hòa" ], u"Ninh Bình": [ u"Gia Viễn", u"Hoa Lư", u"Kim Sơn", u"Nho Quan", u"Yên Khánh", u"Yên Mô", u"Ninh Bình", u"Thị xã Tam Điệp" ], u"Ninh Thuận": [ u"Huyên Bác ái", u"Ninh Hải", u"Ninh Phước", u"Ninh Sơn", u"Thuận Bắc", u"Thuận Nam", u"Phan Rang-Tháp Chàm" ], u"Phú Thọ": [ u"Cẩm Khê", u"Đoan Hùng", u"Hạ Hòa", u"Lâm Thao", u"Phù Ninh", u"Tam Nông", u"Tân Sơn", u"Thanh Ba", u"Thanh Sơn", u"Thanh Thủy", u"Yên Lập", u"Việt Trì", u"Thị xã Phú Thọ" ], u"Phú Yên": [ u"Đông Hòa", u"Đồng Xuân", u"Phú Hòa", u"Sơn Hòa", u"Sông Hinh", u"Tây Hòa", u"Tuy An", u"Tuy Hòa", u"Thị xã Sông Cầu" ], u"Quảng Bình": [ u"Bố Trạch", u"Lệ Thủy", u"MinhHoá", u"Quảng Ninh", u"Quảng Trạch", u"Tuyên Hoá", u"Đồng Hới" ], u"Quảng Nam": [ u"Bắc Trà My", u"Đại Lộc", u"Điện Bàn", u"Đông Giang", u"Duy Xuyên", u"Hiệp Đức", u"Nam Giang", u"Nam Trà My", u"Nông Sơn", u"Núi Thành", u"Phú Ninh", u"Phước Sơn", u"Quế Sơn", u"Tây Giang", u"Thăng Bình", u"Tiên Phước", u"Hội An", u"Tam Kỳ" ], u"Quảng Ngãi": [ u"Ba Tơ", u"Bình Sơn", u"Đức Phổ", u"Lý sơn", u"Minh Long", u"Mộ Đức", u"Nghĩa Hành", u"Sơn Hà", u"Sơn Tây", u"Sơn Tịnh", u"Tây Trà", u"Trà Bồng", u"Tư Nghĩa", u"Quảng Ngãi" ], u"Quảng Ninh": [ u"Ba Chẽ", u"Bình Liêu", u"Cô Tô", u"Đầm Hà", u"Đông Triều", u"Hải Hà", u"Hoành Bồ", u"Tiên Yên", u"Vân Đồn", u"Yên Hưng", u"Hạ Long", u"Móng Cái", u"Thị xã Cẩm Phả", u"Thị xã Uông Bí" ], u"Quảng Trị": [ u"Cam Lộ", u"Cồn Cỏ", u"Đa Krông", u"Gio Linh", u"Hải Lăng", u"Hướng Hóa", u"Triệu Phong", u"Vính Linh", u"Đông Hà", u"Thị xã Quảng Trị" ], u"Sóc Trăng": [ u"Châu Thành", u"Cù Lao Dung", u"Kế Sách", u"Long Phú", u"Mỹ Tú", u"Mỹ Xuyên", u"Ngã Năm", u"Thạnh Trị", u"Trần Đề", u"Vĩnh Châu", u"Sóc Trăng" ], u"Sơn La": [ u"Bắc Yên", u"Mai Sơn", u"Mộc Châu", u"Mường La", u"Phù Yên", u"Quỳnh Nhai", u"Sông Mã", u"Sốp Cộp", u"Thuận Châu", u"Yên Châu", u"Sơn La" ], u"Tây Ninh": [ u"Bến Cầu", u"Châu Thành", u"Dương Minh Châu", u"Gò Dầu", u"Hòa Thành", u"Tân Biên", u"Tân Châu", u"Trảng Bàng", u"Thị xã Tây Ninh" ], u"Thái Bình": [ u"Đông Hưng", u"Hưng Hà", u"Kiến Xương", u"Quỳnh Phụ", u"Thái Thụy", u"Tiền Hải", u"Vũ Thư", u"Thái Bình" ], u"Thái Nguyên": [ u"Đại Từ", u"Định Hóa", u"Đồng Hỷ", u"Phổ Yên", u"Phú Bình", u"Phú Lương", u"Võ Nhai", u"Thái Nguyên", u"Thị xã Sông Công" ], u"Thanh Hóa": [ u"Bá Thước", u"Cẩm Thủy", u"Đông Sơn", u"Hà Trung", u"Hậu Lộc", u"Hoằng Hóa", u"Lang Chánh", u"Mường Lát", u"Nga Sơn", u"Ngọc Lặc", u"Như Thanh", u"Như Xuân", u"Nông Cống", u"Quan Hóa", u"Quan Sơn", u"Quảng Xương", u"Thạch Thành", u"Thiệu Hóa", u"Thọ Xuân", u"Thường Xuân", u"Tĩnh Gia", u"Triệu Sơn", u"Vĩnh Lộc", u"Yên Định", u"Thanh Hóa", u"Thị xã Bỉm Sơn", u"Thị xã Sầm Sơn" ], u"Thừa Thiên Huế": [ u"A Lưới", u"Hương Trà", u"Nam Dông", u"Phong Điền", u"Phú Lộc", u"Phú Vang", u"Quảng Điền", u"Huế", u"thị xã Hương Thủy" ], u"Tiền Giang": [ u"Cái Bè", u"Cai Lậy", u"Châu Thành", u"Chợ Gạo", u"Gò Công Đông", u"Gò Công Tây", u"Tân Phú Đông", u"Tân Phước", u"Mỹ Tho", u"Thị xã Gò Công" ], u"Trà Vinh": [ u"Càng Long", u"Cầu Kè", u"Cầu Ngang", u"Châu Thành", u"Duyên Hải", u"Tiểu Cần", u"Trà Cú", u"Trà Vinh" ], u"Tuyên Quang": [ u"Chiêm Hóa", u"Hàm Yên", u"Na hang", u"Sơn Dương", u"Yên Sơn", u"Tuyên Quang" ], u"Vĩnh Long": [ u"Bình Minh", u"Bình Tân", u"Long Hồ", u"Mang Thít", u"Tam Bình", u"Trà Ôn", u"Vũng Liêm", u"Vĩnh Long" ], u"Vĩnh Phúc": [ u"Bình Xuyên", u"Lập Thạch", u"Sông Lô", u"Tam Đảo", u"Tam Dương", u"Vĩnh Tường", u"Yên Lạc", u"Vĩnh Yên", u"Thị xã Phúc Yên" ], u"Yên Bái": [ u"Lục Yên", u"Mù Cang Chải", u"Trạm Tấu", u"Trấn Yên", u"Văn Chấn", u"Văn Yên", u"Yên Bình", u"Yên Bái", u"Thị xã Nghĩa Lộ" ] } 
        result_province = None
        result_district = None

        for pro in province_list:
            if text.find(pro) > -1:
                result_province = pro
    
        if result_province != None:
            if not province_district_list[result_province]:
                return None
            else:
                districts = province_district_list[result_province]
                for dis in districts:
                    if text.find(dis) > -1:
                        result_district = dis 

        return result_province, result_district

    def parse_email_from_raw(self, text):
        if text == None:
            return None 
            
        email = None
        email_extract = re.search(r"mailto\:(.*)'", text)
        if email_extract.group(1):
            email = email_extract.group(1)
            email = h.unescape(email)

        return email

    def parse_real_image_url(self, text_list):
        url = []

        if not text_list:
            return []

        for text in text_list:
            url.append(text.replace('200x200', '745x510'))

        return url

    def parse_post_type(self, text):
        if text.find(u'thuê') > -1:
            return 'bds_hire'

        return 'bds_sale'

    def parse_post_cat(self, text):
        return text