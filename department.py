'''department's data'''
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
import edit_department as ed
import cx_Oracle as oracle
import os

#oracle.init_oracle_client(lib_dir=os.environ.get("HOME")+"/Downloads/instantclient_19_8")

def create_connection():
    global conn,c
    conn = oracle.connect(user="payroll", password="password",dsn="localhost/xepdb1")
    c = conn.cursor()

def close_connection():
    global conn,c
    c.close()
    conn.close()

def retrieve_data():
    global table,c,result_data
    create_connection()
    sql = ('''SELECT
                       *
                  FROM
                       department
                 ORDER BY
                       dept_id''')
    result_data = c.execute(sql)
    result_data = result_data.fetchall()
    for i in range(len(result_data)):
        if(i%2!=0):
            table.insert(parent='', index='end', iid=i, text="Label", values=(result_data[i][0],result_data[i][1]),tag = 'odd')
        else:
            table.insert(parent='', index='end', iid=i, text="Label", values=(result_data[i][0],result_data[i][1]))

def add():
    ed.edit_datatable(columns,table,'add')

def refresh():
    for i in table.get_children():
        table.delete(i)
    retrieve_data()

def select_data(event):
    global table
    ed.edit_datatable(columns,table,'edit')

def on_focusin(event):
    global entry_search
    if entry_search.get() == 'Search':
       entry_search.delete(0, "end") 
       entry_search.insert(0, '') 
       entry_search.config(fg = 'black')

def on_focusout(event):
    global entry_search
    if entry_search.get() == '':
        entry_search.insert(0, 'Search')
        entry_search.config(fg = 'grey')

def search(event): 
    search_word = entry_search.get()
    if search_word=='':
        for record in table.get_children():
            table.delete(record)
        retrieve_data()
    else:
        dept_names = []
        for i in range(len(result_data)):
            if(search_word.lower() in result_data[i][1].lower()):
                dept_names.append(i)
        for record in table.get_children():
            table.delete(record)
        for i in dept_names:
            table.insert(parent='', index='end', iid=i, text="Label", values=(result_data[i][0],result_data[i][1]))

def create_table_GUI(main,text,columns,width,double_click):
    global entry_search, table
    fr_table = tk.Frame(main,width=500,height=50)
    fr_table.pack(side='top',anchor='center')
    entry_search = tk.Entry(fr_table,relief="groove")
    entry_search.insert(0, 'Search')
    entry_search.bind('<FocusIn>', on_focusin)
    entry_search.bind('<FocusOut>', on_focusout)
    entry_search.bind('<KeyRelease>',search)
    entry_search.config(fg = 'grey')
    entry_search.pack(anchor='ne')
    table = ttk.Treeview(fr_table)
    table['columns'] = columns
    for i in columns:
        table.heading(i,text=i,anchor='center')
    table.column("#0",width=0,stretch='no')
    for i in range(0,len(columns)):
        table.column(columns[i],anchor='center',width=width[i])
    style = ttk.Style()
    style.configure("Treeview",rowheight=35, font=('Times New Roman', 18))
    style.configure("Treeview.Heading",font=('Times New Roman', 18,'bold'))
    table.tag_configure('odd', background='#DFDFDF')
    if(double_click):
        table.bind("<Double-1>",select_data)
    else:
        pass
    retrieve_data()
    table.pack(anchor='center')

def create_main_window():
    global month_cb ,columns
    main = tk.Tk()
    main.title("Departments | Employee Payroll Management System")
    heading = tkfont.Font(family="Times New Roman", size=25,weight='bold')
    text = tkfont.Font(family="Times New Roman", size=16)
    tk.Label(main,text = "LIST OF DEPARTMENTS",font=heading).pack(anchor='n')
    columns = ('id','Department Name')
    width = [50,300]
    create_table_GUI(main,text,columns,width,True)
    fr_btn = tk.Frame(main,width=300,height=60)
    fr_btn.pack(side='top',anchor='n')
    btn_refresh = tk.Button(fr_btn,text='refresh', command=refresh, width=7,height=2)
    btn_add = tk.Button(fr_btn, text='add', command=add, width=7, height=2)
    btn_refresh.place(x=50, y=10)
    btn_add.place(x=150, y=10)
    main.mainloop()

#create_main_window()