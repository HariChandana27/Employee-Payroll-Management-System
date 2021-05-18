import tkinter as tk
import tkinter.messagebox
import tkinter.font as tkfont
import cx_Oracle as oracle
import os
import home

oracle.init_oracle_client(lib_dir=os.environ.get("HOME")+"/Downloads/instantclient_19_8")
conn = oracle.connect(user="payroll", password="password",dsn="localhost/xepdb1")
c = conn.cursor()

window = tk.Tk()
window.title('Login | Employee Payroll Management System')
window.geometry('450x200')
heading = tkfont.Font(family="Times New Roman", size=25,weight='bold')
text = tkfont.Font(family="Times New Roman", size=16)
tk.Label(window,text = 'LOGIN FORM',font=heading).place(x=180,y=10)
tk.Label(window ,text='Username:',height = 3,font=text).place(x=100,y=48)
tk.Label(window,text='Password:',height = 3,font=text).place(x=100,y=88)
var_usr_name = tk.StringVar()
entry_usr_name = tk.Entry(window,textvariable=var_usr_name)
entry_usr_name.place(x=180,y=60)
var_usr_pwd = tk.StringVar()
entry_usr_pwd = tk.Entry(window,textvariable = var_usr_pwd,show='*')
entry_usr_pwd.place(x=180,y=100)

def quit_():
    window.destroy()
    c.close()
    conn.close()
    
def usr_log_in():
    usr_name = var_usr_name.get()
    usr_pwd = var_usr_pwd.get()
    result = c.execute('''SELECT
                                           *
                                       FROM
                                           users_payroll''')
    result = result.fetchall()
    users = []
    for i in result:
        users.append(i[1])
    if usr_name in users:
        sql = '''SELECT
                          *
                     FROM
                          users_payroll
                     WHERE
                          user_name=:a '''
        result = c.execute(sql,a=usr_name)
        result = result.fetchall()
        for row in result:
            password = row[2]
        if(password==usr_pwd):
            usr_name = usr_name.capitalize()
            tk.messagebox.showinfo(title='Welcome',message='Welcome '+ usr_name)
            quit_()
            home.create_home()
        elif usr_pwd=='':
            tk.messagebox.showerror(message='Enter Password')
        else:
            tk.messagebox.showerror(message='Wrong password')
    elif usr_name == '':
        tk.messagebox.showerror(message='Enter Username')
    else:
        tk.messagebox.showerror(message='Wrong username')

bt_log_in = tk.Button(window,text='Login',height = 2,width = 4,font=text,command=usr_log_in).place(x=140,y=150)
bt_quit = tk.Button(window,text='Quit',height = 2,width = 4,font=text,command=quit_).place(x=280,y=150)
window.mainloop()
