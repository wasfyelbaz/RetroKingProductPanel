import os

INPUT_EXCEL_SHEET_PATH = "files/input.xlsx"
PROGRESS_FILE_PATH = "files/progress.csv"
OUTPUT_FILE_PATH = "files/output.csv"

SHEET_NAMES = ["Men", "Women", "Youth"]

EXCEL_SHEET_COLUMN_NAMES = {
	"Men": ["Product", "Size - Men", "Price", "Style #", "Quantity"],
    "Women": ["Product", "Size - Women", "Price", "Style #", "Quantity"],
    "Youth": ["Product", "Size - Youth", "Price", "Style #", "Quantity"]
}

CSV_HEADERS = [
    "Handle", "Title", "Body (HTML)", "Vendor", "Standard Product Type", "Custom Product Type", "Tags",
    "Published", "Option1 Name", "Option1 Value", "Option2 Name", "Option2 Value",
    "Option3 Name", "Option3 Value", "Variant SKU", "Variant Grams", "Variant Inventory Tracker",
    "Variant Inventory Qty", "Variant Inventory Policy", "Variant Fulfillment Service", "Variant Price",
    "Variant Compare At Price", "Variant Requires Shipping", "Variant Taxable", "Variant Barcode",
    "Image Src", "Image Position", "Image Alt Text", "Gift Card", "SEO Title", "SEO Description",
    "Google Shopping / Google Product Category", "Google Shopping / Gender", "Google Shopping / Age Group",
    "Google Shopping / MPN", "Google Shopping / AdWords Grouping", "Google Shopping / AdWords Labels",
    "Google Shopping / Condition", "Google Shopping / Custom Product", "Google Shopping / Custom Label 0",
    "Google Shopping / Custom Label 1", "Google Shopping / Custom Label 2",
    "Google Shopping / Custom Label 3", "Google Shopping / Custom Label 4", "Variant Image",
    "Variant Weight Unit", "Variant Tax Code", "Cost per item", "Status"
]

SCRAPER_ENDPOINT = os.getenv("SCRAPER_ENDPOINT")

INVALID_PRODUCT_JSON_FILE_PATH = "files/invalid_products.json"
