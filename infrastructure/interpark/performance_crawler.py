import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

from infrastructure.web_driver.driver_manager import WebDriverManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class PerformanceCrawler:
    """인터파크 공연 정보 크롤러"""
    
    BASE_URL = "https://nol.interpark.com"
    TICKET_BASE_URL = "https://tickets.interpark.com"
    SEARCH_URL = f"{TICKET_BASE_URL}/search"
    DETAIL_URL = f"{TICKET_BASE_URL}/goods"
    LIST_URL = f"{TICKET_BASE_URL}/contents/genre/concert"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        })
        self.driver_manager = None
        
    def search_performances(self, keyword: str) -> List[Dict]:
        """공연 검색"""
        try:
            # 인터파크 티켓 사이트에서 검색
            search_url = f"{self.TICKET_BASE_URL}/search?q={requests.utils.quote(keyword)}"
            logger.info(f"공연 검색 중: {search_url}")
            
            response = self.session.get(search_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            performances = []
            
            # 검색 결과 파싱
            items = soup.select('.stit') 
            
            for item in items[:20]:
                try:
                    link = item.select_one('a')
                    if not link:
                        continue
                        
                    href = link.get('href', '')
                    if '/goods/' not in href:
                        continue
                        
                    goods_code = re.search(r'/goods/(\d+)', href)
                    if not goods_code:
                        continue
                    goods_code = goods_code.group(1)
                    
                    # 공연명 추출
                    name_elem = item.select_one('.fw_bold') or link
                    name = name_elem.text.strip() if name_elem else ''
                    
                    # 장소 추출
                    place_elem = item.select_one('.fw_normal')
                    place = place_elem.text.strip() if place_elem else ''
                    
                    # 날짜 추출
                    date_elem = item.select_one('.fw_light')
                    if date_elem:
                        date_text = date_elem.text.strip()
                        dates = re.findall(r'\d{4}\.\d{2}\.\d{2}', date_text)
                        start_date = dates[0] if dates else ''
                        end_date = dates[1] if len(dates) > 1 else start_date
                    else:
                        start_date = end_date = ''
                    
                    performance = {
                        'id': goods_code,
                        'name': name,
                        'place': place,
                        'start_date': start_date,
                        'end_date': end_date,
                        'poster_url': '',
                        'url': f"{self.DETAIL_URL}/{goods_code}"
                    }
                    
                    if name:
                        performances.append(performance)
                        
                except Exception as e:
                    logger.error(f"항목 파싱 오류: {str(e)}")
                    continue
            
            logger.info(f"{len(performances)}개의 공연 검색 결과")
            return performances
            
        except Exception as e:
            logger.error(f"공연 검색 실패: {str(e)}")
            return []
            
    def get_latest_performances(self, genre_code: str = "", page: int = 1, size: int = 40) -> List[Dict]:
        """최신 공연 목록 조회"""
        try:
            # 인터파크 콘서트 페이지 직접 크롤링
            url = "https://tickets.interpark.com/contents/genre/concert"
            logger.info(f"콘서트 페이지 크롤링: {url}")
            
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            performances = []
            
            # 모든 goods 링크 찾기 (가장 직접적인 방법)
            goods_links = soup.find_all('a', href=re.compile(r'/goods/(\d+)'))
            logger.info(f"{len(goods_links)}개의 공연 링크 발견")
            
            for link in goods_links[:size]:
                try:
                    href = link.get('href', '')
                    goods_match = re.search(r'/goods/(\d+)', href)
                    if not goods_match:
                        continue
                        
                    goods_code = goods_match.group(1)
                    
                    # 링크 텍스트를 공연명으로 사용
                    name = link.get_text(strip=True)
                    
                    # 이미지 태그 찾기
                    img = link.find('img')
                    if img:
                        name = img.get('alt', name).strip()
                        poster_url = img.get('src', '')
                    else:
                        poster_url = ''
                    
                    # 부모 요소에서 추가 정보 찾기
                    parent = link.parent
                    place = ''
                    start_date = ''
                    end_date = ''
                    
                    # 부모 요소의 텍스트에서 날짜 패턴 찾기
                    if parent:
                        parent_text = parent.get_text()
                        date_matches = re.findall(r'\d{4}\.\d{2}\.\d{2}', parent_text)
                        if date_matches:
                            start_date = date_matches[0]
                            end_date = date_matches[1] if len(date_matches) > 1 else start_date
                    
                    performance = {
                        'id': goods_code,
                        'name': name,
                        'place': place,
                        'start_date': start_date,
                        'end_date': end_date,
                        'poster_url': poster_url,
                        'url': f"{self.DETAIL_URL}/{goods_code}"
                    }
                    
                    if name and goods_code:
                        performances.append(performance)
                        logger.info(f"공연 추가: {name} (ID: {goods_code})")
                        
                except Exception as e:
                    logger.error(f"링크 파싱 오류: {str(e)}")
                    continue
            
            logger.info(f"총 {len(performances)}개의 공연 발견")
            return performances
            
        except Exception as e:
            logger.error(f"최신 공연 목록 가져오기 실패: {str(e)}")
            return []
            
            
    def get_performance_detail(self, performance_id: str) -> Optional[Dict]:
        """공연 상세 정보 조회"""
        try:
            url = f"{self.DETAIL_URL}/{performance_id}"
            logger.info(f"공연 상세 정보 가져오기: {url}")
            
            # Selenium으로 페이지 로드
            if not self.driver_manager:
                self.driver_manager = WebDriverManager()
                self.driver_manager.initialize(headless=True)
            
            driver = self.driver_manager.get_driver()
            wait = self.driver_manager.get_wait()
            
            driver.get(url)
            
            # 페이지 로드 대기
            time.sleep(3)
            
            # 날짜와 시간 정보 추출
            dates = []
            times = []
            
            try:
                # 캘린더 열기 버튼 클릭 시도
                calendar_btn = driver.find_element(By.CSS_SELECTOR, '[class*="calendar"], [class*="date"], .sideContainer.containerTop')
                if calendar_btn:
                    driver.execute_script("arguments[0].click();", calendar_btn)
                    time.sleep(1)
            except:
                pass
            
            # 날짜 추출
            try:
                # 다양한 날짜 셀렉터 시도
                date_selectors = [
                    'li[data-date]',
                    'li[data-playdate]',
                    '.calendar li.possible',
                    '.dateList li',
                    '[class*="date"][data-date]'
                ]
                
                for selector in date_selectors:
                    date_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in date_elements:
                        date_val = elem.get_attribute('data-date') or elem.get_attribute('data-playdate')
                        if date_val:
                            # YYYYMMDD를 YYYY-MM-DD로 변환
                            if len(date_val) == 8:
                                formatted_date = f"{date_val[:4]}-{date_val[4:6]}-{date_val[6:8]}"
                                dates.append(formatted_date)
                            else:
                                dates.append(date_val)
                
                # JavaScript에서 날짜 데이터 추출
                if not dates:
                    js_dates = driver.execute_script("""
                        var dates = [];
                        // 전역 변수에서 찾기
                        if (typeof playDateList !== 'undefined') {
                            dates = playDateList;
                        }
                        // DOM에서 찾기
                        document.querySelectorAll('[data-date], [data-playdate]').forEach(function(el) {
                            var date = el.getAttribute('data-date') || el.getAttribute('data-playdate');
                            if (date) dates.push(date);
                        });
                        return dates;
                    """)
                    if js_dates:
                        for date_val in js_dates:
                            if len(str(date_val)) == 8:
                                formatted_date = f"{str(date_val)[:4]}-{str(date_val)[4:6]}-{str(date_val)[6:8]}"
                                dates.append(formatted_date)
                            else:
                                dates.append(str(date_val))
                
            except Exception as e:
                logger.error(f"날짜 추출 중 오류: {str(e)}")
            
            # 시간 추출
            try:
                # 회차 선택 영역 클릭 시도
                time_btn = driver.find_element(By.CSS_SELECTOR, '[class*="time"], [class*="round"], .sideContainer.containerMiddle')
                if time_btn:
                    driver.execute_script("arguments[0].click();", time_btn)
                    time.sleep(1)
            except:
                pass
            
            try:
                # 다양한 시간 셀렉터 시도
                time_selectors = [
                    'li[data-time]',
                    'li[data-playtime]',
                    '.timeList li',
                    '.roundList li',
                    '[class*="time"][data-time]'
                ]
                
                for selector in time_selectors:
                    time_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in time_elements:
                        time_text = elem.text.strip()
                        # 시간 패턴 추출
                        time_matches = re.findall(r'\d{1,2}:\d{2}', time_text)
                        times.extend(time_matches)
                
                # JavaScript에서 시간 데이터 추출
                if not times:
                    js_times = driver.execute_script("""
                        var times = [];
                        // 전역 변수에서 찾기
                        if (typeof playTimeList !== 'undefined') {
                            times = playTimeList;
                        }
                        // DOM에서 텍스트 찾기
                        document.querySelectorAll('[class*="time"], [class*="round"]').forEach(function(el) {
                            var text = el.textContent;
                            var timeMatches = text.match(/\\d{1,2}:\\d{2}/g);
                            if (timeMatches) times = times.concat(timeMatches);
                        });
                        return times;
                    """)
                    if js_times:
                        times.extend(js_times)
                
            except Exception as e:
                logger.error(f"시간 추출 중 오류: {str(e)}")
            
            # 페이지 소스로 BeautifulSoup 생성
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 중복 제거
            dates = sorted(list(set(dates)))
            times = sorted(list(set(times)))
            
            if not dates:
                logger.warning("Selenium으로도 날짜 정보를 찾을 수 없음")
            
            if not times:
                logger.warning("Selenium으로도 시간 정보를 찾을 수 없음")
            
            detail = {
                'id': performance_id,
                'url': url,
                'dates': dates,
                'times': times,
                'seat_grades': self._extract_seat_grades(soup)
            }
            
            logger.info(f"추출된 날짜: {dates}")
            logger.info(f"추출된 시간: {times}")
            
            return detail
            
        except Exception as e:
            logger.error(f"공연 상세 정보 조회 실패: {str(e)}")
            return None
        finally:
            # WebDriver 종료
            if self.driver_manager:
                self.driver_manager.quit()
                self.driver_manager = None
            
    def _extract_dates(self, soup: BeautifulSoup) -> List[str]:
        """공연 날짜 추출"""
        dates = []
        try:
            # 1. JavaScript에서 날짜 데이터 찾기
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'playDate' in script.string:
                    # JSON 형태의 날짜 데이터 추출
                    date_matches = re.findall(r'"playDate"\s*:\s*"(\d{8})"', script.string)
                    for date_match in date_matches:
                        # YYYYMMDD를 YYYY-MM-DD로 변환
                        formatted_date = f"{date_match[:4]}-{date_match[4:6]}-{date_match[6:8]}"
                        dates.append(formatted_date)
            
            # 2. data-playdate 속성에서 찾기
            if not dates:
                elements_with_playdate = soup.find_all(attrs={'data-playdate': True})
                for elem in elements_with_playdate:
                    date_str = elem.get('data-playdate', '')
                    if date_str and len(date_str) == 8:
                        formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                        dates.append(formatted_date)
            
            # 3. sideContainer에서 찾기
            if not dates:
                date_container = soup.select_one('.sideContainer.containerTop.sideToggleWrap')
                if date_container:
                    # 날짜 리스트 아이템 찾기
                    date_elements = date_container.select('li[data-date]')
                    for elem in date_elements:
                        date_str = elem.get('data-date', '')
                        if date_str:
                            dates.append(date_str)
                    
                    # 텍스트에서 날짜 패턴 찾기
                    if not dates:
                        date_text = date_container.get_text()
                        # YYYY.MM.DD 또는 YYYY-MM-DD 패턴 찾기
                        date_pattern = re.compile(r'(\d{4}[-\.]\d{2}[-\.]\d{2})')
                        found_dates = date_pattern.findall(date_text)
                        dates.extend(found_dates)
            
            # 4. 전체 페이지에서 날짜 패턴 찾기
            if not dates:
                # 공연 기간 정보에서 찾기
                period_elem = soup.find(text=re.compile(r'공연기간|기간'))
                if period_elem:
                    parent = period_elem.parent
                    if parent:
                        period_text = parent.get_text()
                        date_matches = re.findall(r'\d{4}\.\d{2}\.\d{2}', period_text)
                        dates.extend([d.replace('.', '-') for d in date_matches])
                        
        except Exception as e:
            logger.error(f"날짜 추출 실패: {str(e)}")
        
        # 중복 제거 및 정렬
        dates = sorted(list(set(dates)))
        logger.debug(f"추출된 날짜 목록: {dates}")
        
        return dates
        
    def _extract_times(self, soup: BeautifulSoup) -> List[str]:
        """공연 시간 추출"""
        times = []
        try:
            # 1. JavaScript에서 시간 데이터 찾기
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and ('playTime' in script.string or 'scheduleData' in script.string):
                    # 시간 패턴 추출
                    time_matches = re.findall(r'(\d{1,2}:\d{2})', script.string)
                    times.extend(time_matches)
            
            # 2. data-playtime 속성에서 찾기
            if not times:
                elements_with_playtime = soup.find_all(attrs={'data-playtime': True})
                for elem in elements_with_playtime:
                    time_str = elem.get('data-playtime', '')
                    if time_str:
                        # HHmm 형식을 HH:mm로 변환
                        if len(time_str) == 4 and time_str.isdigit():
                            formatted_time = f"{time_str[:2]}:{time_str[2:4]}"
                            times.append(formatted_time)
                        elif ':' in time_str:
                            times.append(time_str)
            
            # 3. sideContainer에서 시간 찾기
            if not times:
                time_container = soup.select_one('.sideContainer.containerMiddle.sideToggleWrap')
                if time_container:
                    # 시간 리스트 아이템 찾기
                    time_elements = time_container.select('li')
                    for elem in time_elements:
                        time_text = elem.get_text(strip=True)
                        # 시간 패턴 추출 (예: 14:00, 19:30)
                        time_matches = re.findall(r'\d{1,2}:\d{2}', time_text)
                        times.extend(time_matches)
            
            # 4. 공연시간 정보에서 찾기
            if not times:
                # "공연시간", "시간" 텍스트 근처에서 찾기
                time_labels = soup.find_all(text=re.compile(r'공연시간|상영시간|시간'))
                for label in time_labels:
                    parent = label.parent
                    if parent:
                        sibling = parent.find_next_sibling()
                        if sibling:
                            time_text = sibling.get_text()
                        else:
                            time_text = parent.get_text()
                        
                        time_matches = re.findall(r'\d{1,2}:\d{2}', time_text)
                        times.extend(time_matches)
            
            # 5. 전체 페이지에서 시간 패턴 찾기
            if not times:
                # 회차 정보 영역 찾기
                schedule_areas = soup.find_all(['div', 'ul'], class_=re.compile(r'schedule|time|round', re.I))
                for area in schedule_areas:
                    area_text = area.get_text()
                    time_matches = re.findall(r'\b\d{1,2}:\d{2}\b', area_text)
                    times.extend(time_matches)
                    
        except Exception as e:
            logger.error(f"시간 추출 실패: {str(e)}")
        
        # 중복 제거 및 정렬
        times = sorted(list(set(times)))
        # 유효한 시간만 필터링 (00:00 ~ 23:59)
        valid_times = []
        for time in times:
            hour, minute = map(int, time.split(':'))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                valid_times.append(time)
        
        logger.debug(f"추출된 시간 목록: {valid_times}")
        
        return valid_times
        
    def _extract_seat_grades(self, soup: BeautifulSoup) -> List[Dict]:
        """좌석 등급 정보 추출"""
        grades = []
        try:
            grade_elements = soup.select('.seatGrade li')
            for elem in grade_elements:
                grade_name = elem.select_one('.name')
                grade_price = elem.select_one('.price')
                
                if grade_name and grade_price:
                    grades.append({
                        'name': grade_name.text.strip(),
                        'price': grade_price.text.strip()
                    })
                    
        except Exception as e:
            logger.error(f"좌석 등급 추출 실패: {str(e)}")
            
        return grades