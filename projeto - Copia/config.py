import os

class Config:
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://reduzgestao_user:hAvAVESGXiKKUJfMjddrPWYoOo5oxftE@dpg-cpsvf0mehbks73eroe40-a.oregon-postgres.render.com/reduzgestao')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
