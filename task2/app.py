import os

from flask import Flask, jsonify, request, send_file
from pydub import AudioSegment
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
Base = declarative_base()

# Конфигурация базы данных
db_username = "your_username"
db_password = "your_password"
db_name = "your_database_name"
db_host = "db"
db_port = "5432"

db_url = f"postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)


# Модель данных
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    access_token = Column(String)

    def __init__(self, name, access_token):
        self.name = name
        self.access_token = access_token


class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    filename = Column(String)
    uuid = Column(String)

    def __init__(self, user_id, filename, uuid):
        self.user_id = user_id
        self.filename = filename
        self.uuid = uuid


Base.metadata.create_all(engine)


# Создание пользователя
@app.route("/users", methods=["POST"])
def create_user():
    name = request.json.get("name")

    if not name:
        return jsonify({"error": "Name is required"}), 400

    access_token = os.urandom(16).hex()

    user = User(name=name, access_token=access_token)

    session = Session()
    session.add(user)
    session.commit()

    return jsonify({"id": user.id, "access_token": user.access_token}), 201


# Добавление аудиозаписи
@app.route("/records", methods=["POST"])
def add_record():
    user_id = request.json.get("user_id")
    access_token = request.json.get("access_token")

    if not user_id or not access_token:
        return jsonify({"error": "User ID and access token are required"}), 400

    session = Session()
    user = session.query(User).filter_by(id=user_id, access_token=access_token).first()

    if not user:
        return jsonify({"error": "Invalid user ID or access token"}), 401

    file = request.files.get("file")

    if not file:
        return jsonify({"error": "Audio file is required"}), 400

    filename = file.filename
    uuid = os.urandom(16).hex()

    # Сохранение аудиозаписи в формате WAV
    wav_path = f"uploads/{uuid}.wav"
    file.save(wav_path)

    # Преобразование аудиозаписи в формат MP3
    mp3_path = f"uploads/{uuid}.mp3"
    audio = AudioSegment.from_wav(wav_path)
    audio.export(mp3_path, format="mp3")
    record = Record(user_id=user_id, filename=filename, uuid=uuid)

    session.add(record)
    session.commit()

    return jsonify(
        {"url": f"http://host:port/record?id={record.uuid}&user={record.user_id}"}
    ), 201


# Доступ к аудиозаписи
@app.route("/record", methods=["GET"])
def get_record():
    record_id = request.args.get("id")
    user_id = request.args.get("user")

    if not record_id or not user_id:
        return jsonify({"error": "Record ID and user ID are required"}), 400

    session = Session()
    record = (
        session.query(Record)
        .filter_by(uuid=record_id, user_id=user_id)
        .first()
    )

    if not record:
        return jsonify({"error": "Record not found"}), 404

    mp3_path = f"uploads/{record.uuid}.mp3"

    if not os.path.exists(mp3_path):
        return jsonify({"error": "MP3 file not found"}), 404

    return send_file(mp3_path, mimetype="audio/mpeg")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
