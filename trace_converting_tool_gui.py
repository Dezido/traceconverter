import configparser
import datetime
import json
import os
import pathlib
import sys
import tkinter.filedialog as fd
import tkinter.messagebox as mb
from idlelib.tooltip import Hovertip
from tkinter import *
from tkinter import ttk, scrolledtext

import pandas as pd

import trace_converting_tool_model as model
from trace_converting_tool_model import trace_template

# Load config file
config = configparser.RawConfigParser()
config.read('config.properties')


class TraceConvertingToolGUI:
    def __init__(self, master):
        """Creates a GUI for the tool"""
        self.master = master
        master.title("Trace Converting Tool")
        # Notebook and Tabs
        tab_parent = ttk.Notebook(master)
        prepare_file_tab = PrepareFileTab(tab_parent)
        convert_trace_tab = ConvertTraceTab(tab_parent)
        filter_traces_tab = FilterTraceTab(tab_parent)
        extract_tracedata_tab = ExtractTracedataTab(tab_parent)
        validate_trace_tab = ValidateTraceTab(tab_parent)

        # Add tabs to master
        tab_parent.add(prepare_file_tab, text="Prepare File")
        tab_parent.add(convert_trace_tab, text="Convert Trace")
        tab_parent.add(filter_traces_tab, text="Filter Traces")
        tab_parent.add(extract_tracedata_tab, text="Extract Tracedata")
        tab_parent.add(validate_trace_tab, text="Validate Trace")
        tab_parent.pack(expand=1, fill='both')


