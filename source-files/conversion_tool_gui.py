import json
import tkinter.filedialog as fd
import os
from tkinter import *
from tkinter import ttk

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
        Label(convert_tab, text="Field", font='TkDefaultFont 10 bold').grid(row=0)
        Label(convert_tab, text="Trace").grid(row=1)
        Label(convert_tab, text="Columns to remove").grid(row=2)
        Label(convert_tab, text="Tracesource").grid(row=3)
        Label(convert_tab, text="Tracedescription").grid(row=4)
        Label(convert_tab, text="Tracedatadescription").grid(row=5)
        Label(convert_tab, text="Date").grid(row=6)
        Label(convert_tab, text="Username").grid(row=7)
        Label(convert_tab, text="Additional Information").grid(row=8)
        Label(convert_tab, text="Result Filename").grid(row=9)

        Label(convert_tab, text="Input", font='TkDefaultFont 10 bold').grid(row=0, column=1)

        # Hints
        Label(convert_tab, text="Hints", font='TkDefaultFont 10 bold').grid(row=0, column=3)
        Label(convert_tab, text="Choose the trace you want to convert").grid(row=1, column=3)
        Label(convert_tab, text="Which columns of the original trace that shall be ignored for the conversion."
                                " Delimit multiple numbers with a ',' ").grid(row=2, column=3)
        Label(convert_tab, text="From which source (repository/archive) does the trace originate").grid(row=3, column=3)
        Label(convert_tab, text="Description of the whole trace").grid(row=4, column=3)
        Label(convert_tab, text="Description of the tracedata. If the tracedata consists of multiple columns use '||' "
                                "between describing different columns.  ").grid(row=5, column=3)
        Label(convert_tab, text="Date of the conversion").grid(row=6, column=3)
        Label(convert_tab, text="Who is using the tool").grid(row=7, column=3)
        Label(convert_tab, text="Additional information about the trace (optional)").grid(row=8, column=3)
        Label(convert_tab, text="Filename for the converted trace").grid(row=9, column=3)

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
            org_name_entry.grid(row=1, column=1)

        # Entries
        org_name_button = Button(convert_tab, text="Browse Files", command=browse_file)

        columns_entry = Entry(convert_tab, width=53)
        columns_entry.insert(END, ['0'])
        source_entry = Entry(convert_tab, width=53)
        source_entry.insert(END, "Example Tracerepository")
        description_entry = Entry(convert_tab, width=53)
        description_entry.insert(END,
                                 "Exampledescription")
        tracedatadescription_entry = Entry(convert_tab, width=53)
        tracedatadescription_entry.insert(END, "Exampledatadescription")
        date_entry = Entry(convert_tab, width=53)
        date_entry.insert(END, "27.12.2021")
        username_entry = Entry(convert_tab, width=53)
        username_entry.insert(END, "Dennis Ziebart")
        custom_field_entry = Text(convert_tab, width=40, height=20)
        custom_field_entry.insert(END,
                                  "Additional information about the Trace: "
                                  "Exampleinformation")
        result_filename_entry = Entry(convert_tab, width=53)
        result_filename_entry.insert(END, "exampleresult")

        # Place Entries
        org_name_button.grid(row=1, column=2)

        columns_entry.grid(row=2, column=1)
        source_entry.grid(row=3, column=1)
        description_entry.grid(row=4, column=1)
        tracedatadescription_entry.grid(row=5, column=1)
        date_entry.grid(row=6, column=1)
        username_entry.grid(row=7, column=1)
        custom_field_entry.grid(row=8, column=1)
        result_filename_entry.grid(row=9, column=1)

        # Generates converted Trace from User Input
        def convert_trace():
            col = list(map(int, (columns_entry.get().split(","))))
            trace_template["tracebody"]["tracedata"] = get_tracedata_from_file(org_name_entry.get(), col)
            trace_template["tracebody"]["tracedatadescription"] = tracedatadescription_entry.get().split("||")
            trace_template["traceheader"]["metainformation"]["name"] = org_name_entry.get()
            trace_template["traceheader"]["metainformation"]["source"] = source_entry.get()
            trace_template["traceheader"]["metainformation"]["description"] = description_entry.get()
            trace_template["traceheader"]["metainformation"]["date"] = date_entry.get()
            trace_template["traceheader"]["metainformation"]["user"] = username_entry.get()
            if len(custom_field_entry.get('1.0', 'end-1c')) != 0:
                trace_template["traceheader"]["metainformation"]["additional information"] = custom_field_entry. \
                    get('1.0', 'end-1c')
            else:
                trace_template["traceheader"]["metainformation"].pop("additional information")

            # Generates statistics and adds them into a list. Each list entry represents one column of the raw trace
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

        Button(convert_tab, text='Exit', command=master.destroy).grid(row=10, column=8, sticky=W, pady=4)
        Button(convert_tab, text='Convert', command=convert_trace).grid(row=10, column=1, sticky=W, pady=4)

        # === Filter Tab Widgets
        selected_traces = []

        def browse_files():
            file_tuple = fd.askopenfilenames(initialdir=
                                             "C:/Users/Dennis/PycharmProjects/"
                                             "traceconverter/source-files/converted_traces",
                                             title="Select a File",
                                             filetypes=(("JSON files", "*.json*"),))
            trace_list = []
            tracename_list = []
            for i in file_tuple:
                with open(str(i)) as json_file:
                    trace_list.append(json.load(json_file))
                    tracename_list.append(os.path.basename(i))
            selected_traces.clear()
            selected_traces.append(trace_list)
            label_selected_tracenames = Label(filter_tab, text="Selected files: " + str(tracename_list), width=100,
                                              height=4)
            label_selected_tracenames.grid(column=1, row=2)
            # print(selected_traces)

        # Label and Buttons
        label_file_explorer = Label(filter_tab, text="Selected files: " + str(selected_traces), width=100, height=4)
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

        def extract_columns():
            with open(choose_trace_entry_profido.get()) as trace_in:
                tracedata = json.load(trace_in)["tracebody"]["tracedata"]
                df = pandas.DataFrame(tracedata)
                df.transpose().to_csv(result_filename_entry_profido.get() + '_dat.trace', sep='\t', float_format="%e",
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
