import scrapy
from basic_scrapy_spider.items import QuoteItem
from scrapy_playwright.page import PageMethod
import re
from urllib.parse import urlparse, parse_qs
from scrapy.exceptions import CloseSpider


def abort_req(request):
    if request.resource_type == 'image':
         return True
    else:
         return False
     

class QuotesSpider(scrapy.Spider):
    name = 'dnb'
    # allowed_domains = ['quotes.toscrape.com']
    # start_urls = ['https://www.dnb.com/business-directory/company-information.residential_building_construction.us.html']ççç

    custom_settings = {
         "PLAYWRIGHT_ABORT_REQUEST" : abort_req
    }

    def start_requests(self):

        # for i in range(1,3):
            # i=1
            start_url = "https://www.dnb.com/business-directory/company-information.residential_building_construction.us.florida.palm_beach_gardens.html"
            yield scrapy.Request(url=start_url, meta=dict(
                playwright = True,
                # page_number = i,
                # name = name,
                playwright_include_page = True,
                playwright_page_methods = [
                    PageMethod("wait_for_timeout", 15000),
                    
                    # PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight);")
                    PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight);")
                ]

            ), callback=self.iterate_business)

    async def iterate_business(self, response):

        page = response.meta["playwright_page"]
        await page.close()

        # print(response.css(".data"))
        companies = response.css(".data")
        # bus_urls = response.css(".data > div > a ::attr(href)").getall()
        response.css("#companyResults a")
        print("##########################    Company Results #####################################")
        # print(len(compres))
        # print(companies)

        # page_number = response.meta["page_number"]

        
        # print(next_url)

        page_url = response.url
        parsed_url = urlparse(page_url)
        query_params = parse_qs(parsed_url.query)
        page_number = query_params.get('page', [''])[0]

        for i, comp in enumerate(companies):

            bus_url = comp.css("div > a ::attr(href)").get()
            # print(bus_url)
            revenue_text = comp.css('.col-md-2.last').extract()
            revenue_html = revenue_text[0]
            revenue_value = revenue_html.split("$")[-1].strip().rstrip("</div>")

            location_html = comp.css("div.col-md-4").extract_first()
            location = "".join(comp.css("div.col-md-4 *::text").getall()).strip()

            business_url = "https://www.dnb.com" + bus_url
            print("location")
            print(location)


            if comp == companies[3]:
                break

            # # print(revenue_value)

            # if i < 44:
            #     pass


            
            
            yield scrapy.Request(url=business_url, meta=dict(
                playwright = True,
                page_number = page_number,
                revenue_text = revenue_value,
                location = location,
                playwright_include_page = True,


                playwright_page_methods = [
                     

                     PageMethod('wait_for_selector', 'div#company_profile_snapshot'),
                    # PageMethod("wait_for_timeout", 16000),

                    # PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight);")
                    # PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight);")
                ]

            ), callback=self.parse)



        next_url = response.css("li.page.current + li > a::attr(href)").get()

        print("NNNNEEEEEXTTTTTT URRRRLLL")
        print(next_url)
        if next_url is not None:
            # if next_url  == "https://www.dnb.com/business-directory/company-information.residential_building_construction.us.florida.miami.html?page=5":
            #     self.logger.info("Stopping spider because next_url is equal to SPECIFIC_URL_TO_STOP_AT")
            #     raise CloseSpider(reason='Specific URL reached')
            
            # else:
                 
            yield scrapy.Request(url=next_url, meta=dict(
                playwright = True,
                        # name = name,
                playwright_include_page = True,
                playwright_page_methods = [
                PageMethod("wait_for_timeout", 15000),
                # PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight);")
                PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight);")
                ]

                ), callback=self.iterate_business)
         
    async def parse(seld, response):

        page = response.meta["playwright_page"]
       
        await page.close()

        
        

        # print("pageeee URLLLLLLLLL")

        # # print(page_url)

        # print(page_number)

        revenue_text = response.meta.get("revenue_text")
        page_number = response.meta.get("page_number")
        location = response.meta.get("location")
        address_text = ""
        address_text = response.css('span.company_data_point[name="company_address"] > span > a.ext-icon::text').get()
        if address_text is None:
             address_text = response.css('span.company_data_point[name="company_address"] > span::text').get()
             

        company_name = response.css(".company-profile-header-title::text").get()
        address_text = address_text
        revenue_text = revenue_text
        website_url = response.css('span.company_data_point[name="company_website"] > span.company_profile_overview_underline_links > a::attr(href)').get()
        # .company-profile-overview-icon-address+ .col-md-11 .ext-icon


        yield {
           'Name' :  company_name,
           "Address"  : address_text,
           'location' : location,
           'Revenue' : revenue_text,
           'Website Url' : website_url,
           'Page Number' : page_number
        }