class PrepareFileTab(Frame):
    def __init__(self, master):
        """Creates a Prepare File Tab"""
        ttk.Frame.__init__(self, master)

        def browse_file_pft():
            """Opens file explorer to select a file"""
            try:
                file_entry_pft.delete(0, END)  # removes previously selected file
                selected_file = fd.askopenfilename(initialdir=config.get('directories', 'raw_traces_dir'),
                                                   title="Select a File",
                                                   filetypes=(("CSV files", "*.csv*"), ("all files", "*.*")))
                if not selected_file:
                    mb.showinfo('No file selected', 'Please select a valid file')
                file_entry_pft.insert(END, selected_file)
                file_entry_pft.grid(row=0, column=1)
                browse_file_button_pft.grid(row=0, column=0)
                if selected_file:
                    display_file_pft(file_entry_pft.get())
            except UnicodeDecodeError:
                mb.showerror('Invalid file selected', 'The selected file seems to invalid. Please try a different file')

        def calculate_timestamp_pft(file, date_and_time_column_index_list, date_and_time_format_list):
            """
            Overwrites timestamps in passed columns to unix timestamps
            :param file: Input file
            :param date_and_time_column_index_list: List with column indexes. Passed via GUI
            :param date_and_time_format_list: List with format strings. Passed via GUI
            """
            columns_list = list(map(int, (date_and_time_column_index_list.split(';'))))
            format_list = date_and_time_format_list.split(';')
            df = pd.read_csv(file, header=0, delimiter=',')
            try:
                df = model.df_columns_to_epoch(df, columns_list, format_list)
                df.to_csv(file, index=False, sep=',')
                mb.showinfo('Timestamps successfully calculated', 'Displaying file')
                display_file_pft(file)
            except IndexError:
                mb.showerror('Error during timestamp conversion', 'Column indexes invalid')
            except TypeError:
                mb.showerror('Error during timestamp conversion', 'The columns need to contain strings')
            except ValueError:
                mb.showerror('Error during timestamp conversion',
                             'Timestamp could not be converted with the passed format strings.\nPlease check if you'
                             ' passed the same number of format strings and column indexes '
                             'or if the timestamps need further preparation')
            except PermissionError:
                mb.showerror('Permission to edit file denied',
                             'Please check if the file is used by another application')

        def calculate_difference_rows_pft(file):
            """
            Creates/overwrites column with the row-wise difference for a passed column index
            :param file: Input file
            """
            df = pd.read_csv(file)
            try:
                df[row_wise_difference_result_column_entry_pft.get()] = df[
                    df.columns[int(row_wise_difference_entry_pft.get())]].diff()
                df.to_csv(file, index=False, sep=',')
                mb.showinfo('Inter arrival time successfully calculated', 'Displaying file')
                display_file_pft(file)
            except (IndexError, ValueError):
                mb.showerror('Error during calculation', 'Column index invalid')
            except TypeError:
                mb.showerror('Error during calculation', 'Columns needs to contain numbers')

        def calculate_difference_columns_pft(file, columns):
            """
            Adds or overwrites a column with inter arrival times. Calculated by subtracting two columns
            :param file: Input file
            :param columns: Indexes of the columns. Second column will be subtracted from first
            """
            try:
                columns = list(map(int, (columns.split(';'))))
            except ValueError:
                mb.showerror('Error during calculation', 'Both columns need to contain positive integers')
                return
            if len(columns) != 2 or columns[0] < 0 or columns[1] < 0:
                mb.showerror('Invalid number of columns', 'Pass two positive integers to calculate inter arrival time')
                return
            df = pd.read_csv(file)
            try:
                df[column_wise_difference_result_column_entry_pft.get()] = df[df.columns[columns[0]]] - df[
                    df.columns[columns[1]]]
                df.to_csv(file, index=False, sep=',')
                mb.showinfo('Inter arrival time successfully calculated', 'Displaying file')
                display_file_pft(file)
            except IndexError:
                mb.showerror('Error during calculation', 'Column indexes invalid')
            except TypeError:
                mb.showerror('Error during calculation', 'Both columns need to contain numbers')

        def display_file_pft(filename):
            """
            Displays the selected file in the preparation tab
            :param filename: File that will be displayed
            """
            if os.path.isfile(filename):
                with open(filename, 'r') as file:
                    file_displayer_label_pft.configure(text=os.path.basename(filename))
                    file_displayer_pft.grid(column=0, row=9, columnspan=12, rowspan=10)
                    file_displayer_pft.config(state=NORMAL)
                    file_displayer_pft.delete("1.0", "end")
                    file_displayer_pft.insert(INSERT, file.read())
                    file_displayer_pft.config(state=DISABLED)

        def convert_file_to_csv_pft(filename, delimiter):
            """
            Converts file to csv format
            :param filename:Input file
            :param delimiter:Delimiter of the file. For example regex
            """
            write_file = 1
            try:
                if len(delimiter) == 0:
                    delimiter = None
                if keep_header_checkbutton_var_pft.get() == 1:
                    df = pd.read_csv(filename, header=0, sep=delimiter)
                else:
                    df = pd.read_csv(filename, header=None, sep=delimiter)
                result_filename = filename.split('.')[0] + '.csv'
            except ValueError:
                mb.showerror("Error while reading file", "Please check if the file and the delimiter are valid."
                                                         "Note: The '\s+' delimiter also does not work if values in a "
                                                         "column are also seperated by whitespaces.")
                return
            if os.path.exists(result_filename):
                write_file = mb.askyesno("File already exists", result_filename +
                                         " already exists. \n Would you like to overwrite it?")
            try:
                if write_file:
                    if header_entry_pft.get() != "" and keep_header_checkbutton_var_pft.get() == 0:
                        df.to_csv(result_filename, index=False, sep=',', header=header_entry_pft.get().split(','))
                    else:
                        df.to_csv(result_filename, index=False, sep=',')
                    mb.showinfo('File successfully converted', 'Displaying file')
                    display_file_pft(result_filename)
                    file_entry_pft.delete(0, END)
                    file_entry_pft.insert(END, result_filename)
            except ValueError:
                mb.showerror("Error while converting file", "Please check if the file and the header are valid")
            except PermissionError:
                mb.showerror('Permission to edit file denied',
                             'Please check if the file is used by another application')

        # GUI Elements
        file_entry_pft = Entry(self, width=config.get('entries', 'entry_width'))

        browse_file_button_pft = Button(self, text="Choose File", command=browse_file_pft)
        browse_file_button_pft.grid(column=1, row=0)

        remove_rows_label_pft = Label(self, text="Number of Lines to Be Removed")
        remove_rows_label_pft.grid(column=0, row=2)

        remove_rows_entry_pft = Entry(self, width=config.get('entries', 'entry_width'))
        remove_rows_entry_pft.grid(column=1, row=2)

        remove_rows_button_pft = Button(self, text="Remove Lines",
                                        command=lambda: [model.remove_lines_from_csv(file_entry_pft.get(),
                                                                                     remove_rows_entry_pft.get()),
                                                         display_file_pft(file_entry_pft.get())])
        remove_rows_button_pft.grid(column=2, row=2)

        add_header_label_pft = Label(self, text="Header")
        add_header_label_pft.grid(column=0, row=3)

        add_header_entry_pft = Entry(self, width=config.get('entries', 'entry_width'))
        add_header_entry_pft.grid(column=1, row=3)

        add_header_button_pft = Button(self, text="Add Header to CSV File",
                                       command=lambda: [model.add_header_to_csv(file_entry_pft.get(),
                                                                                list(
                                                                                    add_header_entry_pft.get().split(
                                                                                        ","))),
                                                        display_file_pft(file_entry_pft.get())])
        add_header_button_pft.grid(column=2, row=3)

        file_displayer_label_pft = Label(self)
        file_displayer_label_pft.grid(column=0, row=8)
        file_displayer_pft = scrolledtext.ScrolledText(self, width=200, height=33)

        date_format_label_pft = Label(self, text="Format Strings of Timestamps")
        date_format_label_pft.grid(column=2, row=4)
        date_format_entry_pft = Entry(self, width=config.get('entries', 'entry_width'))
        date_format_entry_pft.grid(column=3, row=4)
        date_format_entry_pft.insert(END, config.get('entries', 'default_date_format_entry_pft'))

        date_columns_label_pft = Label(self, text="Timestamp Column Indexes")
        date_columns_label_pft.grid(column=0, row=4)
        date_columns_entry_pft = Entry(self, width=config.get('entries', 'entry_width'))
        date_columns_entry_pft.grid(column=1, row=4)

        column_wise_difference_label_pft = Label(self, text="Difference between Columns: Indexes")
        column_wise_difference_label_pft.grid(column=0, row=5)
        column_wise_difference_entry_pft = Entry(self, width=config.get('entries', 'entry_width'))
        column_wise_difference_entry_pft.grid(column=1, row=5)

        column_wise_difference_result_column_label_pft = Label(self,
                                                               text="Difference between Columns: Result Column Name")
        column_wise_difference_result_column_label_pft.grid(column=2, row=5)
        column_wise_difference_result_column_entry_pft = Entry(self,
                                                               width=config.get('entries', 'entry_width'))
        column_wise_difference_result_column_entry_pft.grid(column=3, row=5)

        row_wise_difference_label_pft = Label(self, text="Difference over Rows: Column Index")
        row_wise_difference_label_pft.grid(column=0, row=6)
        row_wise_difference_entry_pft = Entry(self, width=config.get('entries', 'entry_width'))
        row_wise_difference_entry_pft.grid(column=1, row=6)

        row_wise_difference_result_column_label_pft = Label(self,
                                                            text="Difference over Rows: Result Column Name")
        row_wise_difference_result_column_label_pft.grid(column=2, row=6)
        row_wise_difference_result_column_entry_pft = Entry(self,
                                                            width=config.get('entries', 'entry_width'))
        row_wise_difference_result_column_entry_pft.grid(column=3, row=6)

        calculate_timestamp_button_pft = Button(self, text="Calculate Unix Time",
                                                command=lambda: calculate_timestamp_pft(
                                                    file_entry_pft.get(),
                                                    date_columns_entry_pft.get(),
                                                    date_format_entry_pft.get()))
        calculate_timestamp_button_pft.grid(column=4, row=4)

        column_wise_difference_button_pft = Button(self, text="Calculate Difference between Columns",
                                                   command=lambda: calculate_difference_columns_pft(
                                                       file_entry_pft.get(),
                                                       column_wise_difference_entry_pft.get()))
        column_wise_difference_button_pft.grid(column=4, row=5)

        row_wise_difference_button_pft = Button(self, text="Calculate Difference over Rows",
                                                command=lambda: calculate_difference_rows_pft(
                                                    file_entry_pft.get()))
        row_wise_difference_button_pft.grid(column=4, row=6)

        delimiter_label_pft = Label(self, text="Delimiter of the Input File")
        delimiter_label_pft.grid(column=0, row=7)
        delimiter_entry_pft = Entry(self, width=config.get('entries', 'entry_width'))
        delimiter_entry_pft.grid(column=1, row=7)
        header_label_pft = Label(self, text="Header of the New CSV File")
        header_label_pft.grid(column=2, row=7)
        header_entry_pft = Entry(self, width=config.get('entries', 'entry_width'),
                                 bg=config.get('entries', 'background_colour_optional_entries'))
        header_entry_pft.grid(column=3, row=7)

        keep_header_checkbutton_var_pft = IntVar()
        keep_header_checkbutton_pft = Checkbutton(self, text="Use first Line as Header",
                                                  variable=keep_header_checkbutton_var_pft, onvalue=1,
                                                  offvalue=0,
                                                  selectcolor=config.get('entries',
                                                                         'background_colour_optional_entries'))
        keep_header_checkbutton_pft.grid(column=5, row=7)

        transform_filetype_button_pft = Button(self,
                                               text="Convert File to CSV",
                                               command=lambda:
                                               convert_file_to_csv_pft(file_entry_pft.get(),
                                                                       delimiter_entry_pft.get()))
        transform_filetype_button_pft.grid(column=4, row=7)

        # Tooltips
        browse_file_button_tooltip_pft = Hovertip(browse_file_button_pft,
                                                  config.get('tooltips', 'browse_file_button_pft'))
        remove_rows_label_tooltip_pft = Hovertip(remove_rows_label_pft, config.get('tooltips', 'remove_rows_label_pft'))
        remove_rows_button_tooltip_pft = Hovertip(remove_rows_button_pft,
                                                  config.get('tooltips', 'remove_rows_button_pft'))
        add_header_label_tooltip_pft = Hovertip(add_header_label_pft, config.get('tooltips', 'add_header_label_pft'))
        add_header_button_tooltip_pft = Hovertip(add_header_button_pft, config.get('tooltips', 'add_header_button_pft'))
        delimiter_tooltip_label_pft = Hovertip(delimiter_label_pft, config.get('tooltips', 'delimiter_label_pft'))
        transform_button_tooltip_pft = Hovertip(transform_filetype_button_pft,
                                                config.get('tooltips', 'transform_button_pft'))
        timestamp_format_label_tooltip_pft = Hovertip(date_format_label_pft,
                                                      config.get('tooltips', 'timestamp_format_label_pft'))
        timestamp_columns_label_tooltip_pft = Hovertip(date_columns_label_pft,
                                                       config.get('tooltips', 'timestamp_columns_label_pft'))
        calculate_timestamp_button_tooltip_pft = Hovertip(calculate_timestamp_button_pft,
                                                          config.get('tooltips', 'calculate_timestamp_button_pft'))
        columns_wise_difference_label_tooltip_pft = Hovertip(
            column_wise_difference_label_pft, config.get('tooltips', 'columns_wise_difference_label_pft'))
        columns_wise_difference_result_column_label_tooltip_pft = Hovertip(
            column_wise_difference_result_column_label_pft,
            config.get('tooltips', 'columns_wise_difference_result_column_label_pft'))
        columns_wise_difference_button_tooltip_pft = Hovertip(column_wise_difference_button_pft,
                                                              config.get('tooltips', 'columns_wise_difference_button'))
        row_wise_difference_label_tooltip_pft = Hovertip(row_wise_difference_label_pft,
                                                         config.get('tooltips', 'row_wise_difference_label_pft'))
        row_wise_difference_result_column_tooltip_pft = Hovertip(row_wise_difference_result_column_label_pft,
                                                                 config.get(
                                                                     'tooltips',
                                                                     'row_wise_difference_result_column_label_pft'))
        row_wise_difference_button_tooltip_pft = Hovertip(row_wise_difference_button_pft,
                                                          config.get('tooltips', 'row_wise_difference_button'))
        header_label_tooltip_pft = Hovertip(header_label_pft, config.get('tooltips', 'header_label_pft'))
        header_checkbutton_tooltip_pft = Hovertip(keep_header_checkbutton_pft,
                                                  config.get('tooltips', 'keep_header_checkbutton_pft'))


