import configparser
import datetime
import json
import logging
import os
import tkinter.filedialog as fd
from tkinter import *
from tkinter import ttk

import pandas
import pandas as pd

from converter import trace_template, get_tracedata_from_file, get_all_traces_from

# Load config
config = configparser.RawConfigParser()
config.read('config.properties')

# Logging
logging.basicConfig(format=config.get('logging', 'logging_format'), level=logging.INFO)


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
        Label(convert_tab, text="Field", font=config.get('fonts', 'default_font_bold')).grid(row=0)
        Label(convert_tab, text="Trace").grid(row=1)
        Label(convert_tab, text="Columns to keep").grid(row=2)
        Label(convert_tab, text="Tracesource").grid(row=3)
        Label(convert_tab, text="Tracedescription").grid(row=4)
        Label(convert_tab, text="Tracedatadescription").grid(row=5)
        # Label(convert_tab, text="Date").grid(row=6)
        Label(convert_tab, text="Username").grid(row=7)
        Label(convert_tab, text="Additional Information").grid(row=8)
        Label(convert_tab, text="Result Filename").grid(row=9)

        Label(convert_tab, text="Input", font=config.get('fonts', 'default_font_bold')).grid(row=0, column=1)

        # Hints
        # Label(convert_tab, text="Hints", font=config.get('fonts', 'default_font_bold')).grid(row=0, column=3)
        # Label(convert_tab, text="Choose the trace you want to convert").grid(row=1, column=3)
        # Label(convert_tab, text="Which columns of the original trace contain the relevant tracedata."
        #                       " Delimiter: , ").grid(row=2, column=3)
        # Label(convert_tab, text="From which source (repository/archive) does the trace originate").grid(row=3, column=3)
        # Label(convert_tab, text="Description of the whole trace").grid(row=4, column=3)
        # Label(convert_tab, text="Description of the tracedata. Delimiter: ||").grid(row=5, column=3)
        # Label(convert_tab, text="Date of the conversion").grid(row=6, column=3)
        # Label(convert_tab, text="Who is using the tool").grid(row=7, column=3)
        # Label(convert_tab, text="Additional information about the trace (optional)").grid(row=8, column=3)
        # Label(convert_tab, text="Filename for the converted trace").grid(row=9, column=3)

        org_name_entry = Entry(convert_tab, width=config.get('entries', 'entry_width'))

        def browse_file():
            # Clears entry before new filepath is chosen
            org_name_entry.delete(0, END)
            sel_file = fd.askopenfilename(initialdir=config.get('directories', 'raw_traces_dir'),
                                          title="Select a File",
                                          filetypes=(("CSV files", "*.csv*"),))

            org_name_entry.insert(END, sel_file)
            org_name_entry.grid(row=1, column=1)
            org_name_button.grid(row=1, column=2)

        # Entries
        org_name_button = Button(convert_tab, text="Browse Files", command=browse_file)

        columns_entry = Entry(convert_tab, width=config.get('entries', 'entry_width'))
        # noinspection PyTypeChecker
        columns_entry.insert(END, ['0'])
        source_entry = Entry(convert_tab, width=config.get('entries', 'entry_width'))
        source_entry.insert(END, config.get('default_entries', 'default_source_entry'))
        description_entry = Entry(convert_tab, width=config.get('entries', 'entry_width'))
        description_entry.insert(END,
                                 config.get('default_entries', 'default_description_entry'))
        tracedatadescription_entry = Entry(convert_tab, width=config.get('entries', 'entry_width'))
        tracedatadescription_entry.insert(END, config.get('default_entries', 'default_tracedatadescription_entry'))
        # date_entry = Entry(convert_tab, width=config.get('entries', 'entry_width'))
        # date_entry.insert(END, "27.12.2021")
        username_entry = Entry(convert_tab, width=config.get('entries', 'entry_width'))
        username_entry.insert(END, config.get('default_entries', 'default_username_entry'))
        custom_field_entry = Text(convert_tab, width=config.get('entries', 'entry_width'), height=25,
                                  font=config.get('fonts', 'default_font'))
        custom_field_entry.insert(END,
                                  config.get('default_entries', 'default_customfield_entry'))
        result_filename_entry = Entry(convert_tab, width=config.get('entries', 'entry_width'))
        result_filename_entry.insert(END, config.get('default_entries', 'default_filename_entry'))

        # Place Entries
        org_name_button.grid(row=1, column=1)

        columns_entry.grid(row=2, column=1)
        source_entry.grid(row=3, column=1)
        description_entry.grid(row=4, column=1)
        tracedatadescription_entry.grid(row=5, column=1)
        # date_entry.grid(row=6, column=1)
        username_entry.grid(row=7, column=1)
        custom_field_entry.grid(row=8, column=1)
        result_filename_entry.grid(row=9, column=1)

        trace_view_ct = Text(convert_tab, width=100, height=33)
        trace_view_label_ct = Label(convert_tab, text="Converted Trace:")

        # Generates converted Trace from User Input
        def convert_trace():
            col = list(map(int, (columns_entry.get().split(","))))
            trace_template["tracebody"]["tracedata"] = get_tracedata_from_file(org_name_entry.get(), col)
            trace_template["tracebody"]["tracedatadescription"] = tracedatadescription_entry.get().split("||")
            trace_template["traceheader"]["metainformation"]["name"] = os.path.basename(org_name_entry.get())
            trace_template["traceheader"]["metainformation"]["source"] = source_entry.get()
            trace_template["traceheader"]["metainformation"]["description"] = description_entry.get()
            trace_template["traceheader"]["metainformation"]["date"] = str(datetime.datetime.now())
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
            try:
                with open('converted_traces/' + result_filename_entry.get() + '_converted.json', 'w') as fp:
                    json.dump(trace_template, fp, indent=4)
            except BaseException as e:
                print("Error while converting trace: " + str(e))
                Label(profido_format_tab, bg="red", text="An error occurred. Are all inputs valid?").grid(column=0,
                                                                                                          row=4)

            # Clear statistic lists so the next trace won't have old values
            trace_template["traceheader"]["statistical characteristics"]["mean"].clear()
            trace_template["traceheader"]["statistical characteristics"]["median"].clear()
            trace_template["traceheader"]["statistical characteristics"]["skew"].clear()
            trace_template["traceheader"]["statistical characteristics"]["kurtosis"].clear()
            trace_template["traceheader"]["statistical characteristics"]["autocorrelation"].clear()

            with open('converted_traces/' + result_filename_entry.get() + '_converted.json', 'r') as f:
                trace_view_ct.config(state=NORMAL)
                trace_view_ct.delete("1.0", "end")
                trace_view_ct.insert(INSERT, f.read())
                trace_view_ct.config(state=DISABLED)
                trace_view_ct.grid(column=4, row=1, columnspan=12, rowspan=10)
                trace_view_label_ct.grid(column=4, row=0)

            print(custom_field_entry.winfo_height())
            print(org_name_entry.winfo_height())

        exit_button_ct = Button(convert_tab, text='Exit', command=master.destroy)
        exit_button_ct.grid(row=12, column=8, sticky=W, pady=4)
        convert_button_ct = Button(convert_tab, text='Convert', command=convert_trace)
        convert_button_ct.grid(row=12, column=1, sticky=W, pady=4)

        # === Filter Tab Widgets
        selected_traces_label = Label(filter_tab, text="Selected traces")
        selected_traces_label.grid(column=1, row=1)

        trace_lb = Listbox(filter_tab, width=50)
        result_lb = Listbox(filter_tab, width=50)

        sel_names_ft = []
        sel_files_ft = []
        sel_filtered_ft = []

        def browse_files():
            file_tuple = fd.askopenfilenames(initialdir=config.get('directories', 'converted_traces_dir'),
                                             title="Select a File",
                                             filetypes=(("JSON files", "*.json*"),))
            trace_lb.delete(0, 'end')
            sel_files_ft.clear()
            sel_names_ft.clear()
            for i in file_tuple:
                with open(str(i)) as json_file:
                    sel_files_ft.append(json.load(json_file))
                    sel_names_ft.append(os.path.basename(i))
            for i in range(len(sel_names_ft)):
                trace_lb.insert(i, sel_names_ft[i])
            trace_lb.grid(column=1, row=2)
            browse_button_ft.grid(column=1, row=3)

        def filter_traces():
            sel_filtered_ft.clear()
            statistic = statistics_combobox.get()
            operator = operator_combobox.get()
            value = float(value_entry.get())
            comp = comp_ops[operator]
            for i in range(len(sel_files_ft)):
                trace_stat = sel_files_ft[i]["traceheader"]["statistical characteristics"][statistic]
                for j in range(len(trace_stat)):
                    if comp(trace_stat[j], value):
                        sel_filtered_ft.append(os.path.basename(sel_names_ft[i]))
            result_lb.delete(0, 'end')
            sel_filtered_ft_unique = list(set(sel_filtered_ft))
            for i in range(len(sel_filtered_ft_unique)):
                result_lb.insert(i, sel_filtered_ft_unique[i])
            Label(filter_tab, text="Results").grid(column=1, row=4)
            result_lb.grid(column=1, row=5)

        statistic_options = [
            "mean",
            "median",
            "skew",
            "kurtosis",
            "autocorrelation"
        ]

        operator_options = [
            "equal: ==",
            "not equal: !=",
            "less than: <",
            "less than or equal to: <=",
            "greater than: >",
            "greater than or equal to: >="
        ]

        comp_ops = {
            "equal: ==": lambda x, y: x == y,
            "not equal: !=": lambda x, y: x != y,
            "less than: <": lambda x, y: x < y,
            "less than or equal to: <=": lambda x, y: x <= y,
            "greater than: >": lambda x, y: x > y,
            "greater than or equal to: >=": lambda x, y: x >= y
        }

        statistics_label = Label(filter_tab, text="Statistical characteristic")
        statistics_label.grid(column=2, row=1)
        statistics_combobox = ttk.Combobox(filter_tab, state="readonly", values=statistic_options)
        statistics_combobox.grid(column=2, row=2)
        statistics_combobox.current(0)

        operator_label = Label(filter_tab, text="comparison operator")
        operator_label.grid(column=3, row=1)
        operator_combobox = ttk.Combobox(filter_tab, state="readonly", values=operator_options, width=30)
        operator_combobox.grid(column=3, row=2)
        operator_combobox.current(0)

        value_label = Label(filter_tab, text="Comparison value")
        value_label.grid(column=4, row=1)
        value_entry = Entry(filter_tab, width=25)
        value_entry.grid(column=4, row=2)

        # Label and Buttons
        filter_button = Button(filter_tab, text="Filter Traces", command=filter_traces)
        filter_button.grid(column=5, row=2)

        browse_button_ft = Button(filter_tab, text="Browse Files", command=browse_files)
        browse_button_ft.grid(column=1, row=2)

        exit_button_ft = Button(filter_tab, text="Exit", command=master.destroy)
        exit_button_ft.grid(column=2, row=3)

        # ===ProFiDo format Tab
        Label(profido_format_tab, text="Trace").grid(row=0)
        Label(profido_format_tab, text="Result filename").grid(row=1)
        choose_trace_entry_profido = Entry(profido_format_tab, width=config.get('entries', 'entry_width'))

        trace_col_pt = Text(profido_format_tab, width=45, height=20)
        profido_format_label_pt = Label(profido_format_tab, text="Extracted data")

        def browse_trace():
            choose_trace_entry_profido.delete(0, END)
            selected_trace_profido = fd.askopenfilename(initialdir=config.get('directories', 'converted_traces_dir'),
                                                        title="Select a File",
                                                        filetypes=(("JSON files", "*.json*"),))
            choose_trace_entry_profido.insert(END, selected_trace_profido)
            choose_trace_entry_profido.grid(row=0, column=1)
            choose_trace_button_pt.grid(row=0, column=2)

        error_label = Label(profido_format_tab, bg="red", text="An error occurred. Are all inputs valid?")

        def extract_columns():
            error_label.destroy()
            try:
                with open(choose_trace_entry_profido.get()) as trace_in:
                    tracedata = json.load(trace_in)["tracebody"]["tracedata"]
                    df = pandas.DataFrame(tracedata)
                    df.transpose().to_csv(result_filename_entry_pt.get() + '_dat.trace', sep='\t',
                                          float_format="%e",
                                          index=False, header=False)
            except BaseException as e:
                print("Error while extracting columns: " + str(e))
                error_label.grid(column=0, row=4)
            with open(result_filename_entry_pt.get() + '_dat.trace', 'r') as f:
                trace_col_pt.config(state=NORMAL)
                trace_col_pt.delete("1.0", "end")
                trace_col_pt.insert(INSERT, f.read())
                trace_col_pt.config(state=DISABLED)
                trace_col_pt.grid(column=0, row=6)
                profido_format_label_pt.grid(column=0, row=5)

        choose_trace_button_pt = Button(profido_format_tab, text="Browse Trace", command=browse_trace)
        choose_trace_button_pt.grid(row=0, column=1)

        result_filename_entry_pt = Entry(profido_format_tab, width=config.get('entries', 'entry_width'))
        result_filename_entry_pt.grid(row=1, column=1)

        extract_columns_button_pt = Button(profido_format_tab, text="Extract ProFiDo format from trace",
                                           command=extract_columns)
        extract_columns_button_pt.grid(row=3, column=1)

        exit_button_pt = Button(profido_format_tab, text='Exit', command=master.destroy)
        exit_button_pt.grid(row=3, column=2, sticky=W, pady=4)


# Create TCGUI instance and run mainloop
root = Tk()
my_gui = TraceConverterGUI(root)
root.mainloop()
