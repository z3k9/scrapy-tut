import scrapy
from bookscrapper.items import BookItem 


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response):
        books = response.css('article.product_pod')

        for book in books:
            book_page_url = book.css('h3 a').attrib['href']

            if 'catalogue/' in book_page_url:
                book_page = 'https://books.toscrape.com' + book_page_url
            else:
                book_page = 'https://books.toscrape.com/catalogue/' + book_page_url

            yield response.follow(book_page, callback=self.parse_book_page)
        
        next_page = response.css('.next a').attrib['href']

        if next_page is not None:
            if 'catalogue/' in next_page:
                next_page_url = 'https://books.toscrape.com/' + next_page
            else:
                next_page_url = 'https://books.toscrape.com/catalogue/' + next_page

            yield response.follow(next_page_url, callback= self.parse)

    def parse_book_page(self, response):
        table_rows = response.css('table tr')
        book_item = BookItem()
        
        book_item['url'] = response.url,
        book_item['title'] = response.css('.product_main h1::text').get(),
        book_item['upc'] = table_rows[0].css('td ::text').get(),
        book_item['product_type'] = table_rows[1].css('td ::text').get(),
        book_item['price_excl_tax'] = table_rows[2].css('td ::text').get(),
        book_item['price_incl_tax'] = table_rows[3].css('td ::text').get(),
        book_item['tax'] = table_rows[4].css('td ::text').get(),
        book_item['availability'] = table_rows[5].css('td ::text').get(),
        book_item['no_of_reviews'] = table_rows[6].css('td ::text').get(),
        book_item['stars'] = response.css('.star-rating').attrib['class'],
        book_item['category'] = response.xpath('/html/body/div[1]/div/ul/li[3]/a/text()').get(),
        book_item['description'] =response.xpath("/html/body/div[1]/div/div[2]/div[2]/article/p/text()").get(),
       

        yield book_item
        