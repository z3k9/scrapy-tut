# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class BookscrapperPipeline:
    def process_item(self, item, spider):

        adapter =ItemAdapter(item)

        #Strip all whitespaces from strings
        field_names = adapter.field_names()
        print(field_names)
        for field_name in field_names:
            print(field_name)
            if field_name != 'description':
                value = adapter.get(field_name)
                print('#######################')
                print('#######################')
                print('#######################')
                print(value)
                
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
            print('#######################')
            print('#######################')
            print('#######################')
            print(value)
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
    

