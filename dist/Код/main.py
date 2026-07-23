import calendar
import json
import os
import sys
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, simpledialog, ttk

from generator import generate_order


if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


APP_TITLE = "Розпорядження водіїв Вінницького національного медичного університету"
APP_PASSWORD = "111"

BG_COLOR = "#edf3f8"
CARD_COLOR = "#ffffff"
PANEL_COLOR = "#edf1f5"
TEXT_COLOR = "#13283d"
MUTED_COLOR = "#607387"
VNMU_BLUE = "#0a5b9f"
VNMU_RED = "#c9342c"
VNMU_GOLD = "#d8aa39"
SOFT_RED = "#f8e1e0"
SOFT_BLUE = "#dcebf8"
FIELD_BORDER = "#b7c8d8"

MONTHS_UA = [
    "Січень",
    "Лютий",
    "Березень",
    "Квітень",
    "Травень",
    "Червень",
    "Липень",
    "Серпень",
    "Вересень",
    "Жовтень",
    "Листопад",
    "Грудень",
]
WEEKDAYS_UA = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]


def get_path(relative_path):
    return os.path.join(BASE_DIR, relative_path)


def load_json(path, default):
    full_path = get_path(path)
    if not os.path.exists(full_path):
        return default

    with open(full_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path, data):
    full_path = get_path(path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    with open(full_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def load_settings():
    return load_json("data/settings.json", {})


def save_settings(settings):
    save_json("data/settings.json", settings)


def clean_text(value):
    return " ".join((value or "").strip().split())


def split_full_name(full_name):
    parts = clean_text(full_name).split()
    last_name = parts[0] if len(parts) > 0 else ""
    first_name = parts[1] if len(parts) > 1 else ""
    return last_name, first_name


def build_full_name(last_name, first_name):
    return clean_text(" ".join([last_name, first_name]))


def make_cases(full_name):
    normalized_name = clean_text(full_name)
    parts = normalized_name.split()

    if len(parts) < 2:
        return {"acc": normalized_name, "dat": normalized_name}

    last_name = parts[0]
    first_name = parts[1]
    return {
        "acc": f"{last_name}а {first_name}а",
        "dat": f"{last_name}у {first_name}у",
    }


def normalize_driver(driver):
    full_name = build_full_name(*split_full_name(driver.get("name", "")))
    auto_cases = make_cases(full_name)
    return {
        "name": full_name,
        "acc": clean_text(driver.get("acc") or auto_cases["acc"]),
        "dat": clean_text(driver.get("dat") or auto_cases["dat"]),
    }


def save_drivers():
    save_json("data/drivers.json", drivers)


def save_cars():
    save_json("data/cars.json", cars)


def save_destinations():
    save_json("data/destinations.json", destinations)


def get_output_folder():
    settings = load_settings()
    return get_path(settings.get("output_folder", "output"))


def get_current_order_number():
    order_data = load_json("data/order_number.json", {"number": 1})
    return int(order_data.get("number", 1))


def update_order_number_label():
    order_number_var.set(f"№ {get_current_order_number()}")


def get_initial_date():
    settings = load_settings()
    saved_date = clean_text(settings.get("last_used_date", ""))

    try:
        parsed = datetime.strptime(saved_date, "%d.%m.%Y")
        return parsed
    except ValueError:
        return datetime.now()


def save_last_used_date(date_value):
    settings = load_settings()
    settings["last_used_date"] = date_value
    save_settings(settings)


def find_driver_by_name(name):
    clean_name = clean_text(name)
    for index, driver in enumerate(drivers):
        if driver["name"] == clean_name:
            return index, driver
    return None, None


def load_logo_image():
    logo_path = get_path("assets/vnmu_logo.png")
    if not os.path.exists(logo_path):
        return None

    try:
        logo = tk.PhotoImage(file=logo_path)
        return logo.subsample(3, 3)
    except tk.TclError:
        return None


def create_text_entry(parent, width=20, bg=PANEL_COLOR):
    return tk.Entry(
        parent,
        width=width,
        font=("Segoe UI", 10),
        bg=bg,
        fg=TEXT_COLOR,
        relief="flat",
        bd=0,
        highlightthickness=1,
        highlightbackground=FIELD_BORDER,
        highlightcolor=VNMU_BLUE,
        insertbackground=TEXT_COLOR,
    )


def create_small_button(parent, text, command, bg, active_bg):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg="white",
        activebackground=active_bg,
        activeforeground="white",
        relief="flat",
        bd=0,
        cursor="hand2",
        font=("Segoe UI", 9, "bold"),
        padx=10,
        pady=6,
    )


def create_main_button(parent, text, command, bg, active_bg, border):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg,
        fg="white",
        activebackground=active_bg,
        activeforeground="white",
        relief="flat",
        bd=0,
        cursor="hand2",
        font=("Segoe UI", 11, "bold"),
        padx=24,
        pady=12,
        highlightthickness=2,
        highlightbackground=border,
    )


