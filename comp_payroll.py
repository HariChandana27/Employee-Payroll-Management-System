'''company's payroll'''
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
from functools import partial
import emp_payroll as ep
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

def month_changed(event):
    global month
    months_dict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
    month = month_cb.get()
    month = months_dict[month]

def year_changed(event):
    global year
    year = year_cb.get()

def refresh():
    for i in table.get_children():
        table.delete(i)
    retrieve_data()

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
            table.insert(parent='', index='end', iid=i, text="Label", values=(result_data[i][0],result_data[i][1],result_data[i][2],result_data[i][3],result_data[i][4],result_data[i][5]))

def emp_payroll(event):
    global table, month, year
    selected_row = table.focus()
    selected_row_values = table.item(selected_row,'values')
    ep.employee_payroll(selected_row_values,month,year)

def retrieve_data():
    global c,result_data,lbl_total
    create_connection()
    sql = (''' SELECT
                        emp_id,
                        name,
                        salary,
                        allowances,
                        deductions,
                        (salary +  allowances - deductions) AS net_salary
                  FROM
                        (SELECT
                               e.emp_id,
                               TRIM(TRIM(e.first_name || ' ' || e.middle_name) || ' ' || e.last_name) AS name,
                               (CASE WHEN 
                                     ROUND((e.salary_package/365)*attendance.emp_working_days,2) IS NULL
                                 THEN 
                                      0
                                 ELSE
                                       ROUND((e.salary_package/365)*attendance.emp_working_days,2)
                                END )AS salary,
                                (CASE WHEN
                                        allowances.total_allowances IS NULL
                                 THEN
                                        0
                                ELSE
                                        allowances.total_allowances
                                END) AS allowances,
                                (CASE WHEN
                                        deductions.total_deductions IS NULL
                                THEN
                                        0
                                ELSE
                                       deductions.total_deductions
                                END) AS deductions
                         FROM
                                employee e
                        LEFT JOIN
                                (SELECT
                                       *
                                  FROM
                                        attendance
                                  WHERE
                                        month_=:a
                                  AND
                                        year_=:b) attendance
                         ON 
                              e.emp_id = attendance.emp_id
                         LEFT JOIN 
                                (SELECT
                                        emp_id,
                                        SUM(amount) AS total_deductions 
                                 FROM
                                        emp_deductions
                                 WHERE
                                        month_=:a
                                 AND
                                        year_=:b
                                GROUP BY
                                        emp_id) deductions 
                          ON
                                 e.emp_id = deductions.emp_id
                        LEFT JOIN 
                               (SELECT
                                 emp_id,
                                 SUM(amount) AS total_allowances
                            FROM
                                  emp_allowances
                             WHERE
                                  month_=:a
                             AND
                                   year_=:b
                             GROUP BY
                                   emp_id) allowances
                         ON
                             e.emp_id = allowances.emp_id )
                         ORDER BY
                             emp_id''')
    result_data = c.execute(sql,a=month,b=year)
    result_data = result_data.fetchall()
    temp = []
    for i in range(len(result_data)):
        if(result_data[i][2]!=0 and result_data[i][5]!=0):
            temp.append(result_data[i])
    result_data = temp
    for i in range(len(result_data)):
        if(i%2!=0):
            table.insert(parent='', index='end', iid=i, text="Label", values=(result_data[i][0],result_data[i][1],result_data[i][2],result_data[i][3],result_data[i][4],result_data[i][5]),tag = 'odd')
        else:
            table.insert(parent='', index='end', iid=i, text="Label", values=(result_data[i][0],result_data[i][1],result_data[i][2],result_data[i][3],result_data[i][4],result_data[i][5]))
    total = 0
    for i in range(len(result_data)):
        total = total+result_data[i][5]
    if(result_data==[]):
        lbl_total.config(text = '0')
    else:
        lbl_total.config(text = round(total,2))
    close_connection()

def create_table_GUI(fr_table,text,columns,width,double_click):
    global entry_search
    entry_search = tk.Entry(fr_table,relief="groove")
    entry_search.insert(0, 'Search')
    entry_search.bind('<FocusIn>', on_focusin)
    entry_search.bind('<FocusOut>', on_focusout)
    entry_search.bind('<KeyRelease>',search)
    entry_search.config(fg = 'grey')
    entry_search.pack(anchor='ne')
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
    retrieve_data()
    table.pack(anchor='center')
    
def create_main_window():
    global month_cb,year_cb,main,lbl_total,month,year
    main = tk.Tk()
    main.title("Payroll | Employee Payroll Management System")
    heading = tkfont.Font(family="Times New Roman", size=25,weight='bold')
    text = tkfont.Font(family="Times New Roman", size=16)
    text2 = tkfont.Font(family="Times New Roman", size=18,weight='bold')
    tk.Label(main,text = "COMPANY'S PAYROLL",font=heading).pack(anchor='n')
    fr_mon_year = tk.Frame(main,width=600,height=50)
    fr_mon_year.pack(anchor='n')
    month = 0
    year = 0
    tk.Label(fr_mon_year,text = "Month:",font=text).place(x=10, y=10, relx=0.01, rely=0.01)
    selected_month = tk.StringVar()
    month_cb = ttk.Combobox(fr_mon_year, textvariable=selected_month)
    month_cb['values'] = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
    month_cb['state'] = 'readonly'
    month_cb.place(x=70, y=10, relx=0.01, rely=0.01)
    month_cb.bind('<<ComboboxSelected>>', month_changed)
    tk.Label(fr_mon_year,text = "Year:",font=text).place(x=300, y=10, relx=0.01, rely=0.01)
    selected_year = tk.StringVar()
    year_cb = ttk.Combobox(fr_mon_year, textvariable=selected_year)
    year_cb['values'] = ('2020','2021')
    year_cb['state'] = 'readonly'
    year_cb.place(x=350, y=10, relx=0.01, rely=0.01)
    year_cb.bind('<<ComboboxSelected>>',year_changed)
    columns = ('id','Employee Name','Salary per month','Allowances','Deductions','Net Salary')
    width = [50,300,250,190,190,190]
    fr_table = tk.Frame(main,width=500,height=50)
    fr_table.pack(side='top',anchor='center')
    lbl_total = tk.Label(main)
    create_table_GUI(fr_table,text,columns,width,True)
    fr_total = tk.Frame(main,width=1170,height=50)
    fr_total.pack(side='top',anchor='center')
    tk.Label(fr_total,text="TOTAL: Rs.",font=text2,fg='green').place(x=948,y=10)
    lbl_total = tk.Label(fr_total,text='0',font=text2,fg='green')
    lbl_total.place(x=1050,y=10)
    btn_refresh = tk.Button(main,text="Refresh",command=refresh,width=8,height=2) 
    btn_refresh.pack(side='top',anchor='center')
    main.mainloop()

#create_main_window()
