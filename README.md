# 오작교 - 서울 데이트 코스 추천 서비스

서울시 데이터를 기반으로, 선택에 어려움을 겪는 커플들을 위해 **최적의 데이트 코스**를 추천하는 프로젝트입니다.  
맛집, 카페, 놀거리 데이터를 분석하고, 이를 활용해 좋은 데이트 코스를 추천하는 서비스를 구현하였습니다.

---

## 💡 서비스 기능 및 설명

### 1. 지역 선택 기능

서울시 25개 자치구 중 하나를 선택하여 데이트 코스 추천 범위를 설정할 수 있습니다.

![app_gu_selection](https://github.com/addinedu-ros-9th/eda-repo-5/blob/main/image/app_gu_selection.gif)


### 2. 지하철역 선택 기능

선택한 자치구에 포함된 지하철역 중 하나를 선택할 수 있으며,  
각 역에는 내부 분석을 바탕으로 산출된 데이트 선호도 점수가 함께 표시됩니다.

![app_station_select](https://github.com/addinedu-ros-9th/eda-repo-5/blob/main/image/app_station_select.gif)


### 3. 메뉴 및 가격 선택 기능

선호하는 음식 종류와 가격대를 설정할 수 있으며,  
랜덤 추천 기능 선택 시 20대 여성의 외식 선호도 데이터를 기반으로 자동 추천됩니다.

![app_menu_select](https://github.com/addinedu-ros-9th/eda-repo-5/blob/main/image/app_menu_select.gif)


### 4. 추천 장소 선택 및 거리 정보 표시 기능

날씨와 평가지표를 고려한 알고리즘을 통해 맛집, 카페, 놀거리를 추천하고,  
선택한 장소 간의 거리 및 예상 도보 시간이 함께 제공됩니다.

![app_show_course](https://github.com/addinedu-ros-9th/eda-repo-5/blob/main/image/app_show_course.gif)

---

## 📦 프로젝트 개요
### 팀 구성원 및 역할

| 이름   | 주요 역할 |
|--------|-----------|
| **유영훈** | - DB 제작 및 관리 <br> - 카카오맵/네이버지도 맛집·놀거리 데이터 크롤링 <br> - 놀거리,맛집,카페 데이터 분석 및 시각화 <br> - 발표자료 제작<br> - README 작성|
| **김종명** | - 서울시 공공데이터 크롤링 <br> - 카카오맵 카페 데이터 크롤링 <br> - 여가생활, 여성 소비, 날씨 데이터 수집 및 분석, 시각화 <br> - 데이터 기반 알고리즘 설계 및 GUI 개발 | 
| **김경옥** | - 카카오맵/네이버지도 맛집·카페·놀거리 데이터 크롤링 <br> - 발표자료 제작 |
### 기간
2025년 3월 24일 ~ 2025년 3월 28일



### 사용 기술

| 분류 | 기술 |
|------|------|
| 개발 환경 |![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white),	![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-0078d7.svg?style=for-the-badge&logo=visual-studio-code&logoColor=white),![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
| 데이터 분석 및 시각화 | 	![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white),![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white),![Plotly](https://img.shields.io/badge/Plotly-%233F4F75.svg?style=for-the-badge&logo=plotly&logoColor=white),![Matplotlib](https://img.shields.io/badge/Matplotlib-%23ffffff.svg?style=for-the-badge&logo=Matplotlib&logoColor=black),![Seaborn](https://img.shields.io/badge/-Seaborn-3776AB?style=flat&logo=python&logoColor=white&size=40x40)
| 크롤링 |![Selenium](https://img.shields.io/badge/Selenium-43B02A?logo=Selenium&logoColor=white),![Beautifulsoup](https://shields.io/badge/BeautifulSoup-4-green)
| 데이터베이스 |![AWS](https://img.shields.io/badge/AWS-232F3E?style=flat&logo=amazonwebservices&logoColor=white),![Mysql](https://shields.io/badge/MySQL-lightgrey?logo=mysql&style=plastic&logoColor=white&labelColor=blue)
| 협업 | ![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white),![Confluence](https://img.shields.io/static/v1?style=for-the-badge&message=Confluence&color=172B4D&logo=Confluence&logoColor=FFFFFF&label=)



### 요구사항 정의

#### 사용자 요구사항
- 원하는 지역에서 데이트 코스를 추천받고 싶다.
- 본인의 취향(음식 종류, 가격대)에 맞는 장소를 선택하고 싶다.
- 날씨를 반영해 데이트 코스를 추천받고 싶다.
- 여러 데이트 코스를 추천받고 싶다.
- 가까운 거리 내에 있는 데이트 장소들을 추천받고 싶다.

#### 시스템 요구사항
- 선호 요소 선택 기능 : 데이트 지역,음식 카테고리와 가격대 선택
- 날씨/맛집/카페/놀거리 정보 수집 및 저장 기능 : 실시간 날씨정보를 서울시 공공데이터API로,평점/리뷰수/평균가격 등 데이터를 네이버지도와 카카오맵으로 수집 및 DB에 저장
  맛집/카페/놀거리 top10 추천 기능 : 사용자 입력과 내부 평가 지표를 기준으로 각 맛집/카페/놀거리별 상위 10개 추천
- 맛집/카페/놀거리 1개씩 선택 기능 : 각 분류에서 추천된 장소top10 중 각각 1개씩 선택
- 최적 동선 코스 생성 기능 : 선택된 장소들 총3개를 기반으로 최적 경로 자동 구성 및 시각화
- 지도 및 이동 정보 표시 기능 : 장소 위치, 이동 경로, 예상 시간 등 지도 기반 표시
- 저장/공유/후기/히스토리 기능 : 코스 저장,공유,후기 작성,과거 기록 보기 기능

---
## 📁데이터 수집 및 처리

### 데이터 수집 경로

| 데이터 종류       | 출처                      | 수집 방법      |
|------------------|---------------------------|---------------|
| 맛집/카페        | 카카오맵                   | Selenium, beautifulsoup 크롤링 |
| 놀거리           | 네이버 지도                | Selenium, beautifulsoup 크롤링 |
| 명소 주변 지하철 | 구글 맵스 API              | API 호출       |
| 서울시 명소 정보 | 서울시 도시데이터 API         | API 호출     |
| 실시간 날씨 데이터       | 서울시 도시데이터 API      | API 호출       |
| 2024년 날씨 데이터    | 기상청 기상자료포털      | CSV       |
| 성/연령대 식품 및 외식 소비성향 데이터   | 농식품 빅데이터 거래소  | CSV    |
| 기타 데이터    | 공공데이터포털 통계        | CSV           |


### ER 다이어그램
- 주요 테이블: `restaurant`, `cafe`, `enjoy`, `spot`, `score`
- 크롤링/실시간 데이터 저장용 DB(spot,enjoy,cafe,restaurant)와 분석 결과 저장용 DB(score) 분리
![ER_diagram](https://github.com/addinedu-ros-9th/eda-repo-5/blob/main/image/DB_structure.png)
---

### 데이터 통합 및 전처리

본 프로젝트에서는 다양한 출처의 데이터를 통합하고, 사용자 맞춤형 데이트 코스 추천을 위한 지표를 산출하기 위해 다음과 같은 전처리 과정을 수행하였습니다.  
전처리 과정은 **DB에 저장된 원천 데이터 처리**와 **데이터프레임 기반 분석 처리**로 나뉘며, 각 처리 단계는 다음과 같습니다.



#### 1. DB 저장 및 전처리 (원천 데이터 처리)

##### 전체 데이터 흐름 요약

1. 서울시 명소 데이터 → 
2. 명소 기준 지하철역(station) 추출 →
3. 역 기반 주변 장소(cafe/restaurant/enjoy) 수집 →
4. 주소 기반 위경도 변환 (Google Maps API) →
5. DB 저장

##### 1) `spot` 테이블: 명소 정보 수집
- 서울시 도시데이터 API로부터 명소의 주소, 시간대별 인구, 기온, 습도, 풍속 등 정보를 수집
- 명소 기준으로 가장 가까운 지하철역(station)을 매핑하여 저장

##### 2) 주변 장소 정보 크롤링
- `spot` 테이블에서 추출한 **지하철역 이름**을 기반으로
  - **맛집/카페**: 카카오맵
  - **놀거리**: 네이버 지도  
  에서 장소 정보를 크롤링하여 수집

##### 3) 주소 기반 위경도 좌표 변환
- 크롤링된 장소들의 주소를 Google Maps API를 통해 위도/경도 정보로 변환

##### 4) 장소별 데이터베이스 저장
- 정제 및 변환된 데이터를 다음 테이블에 저장
  - `restaurant`: 맛집 정보
  - `cafe`: 카페 정보
  - `enjoy`: 놀거리 정보
  - `spot`: 명소 및 해당 지하철역 정보



#### 2. 데이터프레임 기반 분석 및 지표 계산

##### 목적
DB에 저장된 원천 데이터를 기반으로, **사용자 맞춤형 추천을 위한 지표를 계산**하고  
이를 통해 **역 단위 종합 점수**를 산출하여 추천 우선순위를 설정합니다.

##### 1) 평가지표 계산
- **맛집 / 카페**  
  `평가지수 = 평점 × log(리뷰 수 + 1)`
- **맛집 추가 지표**  
  `가성비 지수 = 평가지수 / 평균가격`
- **놀거리**  
  `리뷰 수 기준 지표 = log(리뷰 수 + 1)`

##### 2) 지표 정규화 및 역별 점수 산출
- 각 지표를 0~100점 범위로 정규화
- 역 단위로 장소들의 평균 점수를 계산
- 맛집 + 카페 + 놀거리의 평균값을 종합하여 **종합 점수 산출**

##### 3) 최종 결과 DB 저장
- 분석된 **역별 종합 점수 결과**는 `score` 테이블에 저장
- 사용자 입력에 따라 상위 지역 및 장소를 추천하는 데 활용
---

## 📊 데이터 분석 및 결과

### 가설
1. 카페, 맛집, 놀거리 순으로 구성된 코스가 이상적이다.
2. 카페, 맛집, 놀거리는 리뷰 수, 평점이 높을수록 선호도가 높다.
3. 식당의 경우 가격까지 고려한 가성비 지수가 중요하다.
4. 불쾌지수가 높을 땐 실내 위주 놀거리 추천이 적절하다.



### 시각화 기반 분석 결과
#### 여가생활 공간 이용 순위 TOP 3  
데이트 코스 구성 시 필수 고려 요소는 **카페와 식당**이다.

![free_time_usage](https://github.com/addinedu-ros-9th/eda-repo-5/blob/main/image/free_time_usage.png)

> 1위: 카페 (17.4%)  
> 2위: 식당 (14.5%)  
> 3위: 아파트 내 공터 (14.1%)



#### 여가생활 불만족 이유 TOP 3  
**경제적 부담**이 가장 큰 불만족 요소 → 데이트 코스 구성 시 **가격**이 매우 중요!

![ree_time_unsatisfied](https://github.com/addinedu-ros-9th/eda-repo-5/blob/main/image/free_time_unsatifsied.png)

> 1위: 경제적 부담 (56.2%)  
> 2위: 시간 부족 (24.2%)  
> 3위: 체력 부족 (14.3%)



#### 카페와 식당의 평균 가격  
데이트 지출에서 가장 큰 비중은 **식당**! (1인 평균 1만원)

![pricee_cafe](https://github.com/addinedu-ros-9th/eda-repo-5/blob/main/image/price_cafe.png)  
![price_restaurant](https://github.com/addinedu-ros-9th/eda-repo-5/blob/main/image/price_restaurant.png)



#### 주말 평균 여가 시간  
평균 여가 시간은 **5.5시간** → 최소한 이 시간을 커버하는 데이트 코스가 필요 → 놀거리,카페,맛집 3종 코스로 커버

![free_time](https://github.com/addinedu-ros-9th/eda-repo-5/blob/main/image/free_time.png)



#### 20대 여성 외식 매출액  
20대 여성은 **고기요리 > 한식 > 일식** 순으로 외식을 선호

![women_price](https://github.com/addinedu-ros-9th/eda-repo-5/blob/main/image/women_price.png)



#### 20대 여성 역별 외식 매출액  
가장 많이 소비하는 지역은 **강남역, 건대입구역, 신촌역**

![women_station](https://github.com/addinedu-ros-9th/eda-repo-5/blob/main/image/women_station.png)



#### 주말 기상 데이터와 이동 인구  
**불쾌지수 75 이상**일 때는 실내 중심 놀거리 추천 필요

![weather_population1](https://github.com/addinedu-ros-9th/eda-repo-5/blob/main/image/weather_population1.png)  
![weather_population2](https://github.com/addinedu-ros-9th/eda-repo-5/blob/main/image/weather_population2.png)



#### 좋은 놀거리의 기준  
**평가지표: `log(리뷰 수 + 1)`**  
**순위 기준: 평가지표가 평균 이상인 놀거리의 수를 기준으로 역별 순위 도출**  
→ 결과: **경복궁역, 서울역, 동대문역사문화공원역** 순

![enjoy_histogram](https://github.com/addinedu-ros-9th/eda-repo-5/blob/main/image/enjoy_histogram.png)  
![enjoy_station](https://github.com/addinedu-ros-9th/eda-repo-5/blob/main/image/enjoy_station.png)



#### 좋은 카페의 기준  
**평가지표: `별점 × log(리뷰 수 + 1)`**  
**순위 기준: 평가지표가 평균 이상인 카페 수를 기준으로 역별 순위 도출**  
→ 결과: **합정역, 뚝섬역, 종로3가역** 순

![cafe_histogram](https://github.com/addinedu-ros-9th/eda-repo-5/blob/main/image/cafe_histogram.png)  
![cafe_station](https://github.com/addinedu-ros-9th/eda-repo-5/blob/main/image/cafe_station.png)



#### 좋은 맛집의 기준  
**평가지표 1: `별점 × log(리뷰 수 + 1)`**  
**평가지표 2: `별점 × log(리뷰 수 + 1) ÷ 평균가격`** *(가성비 반영)*  
**순위 기준: 평가지표가 평균 이상인 맛집 수를 기준으로 역별 순위 도출**  
→ 1차 기준 순위: **홍대입구 > 혜화 > 신사**  
→ 2차 기준 순위: **홍대입구 > 혜화 > 이태원**

![restaurant_value_histogram](https://github.com/addinedu-ros-9th/eda-repo-5/blob/main/image/restaurant_value_histogram.png)  
![restaurant_value_station](https://github.com/addinedu-ros-9th/eda-repo-5/blob/main/image/restaurant_value_station.png)  
![restaurant_performance_histogram](https://github.com/addinedu-ros-9th/eda-repo-5/blob/main/image/restaurant_performance_histogram.png)  
![restaurant_performance_station](https://github.com/addinedu-ros-9th/eda-repo-5/blob/main/image/restaurant_performance_station.png)



#### 종합 기준 (놀거리 + 맛집 + 카페 평균 점수 기반 종합 평가)  
**종합 점수 계산 방식**:

1. 각 역에서 놀거리, 카페, 맛집 각각  
   → **평균 이상 가게 수 기준으로 1등은 100점**, 나머지는 **0~100점으로 정규화**

2. 세 항목의 점수 평균을 구해 **종합 점수 원본 계산**

3. 그 평균 점수를 기준으로 다시 정규화 →  
   **최종적으로 1등은 100점**, 나머지는 **0~100점으로 수치화한 종합 점수** 도출

→ 결과: **합정역 > 혜화역 > 경복궁역**

![station](https://github.com/addinedu-ros-9th/eda-repo-5/blob/main/image/station.png)



### 결론

1. **카페 → 맛집 → 놀거리 순의 코스 구성은 이상적**이다.  
   → 여가생활 공간 이용 순위에서 카페와 식당이 상위에 위치하고, 평균 여가 시간이 5.5시간으로 확인되어 해당 구성이 사용자 생활 패턴과 부합함.

2. **리뷰 수와 평점이 높은 장소일수록 선호도가 높다**는 가설은,  
   → 본 프로젝트에서는 해당 요소를 기반으로 평가지표를 산정하였으며, 상위 지역이 주요 상권과 일부 일치하는 결과를 도출하였으나,  
   **실제 선호도(방문자 수, 매출 등)와의 직접적 검증은 이뤄지지 않아 후속 검토가 필요함.**

3. **맛집의 경우, 가격을 반영한 가성비 지수가 중요하다는 가설**에 따라  
   → 가성비 지표를 통해 기존 순위와 다른 결과가 도출되었고, 가격이 평가에 영향을 줄 수 있다는 가능성을 확인함.  
   다만 **해당 지표가 실제 만족도나 방문 행동과 일치하는지는 검증되지 않음.**

4. **불쾌지수가 높을 때는 실내 놀거리 추천이 적절하다.**  
   → 불쾌지수 75 이상인 날에 외부 활동 감소 경향이 관찰되어, 날씨 조건에 따라 실내 중심 코스를 추천할 필요성이 뚜렷함.
   

### 분석 한계점

1. **평가지표의 실제 선호도 설명력 부족**  
   리뷰 수와 평점을 기반으로 평가지표를 설정하였으나, 실제 사용자 선호나 방문 행동과의 상관관계는 검증되지 않음.  

2. **외부 실측 데이터와의 연계 부족**  
   방문자 수, 매출, 검색량 등 실제 사용자 행동 데이터를 활용한 교차 검증이 부족함.

3. **정성적 요소 미반영**  
   장소의 분위기, 서비스 품질, 이용자 리뷰의 감성 등 정성적 요소는 고려되지 않았음.
---

## 🔧프로젝트 문제점 및 해결
프로젝트 진행 중 크고 명확한 오류보다도, 여러 자잘한 이슈들이 반복적으로 발생하며 전체 개발 흐름의 난이도를 높였습니다.  
이러한 문제들은 단독으로는 단순해 보이지만, 해결 과정에서 많은 시행착오와 기술적 트러블슈팅 경험을 쌓을 수 있는 기회가 되었습니다

### 주요 문제 사례 및 해결 방식
**지하철역 정보 누락**  
- 일부 명소 주변 지하철 정보 누락 → 누락된 명소만 가장 가까운 지하철역 정보를 Google Maps API로 습득
  ![hard_station](https://github.com/addinedu-ros-9th/eda-repo-5/blob/main/image/hard_station.png)

**네이버 지도 iframe 구조**  
-놀거리 정보는 iframe 내부에 포함되어 있어, Selenium으로 바로 접근할 수 없음 → driver.switch_to.frame()을 사용해 iframe으로 전환 후 접근 가능
![hard_iframe](https://github.com/addinedu-ros-9th/eda-repo-5/blob/main/image/hard_iframe.png)

**크롤링 시 요소 stale 문제**  
- 요소 클릭시 요소가 사라지거나 갱신되면서 `StaleElementReferenceException` 발생 → WebDriverWait과 예외 처리 로직 반복 삽입
![hard_crawl](https://github.com/addinedu-ros-9th/eda-repo-5/blob/main/image/hard_crawl.png)
---
## ⚠️프로젝트 한계점

1. **지역 범위의 제한**  
   - 본 프로젝트는 서울시 25개 자치구 내의 데이터만을 활용하여, 타 지역 사용자에게는 적용할 수 없는 제한이 존재함.

2. **최적 동선 지도 시각화 미구현**  
   - 장소 간 거리와 소요 시간 정보는 계산했으나, 실제 지도를 통한 동선 시각화 기능은 구현되지 않음.

3. **후기 및 히스토리 기능 미구현**  
   - 사용자 후기 작성, 코스 저장, 과거 기록 열람 등 일부 핵심 기능이 기획 단계에만 머물러 있고, 구현되지 못함.

4. **사용자 취향 기반 추천 기능의 한계**  
   - 음식 종류 및 가격대 필터는 적용했지만, 사용자 행동 데이터를 활용한 정교한 개인화 추천은 미구현 상태임.
---
> 감사합니다!  
> 본 프로젝트는 선택이 어려운 커플들을 위한 작은 다리가 되고자 하는 마음에서 시작되었습니다.
