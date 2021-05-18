'''add/update/delete departments data'''
import tkinter as tk
from tkinter import ttk
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
    sql = '''INSERT INTO positions(pos_name,dept_id)
                 VALUES(:a,:b)'''
    try:
        result = c.execute(sql,a=entry.get(),b=dept_id)
    except oracle.IntegrityError:
        messagebox.showerror(message="'Position Name' is mandatory")
    else:
        messagebox.showinfo("Success","Successfully added positon's data")
        edit_datatable.destroy()
    conn.commit()
    close_connection()
    
def update(edit_datatable,table,columns,selected_row):
    global c
    create_connection()
    sql = '''UPDATE positions SET
                        pos_name=:b,
                        dept_id=:c
                 WHERE
                        pos_id=:a'''
    try:
        result = c.execute(sql,a=selected_row_values[0],b=entry.get(),c=dept_id)
    except oracle.DatabaseError:
        messagebox.showerror(message="'Position Name' is mandatory")
    else:
        messagebox.showinfo("Success","Successfully updated positon's data")
        edit_datatable.destroy()
    conn.commit()
    close_connection()


def delete(edit_datatable,table,columns,selected_row):
    global entry,c
    create_connection()
    sql = '''DELETE FROM positions
                 WHERE pos_id=:a'''
    result = c.execute(sql,a=selected_row_values[0])
    conn.commit()
    close_connection()
    messagebox.showinfo("Success","Successfully deleted positions's data")
    edit_datatable.destroy()

def dept_changed(event):
    global dept, dept_id
    dept = dept_cb.get()
    create_connection()
    sql = '''SELECT
                      dept_id
                 FROM
                      department
                 WHERE
                      dept_name=:a'''
    dept_id = c.execute(sql,a=dept)
    dept_id = dept_id.fetchall()
    dept_id = dept_id[0][0]
    close_connection()

def edit_datatable(columns,table,command):
    global entry, selected_row_values,dept_cb,dept_id
    heading = tkfont.Font(family="Times New Roman", size=25,weight='bold')
    text = tkfont.Font(family="Times New Roman", size=16)
    edit_datatable = tk.Tk()
    edit_datatable.geometry('450x150')
    if(command=='add'):
        edit_datatable.title("Add Position | Employee Payroll Management System")
        tk.Label(edit_datatable,text = "ADD POSITION",font=heading).pack(side='top',anchor='center')
    else:
        edit_datatable.title("Edit Position | Employee Payroll Management System")
        tk.Label(edit_datatable,text = "EDIT POSITION",font=heading).pack(side='top',anchor='center')
    frame = tk.Frame(edit_datatable,width=10,height=3)
    frame.pack(side='top',anchor='n')
    tk.Label(frame,text = columns[1]+':',font=text).grid(row = 1,column =1,padx=5,pady=5)
    tk.Label(frame,text = columns[2]+':',font=text).grid(row = 2,column =1,padx=5,pady=5)
    entry = tk.Entry(frame)
    entry.grid(row = 1, column = 2,padx=5,pady=5)
    selected_dept = tk.StringVar()
    dept_cb = ttk.Combobox(frame, textvariable=selected_dept)
    create_connection()
    result = c.execute('''SELECT
                                            *
                                       FROM
                                            department
                                       ORDER BY
                                             dept_name ASC''')
    result = result.fetchall()
    dept_list = []
    for i in result:
        dept_list.append(i)
    dept_cb['values'] = [dept_list[i][1] for i in range(len(dept_list))]
    close_connection()
    dept_cb['state'] = 'readonly'
    dept_cb.grid(row=2,column=2)
    dept_cb.set('')
    dept_cb.bind('<<ComboboxSelected>>',dept_changed)
    if(command=='add'):
        add_partial = partial(add, edit_datatable, table, columns)
        btn = tk.Button(edit_datatable, text='add', command=add_partial, width=7, height=2)
        btn.pack(side='top',anchor='center')
        dept_id = 1
    else:
        selected_row = table.focus()
        selected_row_values = table.item(selected_row,'values')
        entry.insert(0,selected_row_values[1])
        dept_id = selected_row_values[2]
        create_connection()
        sql = ''' SELECT
                           *
                      FROM
                           department
                      WHERE
                          dept_id=:a'''
        dept_name = c.execute(sql,a=dept_id)
        dept_name = dept_name.fetchall()
        dept_cb.set(dept_name[0][1])
        close_connection()
        fr_btn = tk.Frame(edit_datatable,width=300,height=60)
        fr_btn.pack(side='top',anchor='center')
        update_partial = partial(update,edit_datatable,table,columns,selected_row)
        delete_partial = partial(delete,edit_datatable,table,columns,selected_row)
        btn_update = tk.Button(fr_btn,text='update', command=update_partial,width=7,height=2)
        btn_delete = tk.Button(fr_btn,text='delete', command=delete_partial,width=7,height=2)
        btn_update.place(x=50, y=10)
        btn_delete.place(x=155, y=10)
    edit_datatable.mainloop()



