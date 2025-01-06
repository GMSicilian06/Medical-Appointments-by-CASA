from flask import Flask, render_template, request, redirect, jsonify

import sqlite3
import csv

conn = sqlite3.connect("Citas.db")
cursor = conn.cursor()


cursor.execute('''CREATE TABLE IF NOT EXISTS descripcion (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL, descripcion TEXT NOT NULL);''')

cursor.execute('''CREATE TABLE IF NOT EXISTS comments(id INTEGER PRIMARY KEY AUTOINCREMENT, comentario TEXT);''')

cursor.execute('''CREATE TABLE IF NOT EXISTS citas1(id INTEGER PRIMARY KEY AUTOINCREMENT, nombres TEXT NOT NULL, detalles TEXT NOT NULL, fecha TEXT NOT NULL, estado TEXT NOT NULL);''')

conn.commit()
conn.close()

def export_to_csv():

    conn = sqlite3.connect('Citas.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM citas1")
    citas_data = cursor.fetchall()

    csv_file = 'citas1_data.csv'

    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)

    
        writer.writerow(['ID', 'Nombres', 'Detalles', 'Fecha', 'Estado'])

        
        for row in citas_data:
            writer.writerow(row)

    
    conn.close()
    print(f'Data has been exported to {csv_file}')


export_to_csv()


app = Flask(__name__)

@app.route('/')
def Home():
    conn = sqlite3.connect('Citas.db')
    cursor = conn.cursor()

    cursor.execute("SELECT comentario FROM comments")
    comments = cursor.fetchall()
    
    conn.close()

    return render_template('principal.html', comments=comments)
    

@app.route('/submit', methods=['POST'])
def submit_form():
    comment = request.form['comment']  
    
    conn = sqlite3.connect('Citas.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO comments (comentario) VALUES (?)", (comment,))

    conn.commit()
    conn.close()

    return redirect('/')

@app.route('/Cita', methods=["GET","POST"])
def Cita():
    if request.method == "POST":
        date = request.form['date']
        estado = "Agendado"
        nombres = request.form.get('nombres')
        detalles = request.form.get('detalles')

        if not date or not nombres or not detalles:
            return "Todos los campos son obligatorios.", 400

        conn = sqlite3.connect('Citas.db')
        cursor = conn.cursor()

        cursor.execute("SELECT *FROM citas1 WHERE fecha = ?", (date,))
        existing = cursor.fetchone()

        if existing:
            conn.close()
            return "Esta fecha ya está agendada!", 400
        
        cursor.execute("INSERT INTO citas1 (nombres, detalles, fecha, estado) VALUES (?, ?, ?, ?)", (nombres, detalles, date, estado))

        conn.commit()
        conn.close()

        export_to_csv()

        return redirect('/Cita')
    conn = sqlite3.connect('Citas.db')
    cursor = conn.cursor()
    cursor.execute("SELECT fecha, estado FROM citas1")
    citas = cursor.fetchall()
    conn.close()

    fechasagendadas = [row[0] for row in citas if row[1] == "Agendado"]
    return render_template("cita.html", fechasagendadas=fechasagendadas)

@app.route('/api/citas', methods=['GET'])
def get_citas():
    with sqlite3.connect('Citas.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT fecha, estado FROM citas1")
        citas = cursor.fetchall()
    return jsonify({"citas": citas})

    


if __name__ == '__main__':
    app.run(debug=True)