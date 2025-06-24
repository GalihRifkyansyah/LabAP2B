# (1) tambahkan
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.routing import Map, Rule
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# (2) tambahkan
# definisi URL untuk save DB bernama mahasiswa
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///mahasiswa.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# buat tabel mahasiswa sebagai model db
class Mahasiswa(db.Model):
    npm = db.Column(db.String(8), primary_key=True)
    nama = db.Column(db.String(150), nullable=False)

    @property
    def as_json(self):
        # Returns object data in a serializable format
        return {
            'npm': self.npm,
            'nama': self.nama
        }

# handle DB from recreate if already exist
if not os.path.exists('mahasiswa.db'):
    # buat semua table yang telah didefinisi (model)
    with app.app_context():
        db.create_all()

# untuk mendapatkan key nya, ketikkan di terminal vscode
# python -c "import secrets; print(secrets.token_hex())"
# Contoh key: '1e0946fcb66ef44e4d56f30f88c3871a3025d3dee508d693881f496c27'
app.secret_key = '878ed82a86252b522b88b2ccd9c20713751486f58166a7da2799b3ef20a60509' # isikan key nya sesuai dengan laptop masing"
USER_CREDS = {'username': 'Galih', 'password': 'secret'} # ganti username dengan nama kalian

# (3) edit route bagian /mahasiswa dan /mahasiswa/npm
url_map = Map([
    Rule('/', endpoint='index'),
    Rule('/mahasiswa', endpoint='mahasiswa', methods=['GET', 'POST']),
    Rule('/mahasiswa/<npm>', endpoint='mahasiswa_npm', methods=['GET', 'POST']),
    Rule('/login', endpoint='login', methods=['GET', 'POST']),
    Rule('/admin', endpoint='admin'),
    Rule('/logout', endpoint='logout')
])

@app.endpoint('index')
def index():
    if 'username' in session:
        username = session['username']
        return render_template('index.html', title='index', username=username)
    else:
        return render_template('index.html', title='index')

# (4) sesuaikan bagian ini
@app.endpoint('mahasiswa')
def mahasiswa():
    # query semua data pada tabel mahasiswa
    mahasiswa = db.session.execute(db.select(Mahasiswa)).scalars().all()
    serialized_mahasiswa = [mahasiswa_.as_json for mahasiswa_ in mahasiswa]

    if 'username' in session:
        username = session['username']

        # kirim data baru
        if request.method == 'POST':
            npm = request.form['npm']
            nama = request.form['nama']

            # cek jika npm berupa string
            if not str(npm).isdigit:
                return render_template('mahasiswa.html', title='mahasiswa', data_mahasiswa=serialized_mahasiswa,
                                       angka=True, npm=npm, nama=nama, username=username)

            # cek jika data mahasiswa telah ada pada db
            existing_mahasiswa = Mahasiswa.query.filter_by(npm=npm).first()
            if existing_mahasiswa:
                return render_template('mahasiswa.html', title='mahasiswa', data_mahasiswa=serialized_mahasiswa,
                                       exist=True, npm=npm, nama=nama, username=username)

            # tambahkan mahasiswa ke db
            new_mahasiswa = Mahasiswa(npm=npm, nama=nama)
            db.session.add(new_mahasiswa)
            db.session.commit()
            return redirect(url_for('mahasiswa'))

        else:
            # untuk method get dapatkan semua data
            return render_template('mahasiswa.html', title='mahasiswa', data_mahasiswa=serialized_mahasiswa,
                                   username=username)

    # check api untuk GET semua data dan membuat data baru dengan POST
    elif request.is_json and request.json['key'] == 'secret':
        # get semua mahasiswa
        if request.method == 'GET':
            serialized_mahasiswa = [mahasiswa_.as_json for mahasiswa_ in mahasiswa]
            return jsonify(serialized_mahasiswa)

        # post data mahasiswa
        if request.method == 'POST':
            npm = request.json['npm']
            nama = request.json['nama']

            if not str(npm).isdigit():
                return {'error': 'npm must be digit.'}, 400  # bad request

            existing_mahasiswa = Mahasiswa.query.filter_by(npm=npm).first()
            if existing_mahasiswa:
                return {'error': 'npm already exist.'}, 409  # conflict

            new_mahasiswa = Mahasiswa(npm=npm, nama=nama)
            db.session.add(new_mahasiswa)
            db.session.commit()
            return new_mahasiswa.as_json, 201  # resource created

    else:
        # jika user belum login
        return render_template('mahasiswa.html', title='mahasiswa', data_mahasiswa=serialized_mahasiswa)
    
@app.endpoint('mahasiswa_npm')
def mahasiswa_npm(npm):
    mahasiswa = Mahasiswa.query.get_or_404(npm)

    if 'username' in session:
        if mahasiswa:
            if request.method == 'POST' and request.form['_method'] == 'put':
                nama = request.form['nama']
                mahasiswa.nama = nama
                db.session.commit()
                return redirect(url_for('mahasiswa'))

            elif request.method == 'POST' and request.form['_method'] == 'delete':
                db.session.delete(mahasiswa)
                db.session.commit()
                return redirect(url_for('mahasiswa'))
        else:
            return "Mahasiswa not found"
    elif request.json['key'] == 'secret':
        # dapetin datanya GET
        if request.method == 'GET':
            mahasiswa = db.get_or_404(Mahasiswa, npm)
            return jsonify(mahasiswa.as_json)

        # edit data nama
        elif request.method == 'POST' and request.json['_method'] == 'put':
            payload = request.get_json()
            mahasiswa = Mahasiswa.query.get(npm)
            if mahasiswa:
                mahasiswa.nama = payload['nama']
                db.session.commit()
                return jsonify(db.get_or_404(Mahasiswa, npm).as_json)
            else:
                return {"error": "mahasiswa not found"}, 404

        # hapus data npm
        elif request.method == 'POST' and request.json['_method'] == 'delete':
            db.session.delete(mahasiswa)
            db.session.commit()
            return {"message": f"{npm} has been deleted."}, 200
    else:
        return "Outside is not allowed."

@app.endpoint('login')
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USER_CREDS['username'] and password == USER_CREDS['password']:
            session['username'] = username
            return redirect(url_for('admin'))
        else:
            return render_template('login.html', title='login', failed=True, username=username)
    else:
        return render_template('login.html', title='login')

@app.endpoint('admin')
def admin():
    if 'username' in session:
        username = session['username']
        return render_template('admin.html', title='admin', username=username)
    else:
        return redirect(url_for('login'))

@app.endpoint('logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

app.url_map = url_map

if __name__ == '__main__':
    app.run(debug=True)