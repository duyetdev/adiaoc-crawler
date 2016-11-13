# -*- coding: utf-8 -*-

t = """
<div class="left-detail">
                            <div id="LeftMainContent__productDetail_project" style="background: #ededed; padding-left: 10px;">
                                <div class="left">

                                </div>
                                <div class="right">
                                    
                                </div>
                                <div style="clear: both">
                                </div>
                            </div>
                            <div style="padding-left: 10px;">
                                <div class="left">
                                    Địa chỉ
                                </div>
                                <div class="right">
                                    Dự án Times City, Đường Minh Khai, Phường Vĩnh Tuy, Hai Bà Trưng, Hà Nội
                                </div>
                                <div style="clear: both">
                                </div>
                            </div>
                             <div style="padding-left: 10px;">
                                <div class="left">
                                    dcdc
                                </div>
                                <div class="right">
                                    Dự án Times City, Đường Minh Khai, Phường Vĩnh Tuy, Hai Bà Trưng, Hà Nội
                                </div>
                                <div style="clear: both">
                                </div>
                            </div>
                            <div style="background: #ededed; padding-left: 10px;">
                                <div class="left">
                                    Mã số
                                </div>
                                <div class="right">
                                    10791961
                                </div>
                                <div style="clear: both">
                                </div>
                            </div>
                            <div style="padding-left: 10px;">
                                <div class="left">
                                    Loại tin rao
                                </div>
                                <div class="right">
                                    Cho thuê căn hộ chung cư
                                </div>
                                <div style="clear: both">
                                </div>
                            </div>
                            <div style="background: #ededed; padding-left: 10px;">
                                <div class="left">
                                    Ngày đăng tin
                                </div>
                                <div class="right">
                                    11-11-2016
                                </div>
                                <div style="clear: both">
                                </div>
                            </div>
                            <div style="padding-left: 10px;">
                                <div class="left">
                                    Ngày hết hạn
                                </div>
                                <div class="right">
                                    21-11-2016
                                </div>
                                <div style="clear: both">
                                </div>
                            </div>
                            
                            <div id="LeftMainContent__productDetail_roomNumber" style="padding-left: 10px;">
                                <div class="left">
                                    Số phòng ngủ
                                </div>
                                <div class="right">
                                    1(phòng)
                                </div>
                                <div style="clear: both">
                                </div>
                            </div>
                            
                            
                            <div id="LeftMainContent__productDetail_toilet" style="background: #ededed; padding-left: 10px;">
                                <div class="left">
                                    Số toilet
                                </div>
                                <div class="right">
                                    1
                                </div>
                                <div style="clear: both">
                                </div>
                            </div>
                            <div id="LeftMainContent__productDetail_interior" style="padding-left: 10px;">
                                <div class="left">
                                    Nội thất
                                </div>
                                <div class="right">
                                    Full nội thất: Sàn gỗ, trần thạch cao, điều hòa, tủ âm tường...
                                </div>
                                <div style="clear: both">
                                </div>
                            </div>
                        </div>
"""


from scrapy import Selector
import urllib 

t = """
<div class="right">
                                <SCRIPT TYPE="text/javascript"><!--
document.write("<a rel='nofollow' href='mailto:&#112;&#104;&#111;&#110;&#103;&#105;&#97;&#110;&#103;&#49;&#51;&#49;&#52;&#64;&#103;&#109;&#97;&#105;&#108;&#46;&#99;&#111;&#109;'>&#112;&#104;&#111;&#110;&#103;&#105;&#97;&#110;&#103;&#49;&#51;&#49;&#52;&#64;&#103;&#109;&#97;&#105;&#108;&#46;&#99;&#111;&#109;</a>");
//--></script>
<NOSCRIPT><em>Địa chỉ email này được bảo vệ bởi JavaScript.<BR>Bạn cần kích hoạt Javascript để có thể xem.</em></NOSCRIPT>

                            </div>

"""
sel = Selector(text=t)

# address_str = u'Địa chỉ'
# print address_str

# # address_str = u'dcdc'

# print sel.xpath('//*[@class="left-detail"]/div[contains(., \''+ address_str +'\')]/div[2]//text()').extract()


# //*[@id="product-detail"]/div[8]/table/tbody/tr/td[1]/div/div[2]/div[2]/div[2]
# //*[@id="product-detail"]/div[8]/table/tbody/tr/td[1]/div/div[2]

email_data = sel.xpath('//*[@class="right"]/script//text()').extract_first()

from HTMLParser import HTMLParser
h = HTMLParser()

import re 

email_extract = re.search(r"mailto\:(.*)'", email_data)
if email_extract.group(1):
    email = email_extract.group(1)
    email = h.unescape(email)

print email