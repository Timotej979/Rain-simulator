import sqlite3
from flask import Flask, request, render_template, jsonify, request, make_response
from datetime import datetime
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import matplotlib.dates
import numpy as np
from flask import redirect, url_for
import csv


app = Flask(__name__, static_url_path="/static", static_folder="static")


@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


app = Flask(__name__)


@app.route('/graph')
def graph():
    con = sqlite3.connect('mydatabase.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM dezemer")
    rows = cur.fetchall()

    x = [datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S') for row in rows]
    y = [row[1] for row in rows]

    dates = matplotlib.dates.date2num(x)
 
    plt.plot_date(x, y)
    plt.xlabel('String Value')
    plt.ylabel('Double Value')
    plt.title('Dezemer')

    # Create a BytesIO object
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue()).decode('ascii')
    #con.close() 
    return render_template('graph.html', figdata_png=figdata_png)


@app.route('/graph/<int:start>/<int:stop>', methods=['GET','POST'])
def graphStartStop(start, stop):
    con = sqlite3.connect('mydatabase.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM dezemer WHERE id > ? AND id < ?", (start, stop))
    rows = cur.fetchall()

    cur.execute("SELECT * FROM dezemer WHERE id > ? AND id < ?", (start, stop))
    rows = cur.fetchall()

    x = [datetime.strptime(str(row[2]), '%Y-%m-%d %H:%M:%S') for row in rows]
    y = [row[1] for row in rows]

    plt.plot_date(x, y)
    plt.xlabel('Datum in ure')
    plt.ylabel('Količina padavin')
    plt.title('Dezemer')

    # Create a BytesIO object
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue()).decode('ascii')
    return render_template('graph.html', figdata_png=figdata_png)

@app.route('/shrani_v_csv/<int:start>/<int:stop>', methods=['GET','POST'])
def shraniCSV(start, stop):
    conn = sqlite3.connect('mydatabase.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dezemer WHERE id > ? AND id < ?", (start, stop))
    with open("out.csv", 'w',newline='') as csv_file: 
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([i[0] for i in cursor.description]) 
        csv_writer.writerows(cursor)
    conn.close()

    response = make_response(open('out.csv').read())
    response.headers.set('Content-Type', 'text/csv')
    response.headers.set('Content-Disposition', 'attachment', filename='out.csv')
    return response

@app.route('/grafikon')
def grafikon():
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()
    c.execute("SELECT * FROM dezemer")
    data = c.fetchall()
    conn.close()
    return render_template('allTime.html', data=data)

@app.route('/')
def index():
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()
    c.execute("SELECT * FROM dezemer")
    data = c.fetchall()
    conn.close()
    return render_template('index.html', data=data)

@app.route('/display')
def display():
    con = sqlite3.connect('mydatabase.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM dezemer")
    rows = cur.fetchall()
    return render_template('display.html', rows=rows)

@app.route('/data/<data>', methods=['POST', 'GET'])
def handle_post_request(data):

    # save current time
    current_time = datetime.now()
    time_string = current_time.strftime("%Y-%m-%d %H:%M:%S")
    
    # post request
    #data = request.form['double_value']

    # connect sqlite3 database
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()
    # c.execute("DROP TABLE dezemer")
    c.execute("CREATE TABLE IF NOT EXISTS dezemer (id INTEGER PRIMARY KEY AUTOINCREMENT, meritev REAL, cas VARCHAR(255))")
    c.execute("INSERT INTO dezemer (meritev, cas) VALUES (?, ?)", (data, time_string))
    conn.commit()

    c.execute("SELECT * FROM dezemer")
    rows = c.fetchall()

    # Iterate through the rows and print the values
    # for row in rows:
    #     id = row
    #     print(f"id: {id}")

    refresh_meter = len(rows)

    print("refresh meter: ", refresh_meter)
    
    conn.close()

    return time_string

@app.route('/double_values_data')
def double_values_data():
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()
    c.execute("SELECT * FROM dezemer")
    results = c.fetchall()
    labels = [i[0] for i in results]
    values = [i[1] for i in results]
    return jsonify({'labels': labels, 'values': values})

@app.route('/eksperimenti', methods=['GET', 'POST'])
def eksperimenti():
    if request.method == 'POST':
        ime = request.form['ime']
        
        print(f'Dodaj eksperiment: {ime}')

        current_time=datetime.now()
        time_string = current_time.strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect('mydatabase.db')
        c = conn.cursor()
        #c.execute("DROP TABLE IF EXISTS eksperimenti")
        c.execute("INSERT INTO eksperimenti (ime,timestamp) VALUES (?,?)", (ime,time_string))
        conn.commit()
        conn.close()

        return redirect(url_for('eksperimenti'))

    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()
    c.execute("SELECT id, ime, timestamp FROM eksperimenti ORDER BY timestamp DESC")
    data = c.fetchall()
    conn.close()
    
    return render_template('eksperimenti.html', data=data)


@app.route('/eksperimenti/<int:id>', methods=['GET','POST'])
def delete_eksperimenti1(id):
    
    return render_template('potrditev.html', id = id)

@app.route('/eksperimenti_izbris/<int:id>', methods=['GET','POST'])
def delete_eksperimenti(id):
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()
    c.execute("DELETE FROM eksperimenti WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('eksperimenti'))


@app.route('/eksperiment/<id_>', methods=['GET', 'POST'])
def eksperiment(id_):
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()
    
    c.execute("INSERT INTO startStop (eid) SELECT ? WHERE NOT EXISTS (SELECT 1 FROM startStop WHERE eid = ?)", (id_, id_))
    
    conn.commit()

    if request.method == 'POST':
        action = request.form['action']
        print(f'Eksperiment: {action}')

        current_time = datetime.now()
        time_string = current_time.strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect('mydatabase.db')
        c = conn.cursor()
        
        if action == 'start':
            c.execute("UPDATE eksperimenti SET start=? WHERE id==?", (time_string, id_))

            c.execute("SELECT id FROM dezemer")
            rows = c.fetchall()
            dolzina_start = len(rows)

            c.execute("SELECT COUNT(*) FROM konfiguracija")
            count = c.fetchone()[0]

            c.execute("UPDATE startStop SET start=?, startPretok=? WHERE eid==?", (dolzina_start, count, id_))
            conn.commit()

        elif action == 'stop':
            c.execute("UPDATE eksperimenti SET stop=? WHERE id==?", (time_string, id_))

            c.execute("SELECT id FROM dezemer")
            rows = c.fetchall()
            dolzina_stop = len(rows)

            c.execute("SELECT COUNT(*) FROM konfiguracija")
            count = c.fetchone()[0]

            c.execute("UPDATE startStop SET stop=?, stopPretok=? WHERE eid==?", (dolzina_stop, count, id_))
            conn.commit()

        elif action == 'save':

            visinaStojala = request.form['visinaStojala']
            pretok = request.form['pretok']
            tlak=request.form['tlak']
            lokacijaTip = request.form['lokacijaTip']
            lokacijaVrednost = request.form['lokacijaVrednost']
            izavajalec = request.form['izvajalec']
            komentar = request.form['komentar']
            
            c.execute("INSERT INTO konfiguracija (eid, izvajalec, timestamp, visina_stojala, pretok, tlak, tip_lokacije, vrednost_lokacije, komentar) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (id_, izavajalec, time_string, visinaStojala, pretok, tlak, lokacijaTip, lokacijaVrednost, komentar))
            conn.commit()

        conn.close()

        return redirect(url_for('eksperiment', id_=id_))

    c.execute("SELECT id, ime, timestamp, start, stop FROM eksperimenti WHERE id==? LIMIT 1", (id_,))
    data = c.fetchall()[0]

    c.execute("SELECT * FROM konfiguracija WHERE eid==?", (id_,))
    conf = c.fetchall()

    c.execute("SELECT start, stop, startPretok, stopPretok FROM startStop WHERE eid==?", (id_,))
    startStop = c.fetchall()

    print('start: ', startStop[0][0], 'stop: ', startStop[0][1], 'start pretok: ', startStop[0][2], 'stop pretok: ', startStop[0][3])

    start_enabled = data[3] == '0000-00-00 00:00:00' and len(conf) > 0
    stop_enabled = data[3] != '0000-00-00 00:00:00' and data[4] == '0000-00-00 00:00:00'
    stanje = len(conf) > 0

    #
    # Izris grafa
    #

    connection = sqlite3.connect('mydatabase.db')
    c2 = connection.cursor()

    results = True
    if not start_enabled and not stop_enabled and stanje:
        c.execute("SELECT * FROM dezemer WHERE cas >= ? AND cas <= ?", (data[3], data[4]))
        c2.execute("SELECT pretok, tlak, timestamp FROM konfiguracija WHERE timestamp >= ? AND timestamp <= ?", (data[3], data[4]))
    elif not start_enabled and stop_enabled and stanje:
        c.execute("SELECT * FROM dezemer WHERE cas >= ?", (data[3],))
        c2.execute("SELECT pretok, tlak, timestamp FROM konfiguracija WHERE timestamp >= ?", (data[3],))
    else:
        results = False

    if results:
        rows = c.fetchall()
        rows2 = c2.fetchall()

        x = [datetime.strptime(str(row[2]), '%Y-%m-%d %H:%M:%S') for row in rows]
        y = [row[1] for row in rows]
        x1 = [datetime.strptime(str(row[2]), '%Y-%m-%d %H:%M:%S') for row in rows2]
        y1 = [row[0] for row in rows2]
        y2 = [row[1] for row in rows2]

        fig, ax = plt.subplots(3, 1, sharex=False)

        ax[0].plot_date(x, y, c='b', ls='-')
        ax[2].set_xlabel('Datum in ure')
        ax[0].set_ylabel('Količina padavin')
        ax[0].set_title('Dezemer')
        ax[1].set_ylabel('pretok')
        ax[1].plot_date(x1, y1, c='b', ls='-')
        ax[2].set_ylabel('tlak')
        ax[2].plot_date(x1, y2, c='b', ls='-')

        # Create a BytesIO object
        figfile = BytesIO()
        plt.savefig(figfile, format='png')
        figfile.seek(0)
        figdata_png = base64.b64encode(figfile.getvalue()).decode('ascii')
    else:
        figdata_png = None

    conn.close()
  
    return render_template('eksperiment.html', data=data, start_enabled=start_enabled, stop_enabled=stop_enabled, stanje=stanje, conf=conf, start = startStop[0][0], stop = startStop[0][1], figdata_png=figdata_png, results=results)

@app.route('/vaja')
def vaja():

    return render_template('vaja.html')

@app.route('/install/<action>', methods=['GET'])    
def install(action):
    conn = sqlite3.connect('mydatabase.db')
    c = conn.cursor()
    
    if action == 'reset':
        c.execute("DROP TABLE IF EXISTS konfiguracija")
        c.execute("DROP TABLE IF EXISTS startStop")

    c.execute("CREATE TABLE IF NOT EXISTS startStop (id INTEGER PRIMARY KEY AUTOINCREMENT, eid INTEGER DEFAULT 0, start INTEGER DEFAULT 0, stop INTEGER DEFAULT 0, startPretok INTEGER DEFAULT 0, stopPretok INTEGER DEFAULT 0)")
    c.execute("CREATE TABLE IF NOT EXISTS konfiguracija (id INTEGER PRIMARY KEY AUTOINCREMENT, eid INTEGER, izvajalec VARCHAR(255) DEFAULT '', timestamp DATETIME DEFAULT '0000-00-00 00:00:00', visina_stojala INTEGER, pretok REAL, tlak REAL, tip_lokacije VARCHAR(255) DEFAULT 'C', vrednost_lokacije INTEGER DEFAULT 0, komentar VARCHAR(255) DEFAULT '')")

    conn.commit()
    conn.close()

    return "OK"

if __name__ == '__main__':
    app.run(debug=True, host = '0.0.0.0')
    #app.run()
