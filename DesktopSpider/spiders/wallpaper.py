# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest

from DesktopSpider.items import DesktopspiderItem

import re


class WallpaperSpider(scrapy.Spider):
    name = 'wallpaper'
    allowed_domains = ['bing.ioliu.cn']
    start_urls = ['http://bing.ioliu.cn/']
    web_site_header = 'http://bing.ioliu.cn'
    splash_args = {"lua_source": """
                                --splash.response_body_enabled = true
                                splash.private_mode_enabled = false
                                splash:set_user_agent("Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36")
                                splash:wait(3)
                                return {html = splash:html()}
                                """,
                   "wait": 3.0}

    def parse(self, response):
        next_page = response.xpath("//div[@class='page']/a[2]/@href").extract()[0]
        photo_xpath = "/html/body/div[@class='container']/div[@class='item']/div[@class='card progressive']/a[@class='mark']/@href"
        photo_urls = response.xpath(photo_xpath).extract()
        photo_urls = ["{:s}{:s}".format(self.web_site_header, url) for url in photo_urls]
        for photo_url in photo_urls:
            yield SplashRequest(photo_url, self.parse_photo_page, args=self.splash_args)

        next_page = "{:s}{:s}".format(self.web_site_header, next_page)
        if next_page != self.web_site_header:
            yield SplashRequest(url=next_page, callback=self.parse, args=self.splash_args)

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, args=self.splash_args)

    def parse_photo_page(self, response):
        photo_url = response.xpath("/html/body/div[@class='preview']/div[@class='mark']/@style").extract()[0]
        pattern = re.compile(r"(?<=url\().*?(?=\)\s?;)")
        all = pattern.findall(photo_url)
        all[0] = all[0].replace("640x360", "1920x1080")
        item = DesktopspiderItem()
        item["image_urls"] = all
        return item
