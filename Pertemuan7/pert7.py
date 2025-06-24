import sys
from PyQt5.QtWidgets import QApplication, QWidget, QFormLayout, QLineEdit, QPushButton, QMessageBox, QLabel, QVBoxLayout

# Window untuk login
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(400, 300, 300, 100)
        self.loginUI()

    def loginUI(self):
        layout = QFormLayout()

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        layout.addRow("Username :", self.username_input)
        layout.addRow("Password :", self.password_input)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.check_login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def check_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # Cek username dan password
        if username == "admin" and password == "mp":
            self.form_window = MainWindow()
            self.form_window.show()
            self.close()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Username atau Password salah!")
            msg.setWindowTitle("Login Gagal!")
            msg.exec_()

# Window untuk input data
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Form Mahasiswa")
        self.setGeometry(400, 300, 600, 200)
        self.create_layout()

    def create_layout(self):
        self.layout = QVBoxLayout()
        form_layout = QFormLayout()
        self.input_nama = QLineEdit(self)
        self.input_kelas = QLineEdit(self)
        self.input_npm = QLineEdit(self)
        self.input_jurusan = QLineEdit(self)

        form_layout.addRow("Nama :", self.input_nama)
        form_layout.addRow("Kelas :", self.input_kelas)
        form_layout.addRow("NPM :", self.input_npm)
        form_layout.addRow("Jurusan :", self.input_jurusan)

        self.layout.addLayout(form_layout)

        self.hasil_label = QLabel(self)
        self.layout.addWidget(self.hasil_label)

        self.button = QPushButton("Tampilkan", self)
        self.layout.addWidget(self.button)

        self.button.clicked.connect(self.tampilkan_hasil)

        self.setLayout(self.layout)
        self.setWindowTitle("Form Mahasiswa")
        self.setGeometry(400, 300, 600, 200)
        self.show()

    def tampilkan_hasil(self):
        nama = self.input_nama.text()
        kelas = self.input_kelas.text()
        npm = self.input_npm.text()
        jurusan = self.input_jurusan.text()

        if nama == '' or kelas == '' or npm == '' or jurusan == '':
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Data tidak boleh kosong!")
            msg.setWindowTitle("Error")
            msg.exec_()
        else:
            hasil = f"Nama : {nama}\nKelas : {kelas}\nNPM : {npm}\nJurusan : {jurusan}"
            self.hasil_label.setText(hasil)

            self.input_nama.clear()
            self.input_kelas.clear()
            self.input_npm.clear()
            self.input_jurusan.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())