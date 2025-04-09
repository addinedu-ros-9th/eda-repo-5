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

# 추천 API
@app.route('/api/recommend', methods=['POST'])
def recommend_course():
    try:
        data = request.json
        district = data.get('district')
        food_category = data.get('food_category', '랜덤')
        budget_range = int(data.get('budget_range', 2))  # 기본값: 1-2만원
        
        engine = RecommendationEngine()
        course = engine.create_date_course(district, food_category, budget_range)
        
        return jsonify(course)
    
    except Exception as e:
        logger.error(f"데이트 코스 추천 중 오류 발생: {e}")
        return jsonify({"error": "데이트 코스를 추천하는 중 오류가 발생했습니다."}), 500

# 결과 화면
@app.route('/result')
def result():
    district = request.args.get('district')
    food_category = request.args.get('food_category', '랜덤')
    budget_range = request.args.get('budget_range', '2')
    
    if not district:
        return redirect(url_for('index'))
    
    return render_template(
        'result.html', 
        district=district, 
        food_category=food_category, 
        budget_range=budget_range
    )

# 에러 핸들러
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# 디버그 모드 및 호스트 설정
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)