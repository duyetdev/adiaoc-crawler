# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BatdongsanItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    desc = scrapy.Field()
    area = scrapy.Field() # Diện tích
    price = scrapy.Field()
    unit = scrapy.Field()
    property_type = scrapy.Field() # loai bat dong san
    provincial_city = scrapy.Field() # Tinh, City
    district = scrapy.Field() # Quan, huyen
    address = scrapy.Field() # Address
    post_type = scrapy.Field() 
    project = scrapy.Field() 
    end_date = scrapy.Field() 
    images = scrapy.Field() 
    youtube_url = scrapy.Field() 
    phone = scrapy.Field() 
    email = scrapy.Field() 
    contact_name = scrapy.Field() 

    last_updated = scrapy.Field(serializer=str)
