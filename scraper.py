from operator import le
from numpy import product
import pandas as pd
import csv
import config
import requests
import json
from concurrent.futures import ThreadPoolExecutor


def is_empty(line):
    return len(line.strip()) == 0


def check_format():

    missings = {
        "Sheet": [],
        "Men": [],
        "Women": [],
        "Youth": []
    }

    try:
        df = pd.read_excel(config.INPUT_EXCEL_SHEET_PATH, sheet_name=config.SHEET_NAMES)
    except ValueError as e:
    	# missing sheet
        e = str(e).split(" ")[2:-2]
        e = " ".join(word for word in e).replace("'", "")
        missings["Sheet"].append(e)
        return missings

    for sheet_name in config.SHEET_NAMES:
    	# replacing none value
        df[sheet_name].replace("", float("NaN"), inplace=True)
        # selecting all rows with valid Style #'
        df[sheet_name].dropna(subset=["Style #"], inplace=True)
        # get sheet keys
        excel_sheet_column_names = df[sheet_name].keys()
        # validate keys
        for name in config.EXCEL_SHEET_COLUMN_NAMES[sheet_name]:
            if name not in excel_sheet_column_names:
                missings[sheet_name].append(name)

    return missings


class Scraper:

    MAX_WORKERS = 4

    def __init__(self):

        self.excel_sheet_data = self.import_excel_as_dict()

        self.csv_file = open(config.PROGRESS_FILE_PATH, 'w')
        self.writer = csv.DictWriter(self.csv_file, fieldnames=config.CSV_HEADERS)
        self.writer.writeheader()

        self.invalid_products = []

        self.reformat_excel_sheet_data()

    def import_excel_as_dict(self):

        excel_data = {}

        df = pd.read_excel(config.INPUT_EXCEL_SHEET_PATH, sheet_name=config.SHEET_NAMES)

        for sheet_name in config.SHEET_NAMES:
        	# replacing none value
            df[sheet_name].replace("", float("NaN"), inplace=True)
            # selecting all rows with valid Style #'
            df[sheet_name].dropna(subset=["Style #"], inplace=True)

            excel_data[sheet_name] = df[sheet_name].to_dict('records')

        return excel_data

    def reformat_excel_sheet_data(self):
        """Reformat imported excel data"""
        products = {}

        for sheet in config.SHEET_NAMES:

            for product in self.excel_sheet_data[sheet]:

                style_code = str(product["Style #"])
                size_name = f"{sheet} " + str(product[f"Size - {sheet}"])

                # if product doesn't already exist
                if style_code not in products.keys():

                    products[style_code] = {
                        "Style #": style_code,
                        "Product": product["Product"],
                        "Size": {
                            size_name: int(product["Quantity"])
                        },
                        "Price": product["Price"]
                    }
                # if exists
                else:
                    if size_name not in products[style_code]["Size"].keys():
                        products[style_code]["Size"][size_name] = int(product["Quantity"])
                
            self.excel_sheet_data[sheet] = None

        self.excel_sheet_data = products

    def scrap_sheet(self):

        with ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            for product in self.excel_sheet_data:
                executor.submit(self.create_product, self.excel_sheet_data[product])
        print("Sssss")

        self.csv_file.close()

        with open(config.PROGRESS_FILE_PATH, 'r') as p, open(config.OUTPUT_FILE_PATH, 'w') as o:
            # read content from first file
            for line in p:
                # append content to second file
                if not is_empty(line):
                    o.write(line)

        with open(config.PROGRESS_FILE_PATH, 'w') as p:
            p.write("")

    def write_line_to_csv(self, line):
        self.writer.writerow(line)

    def create_product(self, product):
        
        scraped_data = self.scrap_product(product["Style #"])

        if not scraped_data:
            self.invalid_products.append({
                "id": product["Style #"],
                "name": product["Product"]
            })
            return

        sizes = product["Size"]
        first_size = list(sizes.keys())[0]

        self.write_line_to_csv({
            "Handle": scraped_data["product"]["_doc"]["urlKey"],
            "Title": product["Product"],
            "Body (HTML)": scraped_data["product"]["_doc"]["description"],
            "Vendor": str(scraped_data["product"]["_doc"]["brand"]).capitalize(),
            "Standard Product Type": "",
            "Custom Product Type": "Shoes",
            "Tags": "",
            "Published": "FALSE",
            "Option1 Name": "Size",
            "Option1 Value": first_size,
            "Option2 Name": "",
            "Option3 Name": "",
            "Option3 Value": "",
            "Variant SKU": "",
            "Variant Grams": "0",
            "Variant Inventory Tracker": "shopify",
            "Variant Inventory Qty": sizes[first_size],
            "Variant Inventory Policy": "deny",
            "Variant Fulfillment Service": "manual",
            "Variant Price": product["Price"],
            "Variant Compare At Price": "",
            "Variant Requires Shipping": "TRUE",
            "Variant Taxable": "TRUE",
            "Variant Barcode": "",
            "Image Src": scraped_data["product"]["_doc"]["thumbnail"],
            "Image Position": "",
            "Image Alt Text": "1",
            "Gift Card": "",
            "SEO Title": scraped_data["product"]["_doc"]["shoeName"],
            "SEO Description": "",
            "Google Shopping / Google Product Category": "",
            "Google Shopping / Gender": "",
            "Google Shopping / Age Group": "",
            "Google Shopping / MPN": "",
            "Google Shopping / AdWords Grouping": "",
            "Google Shopping / AdWords Labels": "",
            "Google Shopping / Condition": "",
            "Google Shopping / Custom Product": "",
            "Google Shopping / Custom Label 0": "",
            "Google Shopping / Custom Label 1": "",
            "Google Shopping / Custom Label 2": "",
            "Google Shopping / Custom Label 3": "",
            "Google Shopping / Custom Label 4": "",
            "Variant Image": "",
            "Variant Weight Unit": "",
            "Variant Tax Code": "lb",
            "Cost per item": "",
            "Status": "active"
        })

        # write images
        for image in scraped_data["prices"]["_doc"]["imageLinks"]:
            self.write_line_to_csv({
                "Handle": scraped_data["product"]["_doc"]["urlKey"],
                "Image Src": image
            })

        # write size options
        for size in sizes:
            if size == first_size:
                continue
            self.write_line_to_csv({
                "Handle": scraped_data["product"]["_doc"]["urlKey"],
                "Option1 Value": size,
                "Variant Grams": 0,
                "Variant Inventory Tracker": "shopify",
                "Variant Inventory Qty": sizes[size],
                "Variant Inventory Policy": "deny",
                "Variant Fulfillment Service": "manual",
                "Variant Price": product["Price"],
                "Variant Compare At Price": "",
                "Variant Requires Shipping": "TRUE",
                "Variant Taxable": "TRUE"
            })

    def scrap_product(self, product_id):

        try:
            r = requests.get(config.SCRAPER_ENDPOINT + str(product_id), timeout=10)
            try:
                json_response = json.loads(r.text)
                print(product_id)
                return json_response
            except:
                return False
        except Exception:
            return False

    def get_invalid_products(self):
        return self.invalid_products
