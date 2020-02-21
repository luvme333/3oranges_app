from tkinter import *
from tkinter.ttk import Combobox
from tkinter import ttk
from tkinter.ttk import Button
from tkinter.ttk import Progressbar
from tkinter import messagebox as mb
import time, threading
import pickle
import socket
import hashlib
from uuid import getnode as get_mac
import os.path
from tkinter import filedialog
# Статистические функции
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure


class NavigationToolbar(NavigationToolbar2Tk):
    # only display the buttons we need
    toolitems = [t for t in NavigationToolbar2Tk.toolitems if
                 t[0] == 'Save']


# def graph_stat(check, name, new_window):
#     df = pd.read_csv('data.csv', encoding='utf-8')
#     if check == 0:
#         None
#     elif check == 1:
#         df = df[df['Name'] == name]
#     elif check == 2:
#         df = df[df['Department'] == name]
#     df.sort_values("timelaps", inplace=True)
#     df.drop_duplicates(subset="hash",
#                        keep='last', inplace=True)
#     metrics = [np.mean((df.q1 + df.q2) / 2), np.mean((df.q3 + df.q4 + df.q5 + df.q6) / 4),
#                np.mean((df.q7 + df.q8 + df.q9 + df.q10) / 4), np.mean((df.q11 + df.q12) / 2)]
#     rates = ['Понимание своих задач \n и обеспеченность ресурсами', 'Нематериальное \n признание',
#              'Ценность работы \n в данной команде', 'Конструктивная обратная связь \n и перспективы развития']
#     colors = ['#005DFF', '#FF0000', '#00C11A', '#D4DB00']
#     fig = Figure(figsize=(16, 8))
#     ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
#     ax.set_ylim(0, 10)
#     ax.bar(rates, metrics, width=0.5, color=colors)
#     ax.set_xlabel('Показатели')
#     canvas = FigureCanvasTkAgg(fig, master=new_window)
#     plt.show()
#     canvas.draw()
#     canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
#     toolbar = NavigationToolbar(canvas, window=new_window)
#     toolbar.update()
#     canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=True)
#     # тянуть на сейв
#     if check == 0:
#         discription = ''
#     elif check == 1:
#         discription = name
#     elif check == 2:
#         discription = name
#     metrics.append(discription)
#     global df_to_save
#     df_to_save = pd.DataFrame([metrics], columns=['st1', 'st2', 'st3', 'st4', 'discript'])
def graph_stat():
    df = pd.read_csv('data.csv', encoding='utf-8')
    if graph_type == 0:
        new_window = company_window
    elif graph_type == 1:
        df = df[df['Name'] == combobox.get()]
        new_window = individual_window
    elif graph_type == 2:
        df = df[df['Department'] == combobox.get()]
        new_window = departments_window
    df.sort_values("timelaps", inplace=True)
    df.drop_duplicates(subset="hash",
                       keep='last', inplace=True)
    metrics = [np.mean((df.q1 + df.q2) / 2), np.mean((df.q3 + df.q4 + df.q5 + df.q6) / 4),
               np.mean((df.q7 + df.q8 + df.q9 + df.q10) / 4), np.mean((df.q11 + df.q12) / 2)]
    rates = ['Понимание своих задач \n и обеспеченность ресурсами', 'Нематериальное \n признание',
             'Ценность работы \n в данной команде', 'Конструктивная обратная связь \n и перспективы развития']
    colors = ['#005DFF', '#FF0000', '#00C11A', '#D4DB00']
    fig = Figure(figsize=(10, 4))
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    ax.set_ylim(0, 10)
    ax.bar(rates, metrics, width=0.5, color=colors)
    ax.set_xlabel('Показатели')
    canvas = FigureCanvasTkAgg(fig, master=new_window)
    plt.show()
    canvas.draw()
    canvas.get_tk_widget().place(x=0, y=900)
    toolbar = NavigationToolbar(canvas, window=new_window)
    toolbar.update()
    canvas._tkcanvas.place(x=5, y=100)
    # тянуть на сейв
    if graph_type == 0:
        description = ''
    elif graph_type == 1:
        description = combobox.get()
    elif graph_type == 2:
        description = combobox.get()
    else:
        description = ''
    metrics.append(description)
    global df_to_save
    df_to_save = pd.DataFrame([metrics], columns=['st1', 'st2', 'st3', 'st4', 'discript'])


path_to_departments = "log/departments.txt"
departments = []
departments_state = []

