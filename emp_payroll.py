'''employee payroll'''
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
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

def create_table_GUI(main,text,columns,width,double_click):
    fr_table = tk.Frame(main,width=500,height=50)
    fr_table.pack(side='top',anchor='center')
    global table
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
        table.bind("<Double-1>",emp_payroll)
    else:
        pass
    table.pack(side='top',anchor=tk.CENTER)
    return table

def employee_payroll(selected_row_values,month,year):
    emp_payroll_window = tk.Tk()
    emp_payroll_window.title("Employee Payroll | Employee Payroll Management System")
    heading = tkfont.Font(family="Times New Roman", size=20,weight='bold')
    text = tkfont.Font(family="Times New Roman", size=16)
    text2= tkfont.Font(family="Times New Roman", size=16,weight='bold')
    tk.Label(emp_payroll_window,text = "EMPLOYEE'S PAYROLL",font=heading).pack(side='top',anchor='n')
    fr_emp_details = tk.Frame(emp_payroll_window,width=750,height=150)
    fr_emp_details.pack(side='top',anchor='n')
    create_connection()
    data = '''SELECT
                        e.emp_id,
                        d.dept_name,
                        p.pos_name
                   FROM
                        employee e
                   LEFT JOIN
                        department d
                   ON
                         e.dept_id = d.dept_id
                   LEFT JOIN
                         positions p
                   ON
                         e.dept_id = p.pos_id
                    WHERE
                        e.emp_id = :1'''
    data = c.execute(data, selected_row_values[0])
    data = data.fetchall()
    tk.Label(fr_emp_details,text = "ID:",font=text).place(x=0, y=10, relx=0.01, rely=0.01)
    tk.Label(fr_emp_details,text = selected_row_values[0],font=text).place(x=20, y=10, relx=0.01, rely=0.01)
    tk.Label(fr_emp_details,text = "Name:",font=text).place(x=0, y=50, relx=0.01, rely=0.01)
    tk.Label(fr_emp_details,text = selected_row_values[1],font=text).place(x=45, y=50, relx=0.01, rely=0.01)
    tk.Label(fr_emp_details,text = "Department:",font=text).place(x=410, y=10, relx=0.01, rely=0.01)
    tk.Label(fr_emp_details,text = data[0][1],font=text).place(x=490, y=10, relx=0.01, rely=0.01)
    tk.Label(fr_emp_details,text = "Position:",font=text).place(x=410, y=50, relx=0.01, rely=0.01)
    tk.Label(fr_emp_details,text = data[0][2],font=text).place(x=470, y=50, relx=0.01, rely=0.01)
    tk.Label(fr_emp_details,text = "Month:",font=text).place(x=0, y=90, relx=0.01, rely=0.01)
    tk.Label(fr_emp_details,text = month ,font=text).place(x=45, y=90, relx=0.01, rely=0.01)
    tk.Label(fr_emp_details,text = "Year:",font=text).place(x=410, y=90, relx=0.01, rely=0.01)
    tk.Label(fr_emp_details,text = year ,font=text).place(x=445, y=90, relx=0.01, rely=0.01)
    sql = '''SELECT
                      *
                 FROM
                      emp_allowances
                 WHERE
                      emp_id = :a
                 AND
                      month_ = :b
                 AND
                      year_ = :c'''
    result = c.execute(sql, a=selected_row_values[0],b=month, c=year)
    result = result.fetchall()
    if(result==[]):
        tk.Label(emp_payroll_window,text='TOTAL ALLOWANCES: Rs. 0',font=text).pack(side='top',anchor='n')
    else:
        columns = ('Allowance Name','Amount')
        width = [300,190]
        allowances_table = create_table_GUI(emp_payroll_window,text,columns,width,False)
        for i in range(len(result)):
            if(i%2!=0):
                allowances_table.insert(parent='', index='end', iid=i, text="Label", values=(result[i][4],result[i][5]),tag = 'odd')
            else:
                allowances_table.insert(parent='', index='end', iid=i, text="Label", values=(result[i][4],result[i][5]))
        sql = '''SELECT
                         SUM(amount) as total
                     FROM
                         emp_allowances
                     WHERE
                         emp_id = :a
                     AND
                         month_ = :b
                     AND
                         year_ = :c'''
        result = c.execute(sql, a=selected_row_values[0],b=month, c=year)
        result = result.fetchall()
        total_allowances = result[0][0]
        fr_total = tk.Frame(emp_payroll_window,width=500,height=30)
        fr_total.pack(side='top',anchor='n')
        tk.Label(fr_total,text='TOTAL ALLOWANCES: Rs. ',font=text2).place(x=160,y=10)
        tk.Label(fr_total,text= total_allowances,font=text2).place(x=325,y=10)   
    sql = '''SELECT
                      *
                  FROM
                      emp_deductions
                  WHERE
                      emp_id = :a
                  AND
                       month_ = :b
                  AND
                       year_ = :c '''
    result = c.execute(sql, a=selected_row_values[0], b=month, c=year)
    result = result.fetchall()
    if(result==[]):
        tk.Label(emp_payroll_window,text='TOTAL DEDUCTIONS: Rs. 0',font=text).pack(side='top',anchor='n')
    else:
        columns = ('Deduction Name','Amount')
        width = [300,190]
        deduction_table = create_table_GUI(emp_payroll_window,text,columns,width,False)
        for i in range(len(result)):
            if(i%2!=0):
                deduction_table.insert(parent='', index='end', iid=i, text="Label", values=(result[i][4],result[i][5]),tag = 'odd')
            else:
                deduction_table.insert(parent='', index='end', iid=i, text="Label", values=(result[i][4],result[i][5]))
        sql = '''SELECT
                          SUM(amount) as total
                     FROM
                          emp_deductions
                     WHERE
                          emp_id = :a
                     AND
                           month_ = :b
                      AND
                            year_ = :c'''
        result = c.execute(sql, a=selected_row_values[0],b=month, c=year)
        result = result.fetchall()
        total_allowances = result[0][0]
        fr_total = tk.Frame(emp_payroll_window,width=500,height=30)
        fr_total.pack(side='top',anchor='n')
        tk.Label(fr_total,text='TOTAL DEDUCITONS: Rs. ',font=text2).place(x=158,y=10)
        tk.Label(fr_total,text= total_allowances,font=text2).place(x=320,y=10)
    tk.Label(emp_payroll_window,text= 'NET SALARY: Rs. '+selected_row_values[5],font=text2).pack(side='top',anchor='n')
    close_connection()
    emp_payroll_window.mainloop()