def center_window(window, parent=None):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()

    if parent is not None and parent.winfo_exists():
        x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
    else:
        x = (window.winfo_screenwidth() - width) // 2
        y = (window.winfo_screenheight() - height) // 2

    window.geometry(f"+{max(x, 0)}+{max(y, 0)}")


class SimpleItemDialog:
    def __init__(self, parent, title, prompt, initial_value=""):
        self.result = None

        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.transient(parent)
        self.window.grab_set()
        self.window.resizable(False, False)
        self.window.configure(bg=BG_COLOR)

        panel = tk.Frame(
            self.window,
            bg=CARD_COLOR,
            padx=18,
            pady=16,
            highlightbackground=VNMU_BLUE,
            highlightthickness=2,
        )
        panel.pack(padx=14, pady=14, fill="both", expand=True)

        tk.Label(
            panel,
            text=prompt,
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            font=("Segoe UI", 10, "bold"),
            wraplength=280,
            justify="left",
        ).pack(anchor="w", pady=(0, 10))

        self.entry = create_text_entry(panel, width=30, bg="#f4f7fa")
        self.entry.pack(fill="x")
        self.entry.insert(0, initial_value)
        self.entry.select_range(0, tk.END)
        self.entry.focus_set()

        actions = tk.Frame(panel, bg=CARD_COLOR)
        actions.pack(anchor="e", pady=(14, 0))
        create_small_button(actions, "Скасувати", self.window.destroy, VNMU_BLUE, "#08497f").pack(
            side="left", padx=(0, 8)
        )
        create_small_button(actions, "Зберегти", self.on_save, VNMU_RED, "#a82721").pack(side="left")

        self.window.bind("<Return>", lambda _event: self.on_save())
        self.window.bind("<Escape>", lambda _event: self.window.destroy())
        center_window(self.window, parent)

    def on_save(self):
        self.result = clean_text(self.entry.get())
        self.window.destroy()


