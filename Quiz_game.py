import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import time
import json
import os
import sys

# ------------- FILE PATH HANDLER -------------
def get_file_path(filename):
    if getattr(sys, 'frozen', False):  # If running in a PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, filename)

# ------------- GLOBAL SETTINGS -------------
root = tk.Tk()
root.title("Math & General Quiz")
root.geometry("800x600")
root.attributes('-fullscreen', True)

best_score = 0
score = 0
lives = 3
question_data = []
available_questions = []
used_questions = {}
dark_mode = True
current_theme = "dark"

# ------------- THEMES -------------
themes = {
    "dark": {"bg": "#1e1e1e", "fg": "#ffffff"},
    "light": {"bg": "#f2f2f2", "fg": "#000000"},
}

def apply_theme_recursive(widget):
    theme = themes[current_theme]
    try:
        widget.config(bg=theme["bg"])
        if isinstance(widget, (tk.Label, tk.Button, tk.Entry, tk.Text)):
            widget.config(fg=theme["fg"])
    except:
        pass
    for child in widget.winfo_children():
        apply_theme_recursive(child)

# ------------- LOAD & FILTER QUESTIONS -------------
def load_questions():
    global question_data, available_questions
    try:
        with open(get_file_path("questions.txt"), "r", encoding="utf-8") as f:
            lines = f.readlines()
            question_data = [json.loads(line) for line in lines]
    except:
        question_data = [
            {"question": "O'zbekiston poytaxti qayer?", "answer": "Toshkent"},
            {"question": "Apple manosi nima?", "answer": "olma"},
            {"question": "Python qanday til?", "answer": "dasturlash"},
        ]
    available_questions = question_data.copy()

# ------------- BAD WORDS FILTER -------------
def clean_text(text):
    bad_words = ["fuck", "shit", "damn"]
    for word in bad_words:
        text = text.replace(word, "***")
    return text

# ------------- QUESTION SELECTION -------------
def generate_question():
    if random.randint(0, 1):
        a, b = random.randint(1, 20), random.randint(1, 20)
        return {"question": f"{a} + {b} = ?", "answer": str(a + b)}
    else:
        available = [q for q in available_questions if time.time() - used_questions.get(q['question'], 0) > 90]
        if not available:
            return generate_question()
        q = random.choice(available)
        used_questions[q['question']] = time.time()
        return q

# ------------- QUIZ LOGIC -------------
def ask_question():
    global current_q, time_left, timer_running
    current_q = generate_question()
    question_label.config(text=current_q["question"])
    answer_entry.delete(0, tk.END)
    time_left = 15
    timer_running = True
    update_timer()

def check_answer():
    global score, lives, best_score, timer_running
    timer_running = False
    user_ans = answer_entry.get().strip().lower()
    correct = current_q["answer"].strip().lower()
    if user_ans == correct:
        score += 1
        if score > best_score:
            best_score = score
            save_best_score()
        status_label.config(text=f"\u2705 To'g'ri! Score: {score}")
    else:
        lives -= 1
        status_label.config(text=f"\u274C Noto'g'ri! Qolgan jon: {lives}")
        if lives <= 0:
            messagebox.showinfo("Game Over", f"Game over! Best score: {best_score}")
            return
    update_ui()
    ask_question()

def update_timer():
    global time_left, timer_running
    if timer_running:
        if time_left <= 0:
            status_label.config(text="\u23F0 Vaqt tugadi!")
            check_answer()
            return
        timer_label.config(text=f"\u23F3 {time_left} s")
        time_left -= 1
        root.after(1000, update_timer)

# ------------- UI ELEMENTS -------------
question_label = tk.Label(root, text="", font=("Arial", 24))
question_label.pack(pady=30)

answer_entry = tk.Entry(root, font=("Arial", 20), justify="center")
answer_entry.pack(pady=10)

submit_btn = tk.Button(root, text="Javob ber", command=check_answer)
answer_entry.bind("<Return>", lambda event: check_answer())
submit_btn.pack(pady=10)

timer_label = tk.Label(root, text="", font=("Arial", 20))
timer_label.pack(pady=5)

