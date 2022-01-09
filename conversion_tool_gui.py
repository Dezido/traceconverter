import configparser
import datetime
import json
import logging
import os
import tkinter
import tkinter.filedialog as fd
from idlelib.tooltip import Hovertip
from tkinter import *
from tkinter import scrolledtext
from tkinter import ttk
import tkinter.messagebox as mb

import pandas as pd

import converter as c
from converter import trace_template, get_tracedata_from_file, remove_lines_from_csv, hash_from_trace

# Load config file
config = configparser.RawConfigParser()
config.read('config.properties')

# Logging configuration
logging.basicConfig(format=config.get('logging', 'logging_format'), level=logging.INFO)


class TraceConverterGUI:
    def __init__(self, master):
        """
        Creates a GUI for the traceconverter
        :param master:
        """
        self.master = master
        master.title("Traceconverting Tool")
        # Notebook and Tabs
        tab_parent = ttk.Notebook(master)

        preparation_tab = ttk.Frame(tab_parent)
        convert_tab = ttk.Frame(tab_parent)
        filter_tab = ttk.Frame(tab_parent)
        profido_format_tab = ttk.Frame(tab_parent)
        validation_tab = ttk.Frame(tab_parent)

        # Add tabs to master
        tab_parent.add(preparation_tab, text="Prepare File")
        tab_parent.add(convert_tab, text="Convert Trace")
        tab_parent.add(filter_tab, text="Filter Traces")
        tab_parent.add(profido_format_tab, text="ProFiDo Format from Trace")
        tab_parent.add(validation_tab, text="Validate Trace")
        tab_parent.pack(expand=1, fill='both')

        # Preparation Tab

        def browse_file_prt():
            """
            Opens a file explorer to select a file
            """
            file_entry_prt.delete(0, END)  # removes previously selected file
            selected_file = fd.askopenfilename(initialdir=config.get('directories', 'raw_traces_dir'),
                                               title="Select a File",
                                               filetypes=(("CSV files", "*.csv*"), ("all files",
                                                                                    "*.*")))
            file_entry_prt.insert(END, selected_file)
            file_entry_prt.grid(row=0, column=1)
            file_button_prt.grid(row=0, column=0)
            print(selected_file + " was chosen in preparation tab")
            display_file_prt(file_entry_prt.get())
            first_line_is_header_checkbutton_prt.grid(row=0, column=2)

        first_line_is_header_checkbutton_var_prt = tkinter.IntVar()
        first_line_is_header_checkbutton_prt = Checkbutton(preparation_tab, text="First line is header",
                                                           variable=first_line_is_header_checkbutton_var_prt,
                                                           onvalue=1, offvalue=0)

        file_entry_prt = Entry(preparation_tab, width=config.get('entries', 'entry_width'))

        file_button_prt = Button(preparation_tab, text="Choose File", command=browse_file_prt)
        file_button_prt.grid(column=1, row=0)

        remove_rows_label_prt = Label(preparation_tab, text="Number of rows to remove")
        remove_rows_label_prt.grid(column=0, row=2)

        remove_rows_entry_prt = Entry(preparation_tab, width=config.get('entries', 'entry_width'))
        remove_rows_entry_prt.grid(column=1, row=2)

        remove_rows_button_prt = Button(preparation_tab, text="Remove Rows",
                                        command=lambda: [remove_lines_from_csv(file_entry_prt.get(),
                                                                               int(remove_rows_entry_prt.get())),
                                                         display_file_prt(file_entry_prt.get())])
        remove_rows_button_prt.grid(column=2, row=2)

        add_header_label_prt = Label(preparation_tab, text="Add header to file")
        add_header_label_prt.grid(column=0, row=3)

        add_header_entry_prt = Entry(preparation_tab, width=config.get('entries', 'entry_width'))
        add_header_entry_prt.grid(column=1, row=3)

        add_header_button_prt = Button(preparation_tab, text="Add Header",
                                       command=lambda: [c.add_header_to_csv(file_entry_prt.get(),
                                                                            list(
                                                                                add_header_entry_prt.get().split(","))),
                                                        display_file_prt(file_entry_prt.get())])
        add_header_button_prt.grid(column=2, row=3)

        file_displayer_label_prt = Label(preparation_tab)
        file_displayer_label_prt.grid(column=0, row=5)
        file_displayer_prt = scrolledtext.ScrolledText(preparation_tab, width=200, height=33)

        delimiter_label_prt = Label(preparation_tab, text="Delimiter")
        delimiter_label_prt.grid(column=0, row=4)
        delimiter_entry_prt = Entry(preparation_tab, width=config.get('entries', 'entry_width'))
        delimiter_entry_prt.grid(column=1, row=4)
        transform_filetype_button_prt = Button(preparation_tab,
                                               text="Change Filetype",
                                               command=lambda:
                                               transform_file_prt(file_entry_prt.get(),
                                                                  delimiter_entry_prt.get(),
                                                                  first_line_is_header_checkbutton_var_prt.get()))
        transform_filetype_button_prt.grid(column=2, row=4)

        def display_file_prt(filename):
            """
            Displays the selected file in the preparation tab
            :param filename: File that will be displayed
            """
            with open(filename, 'r') as f:
                file_displayer_label_prt.configure(text=os.path.basename(filename))
                file_displayer_prt.grid(column=0, row=5, columnspan=12, rowspan=10)
                file_displayer_prt.config(state=NORMAL)
                file_displayer_prt.delete("1.0", "end")
                file_displayer_prt.insert(INSERT, f.read())
                file_displayer_prt.config(state=DISABLED)
                print(filename + " displayed in preparation tab")

        def transform_file_prt(filename, delimiter, header):
            if delimiter == "tabbed":
                delimiter = '\t'
            if delimiter == "space":
                delimiter = ' '
            if delimiter == "comma":
                delimiter = ','
            df = pd.read_csv(filename, sep=delimiter)
            result_filename = \
                config.get('directories', 'raw_traces_dir') + '/' + os.path.basename(filename).split('.')[0] + '.csv'
            dont_overwrite = 0
            if os.path.exists(filename):
                dont_overwrite = not mb.askyesno("File already exists",
                                                 os.path.basename(filename) + " already exists. \n "
                                                                              "Would you like to overwrite it?")
            if not dont_overwrite:
                df.to_csv(result_filename, index=False, sep=',', header=header)
                display_file_prt(result_filename)
                print(filename + " was transformed into csv file")

        # Tooltips
        file_button_tooltip_prt = Hovertip(file_button_prt, config.get('tooltips', 'file_button'))
        remove_rows_tooltip_prt = Hovertip(remove_rows_label_prt, config.get('tooltips', 'remove_rows'))
        remove_rows_button_tooltip_prt = Hovertip(remove_rows_button_prt, config.get('tooltips', 'remove_rows_button'))
        add_header_tooltip_prt = Hovertip(add_header_label_prt, config.get('tooltips', 'add_header'))
        add_header_button_tooltip_prt = Hovertip(add_header_button_prt, config.get('tooltips', 'add_header_button'))
        delimiter_tooltip_prt = Hovertip(delimiter_label_prt, config.get('tooltips', 'delimiter'))
        transform_button_tooltip_prt = Hovertip(transform_filetype_button_prt,
                                                config.get('tooltips', 'transform_button'))

        # Converting Tab
        columns_label_ct = Label(convert_tab, text="Columns to keep")
        columns_label_ct.grid(row=2)
        source_label_ct = Label(convert_tab, text="Tracesource")
        source_label_ct.grid(row=3)
        tracedescription_label_ct = Label(convert_tab, text="Tracedescription")
        tracedescription_label_ct.grid(row=4)
        tracedatadescription_label_ct = Label(convert_tab, text="Tracedatadescription")
        tracedatadescription_label_ct.grid(row=5)
        username_label_ct = Label(convert_tab, text="Username")
        username_label_ct.grid(row=6)
        custom_field_label_ct = Label(convert_tab, text="Additional Information")
        custom_field_label_ct.grid(row=7)
        result_filename_label_ct = Label(convert_tab, text="Result Filename")
        result_filename_label_ct.grid(row=8)

        profido_filename_label_ct = Label(convert_tab, text="ProFiDo filename:")
        profido_filename_entry_ct = Entry(convert_tab)

        def show_name_entry():
            """
            Puts the profido_filename_label on the grid if the checkbox is selected
            """
            if extract_profido_checkbutton_var_ct.get() == 0:
                profido_filename_label_ct.grid_forget()
                profido_filename_entry_ct.grid_forget()
                print("Extract columns for PoFiDo option was unselected in the convert tab")
            if extract_profido_checkbutton_var_ct.get() == 1:
                profido_filename_label_ct.grid(column=4, row=4)
                profido_filename_entry_ct.grid(column=4, row=5)
                print("Extract columns for PoFiDo option was selected in the convert tab")

        extract_profido_checkbutton_var_ct = tkinter.IntVar()
        extract_profido_checkbutton_ct = Checkbutton(convert_tab, text="extract ProFiDo format after conversion",
                                                     variable=extract_profido_checkbutton_var_ct, onvalue=1,
                                                     offvalue=0, command=show_name_entry)
        extract_profido_checkbutton_ct.grid(column=4, row=3)

        scientific_format_checkbutton_var_ct = tkinter.IntVar()
        scientific_format_checkbutton_ct = Checkbutton(convert_tab, text="statistics in scientific notation",
                                                       variable=scientific_format_checkbutton_var_ct, onvalue=1,
                                                       offvalue=0)
        # scientific_format_checkbutton_ct.grid(column=4, row=2)

        statistic_format_label_ct = Label(convert_tab, text="Statistic Format")
        statistic_format_label_ct.grid(row=12, column=0)

        statistic_format_entry_ct = Entry(convert_tab, width=config.get('entries', 'entry_width'))
        statistic_format_entry_ct.grid(row=12, column=1)

        original_tracefile_entry_ct = Entry(convert_tab, width=config.get('entries', 'entry_width'))

        def browse_file_ct():
            """
            Opens a file explorer to select a raw trace
            """
            original_tracefile_entry_ct.delete(0, END)  # removes previously selected file
            selected_file = fd.askopenfilename(initialdir=config.get('directories', 'raw_traces_dir'),
                                               title="Select a File",
                                               filetypes=(("CSV files", "*.csv*"),))
            original_tracefile_entry_ct.insert(END, selected_file)
            original_tracefile_entry_ct.grid(row=1, column=1)
            print(selected_file + " was chosen in convert tab")
            display_file_ct(selected_file)

        # Create entries and set default values
        original_tracefile_button_ct = Button(convert_tab, text="Choose File", command=browse_file_ct)

        columns_entry_ct = Entry(convert_tab, width=config.get('entries', 'entry_width'))
        columns_entry_ct.insert(END, ['0'])

        source_entry_ct = Entry(convert_tab, width=config.get('entries', 'entry_width'))
        source_entry_ct.insert(END, config.get('default_entries', 'default_source_entry'))

        description_entry_ct = Entry(convert_tab, width=config.get('entries', 'entry_width'))
        description_entry_ct.insert(END, config.get('default_entries', 'default_description_entry'))

        tracedatadescription_entry_ct = Entry(convert_tab, width=config.get('entries', 'entry_width'))
        tracedatadescription_entry_ct.insert(END, config.get('default_entries', 'default_tracedatadescription_entry'))

        username_entry_ct = Entry(convert_tab, width=config.get('entries', 'entry_width'))
        username_entry_ct.insert(END, config.get('default_entries', 'default_username_entry'))

        custom_field_entry_ct = Text(convert_tab, width=config.get('entries', 'entry_width'), height=25,
                                     font=config.get('fonts', 'default_font'))
        custom_field_entry_ct.insert(END, config.get('default_entries', 'default_customfield_entry'))

        result_filename_entry_ct = Entry(convert_tab, width=config.get('entries', 'entry_width'))
        result_filename_entry_ct.insert(END, config.get('default_entries', 'default_filename_entry'))

        # Place Entries
        original_tracefile_button_ct.grid(row=1, column=0)
        columns_entry_ct.grid(row=2, column=1)
        source_entry_ct.grid(row=3, column=1)
        description_entry_ct.grid(row=4, column=1)
        tracedatadescription_entry_ct.grid(row=5, column=1)
        username_entry_ct.grid(row=6, column=1)
        custom_field_entry_ct.grid(row=7, column=1)
        result_filename_entry_ct.grid(row=8, column=1)

        # Text widget to display the converted trace
        file_displayer_ct = scrolledtext.ScrolledText(convert_tab, width=100, height=33)

        def convert_trace():
            """
            Takes the user input from the entry fields and converts the selected trace to the predefined standard format
            """
            col = list(map(int, (columns_entry_ct.get().split(","))))
            trace_template["tracebody"]["tracedata"] = get_tracedata_from_file(original_tracefile_entry_ct.get(), col)
            amount_tracedata = len(trace_template["tracebody"]["tracedata"][0])
            trace_template["tracebody"]["tracedatadescription"] = tracedatadescription_entry_ct.get().split("||")
            trace_template["traceheader"]["metainformation"]["name"] = os.path.basename(
                original_tracefile_entry_ct.get())
            trace_template["traceheader"]["metainformation"]["source"] = source_entry_ct.get()
            trace_template["traceheader"]["metainformation"]["description"] = description_entry_ct.get()
            trace_template["traceheader"]["metainformation"]["date"] = str(datetime.datetime.now())
            trace_template["traceheader"]["metainformation"]["user"] = username_entry_ct.get()
            if len(custom_field_entry_ct.get('1.0', 'end-1c')) != 0:
                trace_template["traceheader"]["metainformation"]["additional information"] = custom_field_entry_ct. \
                    get('1.0', 'end-1c')
            else:
                trace_template["traceheader"]["metainformation"].pop("additional information")

            #  Generate statistics and adds them into a list. Each list entry represents one column of the raw trace
            if amount_tracedata > 4:
                trace = generate_statistic(trace_template, statistic_format_entry_ct.get())
            else:
                trace = trace_template
                mb.showinfo("Statistics won't be computed", "Tracedata only contains " +
                            str(amount_tracedata) + " elements per column. Computing statistics requires five or more.")
            # Save trace to file
            filename = 'converted_traces/' + result_filename_entry_ct.get() + '_converted.json'
            dont_overwrite = 0
            if os.path.exists(filename):
                dont_overwrite = not mb.askyesno("File already exists",
                                                 os.path.basename(filename) + " already exists. \n "
                                                                              "Would you like to overwrite it?")
            if not dont_overwrite:
                with open(filename, 'w') as fp:
                    json.dump(trace, fp, indent=4)
                    print("Trace was converted successfully!")
                    # If profido checkbox is selected the columns will also be extracted for profido use
                add_hash_to_trace(filename)
                if extract_profido_checkbutton_var_ct.get() == 1:
                    extract_after_conversion(
                        filename)
                mb.showinfo("Trace converted successfully", "Displaying converted Trace")
            else:
                mb.showinfo("File already exists", "Displaying existing File")
            # Display the created traces
            display_file_ct(filename)

        def generate_statistic(trace, formatstring):
            # Clear statistic lists so the next trace won't have old values
            trace["traceheader"]["statistical characteristics"]["mean"].clear()
            trace["traceheader"]["statistical characteristics"]["median"].clear()
            trace["traceheader"]["statistical characteristics"]["skew"].clear()
            trace["traceheader"]["statistical characteristics"]["kurtosis"].clear()
            trace["traceheader"]["statistical characteristics"]["autocorrelation"].clear()
            formatstring = "{" + formatstring + "}"
            try:
                for i in range(len(trace["tracebody"]["tracedata"])):
                    df = pd.DataFrame(trace["tracebody"]["tracedata"][i])
                    trace["traceheader"]["statistical characteristics"]["mean"].append(
                        formatstring.format(df[0].mean()))
                    trace["traceheader"]["statistical characteristics"]["median"].append(
                        formatstring.format(df[0].median()))
                    trace["traceheader"]["statistical characteristics"]["skew"].append(
                        formatstring.format(df[0].skew()))
                    trace["traceheader"]["statistical characteristics"]["kurtosis"].append(
                        formatstring.format(df[0].kurtosis()))
                    trace["traceheader"]["statistical characteristics"]["autocorrelation"].append(
                        formatstring.format(df[0].autocorr()))
                return trace
            except (KeyError, IndexError):
                mb.showerror("Format Error", "Invalid Statistic Format entered")
                raise

        def add_hash_to_trace(filename):
            with open(filename) as tr:
                tracedata = json.load(tr)
                tracedata["traceheader"]["metainformation"]["hash"] = hash_from_trace(filename)
            with open(filename, 'w') as fp:
                json.dump(tracedata, fp, indent=4)

        def display_file_ct(filename):
            """
            Displays the selected file in the preparation tab
            :param filename: File that will be displayed
            """
            with open(filename, 'r') as f:
                file_displayer_ct.config(state=NORMAL)
                file_displayer_ct.delete("1.0", "end")
                file_displayer_ct.insert(INSERT, f.read())
                file_displayer_ct.config(state=DISABLED)
                file_displayer_ct.grid(column=5, row=1, columnspan=12, rowspan=10)
                print(filename + " displayed in preparation tab")

        def extract_after_conversion(filename):
            """
            Extracts columns for ProFiDo usage from the input trace
            :param filename: Name of the converted tracefile
            """
            with open(filename) as tr:
                tracedata = json.load(tr)["tracebody"]["tracedata"]
                df = pd.DataFrame(tracedata)
                dont_overwrite = 0
                result_filename = config.get('directories', 'profido_traces_dir') + \
                                  profido_filename_entry_ct.get() + '_dat.trace'
                if os.path.exists(result_filename):
                    dont_overwrite = not mb.askyesno("File already exists",
                                                     os.path.basename(result_filename) +
                                                     " already exists. "
                                                     "\n Would you like to overwrite it?")
                if not dont_overwrite:
                    df.transpose().to_csv(result_filename,
                                          sep='\t',
                                          float_format="%e",
                                          index=False, header=False)
                    print("Columns were extracted after conversion")

        convert_button_ct = Button(convert_tab, text='Convert Trace', command=convert_trace)
        convert_button_ct.grid(row=13, column=1)

        # Tooltips
        columns_tooltip_ct = Hovertip(columns_label_ct, config.get('tooltips', 'columns'))
        source_tooltip_ct = Hovertip(source_label_ct, config.get('tooltips', 'source'))
        description_tooltip_ct = Hovertip(tracedescription_label_ct, config.get('tooltips', 'tracedescription'))
        tracedatadescription_tooltip_ct = Hovertip(tracedatadescription_label_ct,
                                                   config.get('tooltips', 'tracedatadescription'))
        username_tooltip_ct = Hovertip(username_label_ct, config.get('tooltips', 'username'))
        custom_field_tooltip_ct = Hovertip(custom_field_label_ct, config.get('tooltips', 'custom_field'))
        result_filename_tooltip_ct = Hovertip(result_filename_label_ct,
                                              config.get('tooltips', 'result_filename'))
        profido_checkbutton_tooltip_ct = Hovertip(extract_profido_checkbutton_ct,
                                                  config.get('tooltips', 'profido_checkbutton'))
        profido_filename_tooltip_ct = Hovertip(profido_filename_label_ct,
                                               config.get('tooltips', 'profido_filename_ct'))
        browse_file_button_tooltip_ct = Hovertip(original_tracefile_button_ct,
                                                 config.get('tooltips', 'browse_file_button'))
        convert_button_tooltip_ct = Hovertip(convert_button_ct,
                                             config.get('tooltips', 'browse_file_button'))
        statistic_format_tooltip_ct = Hovertip(statistic_format_label_ct,
                                               config.get('tooltips', 'statistic_format'))

        # Filter Tab
        selected_traces_label_ft = Label(filter_tab, text="Selected traces")
        selected_traces_label_ft.grid(column=1, row=1)

        selected_traces_lb = Listbox(filter_tab, width=config.get('listbox', 'listbox_width'),
                                     height=config.get('listbox', 'listbox_height'))
        filter_result_lb = Listbox(filter_tab, width=config.get('listbox', 'listbox_width'),
                                   height=config.get('listbox', 'listbox_height'))

        selected_filenames = []
        selected_files = []
        filter_result = []

        def browse_files_ft():
            """
            Select converted traces for filtering
            """
            file_tuple = fd.askopenfilenames(initialdir=config.get('directories', 'converted_traces_dir'),
                                             title="Select a File",
                                             filetypes=(("JSON files", "*.json*"),))
            selected_traces_lb.delete(0, 'end')
            selected_files.clear()
            selected_filenames.clear()
            for i in file_tuple:
                with open(str(i)) as json_file:
                    selected_files.append(json.load(json_file))
                    selected_filenames.append(os.path.basename(i))
            for i in range(len(selected_filenames)):
                selected_traces_lb.insert(i, selected_filenames[i])
            selected_traces_lb.grid(column=1, row=2, rowspan=5)
            browse_button_ft.grid(column=1, row=8)
            print("Traces for filtering were selected")

        def filter_traces():
            """
            Filters selected traces by the specified condition (via combo boxes)
            """
            filter_result.clear()
            statistic = statistics_combobox_ft.get()
            comparison_operator_cb = comparison_operator_combobox_ft.get()
            comparison_operator = comparison_operator_functions[comparison_operator_cb]
            if compare_to_own_statistic_checkbutton_var_ft.get() == 0:  # Compare trace statistic to value
                comparison_value = float(comparison_value_entry_ft.get())
                for i in range(len(selected_files)):
                    trace_statistic = selected_files[i]["traceheader"]["statistical characteristics"][statistic]
                    for j in range(len(trace_statistic)):
                        if comparison_operator(trace_statistic[j], comparison_value):
                            filter_result.append(os.path.basename(selected_filenames[i]))
                print("Filtered traces that satisfy: " + statistic + " " + str(comparison_operator_cb) + " " +
                      str(comparison_value))
            if compare_to_own_statistic_checkbutton_var_ft.get() == 1:  # Compare to other statistic in same column
                operand = float(operand_entry_ft.get())
                comparison_statistic = compare_to_own_statistic_combobox_ft.get()
                arithmetic_operator = arithmetic_operation_combobox_ft.get()
                base_operator = basic_arithmetic_operator_functions[arithmetic_operator]
                for i in range(len(selected_files)):
                    trace_statistic = selected_files[i]["traceheader"]["statistical characteristics"][statistic]
                    comparison_statistic_value = \
                        selected_files[i]["traceheader"]["statistical characteristics"][comparison_statistic]
                    for j in range(len(trace_statistic)):
                        comparison_value = base_operator(comparison_statistic_value[j], operand)
                        if comparison_operator(trace_statistic[j], comparison_value):
                            filter_result.append(os.path.basename(selected_filenames[i]))
                print("Filtered traces that satisfy: " + statistic + " " + str(comparison_operator_cb) + " " +
                      str(comparison_value))

            filter_result_lb.delete(0, 'end')
            unique_filter_result = list(set(filter_result))
            for i in range(len(unique_filter_result)):
                filter_result_lb.insert(i, unique_filter_result[i])
            Label(filter_tab, text="Results").grid(column=1, row=10)
            filter_result_lb.grid(column=1, row=11)

        statistical_characteristics_options = [
            "mean",
            "median",
            "skew",
            "kurtosis",
            "autocorrelation"
        ]

        comparison_operator_options = [
            "equal: ==",
            "not equal: !=",
            "less than: <",
            "less than or equal to: <=",
            "greater than: >",
            "greater than or equal to: >="
        ]

        basic_arithmetic_operator_options = [
            "plus: +",
            "minus: -",
            "multiplied by: *",
            "divided by: /"
        ]

        comparison_operator_functions = {
            "equal: ==": lambda x, y: x == y,
            "not equal: !=": lambda x, y: x != y,
            "less than: <": lambda x, y: x < y,
            "less than or equal to: <=": lambda x, y: x <= y,
            "greater than: >": lambda x, y: x > y,
            "greater than or equal to: >=": lambda x, y: x >= y
        }

        basic_arithmetic_operator_functions = {
            "plus: +": lambda x, y: x + y,
            "minus: -": lambda x, y: x - y,
            "multiplied by: *": lambda x, y: x * y,
            "divided by: /": lambda x, y: x / y
        }

        statistics_label_ft = Label(filter_tab, text="Statistical characteristic")
        statistics_label_ft.grid(column=2, row=1)
        statistics_combobox_ft = ttk.Combobox(filter_tab, state="readonly", values=statistical_characteristics_options)
        statistics_combobox_ft.grid(column=2, row=2)
        statistics_combobox_ft.current(0)

        comparison_operator_label_ft = Label(filter_tab, text="Comparison operator")
        comparison_operator_label_ft.grid(column=3, row=1)
        comparison_operator_combobox_ft = ttk.Combobox(filter_tab, state="readonly", values=comparison_operator_options,
                                                       width=30)
        comparison_operator_combobox_ft.grid(column=3, row=2)
        comparison_operator_combobox_ft.current(0)

        arithmetic_operation_label_ft = Label(filter_tab, text="Operation")
        arithmetic_operation_combobox_ft = ttk.Combobox(filter_tab, state="readonly",
                                                        values=basic_arithmetic_operator_options)
        arithmetic_operation_combobox_ft.current(0)

        compare_to_own_statistic_label_ft = Label(filter_tab, text="Comparison statistic")
        compare_to_own_statistic_combobox_ft = ttk.Combobox(filter_tab, state="readonly",
                                                            values=statistical_characteristics_options)
        compare_to_own_statistic_combobox_ft.current(0)

        operand_label_ft = Label(filter_tab, text="Operand")
        operand_entry_ft = Entry(filter_tab, width=25)

        comparison_value_label_ft = Label(filter_tab, text="Comparison value")
        comparison_value_label_ft.grid(column=4, row=1)
        comparison_value_entry_ft = Entry(filter_tab, width=25)
        comparison_value_entry_ft.grid(column=4, row=2)

        def self_comparison_check():
            """
            Place and remove relevant labels and entries for the selected case
            """
            if compare_to_own_statistic_checkbutton_var_ft.get() == 1:
                comparison_value_label_ft.grid_forget()
                comparison_value_entry_ft.grid_forget()
                arithmetic_operation_label_ft.grid(column=6, row=1)
                arithmetic_operation_combobox_ft.grid(column=6, row=2)
                compare_to_own_statistic_label_ft.grid(column=5, row=1)
                compare_to_own_statistic_combobox_ft.grid(column=5, row=2)
                operand_label_ft.grid(column=7, row=1)
                operand_entry_ft.grid(column=7, row=2)
                filter_button_ft.grid(column=8, row=2)

            if compare_to_own_statistic_checkbutton_var_ft.get() == 0:
                arithmetic_operation_label_ft.grid_forget()
                arithmetic_operation_combobox_ft.grid_forget()
                operand_label_ft.grid_forget()
                operand_label_ft.grid_forget()
                operand_entry_ft.grid_forget()
                compare_to_own_statistic_label_ft.grid_forget()
                compare_to_own_statistic_combobox_ft.grid_forget()
                comparison_value_label_ft.grid(column=4, row=1)
                comparison_value_entry_ft.grid(column=4, row=2)

        compare_to_own_statistic_checkbutton_var_ft = tkinter.IntVar()
        compare_to_own_statistic_checkbutton_ft = Checkbutton(filter_tab, text="compare to own statistic",
                                                              variable=compare_to_own_statistic_checkbutton_var_ft,
                                                              onvalue=1, offvalue=0, command=self_comparison_check)
        compare_to_own_statistic_checkbutton_ft.grid(column=4, row=3)

        # Label and Buttons
        filter_button_ft = Button(filter_tab, text="Filter Traces", command=filter_traces)
        filter_button_ft.grid(column=5, row=2)

        browse_button_ft = Button(filter_tab, text="Choose Files", command=browse_files_ft)
        browse_button_ft.grid(column=1, row=2)

        # Tooltips
        selected_traces_tooltip_ft = Hovertip(selected_traces_label_ft, config.get('tooltips', 'selected_traces'))
        statistical_characteristic_tooltip_ft = Hovertip(statistics_label_ft,
                                                         config.get('tooltips', 'statistical_characteristic'))
        comparison_operator_tooltip_ft = Hovertip(comparison_operator_label_ft,
                                                  config.get('tooltips', 'comparison_operator'))
        comparison_statistic_tooltip_ft = Hovertip(compare_to_own_statistic_label_ft,
                                                   config.get('tooltips', 'comparison_statistic'))
        comparison_value_tooltip_ft = Hovertip(comparison_value_label_ft,
                                               config.get('tooltips', 'comparison_value'))
        operation_tooltip_ft = Hovertip(arithmetic_operation_label_ft,
                                        config.get('tooltips', 'operation'))
        operand_tooltip_ft = Hovertip(operand_label_ft,
                                      config.get('tooltips', 'operand'))
        statistic_checkbutton_tooltip_ft = Hovertip(compare_to_own_statistic_checkbutton_ft,
                                                    config.get('tooltips', 'statistic_checkbutton'))
        browse_files_button_tooltip_ft = Hovertip(browse_button_ft, config.get('tooltips', 'browse_files_button'))
        filter_button_tooltip_ft = Hovertip(filter_button_ft, config.get('tooltips', 'filter_button'))

        # ===ProFiDo format Tab
        converted_trace_label_pt = Label(profido_format_tab, text="Trace")
        converted_trace_label_pt.grid(row=0)
        profido_filename_label_pt = Label(profido_format_tab, text="Result filename")
        profido_filename_label_pt.grid(row=1)
        input_trace_entry_pt = Entry(profido_format_tab, width=config.get('entries', 'entry_width'))

        trace_column_display_pt = scrolledtext.ScrolledText(profido_format_tab, width=45, height=20)

        def browse_file_pt():
            """
            Select trace the columns shall be extracted from
            """
            input_trace_entry_pt.delete(0, END)
            selected_trace = fd.askopenfilename(initialdir=config.get('directories', 'converted_traces_dir'),
                                                title="Select a File",
                                                filetypes=(("JSON files", "*.json*"),))
            input_trace_entry_pt.insert(END, selected_trace)
            input_trace_entry_pt.grid(row=0, column=1)

        def extract_columns():
            """
            Extracts the tracedata as columns so the trace can be used in ProFiDo
            """

            with open(input_trace_entry_pt.get()) as trace_in:
                tracedata = json.load(trace_in)["tracebody"]["tracedata"]
                df = pd.DataFrame(tracedata)
                filename = config.get('directories', 'profido_traces_dir') + profido_filename_entry_pt.get() \
                           + '_dat.trace'
                dont_overwrite = 0
                if os.path.exists(filename):
                    dont_overwrite = not mb.askyesno("File already exists",
                                                     os.path.basename(filename) + " already exists. \n "
                                                                                  "Would you like to overwrite it?")
                if not dont_overwrite:
                    df.transpose().to_csv(filename, sep='\t',
                                          float_format="%e",
                                          index=False, header=False)

            with open(filename, 'r') as f:
                trace_column_display_pt.config(state=NORMAL)
                trace_column_display_pt.delete("1.0", "end")
                trace_column_display_pt.insert(INSERT, f.read())
                trace_column_display_pt.config(state=DISABLED)
                trace_column_display_pt.grid(column=0, row=6)
                mb.showinfo("Data extracted", "Displaying extracted columns")
                print("Columns were extracted from " + str(os.path.basename(input_trace_entry_pt.get())) +
                      "result was saved to " + profido_filename_entry_pt.get() + '_dat.trace')

        choose_trace_button_pt = Button(profido_format_tab, text="Choose File", command=browse_file_pt)
        choose_trace_button_pt.grid(row=0, column=0)

        profido_filename_entry_pt = Entry(profido_format_tab, width=config.get('entries', 'entry_width'))
        profido_filename_entry_pt.grid(row=1, column=1)

        extract_columns_button_pt = Button(profido_format_tab, text="Extract ProFiDo Format from Trace",
                                           command=extract_columns)
        extract_columns_button_pt.grid(row=3, column=1)

        # Tooltips
        converted_trace_label_tooltip_pt = Hovertip(converted_trace_label_pt,
                                                    config.get('tooltips', 'converted_trace'))
        profido_filename_entry_tooltip_pt = Hovertip(profido_filename_label_pt,
                                                     config.get('tooltips', 'profido_filename'))
        browse_trace_button_tooltip_pt = Hovertip(choose_trace_button_pt,
                                                  config.get('tooltips', 'browse_trace_button'))
        extract_button_tooltip_pt = Hovertip(extract_columns_button_pt,
                                             config.get('tooltips', 'extract_button'))

        # Validation tab

        def browse_file_vt():
            """
            Select trace you want to validate
            """
            file_entry_vt.delete(0, END)
            selected_trace = fd.askopenfilename(initialdir=config.get('directories', 'converted_traces_dir'),
                                                title="Select a File",
                                                filetypes=(("JSON files", "*.json*"),))
            file_entry_vt.insert(END, selected_trace)
            file_entry_vt.grid(row=0, column=0)

        def restore_traceheader(filename):
            """
            (Re)generates statistics and hash for the input trace
            :param filename: Input file
            """
            with open(filename) as tr:
                tracedata = json.load(tr)
                trace = generate_statistic(tracedata, statistic_format_entry_vt.get())
            dont_overwrite = 0
            if os.path.exists(filename):
                dont_overwrite = not mb.askyesno("File already exists",
                                                 os.path.basename(filename) + " already exists. \n "
                                                                              "Would you like to overwrite it?")
            if not dont_overwrite:
                with open(filename, 'w') as fp:
                    json.dump(trace, fp, indent=4)
            add_hash_to_trace(filename)

        file_entry_vt = Entry(validation_tab, width=config.get('entries', 'entry_width'))

        browse_file_button_vt = Button(validation_tab, text="Choose File", command=browse_file_vt)
        browse_file_button_vt.grid(row=1, column=0)

        validate_statistics_button_vt = Button(validation_tab, text="Validate Statistics",
                                               command=lambda: c.verify_statistics(file_entry_vt.get()))
        validate_statistics_button_vt.grid(row=2, column=0)

        validate_hash_button_vt = Button(validation_tab, text="Validate Hash",
                                         command=lambda: c.hash_check(file_entry_vt.get()))
        validate_hash_button_vt.grid(row=3, column=0)

        restore_traceheader_button_vt = Button(validation_tab, text="Restore Traceheader",
                                               command=lambda: restore_traceheader(file_entry_vt.get()))
        restore_traceheader_button_vt.grid(row=4, column=0)

        statistic_format_label_vt = Label(validation_tab, text="Statistic Format")
        statistic_format_label_vt.grid(column=1, row=2)

        statistic_format_entry_vt = Entry(validation_tab, width=config.get('entries', 'entry_width'))
        statistic_format_entry_vt.grid(column=2, row=2)

        # Tooltips
        browse_file_button_tooltip_vt = Hovertip(browse_file_button_vt, config.get('tooltips', 'browse_file_button_vt'))
        validate_statistics_button_tooltip_vt = Hovertip(validate_statistics_button_vt,
                                                         config.get('tooltips', 'validate_statistics_button'))
        validate_hash_button_tooltip_vt = Hovertip(validate_hash_button_vt,
                                                   config.get('tooltips', 'validate_hash_button'))
        restore_traceheader_button_tooltip_vt = Hovertip(restore_traceheader_button_vt,
                                                         config.get('tooltips', 'restore_traceheader_button'))
        statistic_format_tooltip_vt = Hovertip(statistic_format_label_vt,
                                               config.get('tooltips', 'statistic_format'))


# Create TCGUI instance and run mainloop
root = Tk()
converting_tool_gui = TraceConverterGUI(root)
root.mainloop()