class InlineCalendar:
    def __init__(self, parent, initial_date, on_change):
        self.on_change = on_change
        self.selected_date = initial_date
        self.year = initial_date.year
        self.month = initial_date.month
        self.frame = tk.Frame(
            parent,
            bg=CARD_COLOR,
            padx=12,
            pady=10,
            highlightbackground=VNMU_BLUE,
            highlightthickness=1,
        )

        header = tk.Frame(self.frame, bg=CARD_COLOR)
        header.pack(fill="x", pady=(0, 8))

        create_small_button(header, "◀", self.prev_month, VNMU_BLUE, "#08497f").pack(side="left")
        self.title_var = tk.StringVar()
        tk.Label(
            header,
            textvariable=self.title_var,
            font=("Segoe UI", 10, "bold"),
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            width=14,
        ).pack(side="left", padx=8)
        create_small_button(header, "▶", self.next_month, VNMU_BLUE, "#08497f").pack(side="left")

        weekdays = tk.Frame(self.frame, bg=CARD_COLOR)
        weekdays.pack()
        for index, weekday in enumerate(WEEKDAYS_UA):
            tk.Label(
                weekdays,
                text=weekday,
                width=3,
                font=("Segoe UI", 8, "bold"),
                bg=SOFT_BLUE if index < 5 else SOFT_RED,
                fg=TEXT_COLOR,
                pady=3,
            ).grid(row=0, column=index, padx=1, pady=1)

        self.days_frame = tk.Frame(self.frame, bg=CARD_COLOR)
        self.days_frame.pack(pady=(4, 0))
        self.render()

    def render(self):
        for widget in self.days_frame.winfo_children():
            widget.destroy()

        self.title_var.set(f"{MONTHS_UA[self.month - 1]} {self.year}")
        month_matrix = calendar.Calendar(firstweekday=0).monthdayscalendar(self.year, self.month)

        for row_index, week in enumerate(month_matrix):
            for col_index, day in enumerate(week):
                if day == 0:
                    tk.Label(self.days_frame, text="", width=3, bg=CARD_COLOR).grid(
                        row=row_index, column=col_index, padx=1, pady=1
                    )
                    continue

                date_value = datetime(self.year, self.month, day)
                is_selected = date_value.date() == self.selected_date.date()
                is_today = date_value.date() == datetime.now().date()

                if is_selected:
                    bg_color = VNMU_BLUE
                    fg_color = "white"
                elif is_today:
                    bg_color = VNMU_RED
                    fg_color = "white"
                else:
                    bg_color = SOFT_RED if col_index >= 5 else SOFT_BLUE
                    fg_color = TEXT_COLOR

                tk.Button(
                    self.days_frame,
                    text=f"{day:02d}",
                    command=lambda d=day: self.select_day(d),
                    width=3,
                    bg=bg_color,
                    fg=fg_color,
                    activebackground=VNMU_BLUE,
                    activeforeground="white",
                    relief="flat",
                    bd=0,
                    font=("Segoe UI", 8, "bold" if is_selected else "normal"),
                    cursor="hand2",
                    padx=0,
                    pady=4,
                ).grid(row=row_index, column=col_index, padx=1, pady=1)

    def prev_month(self):
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        self.render()

    def next_month(self):
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self.render()

    def select_day(self, day):
        self.selected_date = datetime(self.year, self.month, day)
        self.on_change(self.selected_date)
        self.render()