status_label = tk.Label(root, text="", font=("Arial", 18))
status_label.pack(pady=10)

# ------------- CONTROL PANEL -------------
control_frame = tk.Frame(root)
control_frame.pack(pady=20)

restart_btn = tk.Button(control_frame, text="\U0001F501 Restart", command=lambda: restart_game(False))
restart_btn.grid(row=0, column=0, padx=10)

quit_btn = tk.Button(control_frame, text="\u274C Quit", command=root.destroy)
quit_btn.grid(row=0, column=1, padx=10)

theme_btn = tk.Button(control_frame, text="\U0001F319/\u2600\ufe0f", command=lambda: toggle_theme())
theme_btn.grid(row=0, column=2, padx=10)

# ------------- QUESTION MANAGEMENT -------------
manage_frame = tk.Frame(root)
manage_frame.pack(pady=20)

add_btn = tk.Button(manage_frame, text="\u2795 Savol qo‘shish", command=lambda: add_question())
add_btn.grid(row=0, column=0, padx=10)

view_btn = tk.Button(manage_frame, text="\U0001F4CB Savollar", command=lambda: view_questions())
view_btn.grid(row=0, column=1, padx=10)

# ------------- FUNKSIYALAR -------------
def toggle_theme():
    global current_theme
    current_theme = "light" if current_theme == "dark" else "dark"
    animate_theme_switch()

def animate_theme_switch():
    for i in range(20):
        root.after(i * 10, lambda s=i: apply_theme_recursive(root))

def restart_game(reset_score):
    global score, lives
    score = 0 if reset_score else score
    lives = 3
    update_ui()
    ask_question()

def update_ui():
    question_label.config(text="")
    timer_label.config(text="")
    status_label.config(text=f"Score: {score} | Best: {best_score} | Jon: {lives}")

def add_question():
    q = simpledialog.askstring("Savol qo'shish", "Savolni kiriting:")
    a = simpledialog.askstring("Javob", "Javobni kiriting:")
    if q and a:
        q, a = clean_text(q), clean_text(a)
        question_data.append({"question": q, "answer": a})
        save_questions()
        messagebox.showinfo("Yangi savol", "Savol muvaffaqiyatli qo‘shildi!")

def view_questions():
    win = tk.Toplevel(root)
    win.title("Savollar ro‘yxati")
    win.geometry("500x400")
    box = tk.Listbox(win, font=("Arial", 12))
    for q in question_data:
        box.insert(tk.END, q['question'])
    box.pack(fill=tk.BOTH, expand=True)

    def remove_selected():
        idx = box.curselection()
        if idx:
            del question_data[idx[0]]
            save_questions()
            win.destroy()
            view_questions()

    def edit_selected():
        idx = box.curselection()
        if idx:
            old_q = question_data[idx[0]]
            new_q = simpledialog.askstring("Tahrirlash", "Yangi savol:", initialvalue=old_q['question'])
            new_a = simpledialog.askstring("Tahrirlash", "Yangi javob:", initialvalue=old_q['answer'])
            if new_q and new_a:
                question_data[idx[0]] = {"question": clean_text(new_q), "answer": clean_text(new_a)}
                save_questions()
                win.destroy()
                view_questions()

    tk.Button(win, text="\u274C O‘chirish", command=remove_selected).pack(side=tk.LEFT, padx=5, pady=5)
    tk.Button(win, text="\u270F\ufe0f Tahrirlash", command=edit_selected).pack(side=tk.LEFT, padx=5, pady=5)

def save_questions():
    with open(get_file_path("questions.txt"), "w", encoding="utf-8") as f:
        for q in question_data:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")

def save_best_score():
    with open(get_file_path("best_score.txt"), "w") as f:
        f.write(str(best_score))

def load_best_score():
    global best_score
    try:
        with open(get_file_path("best_score.txt"), "r") as f:
            best_score = int(f.read().strip())
    except:
        best_score = 0

# ------------- INIT -------------
load_best_score()
load_questions()
apply_theme_recursive(root)
update_ui()
ask_question()

root.mainloop()