window = Tk()
window.title("Hello World")
window.geometry('400x250')
window.resizable(False, False)
x = (window.winfo_screenmmwidth() - window.winfo_reqwidth()) / 2
y = (window.winfo_screenheight() - window.winfo_reqheight()) / 2
window.wm_geometry("+%d+%d" % (x, y))


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


def get_departments():
    global departments
    with open(path_to_departments, encoding='utf-8') as file:
        departments = [row.strip() for row in file]
    i = 0
    size = len(departments)
    while i < size:
        if departments[i] == '':
            departments.remove(departments[i])
            i -= 1
            size = len(departments)
        else:
            i += 1


def get_names():
    df = pd.read_csv('data.csv', encoding='utf-8')
    df.drop_duplicates(subset="hash",
                       keep='last', inplace=True)
    names = list(df.Name.values)
    return names


def weight_calculate():
    max = 0
    for department in departments:
        length = len(department)
        if length > max:
            length, max = max, length

    return max * 8 + 200 if max > 30 else 400


def height_calculate():
    count = 0
    for department in departments:
        count += 1
    return count * 30 if count > 4 else 150


def delete_department():
    global departments_state, departments_count, chk_states, departments
    states = [chk_states[i].get() for i in range(len(chk_states))]

    if True not in states:
        mb.showerror("Ошибка", "Выберите хотя бы один отдел для удаления.")
        return -1
    if not mb.askyesno("Подтверждение", "Вы уверены, что хотите удалить выбранные отделы? Операцию нельзя отменить."):
        return 0

    departments_to_delete = []
    count = 0

    for i in range(departments_count):
        if chk_states[i].get():
            departments_to_delete.append(departments[i])
            departments_state[i].destroy()
            count += 1
    with open(path_to_departments, 'w', encoding='utf-8') as file:
        for line in departments:
            if line not in departments_to_delete:
                file.write(line + '\n')

    data = ["hr", departments]
    # send_data(data)

    config_departments_screen()


def new_department():
    global enter, departments_state, add, delete, departments_count, chk_states, window1
    department_to_add = enter.get()
    if department_to_add == "":
        mb.showerror(title="Ошибка", message="Введите название отдела!")
        window1.focus_force()
        return -1
    departments.append(department_to_add)
    departments_count = len(departments) - 1
    data = ["hr", departments]
    # send_data(data)

    file = open(path_to_departments, 'a', encoding='utf-8')
    file.write('\n' + department_to_add)
    file.close()

    mb.showinfo(title="Добавление отдела", message="Отдел успешно добавлен")
    get_departments()
    chk_state = BooleanVar()
    chk_states.append(chk_state)
    w = weight_calculate()
    h = height_calculate()
    window.geometry('{}x{}'.format(w, h))
    config_departments_screen()

    window1.destroy()


def add_department():
    global enter, window1
    window1 = Tk()
    window1.title("Добавление отдела")
    window1.geometry('400x150')
    x = (window.winfo_screenmmwidth() - window.winfo_reqwidth()) / 2 + 200
    y = (window.winfo_screenheight() - window.winfo_reqheight()) / 2 + 200
    window1.wm_geometry("+%d+%d" % (x, y))
    window1.focus_force()

    text = Label(window1, text="Введите название нового отдела:")
    text.place(x=25, y=20)
    enter = Entry(window1, width=50)
    enter.place(x=25, y=45)
    ok_button = Button(window1, text="Добавить", command=new_department)
    ok_button.place(x=200, y=85)
    cancel_button = Button(window1, text="Отмена", command=window1.destroy)
    cancel_button.place(x=100, y=85)


def by_company_screen():
    global graph_type, company_window
    graph_type = 0
    company_window = Tk()
    company_window.title("По всей компании")
    company_window.geometry("1000x600")
    company_window.wm_geometry("+%d+%d" % (x, y))
    graph_stat()
    save_butt = Button(company_window, text="Сохранить срез", command=save_departs_csv)
    save_butt.place(x=25, y=35)


def by_departments_screen():
    global graph_type, departments_window, combobox
    graph_type = 2
    departments_window = Tk()
    departments_window.title("По отделам")
    departments_window.geometry("1000x600")
    departments_window.wm_geometry("+%d+%d" % (x, y))
    get_departments()
    combobox = ttk.Combobox(departments_window, values=departments, height=4, width=40)
    combobox.place(x=25, y=50)
    save_butt = Button(departments_window, text="Сохранить срез", command=save_departs_csv)
    save_butt.place(x=300, y=47)
    paint_butt = Button(departments_window, text="Построить график", command=graph_stat)
    paint_butt.place(x=410, y=47)


