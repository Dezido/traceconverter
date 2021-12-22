import csv
import json
from tkinter import *
from tkinter import ttk
import tkinter.filedialog as fd

import pandas
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
        profido_format_tab = ttk.Frame(tab_parent)

        tab_parent.add(convert_tab, text="Convert Trace")
        tab_parent.add(filter_tab, text="Filter Traces")
        tab_parent.add(profido_format_tab, text="ProFiDo Format from Trace")

        tab_parent.pack(expand=1, fill='both')

        # === Converting Tab Widgets
        # Labels
        Label(convert_tab, text="Trace").grid(row=0)
        Label(convert_tab, text="Columns to remove").grid(row=1)
        Label(convert_tab, text="Tracesource").grid(row=2)
        Label(convert_tab, text="Tracedescription").grid(row=3)
        Label(convert_tab, text="Tracedatadescription").grid(row=4)
        Label(convert_tab, text="Date").grid(row=5)
        Label(convert_tab, text="Username").grid(row=6)
        Label(convert_tab, text="Custom Field").grid(row=7)
        Label(convert_tab, text="Result Filename").grid(row=8)

        org_name_entry = Entry(convert_tab, width=53)

        def browse_file():
            # Clears entry before new filepath is chosen
            org_name_entry.delete(0, END)
            sel_file = fd.askopenfilename(initialdir=
                                          "C:/Users/Dennis/PycharmProjects/"
                                          "traceconverter/source-files/raw_traces",
                                          title="Select a File",
                                          filetypes=(("CSV files", "*.csv*"),))

            org_name_entry.insert(END, sel_file)
            org_name_entry.grid(row=0, column=1)

        # Entries
        org_name_button = Button(convert_tab, text="Browse Files", command=browse_file)

        columns_entry = Entry(convert_tab, width=53)
        columns_entry.insert(END, ['0'])
        source_entry = Entry(convert_tab, width=53)
        source_entry.insert(END, "UMass Tracerepository")
        description_entry = Entry(convert_tab, width=53)
        description_entry.insert(END,
                                 "Result of a simple timing attack on the OneSwarm peer-to-peer data sharing network")
        tracedatadescription_entry = Entry(convert_tab, width=53)
        tracedatadescription_entry.insert(END, "Shows the delay during the resulting from the timing-attack")
        date_entry = Entry(convert_tab, width=53)
        date_entry.insert(END, "21.12.2021")
        username_entry = Entry(convert_tab, width=53)
        username_entry.insert(END, "Dennis Ziebart")
        custom_field_entry = Text(convert_tab, width=40, height=20)
        custom_field_entry.insert(END,
                                  "Additional information about the Trace: This trace serves as an example for the converter")
        result_filename_entry = Entry(convert_tab, width=53)
        result_filename_entry.insert(END, "oneswarm-timing-attack-trace")

        # Place Entries
        org_name_button.grid(row=0, column=2)

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
            trace_template["tracebody"]["tracedata"] = get_tracedata_from_file(org_name_entry.get(),
                                                                               int(columns_entry.get()))
            trace_template["tracebody"]["tracedatadescription"] = tracedatadescription_entry.get()
            trace_template["traceheader"]["metainformation"]["name"] = org_name_entry.get()
            trace_template["traceheader"]["metainformation"]["source"] = source_entry.get()
            trace_template["traceheader"]["metainformation"]["description"] = description_entry.get()
            trace_template["traceheader"]["metainformation"]["date"] = date_entry.get()
            trace_template["traceheader"]["metainformation"]["user"] = username_entry.get()
            trace_template["traceheader"]["metainformation"]["customfield"] = custom_field_entry.get('1.0', 'end-1c')

            # Generates statistics and adds them into a list. Each list entry represents one column of the raw trace
            # df = pd.DataFrame(trace_template["tracebody"]["tracedata"][0])
            for i in range(len(trace_template["tracebody"]["tracedata"])):
                df = pd.DataFrame(trace_template["tracebody"]["tracedata"][i])
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

        Button(convert_tab, text='Exit', command=master.destroy).grid(row=9, column=8, sticky=W, pady=4)
        Button(convert_tab, text='Convert', command=convert_trace).grid(row=9, column=1, sticky=W, pady=4)

        # === Filter Tab Widgets
        selected_traces = []

        def browse_files():
            file_tuple = fd.askopenfilenames(initialdir=
                                             "C:/Users/Dennis/PycharmProjects/"
                                             "traceconverter/source-files/converted_traces",
                                             title="Select a File",
                                             filetypes=(("JSON files", "*.json*"),))
            trace_list = []
            for i in file_tuple:
                with open(str(i)) as json_file:
                    trace_list.append(json.load(json_file))
            selected_traces.clear()
            selected_traces.append(trace_list)
            print(selected_traces)

        # Label and Buttons
        label_file_explorer = Label(filter_tab, text="File Explorer using Tkinter", width=100, height=4, fg="blue")
        label_file_explorer.grid(column=1, row=1)

        button_explore = Button(filter_tab, text="Browse Files", command=browse_files)
        button_explore.grid(column=1, row=2)

        button_exit = Button(filter_tab, text="Exit", command=master.destroy)
        button_exit.grid(column=1, row=3)

        # ===ProFiDo format Tab

        Label(profido_format_tab, text="Trace").grid(row=0)
        Label(profido_format_tab, text="Result filename").grid(row=1)
        choose_trace_entry_profido = Entry(profido_format_tab, width=53)

        def browse_trace():
            choose_trace_entry_profido.delete(0, END)
            selected_trace_profido = fd.askopenfilename(initialdir=
                                                        "C:/Users/Dennis/PycharmProjects/"
                                                        "traceconverter/source-files/converted_traces",
                                                        title="Select a File",
                                                        filetypes=(("JSON files", "*.json*"),))
            choose_trace_entry_profido.insert(END, selected_trace_profido)
            choose_trace_entry_profido.grid(row=0, column=1)
            print(selected_trace_profido)

        def extract_columns():
            with open(choose_trace_entry_profido.get()) as trace_in:
                tracedata = json.load(trace_in)["tracebody"]["tracedata"]
                df = pandas.DataFrame(tracedata)
                df.transpose().to_csv(result_filename_entry_profido.get() + '_dat.trace', float_format="%e",
                                      index=False, header=False)

        choose_trace_button_profido = Button(profido_format_tab, text="Browse Trace",
                                             command=browse_trace)
        choose_trace_button_profido.grid(row=0, column=2)

        result_filename_entry_profido = Entry(profido_format_tab, width=53)
        result_filename_entry_profido.grid(row=1, column=1)

        extract_columns_button_profido = Button(profido_format_tab, text="Extract ProFiDo format from trace",
                                                command=extract_columns)
        extract_columns_button_profido.grid(row=1, column=2)


# Create TCGUI instance and run mainloop
root = Tk()
my_gui = TraceConverterGUI(root)
root.mainloop()