class ConvertTraceTab(Frame):
    def __init__(self, master):
        """Creates a Convert Trace Tab"""
        ttk.Frame.__init__(self, master)

        def show_tracedata_filename_entry_ctt():
            """Puts the tracedata_filename_label on the grid if the checkbox is selected"""
            if extract_tracedata_checkbutton_var_ctt.get() == 0:
                tracedata_filename_label_ctt.grid_forget()
                tracedata_filename_entry_ctt.grid_forget()
                float_format_label_ctt.grid_forget()
                float_format_entry_ctt.grid_forget()
            if extract_tracedata_checkbutton_var_ctt.get() == 1:
                tracedata_filename_label_ctt.grid(column=4, row=3)
                tracedata_filename_entry_ctt.grid(column=4, row=4)
                float_format_label_ctt.grid(column=4, row=5)
                float_format_entry_ctt.grid(column=4, row=6)

        def browse_file_ctt():
            """Opens file explorer to select a file"""
            original_tracefile_entry_ctt.delete(0, END)  # removes previously selected file
            selected_file = fd.askopenfilename(initialdir=config.get('directories', 'raw_traces_dir'),
                                               title="Select a File",
                                               filetypes=(("CSV files", "*.csv*"),))
            if not selected_file:
                mb.showinfo('No file selected', 'Please select a valid file')
            original_tracefile_entry_ctt.insert(END, selected_file)
            original_tracefile_entry_ctt.grid(row=1, column=1)
            if selected_file:
                display_file_ctt(selected_file)

        def convert_trace():
            """Takes the user input from the entry fields and converts the selected trace to the standard format"""
            org_filename = original_tracefile_entry_ctt.get()
            if os.path.isfile(org_filename) and pathlib.Path(org_filename).suffix == ".csv":
                try:
                    col = list(map(int, (column_indexes_entry_ctt.get().split(";"))))
                except ValueError:
                    mb.showerror("Column indexes invalid",
                                 "Indexes need to be integers seperated by a semicolon [;]")
                    return
                trace_template["tracebody"]["tracedata"] = \
                    model.get_tracedata_from_file(original_tracefile_entry_ctt.get(), col)
                amount_tracedata = len(trace_template["tracebody"]["tracedata"][0])
                trace_template["tracebody"]["tracedata description"] = tracedata_description_entry_ctt.get().split(";")
                trace_template["traceheader"]["metainformation"]["original name"] = os.path.basename(
                    original_tracefile_entry_ctt.get())
                trace_template["traceheader"]["metainformation"]["description"] = description_entry_ctt.get()
                trace_template["traceheader"]["metainformation"]["source"] = source_entry_ctt.get()
                trace_template["traceheader"]["metainformation"]["user"] = username_entry_ctt.get()
                trace_template["traceheader"]["metainformation"]["additional information"] = \
                    additional_information_entry_ctt.get('1.0', 'end-1c').replace("\n", "").split(";")
                trace_template["traceheader"]["metainformation"]["creation time"] = str(datetime.datetime.now())
                # Generates statistics and adds them into a list. Each list entry represents one column of the raw trace
                if amount_tracedata > 4:
                    trace = model.generate_statistic(trace_template, statistics_format_entry_ctt.get())
                else:
                    trace = trace_template
                    mb.showinfo("Statistics won't be computed", "Tracedata only contains " + str(amount_tracedata) +
                                " elements per column. Computing statistics requires five or more.")
                # Save trace to file
                filename = config.get('directories', 'converted_traces_dir') + \
                           '/' + result_filename_entry_ctt.get() + config.get('files', 'trace_file_suffix')
                write_file = 1
                if os.path.exists(filename):
                    write_file = mb.askyesno("File already exists",
                                             os.path.basename(filename) + " already exists. \n "
                                                                          "Would you like to overwrite it?")
                if write_file:
                    with open(filename, 'w') as fp:
                        json.dump(trace, fp, indent=4)
                    model.add_hash_value_to_trace(filename)
                    # If tracedata checkbox is selected the data will also be extracted
                    if extract_tracedata_checkbutton_var_ctt.get() == 1:
                        tracedata_filename = config.get('directories',
                                                        'tracedata_dir') + tracedata_filename_entry_ctt.get() + \
                                             config.get('files', 'tracedata_file_suffix')
                        model.extract_tracedata(
                            filename, tracedata_filename, float_format_entry_ctt.get())
                    mb.showinfo("Trace successfully converted", "Displaying converted Trace")
                else:
                    mb.showinfo("File already exists", "Displaying existing File")
                # Display the created traces
                display_file_ctt(filename)
            else:
                mb.showinfo('No file selected', 'Please select a valid file')

        def display_file_ctt(filename):
            """
            Displays the selected file in the convert tab
            :param filename: File that will be displayed
            """
            with open(filename, 'r') as f:
                file_displayer_ctt.config(state=NORMAL)
                file_displayer_ctt.delete("1.0", "end")
                file_displayer_ctt.insert(INSERT, f.read())
                file_displayer_ctt.config(state=DISABLED)
                file_displayer_ctt.grid(column=5, row=1, columnspan=12, rowspan=10)

        # GUI Elements
        columns_label_ctt = Label(self, text="Tracedata Column Indexes")
        columns_label_ctt.grid(row=2)
        tracedata_description_label_ctt = Label(self, text="Tracedata Description")
        tracedata_description_label_ctt.grid(row=3)
        trace_description_label_ctt = Label(self, text="Trace Description")
        trace_description_label_ctt.grid(row=4)
        source_label_ctt = Label(self, text="Trace Source")
        source_label_ctt.grid(row=5)
        username_label_ctt = Label(self, text="Username")
        username_label_ctt.grid(row=6)
        additional_information_label_ctt = Label(self, text="Additional Information")
        additional_information_label_ctt.grid(row=7)
        result_filename_label_ctt = Label(self, text="Result Filename")
        result_filename_label_ctt.grid(row=8)

        tracedata_filename_label_ctt = Label(self, text="Filename")
        tracedata_filename_entry_ctt = Entry(self)

        float_format_label_ctt = Label(self, text="Float Format String")
        float_format_entry_ctt = Entry(self,
                                       bg=config.get('entries', 'background_colour_optional_entries'))
        float_format_entry_ctt.insert(END, config.get('entries', 'default_float_format_entry_ett'))

        extract_tracedata_checkbutton_var_ctt = IntVar()
        extract_tracedata_checkbutton_ctt = Checkbutton(self,
                                                        text="Extract Tracedata after Conversion",
                                                        variable=extract_tracedata_checkbutton_var_ctt, onvalue=1,
                                                        offvalue=0, command=show_tracedata_filename_entry_ctt,
                                                        selectcolor=config.get('entries',
                                                                               'background_colour_optional_entries'))
        extract_tracedata_checkbutton_ctt.grid(column=4, row=2)

        statistics_format_label_ctt = Label(self, text="Statistic Format String")
        statistics_format_label_ctt.grid(row=12, column=0)

        statistics_format_entry_ctt = Entry(self, width=config.get('entries', 'entry_width'),
                                            bg=config.get('entries', 'background_colour_optional_entries'))
        statistics_format_entry_ctt.grid(row=12, column=1)

        original_tracefile_entry_ctt = Entry(self, width=config.get('entries', 'entry_width'))

        # Create entries and set default values
        original_tracefile_button_ctt = Button(self, text="Choose File", command=browse_file_ctt)

        column_indexes_entry_ctt = Entry(self, width=config.get('entries', 'entry_width'))
        column_indexes_entry_ctt.insert(END, config.get('entries', 'default_columns_entry_ctt'))

        source_entry_ctt = Entry(self, width=config.get('entries', 'entry_width'))
        source_entry_ctt.insert(END, config.get('entries', 'default_trace_source_entry_ctt'))

        description_entry_ctt = Entry(self, width=config.get('entries', 'entry_width'))
        description_entry_ctt.insert(END, config.get('entries', 'default_description_entry_ctt'))

        tracedata_description_entry_ctt = Entry(self, width=config.get('entries', 'entry_width'))
        tracedata_description_entry_ctt.insert(END, config.get('entries', 'default_tracedata_description_entry_ctt'))

        username_entry_ctt = Entry(self, width=config.get('entries', 'entry_width'))
        username_entry_ctt.insert(END, config.get('entries', 'default_username_entry_ctt'))

        additional_information_entry_ctt = Text(self, width=config.get('entries', 'entry_width'),
                                                height=25,
                                                font=config.get('fonts', 'default_font_text_widget'))
        additional_information_entry_ctt.insert(END, config.get('entries', 'default_additional_information_entry_ctt'))

        result_filename_entry_ctt = Entry(self, width=config.get('entries', 'entry_width'))
        result_filename_entry_ctt.insert(END, config.get('entries', 'default_filename_entry_ctt'))

        original_tracefile_button_ctt.grid(row=1, column=0)
        column_indexes_entry_ctt.grid(row=2, column=1)
        tracedata_description_entry_ctt.grid(row=3, column=1)
        description_entry_ctt.grid(row=4, column=1)
        source_entry_ctt.grid(row=5, column=1)
        username_entry_ctt.grid(row=6, column=1)
        additional_information_entry_ctt.grid(row=7, column=1)
        result_filename_entry_ctt.grid(row=8, column=1)

        # Text widget to display the converted trace
        file_displayer_ctt = scrolledtext.ScrolledText(self, width=100, height=33)

        convert_button_ctt = Button(self, text='Convert Trace', command=convert_trace)
        convert_button_ctt.grid(row=13, column=1)

        # Tooltips
        columns_label_tooltip_ctt = Hovertip(columns_label_ctt, config.get('tooltips', 'columns_label_ctt'))
        source_label_tooltip_ctt = Hovertip(source_label_ctt, config.get('tooltips', 'source_label_ctt'))
        description_label_tooltip_ctt = Hovertip(trace_description_label_ctt,
                                                 config.get('tooltips', 'trace_description_label_ctt'))
        tracedata_description_label_tooltip_ctt = Hovertip(tracedata_description_label_ctt,
                                                           config.get('tooltips', 'tracedata_description_label_ctt'))
        username_label_tooltip_ctt = Hovertip(username_label_ctt, config.get('tooltips', 'username_label_ctt'))
        additional_information_label_tooltip_ctt = Hovertip(additional_information_label_ctt,
                                                            config.get('tooltips', 'additional_information_label_ctt'))
        result_filename_label_tooltip_ctt = Hovertip(result_filename_label_ctt,
                                                     config.get('tooltips', 'result_filename_label_ctt'))
        tracedata_checkbutton_tooltip_ctt = Hovertip(extract_tracedata_checkbutton_ctt,
                                                     config.get('tooltips', 'tracedata_checkbutton'))
        tracedata_filename_label_tooltip_ctt = Hovertip(tracedata_filename_label_ctt,
                                                        config.get('tooltips', 'tracedata_filename_label_ctt'))
        browse_file_button_tooltip_ctt = Hovertip(original_tracefile_button_ctt,
                                                  config.get('tooltips', 'browse_file_button'))
        convert_button_tooltip_ctt = Hovertip(convert_button_ctt,
                                              config.get('tooltips', 'browse_file_button'))
        numerical_format_label_tooltip_ctt = Hovertip(statistics_format_label_ctt,
                                                      config.get('tooltips', 'statistics_format_string'))
        float_format_label_tooltip_ctt = Hovertip(float_format_label_ctt,
                                                  config.get('tooltips', 'float_format_label_ett'))


