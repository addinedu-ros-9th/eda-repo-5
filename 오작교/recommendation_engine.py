# recommendation_engine.py
import pandas as pd
import numpy as np
import logging
import math
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
            '육류생회류': 41.8
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
        
        # 가격대를 5천원 단위로 구분하기 위한 새로운 열 추가
        self.restaurants_df['price_5k'] = self.restaurants_df['price'].fillna(0).astype(float)
        
        # 평가 점수 계산: score * log(review+1)
        self.restaurants_df['evaluation_score'] = self.restaurants_df.apply(
            lambda row: row['score'] * math.log(row['review'] + 1) if not pd.isna(row['score']) and not pd.isna(row['review']) else 0,
            axis=1
        )
    
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
        
        # 평가 점수 계산: score * log(review+1)
        self.cafes_df['evaluation_score'] = self.cafes_df.apply(
            lambda row: row['score'] * math.log(row['review'] + 1) if not pd.isna(row['score']) and not pd.isna(row['review']) else 0,
            axis=1
        )
    
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
    
    def recommend_restaurants(self, district, food_category, min_budget=None, max_budget=None, budget_range=None, limit=10):
        """
        선호 메뉴와 예산에 맞는 맛집 추천
        
        Args:
            district (str): 선택한 서울시 구 이름
            food_category (str): 선호하는 음식 카테고리
            min_budget (int, optional): 최소 예산 (5천원 단위)
            max_budget (int, optional): 최대 예산 (5천원 단위)
            budget_range (int, optional): 기존 예산 범위 (호환성 유지)
            limit (int): 추천 결과 최대 개수
        
        Returns:
            pandas.DataFrame: 추천 맛집 리스트
        """
        try:
            # 구 필터링
            filtered_df = self.restaurants_df[
                (self.restaurants_df['district'] == district)
            ]
            
            # 예산 범위 필터링 - 새로운 방식: 5천원 단위
            if min_budget is not None and max_budget is not None:
                filtered_df = filtered_df[
                    (filtered_df['price_5k'] >= min_budget) & 
                    (filtered_df['price_5k'] <= max_budget)
                ]
            # 기존 방식 호환성 유지
            elif budget_range is not None:
                budget_mapping = {
                    1: (0, 10000),       # 1만원 이하
                    2: (10000, 20000),   # 1-2만원
                    3: (20000, 30000),   # 2-3만원
                    4: (30000, 50000)    # 3-5만원
                }
                
                if budget_range in budget_mapping:
                    budget_min, budget_max = budget_mapping[budget_range]
                    filtered_df = filtered_df[
                        (filtered_df['price_5k'] >= budget_min) & 
                        (filtered_df['price_5k'] <= budget_max)
                    ]
            
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
                
                # 예산 필터는 유지
                if min_budget is not None and max_budget is not None:
                    filtered_df = filtered_df[
                        (filtered_df['price_5k'] >= min_budget) & 
                        (filtered_df['price_5k'] <= max_budget)
                    ]
            
            # 평가 점수가 19 이상인 맛집만 필터링
            filtered_df = filtered_df[filtered_df['evaluation_score'] >= 19]
            
            # 결과가 없으면 기준 낮추기
            if len(filtered_df) == 0:
                filtered_df = self.restaurants_df[
                    (self.restaurants_df['district'] == district)
                ]
                # 기준을 더 낮춘 평가 점수 적용
                filtered_df = filtered_df[filtered_df['evaluation_score'] >= 15]
            
            # 평가 점수 기준으로 상위 N개 결과 반환
            return filtered_df.sort_values('evaluation_score', ascending=False).head(limit)
        
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
            
            # 평가 점수가 14 이상인 카페만 필터링
            filtered_df = filtered_df[filtered_df['evaluation_score'] >= 14]
            
            # 결과가 없으면 기준 낮추기
            if len(filtered_df) == 0:
                filtered_df = self.cafes_df[
                    (self.cafes_df['district'] == district)
                ]
                # 기준을 더 낮춘 평가 점수 적용
                filtered_df = filtered_df[filtered_df['evaluation_score'] >= 10]
            
            # 맛집 위치 기반 거리 계산
            if restaurant_location:
                filtered_df['distance'] = filtered_df.apply(
                    lambda row: self._calculate_distance(
                        restaurant_location, 
                        (row['latitude'], row['longitude'])
                    ),
                    axis=1
                )
                
                # 거리를 고려한 최종 점수 계산 (가까울수록 높은 점수)
                filtered_df['final_score'] = filtered_df['evaluation_score'] - (filtered_df['distance'] * 0.01)
                
                result = filtered_df.sort_values('final_score', ascending=False).head(limit)
            else:
                # 맛집 위치 없을 경우 평가 점수 기준 정렬
                result = filtered_df.sort_values('evaluation_score', ascending=False).head(limit)
            
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
                    "temp": 25,  # 실제 온도
                    "rainfall": 0,
                    "discomfort_index": 0,
                    "solar_radiation": 5,
                    "recommend_outdoor": True
                }
            
            # 날씨 정보 추출
            weather_info = weather_data[0]
            
            # 온도와 습도 가져오기
            temperature = weather_info.get('temp', 25)
            humidity = weather_info.get('humidity', 50)
            
            # 불쾌지수 계산
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
                "temp": temperature,  # 실제 온도 추가
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
                "temp": 25,  # 실제 온도 추가
                "rainfall": 0,
                "discomfort_index": 0,
                "solar_radiation": 0,
                "recommend_outdoor": True
            }
    def create_date_course(self, district, food_category, station=None, budget_range=None, min_budget=None, max_budget=None):
        """
        전체 데이트 코스 생성
        
        Args:
            district (str): 선택한 서울시 구 이름
            food_category (str): 선호하는 음식 카테고리
            station (str, optional): 선택한 역 이름
            budget_range (int, optional): 기존 예산 범위
            min_budget (int, optional): 최소 예산 (5천원 단위)
            max_budget (int, optional): 최대 예산 (5천원 단위)
        
        Returns:
            dict: 추천 데이트 코스 정보
        """
        try:
            # 1. 날씨 정보 조회
            weather_info = self.get_weather_recommendation(district)
            
            # 역 정보가 있는 경우, 역 기반 추천 사용
            if station:
                # 역 근처 맛집 추천
                recommended_restaurants = self._recommend_restaurants_near_station(
                    district, station, food_category, min_budget, max_budget, budget_range
                )
                
                # 역 근처 놀거리 추천
                recommended_attractions = self._recommend_attractions_near_station(
                    district, station, weather_info
                )
                
                # 역 근처 카페 추천
                restaurant_location = None
                if not recommended_restaurants.empty:
                    first_restaurant = recommended_restaurants.iloc[0]
                    restaurant_location = (
                        first_restaurant['latitude'], 
                        first_restaurant['longitude']
                    )
                
                recommended_cafes = self._recommend_cafes_near_station(
                    district, station, restaurant_location
                )
            else:
                # 기존 구 기반 추천 로직
                # 2. 맛집 추천 (새로운 예산 범위 적용)
                recommended_restaurants = self.recommend_restaurants(
                    district, food_category, min_budget, max_budget, budget_range
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
                "station": station,  # 역 정보 추가
                "restaurants": recommended_restaurants.to_dict('records'),
                "attractions": recommended_attractions.to_dict('records'),
                "cafes": recommended_cafes.to_dict('records')
            }
        
        except Exception as e:
            self.logger.error(f"데이트 코스 생성 중 오류 발생: {e}")
            return {
                "error": "데이트 코스를 생성할 수 없습니다.",
                "district": district,
                "station": station  # 역 정보 추가
            }
            
    def _recommend_restaurants_near_station(self, district, station, food_category, min_budget=None, max_budget=None, budget_range=None, limit=10):
        """
        역 근처 맛집 추천
        
        Args:
            district (str): 선택한 서울시 구 이름
            station (str): 선택한 역 이름
            food_category (str): 선호하는 음식 카테고리
            min_budget (int, optional): 최소 예산 (5천원 단위)
            max_budget (int, optional): 최대 예산 (5천원 단위)
            budget_range (int, optional): 기존 예산 범위
            limit (int): 추천 결과 최대 개수
        
        Returns:
            pandas.DataFrame: 추천 맛집 리스트
        """
        try:
            # 해당 역 근처 맛집 필터링
            station_filtered_df = self.restaurants_df[
                self.restaurants_df['station'].str.contains(station, na=False, case=False)
            ]
            
            # 결과가 너무 적으면 구 전체 데이터로 확장
            if len(station_filtered_df) < 5:
                filtered_df = self.restaurants_df[
                    (self.restaurants_df['district'] == district)
                ]
            else:
                filtered_df = station_filtered_df
            
            # 예산 범위 필터링 - 새로운 방식: 5천원 단위
            if min_budget is not None and max_budget is not None:
                filtered_df = filtered_df[
                    (filtered_df['price_5k'] >= min_budget) & 
                    (filtered_df['price_5k'] <= max_budget)
                ]
            # 기존 방식 호환성 유지
            elif budget_range is not None:
                budget_mapping = {
                    1: (0, 10000),       # 1만원 이하
                    2: (10000, 20000),   # 1-2만원
                    3: (20000, 30000),   # 2-3만원
                    4: (30000, 50000)    # 3-5만원
                }
                
                if budget_range in budget_mapping:
                    budget_min, budget_max = budget_mapping[budget_range]
                    filtered_df = filtered_df[
                        (filtered_df['price_5k'] >= budget_min) & 
                        (filtered_df['price_5k'] <= budget_max)
                    ]
            
            # 음식 카테고리 필터링
            if food_category != "랜덤":
                filtered_df = filtered_df[
                    filtered_df['category'].str.contains(food_category, na=False, case=False)
                ]
            
            # 결과가 없으면 카테고리 필터 제거
            if len(filtered_df) == 0:
                if len(station_filtered_df) < 5:
                    filtered_df = self.restaurants_df[
                        (self.restaurants_df['district'] == district)
                    ]
                else:
                    filtered_df = station_filtered_df
                
                # 예산 필터는 유지
                if min_budget is not None and max_budget is not None:
                    filtered_df = filtered_df[
                        (filtered_df['price_5k'] >= min_budget) & 
                        (filtered_df['price_5k'] <= max_budget)
                    ]
            
            # 평가 점수 기준 필터링 (기준 완화)
            filtered_df = filtered_df[filtered_df['evaluation_score'] >= 15]
            
            # 결과가 없으면 더 낮은 기준 적용
            if len(filtered_df) == 0:
                if len(station_filtered_df) < 5:
                    filtered_df = self.restaurants_df[
                        (self.restaurants_df['district'] == district)
                    ]
                else:
                    filtered_df = station_filtered_df
                
                filtered_df = filtered_df[filtered_df['evaluation_score'] >= 10]
            
            # 평가 점수 기준으로 상위 N개 결과 반환
            return filtered_df.sort_values('evaluation_score', ascending=False).head(limit)
        
        except Exception as e:
            self.logger.error(f"역 근처 맛집 추천 중 오류 발생: {e}")
            return pd.DataFrame()

    def _recommend_attractions_near_station(self, district, station, weather_info, limit=10):
        """
        역 근처 놀거리 추천
        
        Args:
            district (str): 선택한 서울시 구 이름
            station (str): 선택한 역 이름
            weather_info (dict): 날씨 정보
            limit (int): 추천 결과 최대 개수
        
        Returns:
            pandas.DataFrame: 추천 놀거리 리스트
        """
        try:
            # 해당 역 근처 놀거리 필터링
            station_filtered_df = self.attractions_df[
                self.attractions_df['station'].str.contains(station, na=False, case=False)
            ]
            
            # 결과가 너무 적으면 구 전체 데이터로 확장
            if len(station_filtered_df) < 5:
                filtered_df = self.attractions_df[
                    (self.attractions_df['district'] == district)
                ]
            else:
                filtered_df = station_filtered_df
            
            # 날씨 기반 필터링
            if not weather_info.get('recommend_outdoor', True):
                indoor_df = filtered_df[filtered_df['activity_type'] == '실내']
                # 실내 장소가 충분하면 실내만 추천
                if len(indoor_df) >= 3:
                    filtered_df = indoor_df
            
            # 정렬 및 상위 N개 반환
            return filtered_df.sort_values('normalized_reviews', ascending=False).head(limit)
        
        except Exception as e:
            self.logger.error(f"역 근처 놀거리 추천 중 오류 발생: {e}")
            return pd.DataFrame()

    def _recommend_cafes_near_station(self, district, station, restaurant_location=None, limit=10):
        """
        역 근처 카페 추천
        
        Args:
            district (str): 선택한 서울시 구 이름
            station (str): 선택한 역 이름
            restaurant_location (tuple): 추천된 맛집 위치 (위도, 경도)
            limit (int): 추천 결과 최대 개수
        
        Returns:
            pandas.DataFrame: 추천 카페 리스트
        """
        try:
            # 해당 역 근처 카페 필터링
            station_filtered_df = self.cafes_df[
                self.cafes_df['station'].str.contains(station, na=False, case=False)
            ]
            
            # 결과가 너무 적으면 구 전체 데이터로 확장
            if len(station_filtered_df) < 5:
                filtered_df = self.cafes_df[
                    (self.cafes_df['district'] == district)
                ]
            else:
                filtered_df = station_filtered_df
            
            # 평가 점수 기준 필터링
            filtered_df = filtered_df[filtered_df['evaluation_score'] >= 14]
            
            # 결과가 없으면 기준 낮추기
            if len(filtered_df) == 0:
                if len(station_filtered_df) < 5:
                    filtered_df = self.cafes_df[
                        (self.cafes_df['district'] == district)
                    ]
                else:
                    filtered_df = station_filtered_df
                
                filtered_df = filtered_df[filtered_df['evaluation_score'] >= 10]
            
            # 맛집 위치 기반 거리 계산
            if restaurant_location:
                filtered_df['distance'] = filtered_df.apply(
                    lambda row: self._calculate_distance(
                        restaurant_location, 
                        (row['latitude'], row['longitude'])
                    ),
                    axis=1
                )
                
                # 거리를 고려한 최종 점수 계산 (가까울수록 높은 점수)
                filtered_df['final_score'] = filtered_df['evaluation_score'] - (filtered_df['distance'] * 0.01)
                
                result = filtered_df.sort_values('final_score', ascending=False).head(limit)
            else:
                # 맛집 위치 없을 경우 평가 점수 기준 정렬
                result = filtered_df.sort_values('evaluation_score', ascending=False).head(limit)
            
            return result
        
        except Exception as e:
            self.logger.error(f"역 근처 카페 추천 중 오류 발생: {e}")
            return pd.DataFrame()


    def calculate_distance(self, point1, point2):
        """
        두 지점 간의 거리를 Haversine 공식으로 계산
        
        Args:
            point1 (tuple): 첫 번째 지점 좌표 (위도, 경도)
            point2 (tuple): 두 번째 지점 좌표 (위도, 경도)
        
        Returns:
            float: 두 지점 간 거리 (미터)
        """
        import math
        
        # 널 체크
        if not point1 or not point2:
            return float('inf')
        
        # 지구 반경(km)
        R = 6371
        
        try:
            # 라디안으로 변환
            lat1 = math.radians(float(point1[0]))
            lon1 = math.radians(float(point1[1]))
            lat2 = math.radians(float(point2[0]))
            lon2 = math.radians(float(point2[1]))
            
            # Haversine 공식
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            distance = R * c * 1000  # 미터 단위로 변환
            
            # 도시 환경 보정 계수 적용 (직선 거리의 1.4배로 실제 도보 거리 추정)
            adjusted_distance = distance * 1.4
            
            return adjusted_distance
        except Exception as e:
            self.logger.error(f"거리 계산 중 오류 발생: {e}")
            return float('inf')

    def sort_places_by_distance(self, center_point, places_list):
        """
        중심점에서부터 가까운 순으로 장소 목록 정렬
        
        Args:
            center_point (tuple): 중심 좌표 (위도, 경도)
            places_list (list): 정렬할 장소 목록
        
        Returns:
            list: 거리순으로 정렬된 장소 목록
        """
        # 각 장소에 거리 속성 추가
        for place in places_list:
            place_point = (place.get('latitude'), place.get('longitude'))
            place['distance'] = self.calculate_distance(center_point, place_point)
        
        # 거리 기준으로 정렬
        return sorted(places_list, key=lambda x: x.get('distance', float('inf')))

    def recommend_optimized_route(self, selected_places):
        """
        선택된 장소들의 최적 경로 추천
        
        Args:
            selected_places (dict): 선택된 장소 정보 (맛집, 놀거리, 카페)
        
        Returns:
            dict: 최적화된 경로 정보
        """
        try:
            # 선택된 장소 추출
            restaurant = selected_places.get('restaurant')
            attraction = selected_places.get('attraction')
            cafe = selected_places.get('cafe')
            
            if not (restaurant and attraction and cafe):
                return {
                    "error": "모든 장소를 선택해야 합니다."
                }
            
            # 맛집 좌표를 중심으로 거리 계산
            restaurant_point = (restaurant.get('latitude'), restaurant.get('longitude'))
            
            # 맛집-놀거리, 맛집-카페 거리 계산
            attraction_distance = self.calculate_distance(
                restaurant_point, 
                (attraction.get('latitude'), attraction.get('longitude'))
            )
            
            cafe_distance = self.calculate_distance(
                restaurant_point, 
                (cafe.get('latitude'), cafe.get('longitude'))
            )
            
            # 경로 순서 결정 (맛집 → 가까운 장소 → 먼 장소)
            if attraction_distance <= cafe_distance:
                route_order = [restaurant, attraction, cafe]
                second_point = (attraction.get('latitude'), attraction.get('longitude'))
                third_point = (cafe.get('latitude'), cafe.get('longitude'))
            else:
                route_order = [restaurant, cafe, attraction]
                second_point = (cafe.get('latitude'), cafe.get('longitude'))
                third_point = (attraction.get('latitude'), attraction.get('longitude'))
            
            # 각 구간별 거리 계산
            first_distance = min(attraction_distance, cafe_distance)
            second_distance = self.calculate_distance(second_point, third_point)
            
            # 총 거리
            total_distance = first_distance + second_distance
            
            return {
                "route": route_order,
                "distances": {
                    "first_segment": round(first_distance),
                    "second_segment": round(second_distance),
                    "total": round(total_distance)
                }
            }
            
        except Exception as e:
            self.logger.error(f"경로 최적화 중 오류 발생: {e}")
            return {
                "error": "경로를 계산할 수 없습니다.",
                "details": str(e)
            }