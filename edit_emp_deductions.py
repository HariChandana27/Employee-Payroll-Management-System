'''add/update/delete emploloyee deductions' data'''
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
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
    sql = '''INSERT INTO emp_deductions(emp_id, month_, year_, deduction_name, amount)
                 VALUES(:a,:b,:c,:d,:e)'''
    try:
        result = c.execute(sql,a=emp_id,b=month,c=year,d=entry[4].get(),e=entry[5].get())
    except oracle.IntegrityError:
        messagebox.showerror(message="Every field is mandatory")
    except oracle.DatabaseError:
        messagebox.showerror(message="Enter only numeric values in 'Amount'")
    else:
        messagebox.showinfo("Success","Successfully added employee's deduction")
        edit_datatable.destroy()
    conn.commit()
    close_connection()
    
def update(edit_datatable,table,columns,selected_row):
    global c
    create_connection()
    sql = '''UPDATE emp_deductions SET
                        emp_id=:b,
                        month_=:c,
                        year_=:d,
                        deduction_name=:e,
                        amount=:f
                WHERE ref_no=:a'''
    try:
        result = c.execute(sql,a=selected_row_values[0],b=emp_id,c=month,d=year,e=entry[4].get(),f=entry[5].get())
    except oracle.DatabaseError:
        messagebox.showerror(message="Every field is mandatory. Enter only numeric values in 'Amount'")
    else:
        messagebox.showinfo("Success","Successfully updated department's deduction")
        edit_datatable.destroy()
    conn.commit()
    close_connection()

def delete(edit_datatable,table,columns,selected_row):
    global entry,c
    create_connection()
    sql = '''DELETE FROM emp_deductions
                 WHERE ref_no=:a'''
    result = c.execute(sql,a=selected_row_values[0])
    conn.commit()
    close_connection()
    messagebox.showinfo("Success","Successfully deleted department's allowance")
    edit_datatable.destroy()

def emp_changed(event):
    global emp,emp_id
    emp = emp_cb.get()
    count = 0
    for i in emp.split(' '):
        count += 1
    create_connection()
    if(count==2):
        first_name, last_name = emp.split(' ')
        sql = '''SELECT
                         emp_id
                     FROM
                         employee
                     WHERE
                          first_name=:a
                     AND
                          last_name=:b'''
        result = c.execute(sql,a=first_name, b=last_name)
    else:
        name = []
        for i in emp.split(' '):
            name.append(i)
        first_name = []
        for i in range(len(name)-1):
            first_name.append(name[i])
        first_name=' '.join(first_name)
        sql = '''SELECT
                          emp_id
                    FROM
                          employee
                    WHERE
                           first_name=:a
                    AND
                           last_name=:b'''
        result = c.execute(sql,a=first_name,b=name[-1])
    result = result.fetchall()
    emp_id = result[0][0]
    close_connection()

def month_changed(event):
    global month
    months_dict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
    month = month_cb.get()
    month = months_dict[month]

def year_changed(event):
    global year
    year = year_cb.get()

def edit_datatable(columns,table,command):
    global entry,selected_row_values,emp_cb,month_cb,year_cb,emp_id,month,year
    heading = tkfont.Font(family="Times New Roman", size=25,weight='bold')
    text = tkfont.Font(family="Times New Roman", size=16)
    edit_datatable = tk.Tk()
    edit_datatable.geometry('500x275')
    if(command=='add'):
        edit_datatable.title("Add Employee Allowances | Employee Payroll Management System")
        tk.Label(edit_datatable,text = "ADD EMPLOYEE ALLOWANCES",font=heading).pack(side='top',anchor='center')
    else:
        edit_datatable.title("Edit Employee Allowances | Employee Payroll Management System")
        tk.Label(edit_datatable,text = "EDIT EMPLOYEE ALLOWANCES",font=heading).pack(side='top',anchor='center')
    frame = tk.Frame(edit_datatable,width=10,height=3)
    frame.pack(side='top',anchor='n')
    entry = ['' for i in range(len(columns))]
    for i in range(1,len(columns)):
        tk.Label(frame,text = columns[i]+':',font=text).grid(row = i+1,column =1,padx=5,pady=5)
        if(i==1 or i==2 or i==3):
            continue
        else:
            entry[i] = tk.Entry(frame)
            entry[i].grid(row = i+1,column = 2,padx=5,pady=5)
    selected_emp = tk.StringVar()
    emp_cb = ttk.Combobox(frame, textvariable=selected_emp)
    create_connection()
    result = c.execute('''SELECT
                                           emp_id,
                                           TRIM(first_name || ' ' ||  last_name) as name
                                       FROM
                                            employee
                                       ORDER BY
                                            name''')
    result = result.fetchall()
    emp_list = []
    for i in result:
        emp_list.append(i)
    emp_cb['values'] = [emp_list[i][1] for i in range(len(emp_list))]
    close_connection()
    emp_cb['state'] = 'readonly'
    emp_cb.grid(row=2,column = 2,padx=5,pady=5)
    emp_cb.bind('<<ComboboxSelected>>', emp_changed)    
    selected_month = tk.StringVar()
    month_cb = ttk.Combobox(frame, textvariable=selected_month)
    month_cb['values'] = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
    month_cb['state'] = 'readonly'
    month_cb.grid(row=3,column = 2,padx=5,pady=5)
    month_cb.bind('<<ComboboxSelected>>', month_changed)
    selected_year = tk.StringVar()
    year_cb = ttk.Combobox(frame, textvariable=selected_year)
    year_cb['values'] = ('2020','2021')
    year_cb['state'] = 'readonly'
    year_cb.grid(row=4,column = 2,padx=5,pady=5)
    year_cb.bind('<<ComboboxSelected>>',year_changed)
    if(command=='add'):
        add_partial = partial(add, edit_datatable, table, columns)
        btn = tk.Button(edit_datatable, text='add', command=add_partial, width=7, height=2)
        btn.pack(side='top',anchor='center')
        month = 1
        year = 2021
    else:
        selected_row = table.focus()
        selected_row_values = table.item(selected_row,'values')
        ref_no = selected_row_values[0]
        for i in range(1,len(columns)):
            if(i==1 or i==2 or i==3):
                continue
            entry[i].insert(0,selected_row_values[i])
        emp_id = selected_row_values[1]
        create_connection()
        sql = '''SELECT
                         TRIM(first_name || ' ' ||  last_name) as name
                     FROM
                          employee
                     WHERE
                          emp_id=:a'''
        result = c.execute(sql,a=emp_id)
        result = result.fetchall()
        emp_cb.set(result[0][0])
        close_connection()
        month = selected_row_values[2]
        month_dict2 =  {'1':'Jan', '2':'Feb', '3':'Mar', '4':'Apr', '5':'May', '6':'Jun', '7':'Jul', '8':'Aug', '9':'Sep', '10':'Oct', '11':'Nov', '12':'Dec'}
        month_name = month_dict2[month]
        month_cb.set(month_name)
        year_list = ['2020','2021']
        year = selected_row_values[3]
        year_cb.set(year)
        fr_btn = tk.Frame(edit_datatable,width=300,height=60)
        fr_btn.pack(side='top',anchor='center')
        update_partial = partial(update,edit_datatable,table,columns,selected_row)
        delete_partial = partial(delete,edit_datatable,table,columns,selected_row)
        btn_update = tk.Button(fr_btn,text='update', command=update_partial,width=7,height=2)
        btn_delete = tk.Button(fr_btn,text='delete', command=delete_partial,width=7,height=2)
        btn_update.place(x=50, y=10)
        btn_delete.place(x=155, y=10)
    edit_datatable.mainloop()



