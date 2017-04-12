import pdb
import requests
import sqlite3
import json
import boto
import boto.s3.connection
from boto.s3.key import Key

URL = 'http://services.krispykreme.com/api/locationsearchresult/?responseType=Full&search=%7B%22Where%22%3A%7B%22LocationTypes%22%3A%5B%22Store%22%2C%22Commissary%22%2C%22Franchise%22%5D%2C%22OpeningDate%22%3A%7B%22ComparisonType%22%3A0%7D%7D%2C%22PropertyFilters%22%3A%7B%22Attributes%22%3A%5B%22FoursquareVenueId%22%2C%22OpeningType%22%5D%7D%7D&lat=33.7971137&lng=-84.38048879999997&_=1488861144613'

s3_data = None
s3_key = None

with open('creds.json') as data_file:
  data = json.load(data_file)
  s3_id = data['id']
  s3_key = data['key']

s3_conn = boto.s3.connect_to_region('us-east-1', aws_access_key_id=s3_id, aws_secret_access_key = s3_key, calling_format = boto.s3.connection.OrdinaryCallingFormat())

bucket = s3_conn.get_bucket('live.hotdonuts.info')
conn = sqlite3.connect('donuts.db')

def store_exists(id):
	resp = conn.execute("SELECT 1 FROM locations WHERE id=?", (id,))
	return resp.fetchone() != None

def insert_store(store):
	stmt = '''INSERT INTO locations(id, locationnum, name, slug, detailurl, locationtype, address1, address2, city, province, postalcode, country, phone, latitude, longitude, coffee, wifi, locationhours) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''
	values = (store['Id'], store['LocationNumber'], store['Name'], store['Slug'], store['DetailUrl'], store['LocationType'], store['Address1'], store['Address2'], store['City'], store['Province'], store['PostalCode'], store['Country'], store['PhoneNumber'], store['Latitude'], store['Longitude'], store['OffersCoffee'], store['OffersWifi'], json.dumps(store['LocationHours']))
	conn.execute(stmt, values)

def set_lit(id, lit):
  # conn.execute("INSERT INTO lightstatus(location_id, lit, time) VALUES(?, ?, strftime('%s','now'))", (id, lit))
  old_lit = None
  for result in conn.execute("SELECT lit FROM transitions WHERE location_id=? ORDER BY time DESC LIMIT 1", (id,)):
    old_lit = result[0]
  if old_lit != lit:
    conn.execute("INSERT INTO transitions(location_id, lit, time) VALUES(?, ?, strftime('%s','now'))", (id, lit))
    return True
  return False

def update_s3_currents():
  current_lit = {}
  for status in conn.execute("SELECT A.location_id, A.lit, A.time FROM transitions A, (SELECT location_id, MAX(time) AS time FROM transitions GROUP BY location_id) AS B WHERE A.location_id = B.location_id AND A.time = B.time;"):
    id, lit, time = status
    current_lit[id] = lit

  k = bucket.new_key("current.data")
  k.set_contents_from_string(json.dumps(current_lit))
  k.set_canned_acl('public-read')

def update_s3_store(store):
  transitions = []
  for status in conn.execute("SELECT lit, time FROM transitions WHERE location_id=? AND time > strftime('%s', 'now', '-15 days') ORDER BY time ASC", (store['Id'],)):
    lit, time = status
    transitions.append([time, lit])
  k = bucket.new_key("%s.data" % store['Id'])
  k.set_contents_from_string(json.dumps(transitions))
  k.set_canned_acl('public-read')

def all_locations():
  stores = requests.get(URL).json()
  any_changed = False
  for store in stores:
    store = store['Location']
    if not store_exists(store['Id']):
      insert_store(store)
    if set_lit(store['Id'], store['Hotlight']):
      any_changed = True
      update_s3_store(store)

  if any_changed:
    update_s3_currents()
  conn.commit()
  conn.close()

def create_tables():
  stmt = '''CREATE TABLE locations (id integer, locationnum integer, name text, slug text, detailurl text, locationtype text, address1 text, address2 text, city text, province text, postalcode text, country text, phone text, latitude text, longitude text, coffee boolean, wifi boolean, locationhours text)'''
  conn.execute(stmt)
  stmt = '''CREATE TABLE lightstatus (location_id integer, lit boolean, time integer)'''
  conn.execute(stmt)

#create_tables()
all_locations()
