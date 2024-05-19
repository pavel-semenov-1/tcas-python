import datetime
import random
import sys
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
from win32api import GetMonitorInfo, MonitorFromPoint

monitor_info = GetMonitorInfo(MonitorFromPoint((0, 0)))
work_area = monitor_info.get("Work")

# SETTINGS
LOG_FILENAME = 'log'
DATA_FILENAME = 'data.csv'
IMAGE_LOCATION = 'img'
BLINK_DELAY = 300
PROGRESS_FONT_SIZE = 15
QUESTION_FONT_SIZE = 18
BUTTON_HITBOX_WIDTH = 100
BUTTON_HITBOX_HEIGHT = 50
LBL_MAIN_HEIGHT = 12
LBL_MAIN_WIDTH = 100
BTN_TEST_WIDTH = 50
LBL_PROGRESS_HEIGHT = 5
LBL_PROGRESS_WIDTH = 20
LBL_MAIN_WRAPLENGTH = 1000
BACKGROUD_WIDTH = 1057
BACKGROUD_HEIGHT = 466
PAD_HEIGHT = 450
CANVAS_BACKGROUND_COLOR = '#eeeee0'
FONT_FAMILY = 'Helvetica'

# ERROR HANDLING & LOGGING
logfile = f'{LOG_FILENAME}-{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.txt'
try:
    LOGFILE = open(logfile, 'w', encoding='utf-8')
except IOError as e:
    messagebox.showerror('Program Error', f'Error: unable to create log file {logfile}')


def ERROR(message):
    line = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} [ERROR] {message}'
    print(line, file=sys.stderr)
    print(line, flush=True, file=LOGFILE)
    messagebox.showerror('Program Error', f'Error: ${message}')


def LOG(message):
    line = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} [DEBUG] {message}'
    print(line)
    print(line, flush=True, file=LOGFILE)


# INITIALIZE VARIABLES
buttons = []
current_question = 0
results = dict()
testing = False
name = ''

# INTITIALIZE GUI
app = tk.Tk()
PAD_HEIGHT = min((work_area[3] - BACKGROUD_HEIGHT, PAD_HEIGHT))
app.geometry(f'{BACKGROUD_WIDTH}x{BACKGROUD_HEIGHT + PAD_HEIGHT}')
app.resizable(width=False, height=True)
app.minsize(BACKGROUD_WIDTH, BACKGROUD_HEIGHT + PAD_HEIGHT)
canvas = tk.Canvas(app, bg=CANVAS_BACKGROUND_COLOR, height=BACKGROUD_HEIGHT, width=BACKGROUD_WIDTH)
canvas.pack(fill=tk.BOTH, expand=True)

LOG("GUI initialized")

try:
    bg = tk.PhotoImage(file=f'{IMAGE_LOCATION}/bg.png')
    canvas.create_image(0, 0, image=bg, anchor=tk.NW)
    LOG("background created")
except FileNotFoundError as e:
    ERROR(e)


class PanelButton:
    def __init__(self, obj, image, image_wrong, image_right, name, x, y, question=None, description=None):
        self.question = question
        self.description = description
        self.obj = obj
        self.name = name
        self.image = image
        self.image_wrong = image_wrong
        self.image_right = image_right
        self.x = x
        self.y = y

    def wrong(self):
        canvas.itemconfig(self.obj, image=self.image_wrong)
        app.after(BLINK_DELAY, self.back)

    def right(self):
        canvas.itemconfig(self.obj, image=self.image_right)
        app.after(BLINK_DELAY, self.back)

    def back(self):
        canvas.itemconfig(self.obj, image=self.image)

    def __str__(self):
        return f'{self.name} {self.x} {self.y}'


# LOAD & DRAW BUTTONS
try:
    with open(f'{IMAGE_LOCATION}/positions.csv', encoding='utf-8') as positions:
        LOG("opened positions file")
        for line in positions.readlines()[1:]:
            line = line.strip()
            if line and not line.startswith('#'):
                filename, x, y = line.split(',')
                image = tk.PhotoImage(file=f'{IMAGE_LOCATION}/{filename}.png')
                obj = canvas.create_image(x, y, image=image, anchor=tk.NW)
                btn = PanelButton(obj, image, tk.PhotoImage(file=f'{IMAGE_LOCATION}/{filename}_wrong.png'),
                                  tk.PhotoImage(file=f'{IMAGE_LOCATION}/{filename}_right.png'), filename, int(x),
                                  int(y))
                buttons.append(btn)
        LOG(f"successfully loaded {len(buttons)} buttons")
except FileNotFoundError as e:
    ERROR(e)
except IOError as e:
    ERROR(e)

