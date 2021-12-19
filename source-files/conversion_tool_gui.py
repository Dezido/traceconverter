from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfile, askopenfilename

import pandas as pd

from converter import trace_template, get_tracedata
import json


class TraceConverterGUI:
    def __init__(self, master):
        self.master = master
        master.title("Traceconverting Tool")

        # Notebook and Tabs
        tab_parent = ttk.Notebook(master)

        convert_tab = ttk.Frame(tab_parent)
        filter_tab = ttk.Frame(tab_parent)
        extract_tab = ttk.Frame(tab_parent)

        tab_parent.add(convert_tab, text="Convert Trace")
        tab_parent.add(filter_tab, text="Filter Traces")
        tab_parent.add(extract_tab, text="Extract ProFiDo Format from Trace")

        tab_parent.pack(expand=1, fill='both')

        # === Converting Tab Widgets
        # Labels
        Label(convert_tab, text="Original Tracename").grid(row=0)
        Label(convert_tab, text="Columns to remove").grid(row=1)
        Label(convert_tab, text="Tracesource").grid(row=2)
        Label(convert_tab, text="Tracedescription").grid(row=3)
        Label(convert_tab, text="Tracedatadescription").grid(row=4)
        Label(convert_tab, text="Date").grid(row=5)
        Label(convert_tab, text="Username").grid(row=6)
        Label(convert_tab, text="Custom Field").grid(row=7)
        Label(convert_tab, text="Result Filename").grid(row=8)

        org_name_entry = Entry(convert_tab)
        columns_entry = Entry(convert_tab)
        source_entry = Entry(convert_tab)
        description_entry = Entry(convert_tab)
        tracedatadescription_entry = Entry(convert_tab)
        date_entry = Entry(convert_tab)
        username_entry = Entry(convert_tab)
        custom_field_entry = Entry(convert_tab)
        result_filename_entry = Entry(convert_tab)

        org_name_entry.grid(row=0, column=1)
        columns_entry.grid(row=1, column=1)
        source_entry.grid(row=2, column=1)
        description_entry.grid(row=3, column=1)
        tracedatadescription_entry.grid(row=4, column=1)
        date_entry.grid(row=5, column=1)
        username_entry.grid(row=6, column=1)
        custom_field_entry.grid(row=7, column=1)
        result_filename_entry.grid(row=8, column=1)

        def convert_trace():
            trace_template["tracebody"]["tracedata"] = get_tracedata(org_name_entry.get(), [0])
            trace_template["tracebody"]["tracedatadescription"] = tracedatadescription_entry.get()
            trace_template["traceheader"]["metainformation"]["name"] = org_name_entry.get()
            trace_template["traceheader"]["metainformation"]["source"] = source_entry.get()
            trace_template["traceheader"]["metainformation"]["description"] = description_entry.get()
            trace_template["traceheader"]["metainformation"]["date"] = date_entry.get()
            trace_template["traceheader"]["metainformation"]["user"] = username_entry.get()
            trace_template["traceheader"]["metainformation"]["customfield"] = custom_field_entry.get()
            df= pd.DataFrame(trace_template["tracebody"]["tracedata"])
            print(df.mean())
            #trace_template["traceheader"]["statistical characteristics"]["mean"] = df.mean()
            #trace_template["traceheader"]["statistical characteristics"]["median"] = df.median()
            #trace_template["traceheader"]["statistical characteristics"]["skew"] = df.skew()
            #trace_template["traceheader"]["statistical characteristics"]["kurtosis"] = df.kurtosis()
            #trace_template["traceheader"]["statistical characteristics"]["correlation"] = df.corr()

            with open(result_filename_entry.get() + '.json', 'w') as fp:
                json.dump(trace_template, fp, indent=4)

        Button(convert_tab, text='Quit', command=master.destroy).grid(row=9, column=8, sticky=W, pady=4)
        Button(convert_tab, text='Convert', command=convert_trace).grid(row=9, column=1, sticky=W, pady=4)


# Create TCGUI instance and run mainloop
root = Tk()
my_gui = TraceConverterGUI(root)
root.mainloop()
