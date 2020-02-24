from tkinter import *
from tkinter.ttk import Combobox
from tkinter import ttk
from tkinter.ttk import Button
from tkinter.ttk import Progressbar
from datetime import datetime
from tkinter import messagebox as mb
import time, threading
import pickle
import socket
import hashlib
from uuid import getnode as get_mac
import os.path

config_path = "log/config.bin"


class Scale(ttk.Scale):
    def __init__(self, master=None, **kwargs):
        ttk.Scale.__init__(self, master, **kwargs)
        self.bind('<Button-1>', self.set_value)

    def set_value(self, event):
        self.event_generate('<Button-3>', x=event.x, y=event.y)
        return 'break'


def get_info(name):
    info = None
    with open(config_path, 'r', encoding='utf-8') as file:
        lines = file.read().splitlines()

    for i in range(len(lines)):
        if name in lines[i]:
            info = lines[i][len(name) + 1:len(lines[i])]
    file.close()
    return info


good_width = 500
server_ip = str(get_info("server_ip"))
address_to_server = (server_ip, 8686)
clients = []


def generate_key():
    if not os.path.exists("log"):
        os.mkdir("log")
    mac = hex(get_mac()).replace('0x', '')
    sha = hashlib.sha1(mac.encode('utf-8')).hexdigest()
    if sha == get_info('key'):
        return True
    elif get_info('key') is not None and sha != get_info('key'):
        mb.showerror('Ошибка', 'Похоже, что Вы пользуетесь не своим экземпляром программы. Просьба обратиться к HR '
                               'или системному администратору для переустановки программы.')
        window.quit()
        return False

    file = open(config_path, "a", encoding='utf-8')
    file.write('\n' + "key:" + sha)
    file.close()
    return True


def set_good_width(width):
    if width < good_width:
        return good_width
    return width


def get_departments():
    global address_to_server
    global clients
    MAX_CONNECTIONS = 1
    clients = [socket.socket(socket.AF_INET, socket.SOCK_STREAM) for i in range(MAX_CONNECTIONS)]
    send_data("get_departments")
    time.sleep(2)

    for i in range(MAX_CONNECTIONS):
        data = clients[i].recv(1024)
        data = pickle.loads(data)

    return data


def send_data(data):
    global address_to_server
    global clients
    MAX_CONNECTIONS = 1

    clients = [socket.socket(socket.AF_INET, socket.SOCK_STREAM) for i in range(MAX_CONNECTIONS)]
    for client in clients:
        try:
            client.connect(address_to_server)
        except TimeoutError:
            mb.showerror("Ошибка", "Ошибка подключения к серверу. Повторите позже или обратитесь к системному "
                                   "администратору.")
            window.quit()
            return -1
    data_to_send = pickle.dumps(data)

    for i in range(MAX_CONNECTIONS):
        clients[i].send(data_to_send)


def is_anon():
    if anon_state.get():
        name_enter.configure(state='disabled')
    else:
        name_enter.configure(state='normal')


def start_btn_clicked():
    global name
    global department
    global question_number
    global experience
    department = str(department_select.get())
    if not anon_state.get() and name_enter.get() == '':
        mb.showerror('Ошибка', 'Введите имя или выберите "Анонимно".')
        return -1

    if anon_state.get():
        name = "Анонимно"
    else:
        name = name_enter.get()
    age = experience_age.get()
    month = experience_month.get()
    experience = age + " " + month
    message = 'Подтвердите введенные Вами данные:' + '\n' + 'Имя: ' + name + '\n' + 'Отдел: ' + department + '\n' + \
              'Ваш стаж: ' + experience
    answer = mb.askyesno('Подтверждение', message)
    if not answer:
        return -1
    result.append(name)
    result.append(str(department))
    result.append(experience)

    objects = [name_request, name_enter, anon_flag, start_btn, quit_button, department_select, department_request,
               experience_month, experience_age, experience_label]
    for object_name in objects:
        object_name.destroy()

    config_question_screen(question_number)


def place_digits_under_scale(width):
    global digits
    d = width / 10 - 0.5

    digits = [Label(window) for i in range(11)]
    start = 25

    for i in range(10):
        digits[i] = Label(window, text=str(i))
        digits[i].place(x=start + i * 0.98 * d, y=120)
    digits[10] = Label(window, text="10")
    digits[10].place(x=start + 10 * 0.98 * d - 2, y=120)


def config_question_screen(question_number):
    global question
    global next_btn
    global scale
    global answers
    global answer

    question = Label(window, text=questions[question_number])
    w = len(questions[question_number]) * 7
    w = set_good_width(w)
    h = 250
    window.geometry('{}x{}'.format(w, h))
    question.place(x=25, y=35)
    answer_text = "0 - " + answers[question_number][0] + "    5 - " + \
                  answers[question_number][1] + "   10 - " + answers[question_number][2]
    answer = Label(window, text=answer_text)
    answer.place(x=25, y=150)
    if question_number == 11:
        next_btn = Button(window, text="Завершить опрос", command=final_action)
    else:
        next_btn = Button(window, text="Следующий вопрос", command=next_question)
    scale = Scale(window, orient=HORIZONTAL, length=w - 75, from_=0, to=10, command=accept_whole_number_only)
    scale.place(x=25, y=85)

    place_digits_under_scale(w - 75)
    next_btn.place(x=w / 2 - 50, y=190)


def accept_whole_number_only(self, e=None):
    value = scale.get()
    if int(value) != value:
        scale.set(round(value))


