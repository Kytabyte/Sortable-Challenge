# Sortable-Challenge
This is the repo for Sortable-Challenge, where we aim to matching the the listing title from third-party retailer to the original product item.

Detailed information about how I played around the data can be found in <code>Sortable-Challenge.ipynb</code>

# Usage
* Clone this repository
* Run <code>./matching.py</code>, and <code>results.txt</code> will appear in the same directory.

# Method

## 1. Extract Manufacturer

By observing the listings data <code>listings.txt</code>, we found out that most of the manufacturer information appeared in the first word of the title. Through checking the first word, we found that only around 3700 out of 20000 pieces of listings are not representing the manufacturer in <code>products.txt</code>. Therefore, for efficiency, we can extract the first word of each listings can match the manufacturer of the listings, such that we can save time from unnecessary matching work.

### 1.1 Data Structure used for storing product data <code>products.txt</code> in Python

Since I first extract the manufacturer information from the listings and comparing the model/family in the next step, a dict was used, associated manufacturers as key, and a tuple of (family, model, product_name) as values. The reason I add product_name in the tuple is that the <code>results.txt</code> is a dict of product_name and Array of listings. Storing the product_name can simply find the correspodent item in results in constant time.

### 1.2 Skipped manufacturer

Through observing the first word of listings, we can see that there are a lot of manufacturers which are not contained in <code>products.txt</code>. For saving time, we can simply ignore them. They are {'fototasche','polaroid','easypix','vivitar','rollei','ge','duragadget'}.

## 2. Cut Title of each listing

## 3. Check if exists any family and model matches the listing