class DriverDialog:
    def __init__(self, parent, title, driver=None):
        self.result = None
        self.auto_fill_enabled = True
        self.is_updating_cases = False

        last_name, first_name = split_full_name(driver["name"] if driver else "")
        auto_cases = make_cases(build_full_name(last_name, first_name))

        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.transient(parent)
        self.window.grab_set()
        self.window.resizable(False, False)
        self.window.configure(bg=BG_COLOR)

        self.last_name_var = tk.StringVar(value=last_name)
        self.first_name_var = tk.StringVar(value=first_name)
        self.acc_var = tk.StringVar(value=driver["acc"] if driver else auto_cases["acc"])
        self.dat_var = tk.StringVar(value=driver["dat"] if driver else auto_cases["dat"])
        self.full_name_var = tk.StringVar(value=build_full_name(last_name, first_name))

        panel = tk.Frame(
            self.window,
            bg=CARD_COLOR,
            padx=18,
            pady=16,
            highlightbackground=VNMU_RED,
            highlightthickness=2,
        )
        panel.pack(padx=14, pady=14, fill="both", expand=True)

        self._add_entry(panel, "Прізвище", self.last_name_var, 0)
        self._add_entry(panel, "Ім'я", self.first_name_var, 1)
        self._add_entry(panel, "Знахідний", self.acc_var, 2)
        self._add_entry(panel, "Давальний", self.dat_var, 3)

        actions = tk.Frame(panel, bg=CARD_COLOR)
        actions.grid(row=4, column=0, columnspan=2, sticky="e", pady=(16, 0))

        create_small_button(actions, "Авто", self.fill_cases_automatically, VNMU_BLUE, "#08497f").pack(
            side="left", padx=(0, 8)
        )
        create_small_button(actions, "Скасувати", self.window.destroy, VNMU_BLUE, "#08497f").pack(
            side="left", padx=(0, 8)
        )
        create_small_button(actions, "Зберегти", self.on_save, VNMU_RED, "#a82721").pack(side="left")

        for variable in (self.last_name_var, self.first_name_var):
            variable.trace_add("write", self.on_name_changed)

        for variable in (self.acc_var, self.dat_var):
            variable.trace_add("write", self.on_cases_changed)

        self.window.bind("<Return>", lambda _event: self.on_save())
        self.window.bind("<Escape>", lambda _event: self.window.destroy())
        center_window(self.window, parent)

    def _add_entry(self, parent, label, variable, row):
        tk.Label(
            parent,
            text=label,
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            font=("Segoe UI", 10, "bold"),
        ).grid(row=row, column=0, sticky="w", pady=4)

        entry = create_text_entry(parent, width=26, bg="#f4f7fa")
        entry.configure(textvariable=variable)
        entry.grid(row=row, column=1, sticky="ew", pady=4)
        parent.grid_columnconfigure(1, weight=1)

    def on_name_changed(self, *_args):
        full_name = build_full_name(self.last_name_var.get(), self.first_name_var.get())
        self.full_name_var.set(full_name)

        if self.auto_fill_enabled:
            auto_cases = make_cases(full_name)
            self.is_updating_cases = True
            self.acc_var.set(auto_cases["acc"])
            self.dat_var.set(auto_cases["dat"])
            self.is_updating_cases = False

    def on_cases_changed(self, *_args):
        if self.is_updating_cases:
            return
        self.auto_fill_enabled = False

    def fill_cases_automatically(self):
        self.auto_fill_enabled = True
        auto_cases = make_cases(self.full_name_var.get())
        self.is_updating_cases = True
        self.acc_var.set(auto_cases["acc"])
        self.dat_var.set(auto_cases["dat"])
        self.is_updating_cases = False

    def on_save(self):
        full_name = clean_text(self.full_name_var.get())
        acc = clean_text(self.acc_var.get())
        dat = clean_text(self.dat_var.get())

        if len(full_name.split()) < 2:
            messagebox.showerror("Помилка", "Вкажіть прізвище та ім'я.", parent=self.window)
            return

        if not acc or not dat:
            messagebox.showerror("Помилка", "Заповніть відмінки.", parent=self.window)
            return

        self.result = {"name": full_name, "acc": acc, "dat": dat}
        self.window.destroy()


def ask_simple_item(title, prompt, initial_value=""):
    dialog = SimpleItemDialog(root, title, prompt, initial_value)
    root.wait_window(dialog.window)
    return clean_text(dialog.result)


def refresh_comboboxes():
    driver_combo["values"] = [driver["name"] for driver in drivers]
    car_combo["values"] = cars
    destination_combo["values"] = destinations

    if drivers and driver_combo.get() not in driver_combo["values"]:
        driver_combo.current(0)
    if cars and car_combo.get() not in cars:
        car_combo.current(0)
    if destinations and destination_combo.get() not in destinations:
        destination_combo.set(destinations[0])


def add_driver_ui():
    dialog = DriverDialog(root, "Додати водія")
    root.wait_window(dialog.window)
    if not dialog.result:
        return

    _, existing_driver = find_driver_by_name(dialog.result["name"])
    if existing_driver:
        messagebox.showwarning("Увага", "Такий водій уже існує.")
        return

    drivers.append(dialog.result)
    drivers.sort(key=lambda item: item["name"])
    save_drivers()
    refresh_comboboxes()
    driver_combo.set(dialog.result["name"])


