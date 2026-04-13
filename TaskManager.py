# ==============================
# 📋 MULTI PAGE TASK MANAGER
# ==============================

import tkinter as tk
from tkinter import ttk, messagebox
import json, os
from datetime import datetime

# ==============================
# 🪟 MAIN WINDOW
# ==============================

root = tk.Tk()
root.title("📋 Multi Page Task Manager")
root.geometry("650x520")
root.configure(bg="#f0f0f0")

# ==============================
# 📂 GLOBAL VARIABLES
# ==============================

TASK_FILE = "tasks_multi.json"
tabs = {}
deleted_tasks = []

# ==============================
# 🧭 FRAME SWITCHING
# ==============================

main_frame = tk.Frame(root, bg="#f0f0f0")
notes_frame = tk.Frame(root, bg="#f0f0f0")

main_frame.pack(fill="both", expand=True)

def show_notes():
    main_frame.pack_forget()
    notes_frame.pack(fill="both", expand=True)

def show_main():
    notes_frame.pack_forget()
    main_frame.pack(fill="both", expand=True)

# ==============================
# 📊 EXTRA FEATURES
# ==============================

def view_details():
    page = notebook.tab(notebook.select(), "text")
    info = tabs[page]

    selected = info['listbox'].curselection()
    if not selected:
        messagebox.showinfo("Info", "Select a task first")
        return

    task = info['task_info'][selected[0]]

    messagebox.showinfo(
        "Task Details",
        f"Task: {task['text']}\n"
        f"Priority: {task['priority']}\n"
        f"Due Date: {task['due']}\n"
        f"Status: {'Completed' if task['done'] else 'Pending'}"
    )

def view_timetable():
    win = tk.Toplevel(root)
    win.title("📅 Timetable")

    text = tk.Text(win)
    text.pack(fill="both", expand=True)

    text.insert(tk.END, "📅 Your Task Timetable\n\n")

    for page, info in tabs.items():
        text.insert(tk.END, f"--- {page} ---\n")
        for task in info['task_info'].values():
            status = "✅" if task['done'] else "📌"
            text.insert(tk.END, f"{status} {task['text']} (Due: {task['due']})\n")
        text.insert(tk.END, "\n")

def show_graph():
    win = tk.Toplevel(root)
    win.title("📊 Productivity Graph")

    canvas = tk.Canvas(win, bg="white")
    canvas.pack(fill="both", expand=True)

    x = 60
    for page, info in tabs.items():
        total = len(info['task_info'])
        done = sum(1 for t in info['task_info'].values() if t["done"])

        percent = int((done / total) * 100) if total > 0 else 0
        bar_height = percent * 2

        canvas.create_rectangle(x, 300-bar_height, x+50, 300, fill="blue")
        canvas.create_text(x+25, 310, text=page.split()[0])
        canvas.create_text(x+25, 290-bar_height, text=f"{percent}%")

        x += 120

# ==============================
# 💾 DATA HANDLING
# ==============================

def save_tasks():
    data = {page: list(info['task_info'].values()) for page, info in tabs.items()}
    with open(TASK_FILE, "w") as f:
        json.dump(data, f)

def load_tasks():
    if not os.path.exists(TASK_FILE):
        return

    with open(TASK_FILE, "r") as f:
        data = json.load(f)

    for page, tasks_list in data.items():
        if page not in tabs:
            continue

        info = tabs[page]
        for task in tasks_list:
            text = f"{'✅' if task['done'] else '📌'} {task['text']}"
            info['listbox'].insert(tk.END, text)

            index = info['listbox'].size() - 1
            info['task_info'][index] = task

            apply_color(info['listbox'], index, task)

        update_counter(page)

# ==============================
# 🎨 UI HELPERS
# ==============================

def apply_color(listbox, index, task):
    if index >= listbox.size():
        return

    if task["done"]:
        listbox.itemconfig(index, fg="green", font=("Arial", 11, "overstrike"))
    else:
        colors = {"High": "red", "Medium": "orange", "Low": "blue"}
        listbox.itemconfig(index, fg=colors.get(task["priority"], "black"))

def update_counter(page):
    info = tabs[page]

    total = len(info['task_info'])
    done = sum(1 for t in info['task_info'].values() if t["done"])

    percent = int((done/total)*100) if total else 0

    info['counter_label'].config(text=f"Total: {total}   Completed: {done}")
    info['productivity_label'].config(text=f"Productivity: {percent}%")

    if total == 0:
        msg = "No tasks yet 😴"
    elif done == total:
        msg = "All tasks done 🏆"
    elif done == 0:
        msg = "Start something ⚡"
    elif done < total/2:
        msg = "Focus more 💪"
    else:
        msg = "Good progress 👍"

    info['ai_label'].config(text=f"AI: {msg}")

