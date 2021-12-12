from tkinter import *
from converter import trace_template
import json


def convert_trace():
    trace_template["traceheader"]["metainformation"]["name"] = e1.get()
    trace_template["traceheader"]["metainformation"]["source"] = e2.get()
    trace_template["traceheader"]["metainformation"]["description"] = e3.get()
    trace_template["traceheader"]["metainformation"]["date"] = e4.get()
    trace_template["traceheader"]["metainformation"]["user"] = e5.get()
    trace_template["traceheader"]["metainformation"]["customfield"] = e6.get()
    print(trace_template)
    with open(e7.get()+'.json', 'w') as fp:
        json.dump(trace_template, fp, indent=4)


master = Tk()
Label(master, text="Original Name").grid(row=0)
Label(master, text="Source").grid(row=1)
Label(master, text="Description").grid(row=2)
Label(master, text="Date").grid(row=3)
Label(master, text="User").grid(row=4)
Label(master, text="Custom Field").grid(row=5)
Label(master, text="New File Name").grid(row=6)

e1 = Entry(master)
e2 = Entry(master)
e3 = Entry(master)
e4 = Entry(master)
e5 = Entry(master)
e6 = Entry(master)
e7 = Entry(master)

e1.grid(row=0, column=1)
e2.grid(row=1, column=1)
e3.grid(row=2, column=1)
e4.grid(row=3, column=1)
e5.grid(row=4, column=1)
e6.grid(row=5, column=1)
e7.grid(row=6, column=1)

Button(master, text='Quit', command=master.destroy).grid(row=9, column=0, sticky=W, pady=4)
Button(master, text='Show', command=convert_trace).grid(row=9, column=1, sticky=W, pady=4)

mainloop()