def edit_driver_ui():
    index, driver = find_driver_by_name(driver_combo.get())
    if driver is None:
        messagebox.showwarning("Увага", "Оберіть водія зі списку.")
        return

    dialog = DriverDialog(root, "Редагувати водія", driver=driver)
    root.wait_window(dialog.window)
    if not dialog.result:
        return

    duplicate_index, duplicate_driver = find_driver_by_name(dialog.result["name"])
    if duplicate_driver is not None and duplicate_index != index:
        messagebox.showwarning("Увага", "Водій з таким ПІБ уже існує.")
        return

    drivers[index] = dialog.result
    drivers.sort(key=lambda item: item["name"])
    save_drivers()
    refresh_comboboxes()
    driver_combo.set(dialog.result["name"])


def delete_driver_ui():
    current = clean_text(driver_combo.get())
    index, driver = find_driver_by_name(current)
    if driver is None:
        messagebox.showwarning("Увага", "Оберіть водія зі списку.")
        return

    if not messagebox.askyesno("Видалити водія", f"Точно видалити водія:\n{driver['name']}?", parent=root):
        return

    drivers.pop(index)
    save_drivers()
    refresh_comboboxes()


def add_car_ui():
    value = ask_simple_item("Додати авто", "Введіть назву авто:")
    if not value:
        return
    if value in cars:
        messagebox.showwarning("Увага", "Таке авто вже існує.")
        return
    cars.append(value)
    cars.sort()
    save_cars()
    refresh_comboboxes()
    car_combo.set(value)


def delete_car_ui():
    current = clean_text(car_combo.get())
    if not current:
        messagebox.showwarning("Увага", "Оберіть авто зі списку.")
        return

    if not messagebox.askyesno("Видалити авто", f"Точно видалити авто:\n{current}?", parent=root):
        return

    cars.remove(current)
    save_cars()
    refresh_comboboxes()


def edit_car_ui():
    current = clean_text(car_combo.get())
    if not current:
        messagebox.showwarning("Увага", "Оберіть авто зі списку.")
        return
    value = ask_simple_item("Редагувати авто", "Змініть назву авто:", current)
    if not value:
        return
    if value != current and value in cars:
        messagebox.showwarning("Увага", "Таке авто вже існує.")
        return
    index = cars.index(current)
    cars[index] = value
    cars.sort()
    save_cars()
    refresh_comboboxes()
    car_combo.set(value)


def add_destination_ui():
    value = ask_simple_item("Додати місце", "Введіть місце поїздки:")
    if not value:
        return
    if value in destinations:
        messagebox.showwarning("Увага", "Таке місце вже існує.")
        return
    destinations.append(value)
    destinations.sort()
    save_destinations()
    refresh_comboboxes()
    destination_combo.set(value)


def edit_destination_ui():
    current = clean_text(destination_combo.get())
    if not current:
        messagebox.showwarning("Увага", "Оберіть місце зі списку.")
        return
    value = ask_simple_item("Редагувати місце", "Змініть місце поїздки:", current)
    if not value:
        return
    if value != current and value in destinations:
        messagebox.showwarning("Увага", "Таке місце вже існує.")
        return
    index = destinations.index(current)
    destinations[index] = value
    destinations.sort()
    save_destinations()
    refresh_comboboxes()
    destination_combo.set(value)


def delete_destination_ui():
    current = clean_text(destination_combo.get())
    if not current:
        messagebox.showwarning("Увага", "Оберіть місце зі списку.")
        return

    if not messagebox.askyesno(
        "Видалити місце",
        f"Точно видалити місце поїздки:\n{current}?",
        parent=root,
    ):
        return

    destinations.remove(current)
    save_destinations()
    refresh_comboboxes()


def on_calendar_change(selected_date):
    global current_selected_date
    current_selected_date = selected_date
    date_var.set(selected_date.strftime("%d.%m.%Y"))


def open_folder():
    folder = get_output_folder()
    os.makedirs(folder, exist_ok=True)
    os.startfile(folder)


