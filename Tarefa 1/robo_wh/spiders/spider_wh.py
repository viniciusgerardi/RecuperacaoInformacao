import scrapy
import os
import csv


class SpiderWhSpider(scrapy.Spider):
    name = 'spider_wh'

    # arquivo inicial
    start_urls = [
        'https://wow.gamepressure.com/quests.asp?TITLE=&MINLVL=0&MAXLVL=80&MAP=14&CATEGORY=0&FACTION=0']

    # Apaga o arquivo csv caso já exista um arquivo, para evitar sobreposição
    if os.path.exists("itens_wh.csv"):
        os.remove("itens_wh.csv")

    def parse(self, response):
        # Detecta a paginação do site
        pagination = response.xpath('//div[@align="right"]/a/text()').getall()
        if pagination != []:
            next_page = ''
            if len(pagination) == 2:
                next_page = response.xpath(
                    '//div[@align="right"]/a/@href')[1].get()
            elif pagination[0] == 'NEXT ':
                next_page = response.xpath(
                    '//div[@align="right"]/a/@href').get()
            if next_page != '':
                next_page = f"https://wow.gamepressure.com/quests.asp{next_page}"
                yield scrapy.Request(next_page, callback=self.parse)

        # identifica os links para as quests
        for i in response.css('tr.qt2').css('a::attr(href)').getall():
            if './quest.asp?' in i:
                link = i[2:]
                if link:
                    text_page = f"https://wow.gamepressure.com/{link}"
                    yield scrapy.Request(text_page, callback=self.parse)

        # processa os detalhes das quests
        name = response.xpath('//div[@class="tit1"]/text()').get()
        if name:
            level = response.xpath(
                '//td[@class="qt2"]//div//b[@class="yellow"]/text()').get()
            if level == ' - ':
                level = 0
            description = response.xpath(
                '//tr[@class="qt2"]//div[@style="margin-bottom:8px;margin-top:8px"]//b/text()').get()
            description = description.replace(';', ',')

            hint = response.xpath(
                '//tr[@class="qt2"]//div[@style="font-size:9pt;text-align:justify;line-height:11pt"]/text()').get()
            hint = hint.replace(';', ',')
            post = {
                'name': name,
                'level': level,
                'description': description,
                'hint': hint
            }

            # Salva os dados em csv
            with open('itens_wh.csv', 'a', newline='', encoding="utf-8") as output_file:
                dict_writer = csv.DictWriter(output_file, post.keys())
                dict_writer.writerows([post])
            yield post
