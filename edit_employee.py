'''add/update/delete employees data'''
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import tkinter.font as tkfont
from tkcalendar import *
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

def dept_changed(event):
    global dept, dept_id,pos_cb
    dept = dept_cb.get()
    create_connection()
    sql = ''' SELECT
                       dept_id
                  FROM
                       department
                  WHERE
                       dept_name=:a'''
    dept_id = c.execute(sql,a=dept)
    dept_id = dept_id.fetchall()
    dept_id = dept_id[0][0]
    sql = '''SELECT
                       *
                 FROM
                       positions
                 WHERE
                       dept_id=:a
                 ORDER BY
                       pos_name ASC '''
    result = c.execute(sql,a=dept_id)
    result = result.fetchall()
    pos_cb.set('')
    pos_list = []
    for i in result:
        pos_list.append(i)
    pos_cb['values'] = [pos_list[i][1] for i in range(len(pos_list))]
    close_connection()

def pos_changed(event):
    global pos,pos_id
    pos = pos_cb.get()
    create_connection()
    sql = '''SELECT
                     pos_id
                 FROM
                     positions
                 WHERE
                     pos_name=:a'''
    pos_id = c.execute(sql,a=pos)
    pos_id = pos_id.fetchall()
    pos_id = pos_id[0][0]
    close_connection()
    
def add(edit_datatable, table, columns):
    global c,entry,lbl_date
    create_connection()
    sql = '''INSERT INTO employee(first_name,middle_name,last_name,age,contact_no,date_of_joining,dept_id,pos_id,salary_package)
                 VALUES(:a,:b,:c,:d,:e, TO_DATE(:f,'MM/DD/YY') ,:g,:h,:i)'''
    try:
        result = c.execute(sql,a=entry[1].get(),b=entry[2].get(),c=entry[3].get(),d=entry[4].get(),e=entry[5].get(),f=cal.get_date(),g=dept_id,h=pos_id,i=entry[9].get())
    except oracle.IntegrityError:
        messagebox.showerror(message='Every field, except the middle name, is mandatory')
    except oracle.DatabaseError:
        messagebox.showerror(message='Enter only numeric values in age, contact number and salary package fields')
    else:
        messagebox.showinfo("Success","Successfully added employee's data")
        edit_datatable.destroy()
    conn.commit()
    close_connection()
    
def update(edit_datatable,table,columns,selected_row):
    global c
    create_connection()
    sql = '''UPDATE employee SET
                        first_name=:b,
                        middle_name=:c,
                        last_name=:d,
                        age=:e,
                        contact_no=:f,
                        date_of_joining= TO_DATE(:g,'MM/DD/YY'),
                        dept_id=:h,
                        pos_id=:i,
                        salary_package=:j
                 WHERE
                        emp_id=:a'''
    try:
        result = c.execute(sql,a=selected_row_values[0][0],b=entry[1].get(),c=entry[2].get(),d=entry[3].get(),e=entry[4].get(),f=entry[5].get(),g=cal.get_date(),h=dept_id,i=pos_id,j=entry[9].get()) ##
    except oracle.IntegrityError:
        messagebox.showerror(message='Every field, except the middle name, is mandatory')
    except oracle.DatabaseError:
        messagebox.showerror(message='Enter only numeric values in age and contact number fields')
    else:
        messagebox.showinfo("Success","Successfully updated employee's data")
        edit_datatable.destroy()
    conn.commit()
    close_connection()

def delete(edit_datatable,table,columns,selected_row):
    global entry,c
    create_connection()
    sql = '''DELETE FROM employee
                 WHERE emp_id=:a'''
    result = c.execute(sql,a=selected_row_values[0][0]) 
    conn.commit()
    close_connection()
    table.delete(selected_row)
    messagebox.showinfo("Success","Successfully deleted employee's data")
    edit_datatable.destroy()
    
def calendar():
    global frame,entry,cal
    cal.grid(row=11,column=2)
    lbl_date.config(text=cal.get_date())
    