def create_document():
    date_value = clean_text(date_var.get())
    driver_name = clean_text(driver_combo.get())
    car = clean_text(car_combo.get())
    destination = clean_text(destination_combo.get())

    if not date_value or not driver_name or not car or not destination:
        messagebox.showerror("Помилка", "Заповніть усі поля форми.")
        return

    try:
        selected_date = datetime.strptime(date_value, "%d.%m.%Y")
    except ValueError:
        messagebox.showerror("Помилка", "Дата має бути у форматі ДД.ММ.РРРР.")
        return

    _, driver = find_driver_by_name(driver_name)
    if driver is None:
        messagebox.showerror("Помилка", "Оберіть водія зі списку або додайте нового.")
        return

    try:
        path = generate_order(
            driver["name"],
            driver["acc"],
            driver["dat"],
            car,
            destination,
            date_value,
        )
        save_last_used_date(date_value)
    except Exception as error:
        messagebox.showerror("Помилка", str(error))
        return

    on_calendar_change(selected_date)
    update_order_number_label()
    messagebox.showinfo("Готово", f"Документ створено:\n{path}")
    os.startfile(path)


def require_password():
    password = simpledialog.askstring("Вхід", "Введіть пароль:", show="*", parent=root)
    if password != APP_PASSWORD:
        messagebox.showerror("Помилка", "Невірний пароль.")
        root.destroy()
        raise SystemExit


drivers = [normalize_driver(driver) for driver in load_json("data/drivers.json", [])]
drivers.sort(key=lambda item: item["name"])
cars = load_json("data/cars.json", [])
destinations = load_json(
    "data/destinations.json",
    [
        "ВНМУ - По місту",
        "ВНМУ - по території",
        "ВНМУ - Університетська лікарня",
        "ВНМУ - Стадниця",
        "ВНМУ - Київ - ВНМУ",
        "ВНМУ - Одеса - ВНМУ",
        "ВНМУ - прибирання сміття",
        "ВНМУ - прибирання снігу",
    ],
)


root = tk.Tk()
root.withdraw()
root.title(APP_TITLE)
root.geometry("1120x670")
root.minsize(1120, 670)
root.configure(bg=BG_COLOR)

require_password()

style = ttk.Style()
style.theme_use("clam")
style.configure(
    "Form.TCombobox",
    padding=(10, 8),
    fieldbackground=PANEL_COLOR,
    background="#cfe7fb",
    foreground=TEXT_COLOR,
    bordercolor="#8bb8de",
    lightcolor="#8bb8de",
    darkcolor="#8bb8de",
    arrowsize=20,
    arrowcolor=VNMU_BLUE,
)
style.map(
    "Form.TCombobox",
    fieldbackground=[("readonly", PANEL_COLOR)],
    background=[("readonly", "#cfe7fb")],
    foreground=[("readonly", TEXT_COLOR)],
)

root.deiconify()
logo_image = load_logo_image()
order_number_var = tk.StringVar()
update_order_number_label()
current_selected_date = get_initial_date()
date_var = tk.StringVar(value=current_selected_date.strftime("%d.%m.%Y"))

outer = tk.Frame(root, bg=BG_COLOR, padx=22, pady=18)
outer.pack(fill="both", expand=True)

shell = tk.Frame(outer, bg=CARD_COLOR, highlightbackground="#d7e1ea", highlightthickness=1)
shell.pack(fill="both", expand=True)

tk.Frame(shell, bg=VNMU_RED, height=14).pack(fill="x")

header = tk.Frame(shell, bg=VNMU_BLUE, padx=28, pady=22)
header.pack(fill="x")
header.grid_columnconfigure(0, weight=1)

title_wrap = tk.Frame(header, bg=VNMU_BLUE)
title_wrap.grid(row=0, column=0, sticky="w")

