// 공통 유틸리티 함수
const utils = {
    // 구/카테고리 선택 공통 로직
    setupSelection: function(selector, onSelectCallback) {
        const items = document.querySelectorAll(selector);
        
        items.forEach(item => {
            item.addEventListener('click', function() {
                // 기존 선택 해제
                items.forEach(el => el.classList.remove('selected'));
                
                // 현재 아이템 선택
                this.classList.add('selected');
                
                // 콜백 함수 호출 (선택된 아이템 정보 전달)
                if (onSelectCallback) {
                    onSelectCallback(this.dataset);
                }
            });
        });
    },

    // 비동기 데이터 로드 함수
    fetchData: async function(url, options = {}) {
        try {
            const response = await axios(url, options);
            return response.data;
        } catch (error) {
            console.error('데이터 로드 중 오류:', error);
            throw error;
        }
    }
};

// 페이지별 스크립트
const pageScripts = {
    // 인덱스 페이지 (구 선택)
    index: function() {
        utils.setupSelection('.btn-district', function(dataset) {
            const district = dataset.district;
            
            // 구 정보 가져오기
            utils.fetchData(`/api/district/${district}`)
                .then(data => {
                    console.log(`${district} 지역 정보:`, data);
                    // 다음 페이지로 이동
                    window.location.href = `/select/${district}?district=${district}`;
                })
                .catch(() => {
                    // 오류 발생해도 페이지 이동
                    window.location.href = `/select/${district}?district=${district}`;
                });
        });
    },

    // 메뉴 선택 페이지
    selectMenu: function() {
        const state = {
            district: null,
            selectedCategory: null,
            budgetRange: 2
        };

        // URL에서 구 정보 추출
        const urlParams = new URLSearchParams(window.location.search);
        state.district = urlParams.get('district');
        
        // 음식 카테고리 선택
        utils.setupSelection('.btn-category', function(dataset) {
            state.selectedCategory = dataset.category;
        });

        // 예산 범위 슬라이더
        const slider = document.getElementById('budget-range');
        const budgetDisplay = document.getElementById('budget-display');
        const budgetRanges = ['0원', '1만원', '1-2만원', '2-3만원', '3-5만원', '5만원 이상'];

        slider.addEventListener('input', function() {
            state.budgetRange = this.value;
            budgetDisplay.textContent = budgetRanges[this.value];
        });

        // 날씨 정보 로드
        async function fetchWeatherInfo() {
            try {
                const data = await utils.fetchData(`/api/district/${state.district}`);
                const weatherInfo = document.getElementById('current-weather');
                
                if (data.weather) {
                    weatherInfo.textContent = `${data.weather.temp}°C | 강수확률 ${data.weather.precipitation}% | ${data.weather.sky_stts}`;
                }
            } catch (error) {
                document.getElementById('current-weather').textContent = '날씨 정보를 불러올 수 없습니다.';
            }
        }

        // 코스 추천 버튼 클릭
        document.getElementById('recommend-btn').addEventListener('click', function() {
            const category = state.selectedCategory || '랜덤';
            window.location.href = `/result?district=${state.district}&food_category=${category}&budget_range=${state.budgetRange}`;
        });

        // 페이지 로드 시 날씨 정보 불러오기
        fetchWeatherInfo();
    },

    // 결과 페이지
    result: function() {
        const state = {
            district: null,
            foodCategory: null,
            budgetRange: null,
            selectedPlaces: {
                restaurants: null,
                attractions: null,
                cafes: null
            }
        };

        // URL 파라미터 추출
        const urlParams = new URLSearchParams(window.location.search);
        state.district = urlParams.get('district');
        state.foodCategory = urlParams.get('food_category');
        state.budgetRange = urlParams.get('budget_range');

        // 탭 전환 로직
        function setupTabNavigation() {
            const tabs = document.querySelectorAll('.tab');
            const contentSections = document.querySelectorAll('.content-section');

            tabs.forEach(tab => {
                tab.addEventListener('click', function() {
                    // 모든 탭과 섹션의 active 클래스 제거
                    tabs.forEach(t => t.classList.remove('active'));
                    contentSections.forEach(s => s.classList.remove('active'));

                    // 클릭된 탭과 해당 섹션에 active 클래스 추가
                    this.classList.add('active');
                    document.getElementById(this.dataset.section).classList.add('active');
                });
            });
        }

        // 날씨 정보 업데이트
        function updateWeatherInfo(weatherInfo) {
            const weatherDisplay = document.getElementById('weather-info');
            weatherDisplay.innerHTML = `
                <strong>${weatherInfo.district}</strong> | 
                ${weatherInfo.weather_status} | 
                온도: ${weatherInfo.discomfort_index}°C | 
                강수량: ${weatherInfo.rainfall}mm
            `;
        }

        // 장소 목록 렌더링
        function renderPlaces(type, places) {
            const container = document.getElementById(type);
            container.innerHTML = places.map((place, index) => `
                <div class="place-item" data-type="${type}" data-index="${index}">
                    <div class="place-details">
                        <strong>${place.name}</strong>
                        <p>${place.category || ''} | 평점: ${place.score || '정보 없음'}</p>
                    </div>
                </div>
            `).join('');

            // 장소 선택 이벤트 리스너 추가
            container.querySelectorAll('.place-item').forEach(item => {
                item.addEventListener('click', function() {
                    const type = this.dataset.type;
                    const index = this.dataset.index;

                    // 같은 타입의 기존 선택 해제
                    document.querySelectorAll(`.place-item[data-type="${type}"]`)
                        .forEach(el => el.classList.remove('selected'));

                    // 현재 아이템 선택
                    this.classList.add('selected');
                    state.selectedPlaces[type] = places[index];

                    // 모든 카테고리 선택 시 버튼 표시
                    checkAllPlacesSelected();
                });
            });
        }

        // 모든 장소 선택 확인
        function checkAllPlacesSelected() {
            const selectedCourseBtn = document.getElementById('selected-course-btn');
            const allSelected = Object.values(state.selectedPlaces).every(place => place !== null);

            if (allSelected) {
                selectedCourseBtn.style.display = 'block';
            }
        }

        // 데이트 코스 추천 API 호출
        async function fetchRecommendations() {
            try {
                const data = await utils.fetchData('/api/recommend', {
                    method: 'POST',
                    data: {
                        district: state.district,
                        food_category: state.foodCategory,
                        budget_range: state.budgetRange
                    }
                });

                const { weather_info, restaurants, attractions, cafes } = data;

                // 날씨 정보 업데이트
                updateWeatherInfo(weather_info);

                // 장소 목록 렌더링
                renderPlaces('restaurants', restaurants);
                renderPlaces('attractions', attractions);
                renderPlaces('cafes', cafes);

                // 탭 네비게이션 설정
                setupTabNavigation();

            } catch (error) {
                console.error('추천 데이터 로드 중 오류:', error);
                alert('데이트 코스를 불러오는 데 실패했습니다.');
            }
        }

        // 코스 보기 버튼 클릭 이벤트
        document.getElementById('selected-course-btn').addEventListener('click', function() {
            const { restaurants, attractions, cafes } = state.selectedPlaces;
            
            // 카카오맵 경로 표시 (임시 구현)
            const mapUrl = `https://map.kakao.com/link/map/${restaurants.name},${attractions.name},${cafes.name}`;
            window.open(mapUrl, '_blank');
        });

        // 페이지 로드 시 추천 데이터 불러오기
        fetchRecommendations();
    }
};

// 페이지 로드 시 스크립트 실행
document.addEventListener('DOMContentLoaded', function() {
    // 현재 페이지에 맞는 스크립트 실행
    if (document.querySelector('.btn-district')) {
        pageScripts.index();
    } else if (document.querySelector('.btn-category')) {
        pageScripts.selectMenu();
    } else if (document.querySelector('.content-section')) {
        pageScripts.result();
    }
});