# ==============================
# ⚙️ TASK OPERATIONS
# ==============================

def add_task(page):
    info = tabs[page]

    text = info['entry'].get()
    priority = info['priority_var'].get()
    due = info['due_entry'].get() or datetime.today().strftime("%Y-%m-%d")

    if not text:
        return

    display = f"📌 {text}"
    info['listbox'].insert(tk.END, display)

    index = info['listbox'].size() - 1
    info['task_info'][index] = {
        "text": text,
        "done": False,
        "priority": priority,
        "due": due
    }

    apply_color(info['listbox'], index, info['task_info'][index])

    info['entry'].delete(0, tk.END)
    update_counter(page)
    save_tasks()

def delete_task(page):
    info = tabs[page]
    selected = info['listbox'].curselection()

    if not selected:
        return

    index = selected[0]
    deleted_tasks.append(info['listbox'].get(index))

    info['listbox'].delete(index)
    info['task_info'].pop(index, None)

    # reindex
    info['task_info'] = {i: v for i, v in enumerate(info['task_info'].values())}

    update_counter(page)
    save_tasks()

def toggle_done(event=None):
    page = notebook.tab(notebook.select(), "text")
    info = tabs[page]

    selected = info['listbox'].curselection()
    if not selected:
        return

    index = selected[0]
    task = info['task_info'][index]

    task["done"] = not task["done"]

    new_text = f"{'✅' if task['done'] else '📌'} {task['text']}"
    info['listbox'].delete(index)
    info['listbox'].insert(index, new_text)

    apply_color(info['listbox'], index, task)

    update_counter(page)
    save_tasks()

def clear_all(page):
    info = tabs[page]

    if messagebox.askyesno("Confirm", f"Delete all tasks in {page}?"):
        deleted_tasks.extend(info['listbox'].get(0, tk.END))

        info['listbox'].delete(0, tk.END)
        info['task_info'].clear()

        update_counter(page)
        save_tasks()

# ==============================
# 🖥️ UI BUILD
# ==============================

notebook = ttk.Notebook(main_frame)
notebook.pack(expand=1, fill='both')

pages = ["Study 📚", "Personal 🧍", "Work 💼"]

for page in pages:
    frame = tk.Frame(notebook, bg="#f0f0f0")
    notebook.add(frame, text=page)

    entry = tk.Entry(frame, width=35)
    entry.pack(pady=8)

    priority_var = tk.StringVar(value="Medium")
    tk.OptionMenu(frame, priority_var, "High", "Medium", "Low").pack()

    due_entry = tk.Entry(frame)
    due_entry.pack()
    due_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))

    btn_frame = tk.Frame(frame)
    btn_frame.pack()

    tk.Button(btn_frame, text="➕", command=lambda p=page: add_task(p)).grid(row=0, column=0)
    tk.Button(btn_frame, text="❌", command=lambda p=page: delete_task(p)).grid(row=0, column=1)
    tk.Button(btn_frame, text="✅", command=toggle_done).grid(row=0, column=2)
    tk.Button(btn_frame, text="🧹", command=lambda p=page: clear_all(p)).grid(row=0, column=3)
    tk.Button(btn_frame, text="📄", command=view_details).grid(row=0, column=4)

    listbox = tk.Listbox(frame, width=50, height=10)
    listbox.pack()
    listbox.bind("<Double-1>", toggle_done)

    counter_label = tk.Label(frame, text="Total: 0 Completed: 0")
    counter_label.pack()

    productivity_label = tk.Label(frame, text="Productivity: 0%")
    productivity_label.pack()

    ai_label = tk.Label(frame, text="AI: Stay productive!")
    ai_label.pack()

    tabs[page] = {
        "entry": entry,
        "priority_var": priority_var,
        "due_entry": due_entry,
        "listbox": listbox,
        "task_info": {},
        "counter_label": counter_label,
        "productivity_label": productivity_label,
        "ai_label": ai_label
    }

tk.Button(main_frame, text="📅 View Timetable", command=view_timetable).pack()
tk.Button(main_frame, text="📊 Show Graph", command=show_graph).pack()

# ==============================
# 📂 SIDE MENU
# ==============================

def open_deleted():
    win = tk.Toplevel(root)
    box = tk.Listbox(win)
    box.pack()
    for t in deleted_tasks:
        box.insert(tk.END, t)

tk.Button(main_frame, text="☰", command=show_notes).pack()

menu_frame = tk.Frame(notes_frame)
menu_frame.pack()

tk.Button(menu_frame, text="🗑 Deleted", command=open_deleted).pack()
tk.Button(notes_frame, text="⬅ Back", command=show_main).pack()

# ==============================
# 🚀 START APP
# ==============================

load_tasks()
root.mainloop()