def save_departs_csv():
    filename = filedialog.asksaveasfilename(initialdir=" ", title="Введите название среза",
                                            filetypes=(
                                                ("csv files", "*.csv"), ("csv files", "*.csv")))
    df_to_save.to_csv(filename + '.csv')


def by_individual_screen():
    global graph_type, combobox, individual_window
    graph_type = 1
    individual_window = Tk()
    individual_window.title("Индивидуально")
    individual_window.geometry("1000x600")
    individual_window.wm_geometry("+%d+%d" % (x, y))
    names = get_names()
    combobox = ttk.Combobox(individual_window, values=names, width=40)
    combobox.place(x=25, y=50)
    # combobox.bind('<<ComboboxSelected>>', lambda event: graph_stat(1, combobox.get(), individual_window))
    save_butt = Button(individual_window, text="Сохранить срез", command=save_departs_csv)
    save_butt.place(x=300, y=47)
    paint_butt = Button(individual_window, text="Построить график", command=graph_stat)
    paint_butt.place(x=410, y=47)


def download_first_departs_csv():
    global filename1
    filename1 = filedialog.askopenfilename(initialdir=" ",
                                           title="Выберите первый срез",
                                           filetypes=(("csv files", "*.csv"),
                                                      ("csv files", "*.csv")))


def download_second_departs_csv():
    global filename2
    filename2 = filedialog.askopenfilename(initialdir=" ",
                                           title="Выберите второй срез",
                                           filetypes=(("csv files", "*.csv"),
                                                      ("csv files", "*.csv")))


def comparison_bars():
    try:
        df1 = pd.read_csv(filename1)
    except NameError:
        mb.showerror("Ошибка", message='Файлы для сравнения не были выбраны.')
        return 0
    try:
        df2 = pd.read_csv(filename2)
    except NameError:
        mb.showerror("Ошибка", message='Файлы для сравнения не были выбраны.')
        return 0

    rates = ['Понимание своих задач \n и обеспеченность ресурсами', 'Нематериальное \n признание',
             'Ценность работы \n в данной команде', 'Конструктивная обратная связь \n и перспективы развития']
    colors = ['#005DFF', '#FF0000', '#00C11A', '#D4DB00']
    colors1 = ['#D4DB00', '#00C11A', '#FF0000', '#005DFF']
    fig = Figure(figsize=(16, 8))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_ylim(0, 10)
    X = np.arange(4)
    width = 0.35
    print(filename1[(filename1.rfind('/') + 1):-4], df1['discript'][0])
    print(filename2[(filename2.rfind('/') + 1):-4], df2['discript'][0])
    ax.bar(X - width / 2, df1[['st1', 'st2', 'st3', 'st4']].values.tolist()[0], width,
           label=filename1[(filename1.rfind('/') + 1):-4])  # +' ' +df1['discript'][0])
    ax.bar(X + width / 2, df2[['st1', 'st2', 'st3', 'st4']].values.tolist()[0], width,
           label=filename2[(filename2.rfind('/') + 1):-4])  # +' ' +df2['discript'][0])
    ax.set_xticks(X)
    ax.set_xticklabels(rates)
    ax.set_ylim(0, 10)
    ax.set_xlabel('Показатели')
    ax.legend()
    co_window = Tk()
    co_window.title("Cравнение")
    co_window.geometry("900x600")
    co_window.wm_geometry("+%d+%d" % (x, y))
    canvas = FigureCanvasTkAgg(fig, master=co_window)
    plt.show()
    canvas.draw()
    canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)
    toolbar = NavigationToolbar2Tk(canvas, window=co_window)
    toolbar.update()
    canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=True)


def comparison_screen():
    global cmp_window_is_open
    cmp_window_is_open = True
    comparison_window = Tk()
    comparison_window.title("Сравнение")
    comparison_window.geometry("300x300")
    comparison_window.wm_geometry("+%d+%d" % (x, y))
    window.wm_geometry("+%d+%d" % (10000, 10000))
    first_butt = Button(comparison_window, text="Выберите первый срез", command=download_first_departs_csv)
    first_butt.place(x=10, y=85)
    second_butt = Button(comparison_window, text="Выберите второй срез", command=download_second_departs_csv)
    second_butt.place(x=155, y=85)
    comparison_butt = Button(comparison_window, text="Сравнить", command=comparison_bars)
    comparison_butt.place(x=100, y=120)