tk.Label(
    title_wrap,
    text=APP_TITLE,
    font=("Times New Roman", 22, "bold"),
    bg=VNMU_BLUE,
    fg="white",
    justify="left",
    wraplength=650,
).pack(anchor="w")
tk.Frame(title_wrap, bg=VNMU_GOLD, height=4, width=260).pack(anchor="w", pady=(12, 0))

if logo_image:
    tk.Label(header, image=logo_image, bg=VNMU_BLUE).grid(row=0, column=1, sticky="e", padx=(20, 0))

content = tk.Frame(shell, bg=CARD_COLOR, padx=24, pady=24)
content.pack(fill="both", expand=True)
content.grid_columnconfigure(0, weight=1)
content.grid_columnconfigure(1, weight=0)

left_panel = tk.Frame(content, bg=CARD_COLOR)
left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 18))

right_panel = tk.Frame(
    content,
    bg=SOFT_BLUE,
    padx=16,
    pady=16,
    highlightbackground=VNMU_BLUE,
    highlightthickness=1,
)
right_panel.grid(row=0, column=1, sticky="ns")

main_area = tk.Frame(left_panel, bg=CARD_COLOR)
main_area.pack(fill="both", expand=True)
main_area.grid_columnconfigure(0, weight=0)
main_area.grid_columnconfigure(1, weight=1)

top_info = tk.Frame(main_area, bg=CARD_COLOR)
top_info.grid(row=0, column=1, pady=(0, 14))

order_banner = tk.Frame(
    top_info,
    bg=SOFT_RED,
    padx=18,
    pady=10,
    highlightbackground=VNMU_RED,
    highlightthickness=1,
)
order_banner.pack(side="left", padx=(0, 6))

tk.Label(order_banner, text="Номер розпорядження", font=("Segoe UI", 10, "bold"), bg=SOFT_RED, fg=VNMU_RED).pack()
tk.Label(order_banner, textvariable=order_number_var, font=("Segoe UI", 17, "bold"), bg=SOFT_RED, fg=TEXT_COLOR).pack(
    pady=(3, 0)
)

date_badge = tk.Frame(
    top_info,
    bg=SOFT_BLUE,
    padx=18,
    pady=10,
    highlightbackground=VNMU_BLUE,
    highlightthickness=1,
)
date_badge.pack(side="left", padx=(6, 0))
tk.Label(date_badge, text="Дата", font=("Segoe UI", 10, "bold"), bg=SOFT_BLUE, fg=VNMU_BLUE).pack()
tk.Label(date_badge, textvariable=date_var, font=("Segoe UI", 15, "bold"), bg=SOFT_BLUE, fg=TEXT_COLOR).pack(
    pady=(3, 0)
)

calendar_panel = tk.Frame(main_area, bg=CARD_COLOR)
calendar_panel.grid(row=1, column=0, sticky="n")

calendar_widget = InlineCalendar(calendar_panel, current_selected_date, on_calendar_change)
calendar_widget.frame.pack()

form_panel = tk.Frame(
    main_area,
    bg=PANEL_COLOR,
    padx=24,
    pady=22,
    highlightbackground=VNMU_BLUE,
    highlightthickness=1,
)
form_panel.grid(row=1, column=1, sticky="n", padx=(18, 0))

driver_label_card = tk.Frame(form_panel, bg=SOFT_BLUE, padx=12, pady=8, highlightbackground=VNMU_BLUE, highlightthickness=1)
driver_label_card.grid(row=0, column=0, sticky="w", pady=10)
tk.Label(driver_label_card, text="Водій", font=("Segoe UI", 12, "bold"), bg=SOFT_BLUE, fg=VNMU_BLUE).pack()
driver_combo = ttk.Combobox(
    form_panel,
    width=28,
    height=12,
    state="readonly",
    font=("Segoe UI", 10),
    style="Form.TCombobox",
)
driver_combo.grid(row=0, column=1, sticky="w", padx=(14, 0), pady=10)

