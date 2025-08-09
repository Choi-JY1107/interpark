import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Callable, List
import threading
from PIL import Image, ImageTk
import requests
from io import BytesIO
import logging

from infrastructure.interpark.performance_crawler import PerformanceCrawler

logger = logging.getLogger(__name__)


class PerformanceSearchDialog:
    """공연 검색 다이얼로그"""
    
    def __init__(self, parent):
        self.parent = parent
        self.crawler = PerformanceCrawler()
        self.selected_performance = None
        self.selected_date = None
        self.selected_time = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("공연 검색")
        self.dialog.geometry("900x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._setup_ui()
        # 다이얼로그 열릴 때 바로 최신 공연 목록 로드
        self.dialog.after(100, self._load_latest_performances)
        
    def _setup_ui(self):
        """UI 구성"""
        # 검색 프레임
        search_frame = ttk.Frame(self.dialog, padding="10")
        search_frame.pack(fill=tk.X)
        
        ttk.Label(search_frame, text="공연명:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry.bind('<Return>', lambda e: self._search())
        
        self.search_button = ttk.Button(search_frame, text="검색", command=self._search)
        self.search_button.pack(side=tk.LEFT)
        
        # 구분선
        ttk.Separator(self.dialog, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # 결과 프레임
        result_frame = ttk.Frame(self.dialog)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # 왼쪽: 검색 결과 리스트
        left_frame = ttk.Frame(result_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        ttk.Label(left_frame, text="검색 결과").pack()
        
        # 리스트박스 스크롤바
        list_scroll = ttk.Scrollbar(left_frame)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.result_listbox = tk.Listbox(left_frame, yscrollcommand=list_scroll.set, width=50)
        self.result_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.result_listbox.bind('<<ListboxSelect>>', self._on_performance_select)
        list_scroll.config(command=self.result_listbox.yview)
        
        # 중간 구분선
        ttk.Separator(result_frame, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # 오른쪽: 상세 정보
        right_frame = ttk.Frame(result_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        ttk.Label(right_frame, text="상세 정보").pack()
        
        self.detail_frame = ttk.Frame(right_frame)
        self.detail_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 버튼 프레임
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.select_button = ttk.Button(button_frame, text="선택", command=self._on_select, state=tk.DISABLED)
        self.select_button.pack(side=tk.RIGHT, padx=10)
        
        ttk.Button(button_frame, text="취소", command=self.dialog.destroy).pack(side=tk.RIGHT)
        
        self.performances = []
        
    def _load_latest_performances(self):
        """최신 공연 목록 로드"""
        self.result_listbox.delete(0, tk.END)
        self.result_listbox.insert(tk.END, "공연 목록을 불러오는 중...")
        
        threading.Thread(target=self._load_latest_thread, daemon=True).start()
        
    def _load_latest_thread(self):
        """최신 공연 목록 로드 스레드"""
        try:
            performances = self.crawler.get_latest_performances(size=50)
            self.performances = performances
            
            self.dialog.after(0, self._update_search_results, performances)
            
        except Exception as e:
            logger.error(f"공연 목록 로드 실패: {str(e)}")
            self.dialog.after(0, messagebox.showerror, "로드 오류", f"공연 목록을 불러오는 중 오류가 발생했습니다: {str(e)}")
        
    def _search(self):
        """공연 검색"""
        keyword = self.search_entry.get().strip()
        if not keyword:
            messagebox.showwarning("입력 오류", "검색어를 입력해주세요.")
            return
            
        self.search_button.config(state=tk.DISABLED)
        self.result_listbox.delete(0, tk.END)
        
        threading.Thread(target=self._search_thread, args=(keyword,), daemon=True).start()
        
    def _search_thread(self, keyword: str):
        """검색 스레드"""
        try:
            performances = self.crawler.search_performances(keyword)
            self.performances = performances
            
            self.dialog.after(0, self._update_search_results, performances)
            
        except Exception as e:
            self.dialog.after(0, messagebox.showerror, "검색 오류", f"검색 중 오류가 발생했습니다: {str(e)}")
        finally:
            self.dialog.after(0, self.search_button.config, {'state': tk.NORMAL})
            
    def _update_search_results(self, performances: List[Dict]):
        """검색 결과 업데이트"""
        self.result_listbox.delete(0, tk.END)
        
        for perf in performances:
            display_text = f"{perf['name']} ({perf['place']}) - {perf['start_date']}~{perf['end_date']}"
            self.result_listbox.insert(tk.END, display_text)
            
        if not performances:
            self.result_listbox.insert(tk.END, "검색 결과가 없습니다.")
            
    def _on_performance_select(self, event):
        """공연 선택 이벤트"""
        selection = self.result_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        if index < len(self.performances):
            performance = self.performances[index]
            self._show_performance_detail(performance)
            
    def _show_performance_detail(self, performance: Dict):
        """공연 상세 정보 표시"""
        # 기존 위젯 제거
        for widget in self.detail_frame.winfo_children():
            widget.destroy()
            
        # 포스터 이미지
        if performance.get('poster_url'):
            threading.Thread(target=self._load_poster, args=(performance['poster_url'],), daemon=True).start()
            
        # 공연 정보
        info_frame = ttk.Frame(self.detail_frame)
        info_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(info_frame, text=f"공연명: {performance['name']}", wraplength=300).pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"장소: {performance['place']}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"기간: {performance['start_date']} ~ {performance['end_date']}").pack(anchor=tk.W)
        
        # 날짜 선택
        date_frame = ttk.LabelFrame(self.detail_frame, text="날짜 선택", padding="10")
        date_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(date_frame, text="날짜:").grid(row=0, column=0, sticky=tk.W)
        self.date_combo = ttk.Combobox(date_frame, width=20)
        self.date_combo.grid(row=0, column=1, padx=(10, 0))
        
        ttk.Label(date_frame, text="시간:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.time_combo = ttk.Combobox(date_frame, width=20)
        self.time_combo.grid(row=1, column=1, padx=(10, 0), pady=(10, 0))
        
        # 상세 정보 로드
        self.selected_performance = performance
        threading.Thread(target=self._load_detail, args=(performance['id'],), daemon=True).start()
        
        self.select_button.config(state=tk.NORMAL)
        
    def _load_poster(self, url: str):
        """포스터 이미지 로드"""
        try:
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))
            img = img.resize((150, 200), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            self.dialog.after(0, self._show_poster, photo)
            
        except Exception as e:
            logger.error(f"포스터 로드 실패: {str(e)}")
            
    def _show_poster(self, photo):
        """포스터 표시"""
        poster_label = ttk.Label(self.detail_frame, image=photo)
        poster_label.image = photo  # 참조 유지
        poster_label.pack(pady=10)
        
    def _load_detail(self, performance_id: str):
        """공연 상세 정보 로드"""
        try:
            detail = self.crawler.get_performance_detail(performance_id)
            if detail:
                self.dialog.after(0, self._update_detail, detail)
                
        except Exception as e:
            logger.error(f"상세 정보 로드 실패: {str(e)}")
            
    def _update_detail(self, detail: Dict):
        """상세 정보 업데이트"""
        if detail.get('dates'):
            self.date_combo['values'] = detail['dates']
            if detail['dates']:
                self.date_combo.set(detail['dates'][0])
                
        if detail.get('times'):
            self.time_combo['values'] = detail['times']
            if detail['times']:
                self.time_combo.set(detail['times'][0])
                
    def _on_select(self):
        """선택 완료"""
        if not self.selected_performance:
            messagebox.showwarning("선택 오류", "공연을 선택해주세요.")
            return
            
        self.selected_date = self.date_combo.get()
        self.selected_time = self.time_combo.get()
        
        if not self.selected_date or not self.selected_time:
            messagebox.showwarning("선택 오류", "날짜와 시간을 선택해주세요.")
            return
            
        self.dialog.destroy()
        
    def get_result(self) -> Optional[Dict]:
        """선택 결과 반환"""
        if self.selected_performance and self.selected_date and self.selected_time:
            return {
                'performance': self.selected_performance,
                'date': self.selected_date,
                'time': self.selected_time
            }
        return None