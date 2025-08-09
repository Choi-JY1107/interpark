import tkinter as tk
from presentation.views.main_window import MainWindow


def launch_gui():
    """GUI 애플리케이션 실행"""
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()