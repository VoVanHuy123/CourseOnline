import os
from dotenv import load_dotenv
import secrets
import cloudinary
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}?charset=utf8mb4"
    )
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key")
    SECRET_KEY = secrets.token_hex(32)

    def init_cloudinary():
        cloudinary.config(
            cloud_name=os.getenv("delrpa4vp"),
            api_key=os.getenv("812578969381167"),
            api_secret=os.getenv("API_SsYRSJNHOTFBM_P-CAwztGS99K2YECRET"),
        )