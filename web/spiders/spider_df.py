from datetime import datetime
import locale

import io

import rows
import scrapy
import re

from .base import BaseCovid19Spider

class Covid19DFSpider(BaseCovid19Spider):
    name = "DF"
    start_urls = ["http://www.saude.df.gov.br/boletinsinformativos-divep-cieves/"]
    
    def parse_pdf(self, response):
        table = rows.import_from_pdf(
            io.BytesIO(response.body),
            page_numbers=[1],
            starts_after='Óbitos',
            ends_before=re.compile(r'^Fonte'),
            force_types={'n': rows.fields.TextField}
        )
        
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        
        # Brasília
        brasilia = [row for row in table if row.uf=='DISTRITO FEDERAL'][0]
        self.add_city_case(
            city = "Brasília",
            # city_ibge_code = 5300108,
            confirmed = locale.atoi(brasilia.n),
            # date = date,
            deaths = brasilia.field_4,
        )
        
        # Importados/indefinidos
        importados_indefinidos = [
            row for row in table if \
                row.uf!='DISTRITO FEDERAL' and
                row.uf!='TOTAL'
        ]
        self.add_city_case(
            city = "Importados/Indefinidos",
            # city_ibge_code = None,
            confirmed = sum(
                locale.atoi(row.n) for row in importados_indefinidos
            ),
            # date = date,
            deaths = sum(row.field_4 for row in importados_indefinidos),
        )
        
        # Total
        total = [row for row in table if row.uf=='TOTAL'][0]
        self.add_state_case(
            confirmed = locale.atoi(total.n),
            # date = date,
            deaths = total.field_4,
        )
    
    def parse(self, response):
        title = response.xpath(
            "//div[@id='conteudo']//a//text()"
        ).extract_first()
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        date = datetime.strptime(title.split()[-1],'%d%b%y')
        
        pdf_url = response.xpath(
            "//div[@id='conteudo']//a/@href"
        ).extract_first()
        self.add_report(date=date, url=pdf_url)
        
        return scrapy.Request(pdf_url, callback=self.parse_pdf)
    
