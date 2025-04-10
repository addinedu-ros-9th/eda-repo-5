from flask import Flask, render_template, redirect, url_for, request, jsonify
import os
import logging
from recommendation_engine import RecommendationEngine
from db_connection import get_db_connection, execute_query, get_dataframe
from config import Config

# 로깅 설정
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Flask 애플리케이션 초기화
app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))

# 애플리케이션 설정
app.config.from_object(Config)

# 가격 형식 포맷팅 함수
def format_price(price):
    try:
        price = int(price)
        if price >= 10000:
            man = price // 10000
            chun = (price % 10000) // 1000
            return f"{man}만{chun}천원" if chun > 0 else f"{man}만원"
        elif price >= 1000:
            return f"{price // 1000}천원"
        else:
            return f"{price}원"
    except (ValueError, TypeError):
        return "금액 오류"

# 메인 페이지 (지도 선택 화면)
@app.route('/')
def index():
    return render_template('index.html')

# 선택된 구에 대한 정보 가져오기
@app.route('/api/district/<district_name>')
def get_district_info(district_name):
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "데이터베이스 연결 실패"}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # 최신 날씨 정보 가져오기
        weather_query = """
        SELECT datetime, temp, precipitation, precpt_type, humidity, air_idx, sky_stts
        FROM spot
        WHERE gu = %s
        ORDER BY datetime DESC
        LIMIT 1
        """
        cursor.execute(weather_query, (district_name,))
        weather_data = cursor.fetchone()
        
        # 구 내 맛집 수 가져오기
        restaurant_query = """
        SELECT COUNT(*) as count
        FROM restaurant
        WHERE address LIKE %s
        """
        cursor.execute(restaurant_query, (f'%{district_name}%',))
        restaurant_count = cursor.fetchone()['count']
        
        # 구 내 놀거리 수 가져오기
        attraction_query = """
        SELECT COUNT(*) as count
        FROM enjoy
        WHERE address LIKE %s
        """
        cursor.execute(attraction_query, (f'%{district_name}%',))
        attraction_count = cursor.fetchone()['count']
        
        # 구 내 카페 수 가져오기
        cafe_query = """
        SELECT COUNT(*) as count
        FROM cafe
        WHERE address LIKE %s
        """
        cursor.execute(cafe_query, (f'%{district_name}%',))
        cafe_count = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "district": district_name,
            "weather": weather_data,
            "stats": {
                "restaurants": restaurant_count,
                "attractions": attraction_count,
                "cafes": cafe_count
            }
        })
        
    except Exception as e:
        logger.error(f"구 정보 조회 중 오류 발생: {e}")
        return jsonify({"error": "정보를 가져오는 중 오류가 발생했습니다."}), 500

# 선택 화면
@app.route('/select/<district>')
def select_menu(district):
    return render_template('select_menu.html', district=district)

# 추천 API - min_budget와 max_budget 처리 추가
@app.route('/api/recommend', methods=['POST'])
def recommend_course():
    try:
        data = request.json
        district = data.get('district')
        station = data.get('station')  # 역 정보 추가
        food_category = data.get('food_category', '랜덤')
        
        # 새로운 이중 슬라이더 값 처리
        min_budget = data.get('min_budget')
        max_budget = data.get('max_budget')
        
        # 기존 budget_range 파라미터 호환성 유지
        budget_range = data.get('budget_range')
        
        engine = RecommendationEngine()
        
        # 새로운 예산 파라미터가 있으면 사용
        if min_budget is not None and max_budget is not None:
            min_budget = int(min_budget)
            max_budget = int(max_budget)
            
            # 수정된 RecommendationEngine의 create_date_course 호출
            course = engine.create_date_course(
                district=district,
                station=station,  # 역 정보 추가
                food_category=food_category,
                min_budget=min_budget,
                max_budget=max_budget
            )
        else:
            # 기존 방식 유지
            budget_range = int(budget_range) if budget_range is not None else 2
            course = engine.create_date_course(
                district=district,
                station=station,  # 역 정보 추가
                food_category=food_category,
                budget_range=budget_range
            )
        
        return jsonify(course)
    
    except Exception as e:
        logger.error(f"데이트 코스 추천 중 오류 발생: {e}")
        return jsonify({"error": "데이트 코스를 추천하는 중 오류가 발생했습니다."}), 500

# 결과 화면 - 이중 슬라이더 처리 추가
@app.route('/result')
def result():
    district = request.args.get('district')
    station = request.args.get('station')  # 역 정보 추가
    food_category = request.args.get('food_category', '랜덤')
    
    # 새로운 이중 슬라이더 값 처리
    min_budget = request.args.get('min_budget')
    max_budget = request.args.get('max_budget')
    
    # 기존 budget_range 파라미터 호환성 유지
    budget_range = request.args.get('budget_range')
    
    if not district:
        return redirect(url_for('index'))
    
    # 템플릿에 전달할 변수 준비
    template_vars = {
        'district': district,
        'station': station,  # 역 정보 추가
        'food_category': food_category
    }
    
    # 새로운 예산 파라미터가 있으면 사용
    if min_budget is not None and max_budget is not None:
        min_budget_int = int(min_budget)
        max_budget_int = int(max_budget)
        budget_display = f"{format_price(min_budget_int)} ~ {format_price(max_budget_int)}"
        
        template_vars.update({
            'budget_display': budget_display,
            'min_budget': min_budget_int,
            'max_budget': max_budget_int
        })
    else:
        # 기존 방식 유지
        budget_range = budget_range or '2'  # 기본값
        template_vars['budget_range'] = budget_range
    
    return render_template('result.html', **template_vars)

# 맵 화면
@app.route('/map')
def map_view():
    # URL 파라미터 확인
    if not (request.args.get('restaurant') and request.args.get('attraction') and request.args.get('cafe')):
        return redirect(url_for('index'))
    
    return render_template('map.html')

# 에러 핸들러
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
# 역 선택 페이지
@app.route('/stations/<district>')
def station_selection(district):
    return render_template('station.html', district=district)

# 역 정보 API
@app.route('/api/stations/<district>')
def get_stations(district):
    try:
        # 해당 구의 역 목록을 점수(star) 높은 순으로 가져오기
        query = """
        SELECT s.station, sc.star 
        FROM spot s
        JOIN score sc ON s.station = sc.station
        WHERE s.gu = %s AND s.station IS NOT NULL AND s.station != ''
        ORDER BY sc.star DESC
        LIMIT 5
        """
        
        stations = execute_query(query, (district,))
        
        if not stations:
            logger.warning(f"{district}에 대한 역 정보가 없습니다.")
            return jsonify({
                "district": district,
                "stations": []
            }), 404
        
        return jsonify({
            "district": district,
            "stations": stations
        })
        
    except Exception as e:
        logger.error(f"역 정보 조회 중 오류 발생: {e}")
        return jsonify({
            "error": "역 정보를 가져오는 중 오류가 발생했습니다.",
            "details": str(e)
        }), 500
# 디버그 모드 및 호스트 설정
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)