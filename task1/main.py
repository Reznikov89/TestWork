from datetime import datetime
from typing import Dict

from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import requests


app = FastAPI()

Base = declarative_base()

engine = create_engine('postgresql://postgres:postgres@db:5432/quiz_db')
Session = sessionmaker(bind=engine)


class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    question = Column(String)
    answer = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(engine)


def get_question_from_api() -> Dict[str, str]:
    url = 'https://jservice.io/api/random?count=1'
    response = requests.get(url)
    data = response.json()[0]
    return {
        'question': data['question'],
        'answer': data['answer']
    }


def get_unique_question() -> Dict[str, str]:
    while True:
        question = get_question_from_api()
        session = Session()
        existing_question = session.query(Question).filter_by(
            question=question['question']).first()
        if not existing_question:
            new_question = Question(**question)
            session.add(new_question)
            session.commit()
            return question


@app.post('/quiz/')
def quiz(questions_num: int) -> Dict[str, str]:
    questions = []
    for _ in range(questions_num):
        question = get_unique_question()
        questions.append(question)
    return {'questions': questions}