class FilterTraceTab(Frame):
    def __init__(self, master):
        """Creates a Filter Trace Tab"""
        ttk.Frame.__init__(self, master)

        def browse_files_ftt():
            """Opens file explorer to select files for filtering"""
            try:
                file_tuple = ()
                additional_files = True
                while additional_files:
                    files = fd.askopenfilenames(initialdir=config.get('directories', 'converted_traces_dir'),
                                                title="Select a File",
                                                filetypes=(("JSON files", "*.json*"),))
                    if files:
                        file_tuple += files
                    additional_files = mb.askyesno('Select additional files',
                                                   'Do you want to add more files to the selection?')
                if len(file_tuple) == 0:
                    mb.showinfo('No files selected', 'Please select at least one valid file')
                selected_traces_lb.delete(0, 'end')
                selected_files.clear()
                selected_filenames.clear()
                for i in file_tuple:
                    with open(str(i)) as json_file:
                        selected_files.append(json.load(json_file)["traceheader"]["statistical characteristics"])
                        selected_filenames.append(os.path.basename(os.path.dirname(i)) + '/' + os.path.basename(i))
                for i in range(len(selected_filenames)):
                    selected_traces_lb.insert(i, selected_filenames[i])
                selected_traces_lb.grid(column=1, row=2, rowspan=5)
                browse_button_ftt.grid(column=1, row=8)
            except json.decoder.JSONDecodeError:
                mb.showerror("Invalid Trace", "Invalid/corrupted traces were selected")

        def filter_traces_ftt(expression):
            """Evaluates the expression for the selected traces"""
            filter_results.clear()
            for i in filter_results_treeviw.get_children():
                filter_results_treeviw.delete(i)
            for i in range(len(selected_files)):
                for j in range(len(selected_files[i]["mean"])):
                    try:
                        mean = float(selected_files[i]["mean"][j])
                        median = float(selected_files[i]["median"][j])
                        skewness = float(selected_files[i]["skewness"][j])
                        kurtosis = float(selected_files[i]["kurtosis"][j])
                        autocorrelation = float(selected_files[i]["autocorrelation"][j])
                        variance = float(selected_files[i]["variance"][j])
                    except ValueError:
                        mb.showerror('Invalid Trace', 'Trace number ' + str(i + 1) + ' contains invalid statistics')
                        return
                    try:
                        if eval(expression):
                            trace = [os.path.basename(selected_filenames[i]),
                                     mean,
                                     median,
                                     skewness,
                                     kurtosis,
                                     autocorrelation,
                                     variance
                                     ]
                            filter_results.append(trace)
                    except (NameError, SyntaxError):
                        mb.showerror("Expression invalid", "Please enter a valid expression")
                        raise
            for i in range(len(filter_results)):
                filter_results_treeviw.insert('', 'end', values=(filter_results[i][0],
                                                                 filter_results[i][1],
                                                                 filter_results[i][2],
                                                                 filter_results[i][3],
                                                                 filter_results[i][4],
                                                                 filter_results[i][5],
                                                                 filter_results[i][6]))
            Label(self, text="Results").grid(column=1, row=10)
            filter_results_treeviw.grid(column=1, row=11, columnspan=10)
            vsb_filter_results_tv.grid(column=11, row=11, sticky=N + S)

        # GUI Elements
        selected_traces_label_ftt = Label(self, text="Selected Traces")
        selected_traces_label_ftt.grid(column=1, row=1)

        selected_traces_lb = Listbox(self, width=config.get('listbox', 'listbox_width'),
                                     height=config.get('listbox', 'listbox_height'))

        treeview_columns = ['name', 'mean', 'median', 'skewness', 'kurtosis', 'autocorrelation', 'variance']
        filter_results_treeviw = ttk.Treeview(self, columns=treeview_columns, show='headings',
                                              height=config.get('treeview', 'filter_treeview_height'))
        vsb_filter_results_tv = ttk.Scrollbar(self, orient="vertical", command=filter_results_treeviw.yview)
        filter_results_treeviw.configure(yscrollcommand=vsb_filter_results_tv.set)
        filter_results_treeviw.heading('name', text='Name')
        filter_results_treeviw.column('name', width=300)
        filter_results_treeviw.heading('mean', text='Mean')
        filter_results_treeviw.heading('median', text='Median')
        filter_results_treeviw.heading('skewness', text='Skewness')
        filter_results_treeviw.heading('kurtosis', text='Kurtosis')
        filter_results_treeviw.heading('autocorrelation', text='Autocorrelation')
        filter_results_treeviw.heading('variance', text='Variance')

        selected_filenames = []
        selected_files = []
        filter_results = []

        expression_label_ftt = Label(self, text="Boolean Expression")
        expression_label_ftt.grid(column=3, row=2)

        expression_entry_ftt = Entry(self, width=config.get('entries', 'entry_width'))
        expression_entry_ftt.grid(column=4, row=2)

        filter_button_ftt = Button(self, text="Filter Traces",
                                   command=lambda: filter_traces_ftt(expression_entry_ftt.get()))
        filter_button_ftt.grid(column=5, row=2)

        browse_button_ftt = Button(self, text="Choose Files", command=browse_files_ftt)
        browse_button_ftt.grid(column=1, row=2)

        # Tooltips
        selected_traces_label_tooltip_ftt = Hovertip(selected_traces_label_ftt,
                                                     config.get('tooltips', 'selected_traces_label_ftt'))
        browse_files_button_tooltip_ftt = Hovertip(browse_button_ftt, config.get('tooltips', 'browse_files_button_ftt'))
        filter_button_tooltip_ftt = Hovertip(filter_button_ftt, config.get('tooltips', 'filter_button_ftt'))
        expression_label_tooltip_ftt = Hovertip(expression_label_ftt, config.get('tooltips', 'expression_label_ftt'))


