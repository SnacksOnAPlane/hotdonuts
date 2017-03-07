import pdb
import sqlite3
import json

conn = sqlite3.connect('donuts.db')

for row in conn.execute("SELECT id FROM locations"):
	id = row[0]
	last_lit = None
	for status in conn.execute("SELECT lit, time FROM lightstatus WHERE location_id=? ORDER BY time ASC", (id,)):
		lit, time = status
		if last_lit != lit:
			conn.execute("INSERT INTO transitions(location_id, lit, time) VALUES (?,?,?)", (id, lit, time))
			last_lit = lit
conn.commit()
conn.close()
