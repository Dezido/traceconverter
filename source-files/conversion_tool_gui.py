import json
from tkinter import *
from tkinter import ttk

import pandas as pd

from converter import trace_template, get_tracedata_from_file


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

        # Entries
        org_name_entry = Entry(convert_tab)
        # Prefill Entry
        org_name_entry.insert(END, "tst.csv")
        columns_entry = Entry(convert_tab)
        columns_entry.insert(END, ['3'])
        source_entry = Entry(convert_tab)
        description_entry = Entry(convert_tab)
        tracedatadescription_entry = Entry(convert_tab)
        date_entry = Entry(convert_tab)
        username_entry = Entry(convert_tab)
        custom_field_entry = Entry(convert_tab)
        result_filename_entry = Entry(convert_tab)

        # Place Entries
        org_name_entry.grid(row=0, column=1)
        columns_entry.grid(row=1, column=1)
        source_entry.grid(row=2, column=1)
        description_entry.grid(row=3, column=1)
        tracedatadescription_entry.grid(row=4, column=1)
        date_entry.grid(row=5, column=1)
        username_entry.grid(row=6, column=1)
        custom_field_entry.grid(row=7, column=1)
        result_filename_entry.grid(row=8, column=1)

        # Generates converted Trace from User Input
        def convert_trace():
            trace_template["tracebody"]["tracedata"] = [get_tracedata_from_file(org_name_entry.get(),
                                                                                int(columns_entry.get()))]
            trace_template["tracebody"]["tracedatadescription"] = tracedatadescription_entry.get()
            trace_template["traceheader"]["metainformation"]["name"] = org_name_entry.get()
            trace_template["traceheader"]["metainformation"]["source"] = source_entry.get()
            trace_template["traceheader"]["metainformation"]["description"] = description_entry.get()
            trace_template["traceheader"]["metainformation"]["date"] = date_entry.get()
            trace_template["traceheader"]["metainformation"]["user"] = username_entry.get()
            trace_template["traceheader"]["metainformation"]["customfield"] = custom_field_entry.get()

            # Generates statistics and adds them into a list. Each list entry represents one column of the raw trace
            for i in range(len(trace_template["tracebody"]["tracedata"][0])):
                df = pd.DataFrame(trace_template["tracebody"]["tracedata"][0][i])
                trace_template["traceheader"]["statistical characteristics"]["mean"].append(df[0].mean())
                trace_template["traceheader"]["statistical characteristics"]["median"].append(df[0].median())
                trace_template["traceheader"]["statistical characteristics"]["skew"].append(df[0].skew())
                trace_template["traceheader"]["statistical characteristics"]["kurtosis"].append(df[0].kurtosis())
                trace_template["traceheader"]["statistical characteristics"]["autocorrelation"].append(df[0].autocorr())

            # Saves trace to file
            with open('converted_traces/' + result_filename_entry.get() + '_converted.json', 'w') as fp:
                json.dump(trace_template, fp, indent=4)

            # Clear statistic lists so the next trace won't have old values
            trace_template["traceheader"]["statistical characteristics"]["mean"].clear()
            trace_template["traceheader"]["statistical characteristics"]["median"].clear()
            trace_template["traceheader"]["statistical characteristics"]["skew"].clear()
            trace_template["traceheader"]["statistical characteristics"]["kurtosis"].clear()
            trace_template["traceheader"]["statistical characteristics"]["autocorrelation"].clear()

        Button(convert_tab, text='Quit', command=master.destroy).grid(row=9, column=8, sticky=W, pady=4)
        Button(convert_tab, text='Convert', command=convert_trace).grid(row=9, column=1, sticky=W, pady=4)


# Create TCGUI instance and run mainloop
root = Tk()
my_gui = TraceConverterGUI(root)
root.mainloop()
