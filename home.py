import tkinter as tk
import tkinter.font as tkfont
from functools import partial
import employee
import department
import position
import attendance
import emp_allowances
import emp_deducitons
import comp_payroll

def open_link(name): 
    if(name=='Employee'):
        employee.create_main_window()
    elif(name=='Department'):
        department.create_main_window()
    elif(name=='Position'):
        position.create_main_window()
    elif(name=='Attendance'):
        attendance.create_main_window()
    elif(name=='Employee Allowances'):
        emp_allowances.create_main_window()
    elif(name=='Emplyee Deducitons'):
        emp_deducitons.create_main_window()
    else:
        comp_payroll.create_main_window() 

def create_home():
    home = tk.Tk()
    home.title("Home | Employee Payroll Management System")
    home.geometry('450x500')
    heading = tkfont.Font(family="Times New Roman", size=25,weight='bold')
    text = tkfont.Font(family="Times New Roman", size=16)
    frame = tk.Frame(home,width=100,height=70)
    frame.place(relx=0.5, rely=0.5, anchor='center')
    tk.Label(frame,text = "HOME",font=heading).grid(row=1,column=1,padx=5,pady=5)
    links = ['Employee','Department','Position','Attendance','Employee Allowances','Emplyee Deducitons',"Company's Payroll"]
    for i in range(7):
        open_link_partial = partial(open_link,links[i])
        tk.Button(frame,text = links[i],command=open_link_partial,font=text,width=25,height=2,padx=3,pady=3).grid(row = i+2,column =1,padx=5,pady=5)
    home.mainloop()