car_combo = ttk.Combobox(
    form_panel,
    width=28,
    height=12,
    state="readonly",
    font=("Segoe UI", 10),
    style="Form.TCombobox",
)
car_label_card = tk.Frame(form_panel, bg=SOFT_BLUE, padx=12, pady=8, highlightbackground=VNMU_BLUE, highlightthickness=1)
car_label_card.grid(row=1, column=0, sticky="w", pady=10)
tk.Label(car_label_card, text="Автомобіль", font=("Segoe UI", 12, "bold"), bg=SOFT_BLUE, fg=VNMU_BLUE).pack()
car_combo.grid(row=1, column=1, sticky="w", padx=(14, 0), pady=10)

place_label_card = tk.Frame(form_panel, bg=SOFT_BLUE, padx=12, pady=8, highlightbackground=VNMU_BLUE, highlightthickness=1)
place_label_card.grid(row=2, column=0, sticky="w", pady=10)
tk.Label(place_label_card, text="Місце поїздки", font=("Segoe UI", 12, "bold"), bg=SOFT_BLUE, fg=VNMU_BLUE).pack()
destination_combo = ttk.Combobox(
    form_panel,
    width=28,
    height=12,
    font=("Segoe UI", 10),
    style="Form.TCombobox",
)
destination_combo.grid(row=2, column=1, sticky="w", padx=(14, 0), pady=10)

buttons = tk.Frame(form_panel, bg=PANEL_COLOR)
buttons.grid(row=3, column=0, columnspan=2, pady=(28, 0))

create_main_button(
    buttons,
    "Створити документ",
    create_document,
    VNMU_RED,
    "#a82721",
    VNMU_GOLD,
).pack(ipadx=20, ipady=4)

tk.Label(
    right_panel,
    text="Керування списками",
    font=("Segoe UI", 12, "bold"),
    bg=SOFT_BLUE,
    fg=TEXT_COLOR,
).pack(anchor="w", pady=(0, 12))

manager_specs = [
    ("Водії", add_driver_ui, edit_driver_ui, delete_driver_ui),
    ("Автомобілі", add_car_ui, edit_car_ui, delete_car_ui),
    ("Місця поїздок", add_destination_ui, edit_destination_ui, delete_destination_ui),
]

for title, add_command, edit_command, delete_command in manager_specs:
    block = tk.Frame(right_panel, bg=CARD_COLOR, padx=14, pady=14, highlightbackground="#b7d1ea", highlightthickness=1)
    block.pack(fill="x", pady=(0, 14))
    tk.Label(block, text=title, font=("Segoe UI", 10, "bold"), bg=CARD_COLOR, fg=TEXT_COLOR).pack(anchor="w")
    actions = tk.Frame(block, bg=CARD_COLOR)
    actions.pack(anchor="w", pady=(12, 0))
    create_small_button(actions, "Додати", add_command, VNMU_RED, "#a82721").pack(side="left", padx=(0, 8))
    create_small_button(actions, "Редагувати", edit_command, VNMU_BLUE, "#08497f").pack(side="left", padx=(0, 8))
    create_small_button(actions, "Видалити", delete_command, "#7c8ea3", "#66798f").pack(side="left")

folder_box = tk.Frame(right_panel, bg=CARD_COLOR, padx=12, pady=12, highlightbackground="#b7d1ea", highlightthickness=1)
folder_box.pack(fill="x", pady=(12, 0))
tk.Label(folder_box, text="Документи", font=("Segoe UI", 10, "bold"), bg=CARD_COLOR, fg=TEXT_COLOR).pack(anchor="w")
create_small_button(folder_box, "Відкрити папку", open_folder, VNMU_BLUE, "#08497f").pack(anchor="w", pady=(10, 0))

tk.Frame(shell, bg=VNMU_BLUE, height=16).pack(fill="x", side="bottom")

refresh_comboboxes()
if drivers:
    driver_combo.current(0)
if cars:
    car_combo.current(0)
if destinations:
    destination_combo.set(destinations[0])

root.mainloop()
