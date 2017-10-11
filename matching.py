#!/usr/bin/env python3

import json
import re


PRODUCTS_PATH = 'products.txt'
LISTINGS_PATH = 'listings.txt'


SKIP_MANUFACTURER = {'fototasche','polaroid','easypix','vivitar','rollei','ge','duragadget'}
SKIP_PATTERN = {' for ', 'pour', ' with ', ' w/ ', ' + ', ' & '}
MODEL_FORMAT = [r'(?<=[a-z])(?=\d+)', r'(?<=[a-z]) (?=\d+)', r'(?<=[a-z])-(?=\d+)']
REPLACE_FORMAT = ['',' ','-']

class Match(object):
	"""
		Attribute:
		@ products: 
			a dict with a form of product_manufacturer : (product_family, product_model, product_name)
		@ listings:
			a list of dict, each entry is a pure json format with attribute 'title', 'model', 'currency', and 'price'
		@ result:
			a dict with a format of product_name : Array[listings]
	"""
	def __init__(self, products_path, listings_path):
		self.products, self.result = self.read_products(products_path)
		self.listings = self.read_listings(listings_path)


	'''
		read_products(self, prod_path) reads the products path and return both structured product dict and result dict
	'''
	def read_products(self, prod_path):
		products = {}
		result = {}

		with open('products.txt') as f:
		    lines = f.readlines()
		    for line in lines:
		    	prod = json.loads(line)

		    	# initialize result dict
		    	result[prod['product_name']] = [] 

		    	# initialize products dict
		    	manufacturer = prod['manufacturer'].lower()
		    	if manufacturer not in products:
		    		products[manufacturer] = []
		    	products[manufacturer].append((prod['family'].lower() if 'family' in prod else '', \
		    		prod['model'].lower(), \
		    		prod['product_name']))
		        

		return products, result

	'''
		read_listings(self, list_path) takes the listings path and return a list of listings in original json format
	'''
	def read_listings(self, list_path):
		listings = []

		with open('listings.txt') as f:
		    lines = f.readlines()
		    for line in lines:
		        listings.append(json.loads(line))

		return listings

	'''
		get_models(self, listing) takes one listing of self.listings, find the first non-number word, take it 
			as the manufacturer, and find the corresponding family and model list to this manufacturer
		Input:
			@ listing: 
				an entry of self.listings
		Output:
			The tuple (product_family, product_model, product_name) corresponding to manufacturer 
				or None if the first word is in the SKIP_MANUFACTURER set
				or [] if the above two options are both not satisfied
	'''
	def get_models(self, listing):
		pattern = r'\b[^\d^\s^\W]+\b'
		try:
			first_word = re.search(pattern, listing['title']).group(0).lower()
		except Exception as e:
			first_word = ''

		# Some special cases
		if first_word == 'fuji': first_word = 'fujifilm'
		elif first_word == 'afgaphoto': first_word = 'afga'
		elif first_word == 'konica' or first_word == 'minolta': first_word = 'konica minolta' 


		# 
		if first_word in self.products:
			return self.products[first_word]
		elif first_word in SKIP_MANUFACTURER:
			return None
		else:
			model = listing['manufacturer'].lower()
			if model in self.products:
				return self.products[model]
			else:
				return []

	# def score(self, tokenized_title, model):
	# 	s = 0
	# 	for keyword in model[0]:
	# 		if keyword in tokenized_title:
	# 			s += 1
	# 		elif '-' in keyword:
	# 			sub_score = 0
	# 			sub_word = keyword.split('-')
	# 			for sub_kwd in sub_word:
	# 				if sub_kwd in tokenized_title:
	# 					sub_score += (1/len(sub_word))

	# 			keyword.replace('-','')
	# 			if keyword in tokenized_title:
	# 				s += 1
	# 			else:
	# 				s += sub_score

	# 	return s / len(model) * 2

	def generate_model_format(self, model):
		generated_model = []
		pattern_index = -1

		for i in range(len(MODEL_FORMAT)):
			if len(re.findall(MODEL_FORMAT[i], model)) > 0:
				pattern_index = i

		if pattern_index != -1:
			for i in range(len(REPLACE_FORMAT)):
				if i != pattern_index:
					generated_model.append(re.sub(MODEL_FORMAT[pattern_index], REPLACE_FORMAT[i], model))
		return generated_model
		

	'''
		cutoff(self, title) takes the title of one listing in self.listings, 
			and remove all contents after the patterns in SKIP_PATTERN
		Input:
			@ title: a string which is a description of a listing
		Output:
			@ roi: the region of interest after cutting all unwanted contents
	'''
	def cutoff(self, title):
		roi = title.lower()
		for word in SKIP_PATTERN:
			idx = roi.find(word)
			if idx != -1:
				roi = roi[:idx]

		# split_pattern = r'[\w-]+'

		# return set(re.findall(split_pattern, roi))
		return roi


		
	'''
		model_match(self, listing, model_list) match the model of the listing, 
			according if the contents of the listing contains the model and family keyword
		Input:
			@ listing: an entry of self.listings
			@ model_list: a list of (family, model) tuples from a single manufacturer
		Output:
			None
		Side effect:
			If there is a match, add the listing to the dict self.result, under the key of 
				this product's name
	'''
	def model_match(self, listing, model_list):
		# Step 2.1 cut off the title and get our region of interest
		cut_title = self.cutoff(listing['title'])

		# Step 2.2 model matching
		for i in range(len(model_list)):
			if (' ' + model_list[i][1] + ' ') in cut_title:
				self.result[model_list[i][2]].append(str(listing))
				return
			if model_list[i][0] != '' and (' ' + model_list[i][0] + ' ') in cut_title:
				generated_model = self.generate_model_format(model_list[i][1])
				for model in generated_model:
					if (' ' + model + ' ') in cut_title:
						self.result[model_list[i][2]].append(listing)
						return

	'''
		dict_match(self, listing, model_list) the listing by comparing the contents of 
			the listing to ALL given products
		Input:
			@ listing: an entry of self.listings
		Output:
			None
		Side effect:
			If there is a match, add the listing to the dict self.result, under the key of 
				this product's name
	'''
	def dict_match(self, listing):
		# Step 2.1 cut off the title and get our region of interest
		cut_title = self.cutoff(listing['title'])

		for manufacturer in self.products:
			if (' ' + manufacturer + ' ') in cut_title:
				self.model_match(listing, self.products[manufacturer])
				return

		for manufacturer in self.products:
			model_list = self.products[manufacturer]
			for model in model_list:
				if model[0] != '' and (' ' + model[0] + ' ') in cut_title:
					if (' ' + model[1] + ' ') in cut_title:
						self.result[model[2]].append(str(listing))
						return
					generated_model = self.generate_model_format(model[1])
					for gen_model in generated_model:
						if (' ' + gen_model + ' ') in cut_title:
							self.result[model[2]].append(str(listing))
							return

	'''
		match(self) is the main method in class Match, which orderly executes the above 
			methods to match listings to products
	'''
	def match(self):
		for listing in self.listings:
			# Step 1: Identify manufacturer and return all (family, model) tuples made from this manufacturer
			model = self.get_models(listing)

			# Step 2: match the model
			if model == None:
				continue
			 
			if len(model) == 0:
				self.dict_match(listing)
			else:
				self.model_match(listing, model)


def main():
	match = Match(PRODUCTS_PATH,LISTINGS_PATH)
	match.match()
	with open('results.txt','w') as f:
		for entry in match.result:
			out = {}
			out['product_name'] = entry
			out['listings'] = match.result[entry]
			json.dump(out, f, separators=(',', ':'))
			f.write('\n')
	# TODO: write model.result to json file



if __name__ == '__main__':
	main()
