'''add/update/delete departments data'''
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox
from functools import partial
import cx_Oracle as oracle
import os

def create_connection():
    global conn,c
    conn = oracle.connect(user="payroll", password="password",dsn="localhost/xepdb1")
    c = conn.cursor()

def close_connection():
    global conn,c
    c.close()
    conn.close()

def add(edit_datatable, table, columns):
    global entry,c
    create_connection()
    sql = "INSERT INTO department(dept_name) VALUES(:a)"
    try:
         result = c.execute(sql,a=entry[1].get())
    except oracle.IntegrityError:
        messagebox.showerror(message='Department name is mandatory')
    else:
        conn.commit()
        messagebox.showinfo("Success","Successfully added department's data")
        edit_datatable.destroy()
    close_connection()
    
def update(edit_datatable,table,columns,selected_row):
    global c,entry
    create_connection()
    sql = "UPDATE department SET dept_id=:a, dept_name=:b WHERE dept_id=:a"
    try:
         result = c.execute(sql,a=selected_row_values[0],b=entry[1].get())
    except oracle.DatabaseError:
        messagebox.showerror(message='Department name is mandatory')
    else:
        conn.commit()
        messagebox.showinfo("Success","Successfully updated department's data")
        edit_datatable.destroy()
    close_connection()

def delete(edit_datatable,table,columns,selected_row):
    global entry,c
    create_connection()
    sql = "DELETE FROM department WHERE dept_id=:a"
    result = c.execute(sql,a=selected_row_values[0])
    conn.commit()
    close_connection()
    messagebox.showinfo("Success","Successfully deleted department's data")
    edit_datatable.destroy()

def edit_datatable(columns,table,command):
    global selected_row_values
    heading = tkfont.Font(family="Times New Roman", size=25,weight='bold')
    text = tkfont.Font(family="Times New Roman", size=16)
    global entry
    edit_datatable = tk.Tk()
    if(command=='add'):
        edit_datatable.title("Add Department | Employee Payroll Management System")
        tk.Label(edit_datatable,text = "ADD DEPARTMENT",font=heading).pack(side='top',anchor='center')
    else:
        edit_datatable.title("Edit Department | Employee Payroll Management System")
        tk.Label(edit_datatable,text = "EDIT DEPARTMENT",font=heading).pack(side='top',anchor='center')
    frame = tk.Frame(edit_datatable,width=10,height=3)
    frame.pack(side='top',anchor='n')
    entry = ['' for i in range(len(columns))]
    for i in range(1,len(columns)):
        tk.Label(frame,text = columns[i]+':',font=text).grid(row = i+1,column =1,padx=5,pady=5)
        entry[i] = tk.Entry(frame)
        entry[i].grid(row = i+1,column = 2,padx=5,pady=5)
    if(command=='add'):
        add_partial = partial(add, edit_datatable, table, columns)
        btn = tk.Button(edit_datatable, text='add', command=add_partial, width=7, height=2)
        btn.pack(side='top',anchor='center')
    else:
        selected_row = table.focus()
        selected_row_values = table.item(selected_row,'values')
        for i in range(1,len(columns)):
            entry[i].insert(0,selected_row_values[i])
        fr_btn = tk.Frame(edit_datatable,width=300,height=60)
        fr_btn.pack(side='top',anchor='center')
        update_partial = partial(update,edit_datatable,table,columns,selected_row)
        delete_partial = partial(delete,edit_datatable,table,columns,selected_row)
        btn_update = tk.Button(fr_btn,text='update', command=update_partial,width=7,height=2)
        btn_delete = tk.Button(fr_btn,text='delete', command=delete_partial,width=7,height=2)
        btn_update.place(x=50, y=10)
        btn_delete.place(x=155, y=10)
    edit_datatable.mainloop()



