import tkinter as tk


def launch_gui():
    root = tk.Tk()
    root.title("인터파크 자동 예매기")
    root.geometry("400x300")

    label = tk.Label(root, text="안녕하세요", font=("맑은 고딕", 14))
    label.pack(pady=100)

    root.mainloop()
