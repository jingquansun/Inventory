from collections import OrderedDict
import datetime
import os
import csv
import sys
from decimal import Decimal

from peewee import *

db = SqliteDatabase('inventory.db')

class Product(Model):
    product_id = AutoField()
    product_name = CharField(unique=True)
    product_quantity = IntegerField(default=0)
    product_price = IntegerField(default=0)
    date_updated = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db

def initialize():
    db.connect()
    db.create_tables([Product], safe=True)

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def add_csv():
    with open('inventory.csv', newline='') as file:
        reader = csv.DictReader(file, delimiter=',')
        rows = list(reader)
        for row in rows:
            try:
                Product.create(product_name=row['product_name'],
                               product_quantity=int(row['product_quantity']),
                               product_price=int(round(float(row['product_price'].replace('$', '')) * 100)),
                               date_updated=datetime.datetime.strptime(row['date_updated'], '%m/%d/%Y')
                               )
            except IntegrityError:
                item = Product.get(product_name=row['product_name'])
                item.product_quantity = int(row['product_quantity'])
                item.product_price = int(round(float(row['product_price'].replace('$', '')) * 100))
                item.date_updated = datetime.datetime.strptime(row['date_updated'], '%m/%d/%Y')
                item.save()

def display(product):
    price = str(product.product_price)
    if len(price) < 3:
        price = "0" + price
    price = price[:-2] + "." + price[-2:]
    print("\n" + product.product_name)
    print("-"*len(product.product_name))
    print("Price: ${}".format(price))
    print("Quantity: {}".format(product.product_quantity))
    print("Last updated: {}".format(product.date_updated.date().strftime('%m/%d/%Y')))

def view_product():
    """View details of a single product."""
    while True:
        try:
            id = input("Enter the ID of the item you would like to view: ")
            product = Product.get(Product.product_id == id)
            display(product)
        except DoesNotExist:
            print("This product does not exist, please enter a valid ID")
            view_product()
        again = input("\n\nWould you like to view another product? [Yes/No]:  \n")
        if again.lower() != 'no':
            view_product()
        else:
            break
        clear()

def add_product():
    """Add a new product."""
    try:
        name = input("Please enter the name of the product:  ")
        price =  input("Please enter the price of the product:  ")
        quantity = input("Please enter the quantity of the product:  ")
        Decimal(price).quantize(Decimal('1.00'))
        int(quantity)
        if not name.isalpha():
            raise TypeError
    except TypeError:
        print("This is not a valid entry, please try again.")
    print("The product information you have entered is:\n")
    print(f"\nProduct name: {name}\nProduct price: ${price}\nProduct quantity: {quantity}\n")
    confirm = input("Are you sure you would like to add this product (Yes/No):   ")
    if confirm.lower() != "no":
        try:
            Product.create(
                product_name = name,
                product_price = price,
                product_quantity = quantity
            )
            print("Product is added into inventory!")
        except IntegrityError:
            last_update = Product.select().where(Product.product_name == name).get().date_updated
            current = datetime.datetime.now()
            if last_update <= current:
                record = Product.select().where(Product.product_name == name).get()
                record.product_price = price
                record.product_quantity = quantity
                record.date_updated = datetime.datetime.now()
                record.save()
                print("\nThis product has been updated.")


def save_inventory():
    """Make a backup of the entire contents."""
    with open("backup.csv", "w", newline=" ") as file:
        writer = csv.writer(file)
        products = Product.select(
            Product.product_name,
            Product.product_price,
            Product.product_quantity,
            Product.date_update
        )
        writer.writerow(products.keys())
        writer.writerows(products.tuples())
        print("\nInventory is successfully backed up!\n")

def menu_loop():
    choice = None
    while choice != "q":
        clear()
        print("Enter 'q' to quit.\n")
        for key, value in menu.item():
            print("{}) {}".format(key, value.__doc__))
        try:
            choice = input("\nAction: ").lower().strip()
            if choice.lower() != "q":
                clear()
                raise ValueError("Please choose a valid option")
            elif choice in menu:
                menu[choice]()
        except ValueError:
            print("\nPlease choose a valid option, or enter 'q' to quit.")

menu = OrderedDict([
    ("v", view_product),
    ("a", add_product),
    ("b", save_inventory),
])

if __name__ == "__main__":
    initialize()
    add_csv()
    menu()