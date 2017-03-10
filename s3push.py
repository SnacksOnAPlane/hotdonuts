import pdb
import sqlite3
import boto
import json
from collections import defaultdict
import boto
import boto.s3.connection
from boto.s3.key import Key

s3_data = None
s3_key = None

with open('creds.json') as data_file:
  data = json.load(data_file)
  s3_id = data['id']
  s3_key = data['key']

s3_conn = boto.s3.connect_to_region('us-east-1', aws_access_key_id=s3_id, aws_secret_access_key = s3_key, calling_format = boto.s3.connection.OrdinaryCallingFormat())

bucket = s3_conn.get_bucket('live.hotdonuts.info')
conn = sqlite3.connect('donuts.db')

current_lit = {}
locations = []

def query(q):
  cur = conn.cursor()
  cur.execute(q)
  r = [dict((cur.description[i][0], value) \
             for i, value in enumerate(row)) for row in cur.fetchall()]
  return r

for row in query("SELECT * FROM locations"):
  id = row['id']
  locations.append(row)
  transitions = []
  for status in conn.execute("SELECT lit, time FROM transitions WHERE location_id=? ORDER BY time ASC", (id,)):
    lit, time = status
    current_lit[id] = lit
    transitions.append([time, lit])
  k = bucket.new_key("%s.data" % id)
  k.set_contents_from_string(json.dumps(transitions))
  k.set_canned_acl('public-read')

conn.close()
k = bucket.new_key("current.data")
k.set_contents_from_string(json.dumps(current_lit))
k.set_canned_acl('public-read')
k = bucket.new_key("locations.data")
k.set_contents_from_string(json.dumps(locations))
k.set_canned_acl('public-read')


