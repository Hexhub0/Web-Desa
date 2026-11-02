from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password, password)

class Resident(db.Model):
    __tablename__ = "resident"
    id = db.Column(db.Integer, primary_key=True)
    nik = db.Column(db.String(20), unique=True, nullable=False)
    nama = db.Column(db.String(150), nullable=False)
    jenis_kelamin = db.Column(db.String(20), nullable=False)
    dusun = db.Column(db.String(50), nullable=False)
    tanggal_lahir = db.Column(db.String(20), nullable=True)
    pekerjaan = db.Column(db.String(100), nullable=True)
    pendidikan = db.Column(db.String(50), nullable=True)

class PopulationHistory(db.Model):
    __tablename__ = "population_history"
    id = db.Column(db.Integer, primary_key=True)
    tahun = db.Column(db.Integer, unique=True, nullable=False)
    jumlah = db.Column(db.Integer, nullable=False)

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama_kegiatan = db.Column(db.String(200), nullable=False)
    tanggal = db.Column(db.String(20), nullable=False)

    images = db.relationship(
        "ActivityImage",
        backref="activity",
        cascade="all, delete-orphan"
    )

class ActivityImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)

    activity_id = db.Column(
        db.Integer,
        db.ForeignKey("activity.id"),
        nullable=False
    )