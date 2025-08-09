import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import logging

from presentation.controllers.reservation_controller import ReservationController
from application.dtos.reservation_dto import ReservationRequestDTO
from presentation.views.performance_search_dialog import PerformanceSearchDialog

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("인터파크 자동 티켓팅")
        self.root.geometry("800x700")
        
        self.controller = ReservationController()
        
        self._setup_ui()
        
    def _setup_ui(self):
        """UI 구성"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self._create_performance_frame(main_frame)
        self._create_seat_frame(main_frame)
        self._create_account_frame(main_frame)
        self._create_control_frame(main_frame)
        self._create_log_frame(main_frame)
        
        self._configure_grid(main_frame)
        
    def _create_performance_frame(self, parent):
        """공연 정보 프레임 생성"""
        frame = ttk.LabelFrame(parent, text="공연 정보", padding="10")
        frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 공연 검색 버튼
        search_button = ttk.Button(frame, text="공연 선택", command=self._open_search_dialog, width=30)
        search_button.pack(pady=10)
        
        # 선택된 공연 정보 표시
        self.selected_performance_label = ttk.Label(frame, text="선택된 공연: 없음", font=('', 10, 'bold'))
        self.selected_performance_label.pack(pady=5)
        
        self.selected_date_label = ttk.Label(frame, text="")
        self.selected_date_label.pack(pady=2)
        
        # 대기 시작 시간만 입력받음
        time_frame = ttk.Frame(frame)
        time_frame.pack(pady=10)
        
        ttk.Label(time_frame, text="대기 시작 시간 (HH:MM:SS):").pack(side=tk.LEFT, padx=(0, 10))
        self.target_time = ttk.Entry(time_frame, width=20)
        self.target_time.pack(side=tk.LEFT)
        
        # 내부 변수 초기화
        self.performance_data = None
        
    def _create_seat_frame(self, parent):
        """좌석 설정 프레임 생성"""
        frame = ttk.LabelFrame(parent, text="좌석 설정", padding="10")
        frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(frame, text="좌석 선택 방식:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.seat_type = ttk.Combobox(frame, values=["일반", "작은 포도알", "큰 포도알"], width=20)
        self.seat_type.set("일반")
        self.seat_type.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(frame, text="선택 방향:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.seat_direction = ttk.Combobox(frame, values=["오른쪽부터", "왼쪽부터"], width=20)
        self.seat_direction.set("오른쪽부터")
        self.seat_direction.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        ttk.Label(frame, text="좌석 수:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.seat_count = ttk.Spinbox(frame, from_=1, to=4, width=10)
        self.seat_count.set(1)
        self.seat_count.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
    def _create_account_frame(self, parent):
        """계정 정보 프레임 생성"""
        frame = ttk.LabelFrame(parent, text="계정 정보 (선택)", padding="10")
        frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.user_id = self._create_entry(frame, "아이디:", 0, 30)
        self.user_pw = self._create_entry(frame, "비밀번호:", 1, 30, show="*")
        
    def _create_control_frame(self, parent):
        """제어 버튼 프레임 생성"""
        frame = ttk.Frame(parent)
        frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.start_button = ttk.Button(frame, text="시작", command=self._on_start)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(frame, text="중지", command=self._on_stop, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5)
        
    def _create_log_frame(self, parent):
        """로그 프레임 생성"""
        frame = ttk.LabelFrame(parent, text="로그", padding="10")
        frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def _create_entry(self, parent, label, row, width, **kwargs):
        """엔트리 위젯 생성 헬퍼"""
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky=tk.W, pady=5)
        entry = ttk.Entry(parent, width=width, **kwargs)
        entry.grid(row=row, column=1, pady=5, padx=(10, 0))
        return entry
        
    def _configure_grid(self, parent):
        """그리드 설정"""
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(4, weight=1)
        
    def _open_search_dialog(self):
        """공연 검색 다이얼로그 열기"""
        dialog = PerformanceSearchDialog(self.root)
        self.root.wait_window(dialog.dialog)
        
        result = dialog.get_result()
        if result:
            # 선택된 공연 정보 저장
            self.performance_data = result
            performance = result['performance']
            
            # 레이블 업데이트
            self.selected_performance_label.config(text=f"선택된 공연: {performance['name']}")
            self.selected_date_label.config(text=f"날짜: {result['date']} | 시간: {result['time']} | 장소: {performance.get('place', '')}")
            
            self._log_message(f"공연 선택: {performance['name']}")
            self._log_message(f"날짜: {result['date']}, 시간: {result['time']}")
        
    def _log_message(self, message):
        """로그 메시지 출력"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert(tk.END, f"[{current_time}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def _on_start(self):
        """시작 버튼 핸들러"""
        if not self._validate_inputs():
            return
            
        request_dto = self._create_request_dto()
        
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        self.controller.start_reservation(
            request_dto,
            self._log_message,
            self._on_completion
        )
        
    def _on_stop(self):
        """중지 버튼 핸들러"""
        self.controller.stop_reservation()
        self._log_message("티켓팅 중지 요청됨")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
    def _on_completion(self, success, message):
        """예매 완료 콜백"""
        self._log_message(message)
        
        if success:
            messagebox.showinfo("성공", message)
        else:
            messagebox.showerror("실패", message)
            
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
    def _validate_inputs(self):
        """입력값 검증"""
        if not self.performance_data:
            messagebox.showerror("입력 오류", "공연을 선택해주세요.")
            return False
            
        if not self.target_time.get():
            messagebox.showerror("입력 오류", "대기 시작 시간을 입력해주세요.")
            return False
                
        return True
        
    def _create_request_dto(self) -> ReservationRequestDTO:
        """요청 DTO 생성"""
        performance = self.performance_data['performance']
        
        return ReservationRequestDTO(
            performance_name=performance['name'],
            performance_url=performance['url'],
            date=self.performance_data['date'],
            time=self.performance_data['time'],
            target_time=self.target_time.get(),
            seat_type=self.seat_type.get(),
            seat_direction=self.seat_direction.get(),
            seat_count=int(self.seat_count.get()),
            user_id=self.user_id.get() if self.user_id.get() else None,
            user_password=self.user_pw.get() if self.user_pw.get() else None
        )