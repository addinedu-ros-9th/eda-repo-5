import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    # 환경 변수에서 값 읽어오기
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_NAME = os.getenv('DB_NAME')

    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback_secret_key')
    DEBUG = True
    
    # 추천 엔진 설정
    RECOMMENDATION_LIMIT = 10  # 각 카테고리별 추천 장소 최대 개수
    
    # 날씨 관련 설정
    WEATHER_RAINFALL_THRESHOLD = 3  # mm 이상일 때 실내 활동 추천
    WEATHER_DISCOMFORT_THRESHOLD = 75  # 불쾌지수 임계값
    UV_INDEX_THRESHOLD = 7  # 자외선 지수 임계값

    # API 관련 설정
    KAKAO_MAP_API_KEY = '9263084982b41627732ca8c2d250e12b'  # 필요시 추가

    @classmethod
    def is_development(cls):
        """
        현재 환경이 개발 환경인지 확인
        """
        return True

    @classmethod
    def get_database_uri(cls):
        """
        데이터베이스 연결 URI 생성
        """
        return f"mysql+mysqlconnector://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"