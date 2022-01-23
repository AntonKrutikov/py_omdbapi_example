import sys
import requests
import sqlite3

if len(sys.argv) < 2:
    print("Please provide api key as argument")
    exit()

current_key = sys.argv[1]

# Using sqlite db to store results
con = sqlite3.connect('store.db')
cur = con.cursor()
# open file with encoding. provided file is ascii not utf8
with open('movienames.txt', 'r', encoding='latin-1') as f:
    # append movie name to db if it not exists
    for line in f:
        name = line.strip()
        cur.execute("INSERT OR IGNORE INTO movie (name) VALUES (?)", (name,))
con.commit()

cur_update = con.cursor()
# get all movies without rating and try to obtain imdb_rating from omdbapi
for row in cur.execute('SELECT name,id FROM movie WHERE imdb_rating IS NULL AND error is NULL'):
    movie_name = row[0]
    id = row[1]
    payload = {'apikey': current_key, 't': movie_name}
    try:
        r = requests.get('https://www.omdbapi.com', params=payload)
        resp = r.json()
        cur_update.execute("UPDATE movie SET imdb_rating=?, response=?, error=null where id=?", (resp['imdbRating'], str(resp), id))
        con.commit()
    except Exception as e:
        print("%s error get response, %s" % (movie_name, e))
        cur_update.execute("UPDATE movie SET response=?, error=? where id=?", (str(resp), str(e), id))
    finally:
        con.commit()

# save result as txt file from db
with open("result.txt", "w") as result:
    for row in cur.execute('SELECT name,imdb_rating FROM movie'):
        result.write("%s -> %s\n" % (row[0], row[1]))