def edit_datatable(columns,table,command):
    global entry,frame,cal,lbl_date,dept_cb,heading,pos_cb,dept_id,pos_id,selected_row_values
    edit_datatable = tk.Tk()
    heading = tkfont.Font(family="Times New Roman", size=25,weight='bold')
    text = tkfont.Font(family="Times New Roman", size=16)
    if(command=='add'):
        edit_datatable.title("Add Employee | Employee Payroll Management System") 
        tk.Label(edit_datatable,text = "ADD EMPLOYEE",font=heading).pack(side='top',anchor='center')
    else:
        edit_datatable.title("Edit Employee | Employee Payroll Management System")
        tk.Label(edit_datatable,text = "EDIT EMPLOYEE",font=heading).pack(side='top',anchor='center')
    frame = tk.Frame(edit_datatable,width=10,height=3)
    frame.pack(side='top',anchor='n')
    entry = ['' for i in range(len(columns))]
    for i in range(1,len(columns)):
        tk.Label(frame,text = columns[i]+':',font=text).grid(row = i+1,column =1,padx=5,pady=5)
        if(i==6 or i==7 or i==8):
            continue
        entry[i] = tk.Entry(frame)
        entry[i].grid(row = i+1,column = 2,pady=5)
    lbl_date = tk.Label(frame,text='')
    lbl_date.grid(row=7,column=2)
    btn_cal = tk.Button(frame,text='Calendar',command=calendar,width=7,height=2)
    btn_cal.grid(row=7,column=3)
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
    dept_cb.grid(row=8,column=2)
    dept_cb.set('')
    dept_cb.bind('<<ComboboxSelected>>',dept_changed)
    selected_pos = tk.StringVar()
    pos_cb = ttk.Combobox(frame, textvariable=selected_pos)
    pos_cb['state'] = 'readonly'
    pos_cb.grid(row=9,column=2)
    pos_cb.set('')
    pos_cb.bind('<<ComboboxSelected>>',pos_changed)
    if(command=='add'):
        add_partial = partial(add, edit_datatable, table, columns)
        btn = tk.Button(edit_datatable, text='add', command=add_partial, width=7, height=2)
        btn.pack(side='top',anchor='center')
        dept_id = 1
        pos_id = 1
        cal = Calendar(frame,selectmode="day")
    else:
        selected_row = table.focus()
        selected_row_values = table.item(selected_row,'values')
        selected_emp_id = selected_row_values[0]
        create_connection()
        sql = ''' SELECT
                           emp_id,
                           first_name,
                           middle_name,
                           last_name,
                           age,
                           contact_no,
                           TRIM(TRIM(extract(month from date_of_joining) || '/' || extract(day from date_of_joining)) || '/' || extract(year from date_of_joining)) AS date_of_joining,
                           dept_id,
                           pos_id,
                           salary_package
                     FROM
                           employee 
                     WHERE
                           emp_id=:a
                     ORDER BY
                           emp_id '''
        selected_row_values = c.execute(sql,a=selected_emp_id)
        selected_row_values = selected_row_values.fetchall()
        month_, day_ , year_ = selected_row_values[0][6].split('/')
        month_, day_ , year_ = int(month_), int(day_), int(year_)
        cal = Calendar(frame,selectmode="day", year = year_ , month = month_, day=day_)
        for i in range(1,len(columns)):
            if(i==6 or i==7 or i==8):
                continue
            if(selected_row_values[0][i]):
                entry[i].insert(0,selected_row_values[0][i]) 
        lbl_date.config(text=selected_row_values[0][6])
        dept_id = selected_row_values[0][7]
        sql = '''SELECT
                         *
                     FROM
                         department
                     WHERE
                         dept_id=:a'''
        dept_name = c.execute(sql,a=dept_id)
        dept_name = dept_name.fetchall()
        dept_cb.set(dept_name[0][1])
        pos_id = selected_row_values[0][8]
        sql = '''SELECT
                         *
                     FROM
                         positions
                     WHERE
                         pos_id=:a '''
        pos_name = c.execute(sql,a=pos_id)
        pos_name = pos_name.fetchall()
        pos_cb.set(pos_name[0][1])
        fr_btn = tk.Frame(edit_datatable,width=300,height=60)
        fr_btn.pack(side='top',anchor='center')
        update_partial = partial(update,edit_datatable,table,columns,selected_row)
        delete_partial = partial(delete,edit_datatable,table,columns,selected_row)
        btn_update = tk.Button(fr_btn,text='update', command=update_partial,width=7,height=2)
        btn_delete = tk.Button(fr_btn,text='delete', command=delete_partial,width=7,height=2)
        btn_update.place(x=50, y=10)
        btn_delete.place(x=150, y=10)
    edit_datatable.mainloop()



