# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import mysql.connector

class BookscrapperPipeline:
    def process_item(self, item, spider):

        adapter =ItemAdapter(item)

        #Strip all whitespaces from strings
        field_names = adapter.field_names()
        for field_name in field_names:
            print(field_name)
            if field_name != 'description':
                value = adapter.get(field_name)                
                adapter[field_name] = value[0].strip()
        
        #Category and product type --> switch to lowercase
        lowercase_keys = ['category', 'product_type']
        for key in lowercase_keys:
            value = adapter.get(key)
            adapter[key] = value.lower()

        
        #convert price to float
        price_keys = ['tax','price_excl_tax', 'price_incl_tax',]
        for price_key in price_keys:
            value = adapter.get(price_key)
            value = value.replace('£', '')
            adapter[price_key] = float(value)


        # Availability, extract numberof books in stock
        str_value = adapter.get('availability')
        str_value_array =str_value.split('(')
        
        if len(str_value_array) < 2:
            adapter['availability'] = 0
        else:
            num_string = str_value_array[1]
            num_string_array = num_string.split()
            adapter['availability'] = int(num_string_array[0])

        #number of reviews string to integer
        value = adapter.get('no_of_reviews')
        adapter['no_of_reviews'] = int(value)

        # Extract star rating
        star_string = adapter.get('stars')
        star_list = star_string.split()
        star_text = star_list[1].lower()
        if star_text == 'zero':
            adapter['stars'] = 0
        elif star_text == 'one':
            adapter['stars'] = 1
        elif star_text == 'two':
            adapter['stars'] = 2
        elif star_text == 'three':
            adapter['stars'] = 3
        elif star_text == 'four':
            adapter['stars'] = 4
        elif star_text == 'five':
            adapter['stars'] = 5

        return item
    

class SaveToMySqlPipeline:

    def __init__(self):
        self.conn = mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            password = '$Oluwa4567',
            database = 'books'
        )

        self.curr = self.conn.cursor()
        self.curr.execute("""
            CREATE TABLE IF NOT EXISTS books(
                        id int NOT NULL auto_increment,
                        url VARCHAR(255),
                        title VARCHAR(255),
                        upc VARCHAR(255),
                        product_type VARCHAR(255),
                        price_excl_tax DECIMAL,
                        price_incl_tax DECIMAL,
                        tax DECIMAL,
                        availability INTEGER,
                        no_of_reviews INTEGER,
                        stars INTEGER,
                        category VARCHAR(255),
                        description text,
                        PRIMARY KEY (id)
            )""")
    
    def process_item(self ,item ,spider):
        self.curr.execute("""
            insert into books(
                        url,
                        title,
                        upc,
                        product_type,
                        price_excl_tax,
                        price_incl_tax,
                        tax,
                        availability,
                        no_of_reviews,
                        stars,
                        category,
                        description
            ) values(
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
            )""", (
            item["url"],
            item["title"],
            item["upc"],
            item["product_type"],
            item["price_excl_tax"],
            item["price_incl_tax"],
            item["tax"],
            item["availability"],
            item["no_of_reviews"],
            item["stars"],
            item["category"],
            str(item["description"][0])
            )
        )
        
        self.conn.commit()
        return item
    
    def close_spider(self, spider):
        self.curr.close()
        self.conn.close()
    