def next_question():
    global question_number
    global grades
    global question
    global next_btn
    global scale
    global answers
    global answer
    global digits

    scale.place(x=-10000, y=10000)
    objects = [question, next_btn, answer]
    for object_name in objects:
        object_name.destroy()
    for i in range(11):
        digits[i].destroy()
    grade = int(scale.get())
    grades.append(grade)
    question_number += 1
    config_question_screen(question_number)


def final_action():
    window.geometry('250x150')
    scale.place(x=-10000, y=10000)
    objects = [question, next_btn, answer]
    for object_name in objects:
        object_name.destroy()
    for i in range(11):
        digits[i].destroy()
    grade = int(scale.get())
    grades.append(grade)
    result.append(grades)

    current_time = str(int(time.time()))
    result.append(current_time)

    send_data(result)

    done = Label(window, text="Благодарим за прохождение опроса!")
    done.place(x=25, y=50)
    quit_button = Button(window, text='Выход', command=window.quit)
    quit_button.place(x=100, y=100)


# переменные
result = ["worker"]
grades = []
digits = []
name = "Анонимно"
department = -1
question_number = 0
departments = [1, 2, 3]
age_list = ["0 лет"]
experience = ''
month_list = ["1 месяц", "2 месяца", "3 месяца", "4 месяца", "5 месяцев", "6 месяцев", "7 месяцев", "8 месяцев",
              "9 месяцев", "10 месяцев", "11 месяцев"]
questions = ["Знаете ли вы, каких именно результатов от вас ожидают на работе?",
             "Есть ли у вас все материалы и оборудование, необходимые для качественного выполнения работы?",
             "Имеете ли вы возможность каждый день на рабочем месте заниматься тем, что у вас получается лучше всего?",
             "Получали ли вы похвалу или награду за хорошую работу в последнюю неделю?",
             "Заботится ли ваш начальник или кто-либо из коллег о вашем личностном развитии?",
             "Имеется ли сотрудник, который поощряет ваше профессиональное развитие?",
             "Считаются ли коллеги и руководство с вашим профессиональным мнением?",
             "Полагаете ли вы, что миссия/цель деятельности вашей компании помогает вам осознать важность вашей работы?",
             "Привержены ли ваши коллеги высоким стандартам качества работы?",
             "Есть ли у вас друг на работе?",
             "Обсуждал ли с вами кто-либо на работе ваш прогресс в последние полгода?",
             "Была ли у вас возможность учиться новому и расти профессионально в последний год?"]

answers = [["Совсем не знаю", "Сомневаюсь", "Точно знаю"],
           ["Абсолютно нет", "Есть, но не все", "Есть все необходимое"],
           ["Совсем не имею", "Сомневаюсь", "Точно имею"],
           ["Совсем не получал", "Получал, но недостаточно", "Получал, и достаточно"],
           ["Совсем не заботится", "Затрудняюсь ответить", "Точно заботится"],
           ["Точно не имеется", "Сомневаюсь", "Точно имеется"],
           ["Совсем не считаются", "Сомневаюсь", "Точно считаются"],
           ["Совсем не помогает", "Сомневаюсь", "Точно помогает"],
           ["Совсем не привержены", "Сомневаюсь", "Точно привержены"],
           ["Точно нет", "Затрудняюсь ответить", "Точно есть"],
           ["Точно не обсуждал", "Затрудняюсь ответить", "Точно обсуждал"],
           ["Совсем не было", "Сомневаюсь", "Точно была"]]

for i in range(1, 21):
    if i % 10 == 1 and i != 11:
        age_list.append(str(i) + " год")
        continue
    if (i % 10 == 2 or i % 10 == 3 or i % 10 == 4) and (i != 12 and i != 13 and i != 14):
        age_list.append(str(i) + " года")
        continue
    age_list.append(str(i) + ' лет')

# общие настройки окна
window = Tk()

window.title("Gallup опрос")
window.geometry('400x275')
window.resizable(False, False)
x = (window.winfo_screenmmwidth() - window.winfo_reqwidth()) / 2
y = (window.winfo_screenheight() - window.winfo_reqheight()) / 2
window.wm_geometry("+%d+%d" % (x, y))
question = Label(window, text=questions[question_number])
next_btn = Button(window, text="Следующий вопрос", command=next_question)
scale = Scale(window, orient=HORIZONTAL, length=300, from_=0, to=10)
answer = Label(window, text="")

# departments = get_departments()
departments = ['1', '2', '3', '4']
# первый экран
name_request = Label(window, text='Введите Ваше имя и фамилию:')
name_request.place(x=45, y=35)
name_enter = Entry(window, width=50, state='normal')
name_enter.place(x=45, y=60)
start_btn = Button(window, text="Приступить к опросу", command=start_btn_clicked)
start_btn.place(x=180, y=225)
department_request = Label(window, text="Выберите Ваш отдел:")
department_request.place(x=45, y=85)
department_select = Combobox(window, width=47)
department_select['values'] = departments
department_select.current(0)
department_select.place(x=45, y=110)
experience_label = Label(window, text="Введите Ваш стаж работы:")
experience_label.place(x=45, y=135)
experience_age = Combobox(window, width=20)
experience_age['values'] = age_list
experience_age.current(0)
experience_age.place(x=45, y=160)
experience_month = Combobox(window, width=20)
experience_month['values'] = month_list
experience_month.current(0)
experience_month.place(x=205, y=160)
anon_state = BooleanVar()
anon_state.set(False)
anon_flag = Checkbutton(window, text='Пройти опрос анонимно', variable=anon_state,
                        onvalue=1, offvalue=0, command=is_anon)
anon_flag.place(x=45, y=185)
quit_button = Button(window, text='Выход', command=window.quit)
quit_button.place(x=100, y=225)

key = get_info("key")
result.append(key)

if generate_key():
    window.mainloop()
