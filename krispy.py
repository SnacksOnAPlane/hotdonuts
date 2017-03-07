import pdb
import requests
import sqlite3
import json

URL = 'http://services.krispykreme.com/api/locationsearchresult/?responseType=Full&search=%7B%22Where%22%3A%7B%22LocationTypes%22%3A%5B%22Store%22%2C%22Commissary%22%2C%22Franchise%22%5D%2C%22OpeningDate%22%3A%7B%22ComparisonType%22%3A0%7D%7D%2C%22PropertyFilters%22%3A%7B%22Attributes%22%3A%5B%22FoursquareVenueId%22%2C%22OpeningType%22%5D%7D%7D&lat=33.7971137&lng=-84.38048879999997&_=1488861144613'

conn = sqlite3.connect('donuts.db')

def store_exists(id):
	resp = conn.execute("SELECT 1 FROM locations WHERE id=?", (id,))
	return resp.fetchone() != None

def insert_store(store):
	stmt = '''INSERT INTO locations(id, locationnum, name, slug, detailurl, locationtype, address1, address2, city, province, postalcode, country, phone, latitude, longitude, coffee, wifi, locationhours) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''
	values = (store['Id'], store['LocationNumber'], store['Name'], store['Slug'], store['DetailUrl'], store['LocationType'], store['Address1'], store['Address2'], store['City'], store['Province'], store['PostalCode'], store['Country'], store['PhoneNumber'], store['Latitude'], store['Longitude'], store['OffersCoffee'], store['OffersWifi'], json.dumps(store['LocationHours']))
	conn.execute(stmt, values)

def set_lit(id, lit):
	conn.execute("INSERT INTO lightstatus(location_id, lit, time) VALUES(?, ?, strftime('%s','now'))", (id, lit))

def all_locations():
	stores = requests.get(URL).json()
	for store in stores:
		store = store['Location']
		if not store_exists(store['Id']):
			insert_store(store)
		set_lit(store['Id'], store['Hotlight'])
	conn.commit()
	conn.close()

def create_tables():
	stmt = '''CREATE TABLE locations (id integer, locationnum integer, name text, slug text, detailurl text, locationtype text, address1 text, address2 text, city text, province text, postalcode text, country text, phone text, latitude text, longitude text, coffee boolean, wifi boolean, locationhours text)'''
	conn.execute(stmt)
	stmt = '''CREATE TABLE lightstatus (location_id integer, lit boolean, time integer)'''
	conn.execute(stmt)

#create_tables()
all_locations()