def config_statistic_screen():
    global by_company, by_departments, by_individual, back, comparison

    objects = [departments_button, statistic_button, quit_button]
    for object_name in objects:
        object_name.destroy()

    by_company = Button(window, text="По всей компании", command=by_company_screen)
    by_company.place(x=125, y=50)
    by_departments = Button(window, text="По отделам", command=by_departments_screen)
    by_departments.place(x=125, y=85)
    by_individual = Button(window, text="Индивидуально", command=by_individual_screen)
    by_individual.place(x=125, y=120)
    comparison = Button(window, text="Сравнить срезы", command=comparison_screen)
    comparison.place(x=125, y=155)
    back = Button(window, text="Вернуться в меню", command=config_main_screen)
    back.place(x=125, y=190)


i_was_here = False


def config_departments_screen():
    global add, delete, back, departments_button, statistic_button, quit_button, departments_state, departments_count, \
        chk_states, i_was_here

    objects = [add, delete, back, departments_button, statistic_button, quit_button]
    for object_name in objects:
        object_name.destroy()
    for i in range(len(departments)):
        try:
            departments_state[i].destroy()
        except IndexError:
            pass

    get_departments()
    w = weight_calculate()
    h = height_calculate()
    window.geometry('{}x{}'.format(w, h))
    window.wm_geometry("+%d+%d" % (x, y))

    i = 0

    if i_was_here:
        for department in departments:
            try:
                chk = Checkbutton(window, text=department, var=chk_states[i])
                departments_state[i] = chk
                departments_state[i].place(x=10, y=10 + i * 25)
                i += 1
            except IndexError:
                chk = Checkbutton(window, text=department, var=chk_states[i])
                departments_state.append(chk)
                departments_state[i].place(x=10, y=10 + i * 25)
    else:
        i_was_here = True
        chk_states = [BooleanVar() for j in range(len(departments))]
        for department in departments:
            chk = Checkbutton(window, text=department, var=chk_states[i])
            departments_state.append(chk)
            departments_state[i].place(x=10, y=10 + i * 25)
            i += 1
    departments_count = len(departments)

    add = Button(window, text="Добавить отдел", command=add_department)
    add.place(x=w - 185, y=25)
    delete = Button(window, text="Удалить выбранные отделы", command=delete_department)
    delete.place(x=w - 185, y=50)
    back = Button(window, text="Вернуться в меню", command=config_main_screen)
    back.place(x=w - 185, y=75)


def config_main_screen():
    global statistic_button, departments_button, quit_button, add, delete, back, by_individual, by_departments, \
        by_company, comparison
    objects = [add, delete, back, by_individual, by_departments, by_company, comparison]
    for object_name in objects:
        object_name.destroy()
    for i in range(len(departments)):
        try:
            departments_state[i].place(x=10000, y=10000)
        except IndexError:
            pass

    window.wm_geometry("+%d+%d" % (x, y))
    window.geometry("400x250")
    statistic_button = Button(window, text="Просмотреть статистику", command=config_statistic_screen)
    statistic_button.place(x=125, y=50)
    departments_button = Button(window, text="Редактировать список отделов", command=config_departments_screen)
    departments_button.place(x=110, y=100)
    quit_button = Button(window, text='Выход', command=window.quit)
    quit_button.place(x=160, y=150)


add = Button(window, text="Добавить отдел")
delete = Button(window, text="Удалить выбранные отделы")
chk_states = []
departments_count = 0
cmp_window_is_open = False
graph_type = None
combobox = None
individual_window = None
company_window = None
departments_window = None

statistic_button = Button(window, text="Просмотреть статистику", command=config_statistic_screen)
statistic_button.place(x=125, y=50)
departments_button = Button(window, text="Редактировать список отделов", command=config_departments_screen)
departments_button.place(x=110, y=100)
quit_button = Button(window, text='Выход', command=window.quit)
quit_button.place(x=160, y=150)

add = Button(window, text="Добавить отдел", command=add_department)
delete = Button(window, text="Удалить выбранные отделы", command=delete_department)
back = Button(window, text="Вернуться в меню", command=config_main_screen)
departments_state = [Checkbutton(window) for i in range(len(departments))]
comparison = Button()
enter = Text(window)
by_departments = Button(window)
by_company = Button(window)
by_individual = Button(window)

window.mainloop()