class ExtractTracedataTab(Frame):
    def __init__(self, master):
        """Creates a Extract Tracedata Tab"""
        ttk.Frame.__init__(self, master)

        def browse_file_ett():
            """Opens file explorer to select a file"""
            self.input_trace_entry_ett.delete(0, END)
            selected_trace = fd.askopenfilename(initialdir=config.get('directories', 'converted_traces_dir'),
                                                title="Select a File",
                                                filetypes=(("JSON files", "*.json*"),))
            if not selected_trace:
                mb.showinfo('No file selected', 'Please select a valid file')
            self.input_trace_entry_ett.insert(END, selected_trace)
            self.input_trace_entry_ett.grid(row=0, column=1)
            display_file_ett(selected_trace)

        def display_file_ett(filename):
            """
            Displays the selected file in the extract tracedata tab
            :param filename: File that will be displayed
            """
            with open(filename, 'r') as f:
                self.trace_column_display_ett.config(state=NORMAL)
                self.trace_column_display_ett.delete("1.0", "end")
                self.trace_column_display_ett.insert(INSERT, f.read())
                self.trace_column_display_ett.config(state=DISABLED)
                self.trace_column_display_ett.grid(column=0, row=6, columnspan=4)

        def extract_tracedata_ett():
            """Extracts the tracedata so it can be used in ProFiDo"""
            org_filename = self.input_trace_entry_ett.get()
            if os.path.isfile(org_filename) and pathlib.Path(org_filename).suffix == ".json":
                try:
                    filename = config.get('directories', 'tracedata_dir') + self.tracedata_filename_entry_ett.get() + \
                               config.get('files', 'tracedata_file_suffix')
                    model.extract_tracedata(self.input_trace_entry_ett.get(), filename,
                                            self.float_format_entry_ett.get())
                    display_file_ett(filename)
                    mb.showinfo("Data extracted", "Displaying extracted columns")
                except json.decoder.JSONDecodeError:
                    mb.showerror('Invalid Trace', 'The selected file is not a valid Trace')
            else:
                mb.showinfo('No file selected', 'Please select a valid file')

        # GUI Elements
        self.converted_trace_label_ett = Label(self, text="Trace")
        self.converted_trace_label_ett.grid(row=0)
        self.tracedata_filename_label_ett = Label(self, text="Result Filename")
        self.tracedata_filename_label_ett.grid(row=1, column=0)
        self.float_format_label_ett = Label(self, text="Float Format String")
        self.float_format_label_ett.grid(row=2, column=0)
        self.float_format_entry_ett = Entry(self, width=config.get('entries', 'entry_width'),
                                            bg=config.get('entries', 'background_colour_optional_entries'))
        self.float_format_entry_ett.grid(row=2, column=1)
        self.float_format_entry_ett.insert(END, config.get('entries', 'default_float_format_entry_ett'))
        self.input_trace_entry_ett = Entry(self, width=config.get('entries', 'entry_width'))

        self.trace_column_display_ett = scrolledtext.ScrolledText(self, width=100, height=33)

        self.choose_trace_button_ett = Button(self, text="Choose File", command=browse_file_ett)
        self.choose_trace_button_ett.grid(row=0, column=0)

        self.tracedata_filename_entry_ett = Entry(self, width=config.get('entries', 'entry_width'))
        self.tracedata_filename_entry_ett.grid(row=1, column=1)

        self.extract_columns_button_ett = Button(self, text="Extract Tracedata",
                                                 command=extract_tracedata_ett)
        self.extract_columns_button_ett.grid(row=2, column=2)

        # Tooltips
        converted_trace_label_tooltip_ett = Hovertip(self.converted_trace_label_ett,
                                                     config.get('tooltips', 'converted_trace_label_ett'))
        tracedata_filename_entry_tooltip_ett = Hovertip(self.tracedata_filename_label_ett,
                                                        config.get('tooltips', 'tracedata_filename_label_ett'))
        browse_trace_button_tooltip_ett = Hovertip(self.choose_trace_button_ett,
                                                   config.get('tooltips', 'browse_trace_button_ett'))
        extract_button_tooltip_ett = Hovertip(self.extract_columns_button_ett,
                                              config.get('tooltips', 'extract_tracedata_button_ett'))
        float_format_label_tooltip_ett = Hovertip(self.float_format_label_ett,
                                                  config.get('tooltips', 'float_format_label_ett'))


