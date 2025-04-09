# recommendation_engine.py
import pandas as pd
import numpy as np
import logging
from db_connection import get_dataframe, execute_query

class RecommendationEngine:
    def __init__(self):
        """
        데이트 코스 추천 엔진 초기화
        """
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 여성 선호 메뉴 가중치
        self.female_preferences = {
            '육류구이류': 80,  # 가장 선호도 높음
            '탕류': 65,
            '일식류': 63.5,
            '국류': 63,
            '중국식면류': 60.9,
            '돈가스류': 58.3,
            '국밥류': 53.5,
            '찌개류': 50.8,
            '한식': 50,
            '육류생회류': 33.8
        }
        
        # 데이터 캐싱
        self.restaurants_df = None
        self.attractions_df = None
        self.cafes_df = None
        self.spots_df = None
        
        # 데이터 로드
        self._load_data()
    
    def _load_data(self):
        """
        데이터베이스에서 필요한 데이터를 불러와 메모리에 캐싱
        """
        try:
            self.restaurants_df = get_dataframe('restaurant')
            self.attractions_df = get_dataframe('enjoy')
            self.cafes_df = get_dataframe('cafe')
            self.spots_df = get_dataframe('spot')
            
            # 데이터 전처리
            if self.restaurants_df is not None:
                self._preprocess_restaurants()
            
            if self.attractions_df is not None:
                self._preprocess_attractions()
            
            if self.cafes_df is not None:
                self._preprocess_cafes()
        
        except Exception as e:
            self.logger.error(f"데이터 로드 중 오류 발생: {e}")
    
    def _preprocess_restaurants(self):
        """레스토랑 데이터 전처리"""
        # 구 추출
        self.restaurants_df['district'] = self.restaurants_df['address'].apply(self._extract_district)
        
        # 가격대 변환
        self.restaurants_df['price_range'] = self.restaurants_df['price'].apply(self._convert_price_range)
        
        # 리뷰 수 정규화
        self.restaurants_df['normalized_reviews'] = (
            self.restaurants_df['review'] - self.restaurants_df['review'].min()
        ) / (self.restaurants_df['review'].max() - self.restaurants_df['review'].min())
    
    def _preprocess_attractions(self):
        """놀거리 데이터 전처리"""
        # 구 추출
        self.attractions_df['district'] = self.attractions_df['address'].apply(self._extract_district)
        
        # 활동 유형 변환
        self.attractions_df['activity_type'] = self.attractions_df['type'].map({
            0: '실내',
            1: '실외',
            None: '정보 없음'
        })
        
        # 리뷰 수 정규화
        self.attractions_df['normalized_reviews'] = (
            self.attractions_df['review'] - self.attractions_df['review'].min()
        ) / (self.attractions_df['review'].max() - self.attractions_df['review'].min())
    
    def _preprocess_cafes(self):
        """카페 데이터 전처리"""
        # 구 추출
        self.cafes_df['district'] = self.cafes_df['address'].apply(self._extract_district)
        
        # 리뷰 수 정규화
        self.cafes_df['normalized_reviews'] = (
            self.cafes_df['review'] - self.cafes_df['review'].min()
        ) / (self.cafes_df['review'].max() - self.cafes_df['review'].min())
    
    def _extract_district(self, address):
        """
        주소에서 구 정보 추출
        
        Args:
            address (str): 주소 문자열
        
        Returns:
            str: 추출된 구 이름 또는 None
        """
        if not isinstance(address, str):
            return None
        
        districts = [
            '강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구',
            '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구',
            '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구'
        ]
        
        for district in districts:
            if district in address:
                return district
        return None
    
    def _convert_price_range(self, price):
        """
        가격 범위 변환
        
        Args:
            price (float): 가격 정보
        
        Returns:
            str: 변환된 가격 범위
        """
        if pd.isna(price) or price == 0:
            return '정보 없음'
        elif price < 10000:
            return '1만원 이하'
        elif price < 20000:
            return '1-2만원'
        elif price < 30000:
            return '2-3만원'
        else:
            return '3-5만원'
    
    def _calculate_preference_score(self, category):
        """
        20대 여성 선호도 점수 계산
        
        Args:
            category (str): 음식 카테고리
        
        Returns:
            float: 선호도 점수
        """
        if not isinstance(category, str):
            return 5  # 기본 점수
        
        for pref_category, weight in self.female_preferences.items():
            if pref_category in category:
                # 선호도 가중치를 0-10 사이 점수로 정규화
                return min(10, weight / 50)
        
        return 5  # 기본 점수
    
    def recommend_restaurants(self, district, food_category, budget_range, limit=10):
        """
        선호 메뉴와 예산에 맞는 맛집 추천
        
        Args:
            district (str): 선택한 서울시 구 이름
            food_category (str): 선호하는 음식 카테고리
            budget_range (int): 예산 범위
            limit (int): 추천 결과 최대 개수
        
        Returns:
            pandas.DataFrame: 추천 맛집 리스트
        """
        try:
            # 구 및 예산 필터링
            filtered_df = self.restaurants_df[
                (self.restaurants_df['district'] == district)
            ]
            
            # 예산 범위 필터링
            budget_mapping = {
                1: "1만원 이하",
                2: "1-2만원", 
                3: "2-3만원", 
                4: "3-5만원"
            }
            
            if budget_range in budget_mapping:
                budget_filter = budget_mapping[budget_range]
                filtered_df = filtered_df[filtered_df['price_range'] == budget_filter]
            
            # 음식 카테고리 필터링
            if food_category != "랜덤":
                filtered_df = filtered_df[
                    filtered_df['category'].str.contains(food_category, na=False, case=False)
                ]
            
            # 결과가 없으면 카테고리 필터 제거
            if len(filtered_df) == 0:
                filtered_df = self.restaurants_df[
                    (self.restaurants_df['district'] == district)
                ]
            
            # 선호도 점수 계산
            filtered_df['preference_score'] = filtered_df['category'].apply(self._calculate_preference_score)
            
            # 종합 점수 계산 (평점, 리뷰, 선호도)
            filtered_df['total_score'] = (
                filtered_df['score'] * 0.4 + 
                filtered_df['normalized_reviews'] * 0.3 + 
                filtered_df['preference_score'] * 0.3
            )
            
            # 상위 N개 결과 반환
            return filtered_df.sort_values('total_score', ascending=False).head(limit)
        
        except Exception as e:
            self.logger.error(f"맛집 추천 중 오류 발생: {e}")
            return pd.DataFrame()
    
    def recommend_attractions(self, district, weather_info, limit=10):
        """
        날씨에 맞는 놀거리 추천
        
        Args:
            district (str): 선택한 서울시 구 이름
            weather_info (dict): 날씨 정보
            limit (int): 추천 결과 최대 개수
        
        Returns:
            pandas.DataFrame: 추천 놀거리 리스트
        """
        try:
            # 구 필터링
            filtered_df = self.attractions_df[
                (self.attractions_df['district'] == district)
            ]
            
            # 날씨 기반 필터링
            if not weather_info.get('recommend_outdoor', True):
                filtered_df = filtered_df[filtered_df['activity_type'] == '실내']
            
            # 결과가 부족하면 확장
            if len(filtered_df) < limit:
                filtered_df = self.attractions_df[
                    self.attractions_df['activity_type'] == ('실내' if not weather_info.get('recommend_outdoor', True) else '실외')
                ]
            
            # 정렬 및 상위 N개 반환
            return filtered_df.sort_values('normalized_reviews', ascending=False).head(limit)
        
        except Exception as e:
            self.logger.error(f"놀거리 추천 중 오류 발생: {e}")
            return pd.DataFrame()
    
    def recommend_cafes(self, district, restaurant_location=None, limit=10):
        """
        맛집 위치에 가까운 카페 추천
        
        Args:
            district (str): 선택한 서울시 구 이름
            restaurant_location (tuple): 맛집 위치 (위도, 경도)
            limit (int): 추천 결과 최대 개수
        
        Returns:
            pandas.DataFrame: 추천 카페 리스트
        """
        try:
            # 구 필터링
            filtered_df = self.cafes_df[
                (self.cafes_df['district'] == district)
            ]
            
            # 맛집 위치 기반 거리 계산
            if restaurant_location:
                filtered_df['distance'] = filtered_df.apply(
                    lambda row: self._calculate_distance(
                        restaurant_location, 
                        (row['latitude'], row['longitude'])
                    ),
                    axis=1
                )
                
                # 거리와 평점 고려한 점수 계산
                filtered_df['score_with_distance'] = (
                    filtered_df['score'] * 0.6 - 
                    filtered_df['distance'] * 0.4
                )
                
                result = filtered_df.sort_values('score_with_distance', ascending=False).head(limit)
            else:
                # 맛집 위치 없을 경우 평점 기준 정렬
                result = filtered_df.sort_values('score', ascending=False).head(limit)
            
            return result
        
        except Exception as e:
            self.logger.error(f"카페 추천 중 오류 발생: {e}")
            return pd.DataFrame()
    
    def _calculate_distance(self, point1, point2):
        """
        두 지점 간의 단순 유클리드 거리 계산
        
        Args:
            point1 (tuple): 첫 번째 지점 좌표 (위도, 경도)
            point2 (tuple): 두 번째 지점 좌표 (위도, 경도)
        
        Returns:
            float: 두 지점 간 거리
        """
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def get_weather_recommendation(self, district):
        """
        날씨 조건에 따른 실내/외 활동 추천
        
        Args:
            district (str): 선택한 서울시 구 이름
        
        Returns:
            dict: 날씨 정보와 추천 장소 유형
        """
        try:
            # 최신 날씨 정보 쿼리
            query = """
            SELECT datetime, temp, precipitation, precpt_type, humidity, 
                   air_idx, sky_stts, wind_spd, uv_idx
            FROM spot
            WHERE gu = %s
            ORDER BY datetime DESC
            LIMIT 1
            """
            
            weather_data = execute_query(query, (district,))
            
            # 날씨 정보 없을 경우 기본값
            if not weather_data:
                return {
                    "district": district,
                    "weather_status": "정보 없음",
                    "rainfall": 0,
                    "discomfort_index": 0,
                    "solar_radiation": 5,
                    "recommend_outdoor": True
                }
            
            # 날씨 정보 추출
            weather_info = weather_data[0]
            
            # 불쾌지수 계산
            temperature = weather_info.get('temp', 25)
            humidity = weather_info.get('humidity', 50)
            discomfort_index = 0.81 * temperature + 0.01 * humidity * (0.99 * temperature - 14.3) + 46.3
            
            # 날씨 상태 결정
            rainfall = weather_info.get('precipitation', 0)
            sky_status = weather_info.get('sky_stts', '')
            uv_index = weather_info.get('uv_idx', 0)
            
            # 야외 활동 추천 여부 결정
            recommend_outdoor = True
            weather_status = "맑음"
            
            if rainfall > 5:
                recommend_outdoor = False
                weather_status = "비"
            elif discomfort_index > 75:
                recommend_outdoor = False
                weather_status = "무더움"
            elif "흐림" in sky_status or "구름많음" in sky_status:
                recommend_outdoor = True
                weather_status = "흐림"
            elif uv_index > 7:
                recommend_outdoor = False
                weather_status = "자외선 주의"
            
            return {
                "district": district,
                "weather_status": weather_status,
                "rainfall": round(rainfall, 1),
                "discomfort_index": round(discomfort_index, 1),
                "solar_radiation": uv_index,
                "recommend_outdoor": recommend_outdoor
            }
        
        except Exception as e:
            self.logger.error(f"날씨 정보 추천 중 오류 발생: {e}")
            return {
                "district": district,
                "weather_status": "정보 없음",
                "rainfall": 0,
                "discomfort_index": 0,
                "solar_radiation": 0,
                "recommend_outdoor": True
            }
    
    def create_date_course(self, district, food_category, budget_range):
        """
        전체 데이트 코스 생성
        
        Args:
            district (str): 선택한 서울시 구 이름
            food_category (str): 선호하는 음식 카테고리
            budget_range (int): 예산 범위
        
        Returns:
            dict: 추천 데이트 코스 정보
        """
        try:
            # 1. 날씨 정보 조회
            weather_info = self.get_weather_recommendation(district)
            
            # 2. 맛집 추천
            recommended_restaurants = self.recommend_restaurants(
                district, food_category, budget_range
            )
            
            # 3. 날씨에 맞는 놀거리 추천
            recommended_attractions = self.recommend_attractions(
                district, weather_info
            )
            
            # 4. 첫 번째 맛집 근처의 카페 추천
            restaurant_location = None
            if not recommended_restaurants.empty:
                first_restaurant = recommended_restaurants.iloc[0]
                restaurant_location = (
                    first_restaurant['latitude'], 
                    first_restaurant['longitude']
                )
            
            recommended_cafes = self.recommend_cafes(
                district, restaurant_location
            )
            
            # 5. 추천 결과 반환
            return {
                "weather_info": weather_info,
                "restaurants": recommended_restaurants.to_dict('records'),
                "attractions": recommended_attractions.to_dict('records'),
                "cafes": recommended_cafes.to_dict('records')
            }
        
        except Exception as e:
            self.logger.error(f"데이트 코스 생성 중 오류 발생: {e}")
            return {
                "error": "데이트 코스를 생성할 수 없습니다.",
                "district": district
            }