# LOAD QUESTIONS
try:
    with open(f'buttons.txt', encoding='utf-8') as settings:
        LOG("opened buttons file")
        for line in settings.readlines()[1:]:
            line = line.strip()
            name, question, description = line.split('|')
            for button in buttons:
                if button.name == name:
                    button.question = question
                    button.description = description
                    break
        LOG(f"loaded questions and descriptions")
except FileNotFoundError as e:
    ERROR(e)

# PLACE BUTTONS
lbl_progress = tk.Label(app, height=LBL_PROGRESS_HEIGHT, width=LBL_PROGRESS_WIDTH, text="Question 0/20", bg=CANVAS_BACKGROUND_COLOR,
                        font=(FONT_FAMILY, PROGRESS_FONT_SIZE, 'bold'), padx=0, pady=0)
lbl_main = tk.Label(app, height=LBL_MAIN_HEIGHT, width=LBL_MAIN_WIDTH, text="Нажимайте на кнопки чтобы увидеть описание", bg=CANVAS_BACKGROUND_COLOR,
                    font=(FONT_FAMILY, QUESTION_FONT_SIZE, 'bold'), wraplength=LBL_MAIN_WRAPLENGTH, justify='center')
lbl_main.place(relx=0.5, y=BACKGROUD_HEIGHT, anchor=tk.N)

btn_test = tk.Button(app, width=BTN_TEST_WIDTH, bg='white', text='Начать тест')
btn_test.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

btn_result = tk.Button(app, bg='white', text='#')


def export_data(event):
    if len(results) == 0:
        ERROR("No tests")
        return
    with open(DATA_FILENAME, 'w', encoding='utf-8') as file:
        LOG(f"opened {DATA_FILENAME} file to export results")
        file.write(f'Имя,{",".join([btn.name for btn in buttons])},Процент успешности\n')
        for name in results.keys():
            success_rate = 100*len(results[name])/len(buttons)
            file.write(f"{name},{','.join([('1' if (btn.obj in results[name]) else '0') for btn in buttons])},{round(success_rate)}\n")
    LOG(f"export finished successfully")


btn_result.bind('<Button-1>', export_data)


def next_question():
    LOG("loading next question")
    global current_question
    global testing
    btn_test.pack_forget()
    btn_test.place_forget()
    lbl_progress.place(relx=0.5, rely=0.9, anchor=tk.N)

    if current_question < len(buttons):
        while buttons[current_question] is None:
            current_question += 1
        q = buttons[current_question]
        LOG(f"question loaded: {q.question}")
        lbl_main.config(text=q.question)
        lbl_main.update()
        lbl_progress.config(text=f'Вопрос {current_question + 1}/{len(buttons)}')
        lbl_progress.update()
    else:
        testing = False
        LOG("showing results")
        lbl_main.config(text=f'Ваш результат: {len(results[name])}/{len(buttons)}')
        lbl_main.update()
        lbl_progress.place_forget()
        btn_test.config(text="Попробовать ещё раз")
        btn_test.place(relx=0.5, rely=0.99, anchor=tk.S)
        btn_result.place(relx=1, rely=1, anchor=tk.SE)


def canvas_click(event):
    global current_question
    if testing:
        if current_question < len(buttons):
            btn = buttons[current_question]
            if btn.x < event.x and btn.x + BUTTON_HITBOX_WIDTH > event.x and btn.y < event.y and btn.y + BUTTON_HITBOX_HEIGHT > event.y:
                LOG("correct answer submitted")
                btn.right()
                current_question += 1
                results[name].append(btn.obj)
                next_question()
            else:
                for btn in buttons:
                    if btn.x < event.x and btn.x + BUTTON_HITBOX_WIDTH > event.x and btn.y < event.y and btn.y + BUTTON_HITBOX_HEIGHT > event.y:
                        LOG("wrong answer submitted")
                        btn.wrong()
                        current_question += 1
                        next_question()
                        break
    else:
        for btn in buttons:
            if btn.x < event.x and btn.x + BUTTON_HITBOX_WIDTH > event.x and btn.y < event.y and btn.y + BUTTON_HITBOX_HEIGHT > event.y:
                LOG(f'printing desription for button {btn.name}')
                lbl_main.config(text=btn.description)
                lbl_main.update()


def start(event):
    global current_question
    global testing
    global results
    global name

    name = simpledialog.askstring("Тест", "Введите имя")
    results[name] = []

    testing = True
    current_question = 0
    random.shuffle(buttons)
    next_question()
    LOG(f"starting the test")


btn_test.bind("<Button-1>", start)
canvas.bind("<Button-1>", canvas_click)


def close():
    LOG("quitting")
    sys.exit(0)


app.protocol("WM_DELETE_WINDOW", close)
app.mainloop()