class ValidateTraceTab(Frame):
    def __init__(self, master):
        """Creates a Validate Trace Tab"""
        ttk.Frame.__init__(self, master)

        def browse_file_vtt():
            """Opens file explorer to select a file"""
            self.file_entry_vtt.delete(0, END)
            selected_trace = fd.askopenfilename(initialdir=config.get('directories', 'converted_traces_dir'),
                                                title="Select a File",
                                                filetypes=(("JSON files", "*.json*"),))
            if not selected_trace:
                mb.showinfo('No file selected', 'Please select a valid file')
            self.file_entry_vtt.insert(END, selected_trace)
            self.file_entry_vtt.grid(row=0, column=0)

        # GUI Elements
        self.file_entry_vtt = Entry(self, width=config.get('entries', 'entry_width'))

        self.relative_tolerance_label_vtt = Label(self, text="Relative Tolerance")
        self.relative_tolerance_label_vtt.grid(column=1, row=2)

        self.relative_tolerance_entry_vtt = Entry(self, width=config.get('entries', 'entry_width'))
        self.relative_tolerance_entry_vtt.grid(column=2, row=2)

        self.browse_file_button_vtt = Button(self, text="Choose File", command=browse_file_vtt)
        self.browse_file_button_vtt.grid(row=1, column=0)

        self.validate_statistics_button_vtt = Button(self, text="Validate Statistics",
                                                     command=lambda:
                                                     model.verify_statistics(self.file_entry_vtt.get(),
                                                                             self.relative_tolerance_entry_vtt.get()))
        self.validate_statistics_button_vtt.grid(row=2, column=0)

        self.validate_hash_button_vtt = Button(self, text="Validate Hash",
                                               command=lambda: model.hash_check(self.file_entry_vtt.get()))
        self.validate_hash_button_vtt.grid(row=3, column=0)

        self.restore_traceheader_button_vtt = Button(self, text="Restore Traceheader",
                                                     command=lambda: model.restore_traceheader(
                                                         self.file_entry_vtt.get(),
                                                         self.statistics_format_string_entry_vtt.get()))
        self.restore_traceheader_button_vtt.grid(row=4, column=0)

        self.statistics_format_string_label_vtt = Label(self, text="Statistics Format String")
        self.statistics_format_string_label_vtt.grid(column=1, row=4)

        self.statistics_format_string_entry_vtt = Entry(self,
                                                        width=config.get('entries', 'entry_width'),
                                                        bg=config.get('entries',
                                                                      'background_colour_optional_entries'))
        self.statistics_format_string_entry_vtt.grid(column=2, row=4)

        # Tooltips
        browse_file_button_tooltip_vtt = Hovertip(self.browse_file_button_vtt,
                                                  config.get('tooltips', 'browse_file_button_vtt'))
        validate_statistics_button_tooltip_vtt = Hovertip(self.validate_statistics_button_vtt,
                                                          config.get('tooltips', 'validate_statistics_button_vtt'))
        relative_tolerance_tooltip_vtt = Hovertip(self.relative_tolerance_label_vtt,
                                                  config.get('tooltips', 'relative_tolerance_vtt'))
        validate_hash_button_tooltip_vtt = Hovertip(self.validate_hash_button_vtt,
                                                    config.get('tooltips', 'validate_hash_button_vtt'))
        restore_traceheader_button_tooltip_vtt = Hovertip(self.restore_traceheader_button_vtt,
                                                          config.get('tooltips', 'restore_traceheader_button_vtt'))
        numerical_format_tooltip_vtt = Hovertip(self.statistics_format_string_label_vtt,
                                                config.get('tooltips', 'statistics_format_string'))


# Create TCGUI instance and run mainloop
if __name__ == "__main__":
    root = Tk()
    converting_tool_gui = TraceConvertingToolGUI(root)
    root.mainloop()
    sys.exit()
