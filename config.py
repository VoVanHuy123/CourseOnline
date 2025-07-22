import os
from dotenv import load_dotenv
import secrets
import cloudinary
load_dotenv()

class Config:
    if(os.getenv('DB_USER')):
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
            f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}?charset=utf8mb4"
        )
    else:
        SQLALCHEMY_DATABASE_URI = (
            f"postgresql+psycopg2://{os.getenv('DB_POSTGRESS_USER')}:{os.getenv('DB_POSTGRESS_PASSWORD')}"
            f"@{os.getenv('DB_POSTGRESS_HOST')}:{os.getenv('DB_POSTGRESS_PORT')}/{os.getenv('DB_POSTGRESS_NAME')}"
        )
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key")
    SECRET_KEY = secrets.token_hex(32)

    def init_cloudinary():
        cloudinary.config(
            cloud_name=os.getenv("CLOUD_NAME"),
            api_key=os.getenv("API_KEY"),
            api_secret=os.getenv("API_SECRET"),

        )