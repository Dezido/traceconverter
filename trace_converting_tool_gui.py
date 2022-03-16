import configparser
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

# Load config file
config = configparser.RawConfigParser()
config.read('config.properties')


class TraceConvertingToolGUI:
    def __init__(self, master):
        """Creates a GUI for the tool"""
        master = master
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

        def browse_file():
            """Opens file explorer to select a file"""
            try:
                file_entry.delete(0, END)  # removes previously selected file
                selected_file = fd.askopenfilename(initialdir=config.get('directories', 'raw_traces_dir'),
                                                   title="Select a File",
                                                   filetypes=(("CSV files", "*.csv*"), ("all files", "*.*")))
                if not selected_file:
                    mb.showinfo('No file selected', 'Please select a valid file')
                file_entry.insert(END, selected_file)
                file_entry.grid(row=0, column=1)
                browse_file_button.grid(row=0, column=0)
                if selected_file:
                    display_file(file_entry.get())
            except UnicodeDecodeError:
                mb.showerror('Invalid file selected', 'The selected file seems to invalid. Please try a different file')

        def calculate_timestamp(file, date_and_time_column_index_list, date_and_time_format_list):
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
                display_file(file)
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

        def calculate_difference_rows(file):
            """
            Creates/overwrites column with the row-wise difference for a passed column index
            :param file: Input file
            """
            df = pd.read_csv(file)
            try:
                df[row_wise_difference_result_column_entry.get()] = df[
                    df.columns[int(row_wise_difference_entry.get())]].diff()
                df.to_csv(file, index=False, sep=',')
                mb.showinfo('Inter arrival time successfully calculated', 'Displaying file')
                display_file(file)
            except (IndexError, ValueError):
                mb.showerror('Error during calculation', 'Column index invalid')
            except TypeError:
                mb.showerror('Error during calculation', 'Columns needs to contain numbers')

        def calculate_difference_columns(file, columns):
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
                df[column_wise_difference_result_column_entry.get()] = df[df.columns[columns[0]]] - df[
                    df.columns[columns[1]]]
                df.to_csv(file, index=False, sep=',')
                mb.showinfo('Inter arrival time successfully calculated', 'Displaying file')
                display_file(file)
            except IndexError:
                mb.showerror('Error during calculation', 'Column indexes invalid')
            except TypeError:
                mb.showerror('Error during calculation', 'Both columns need to contain numbers')

        def display_file(filename):
            """
            Displays the selected file in the preparation tab
            :param filename: File that will be displayed
            """
            if os.path.isfile(filename):
                with open(filename, 'r') as file:
                    file_displayer_label.configure(text=os.path.basename(filename))
                    file_displayer.grid(column=0, row=9, columnspan=12, rowspan=10)
                    file_displayer.config(state=NORMAL)
                    file_displayer.delete("1.0", "end")
                    file_displayer.insert(INSERT, file.read())
                    file_displayer.config(state=DISABLED)

        def convert_file_to_csv(filename, delimiter):
            """
            Converts file to csv format
            :param filename:Input file
            :param delimiter:Delimiter of the file. For example regex
            """
            write_file = 1
            try:
                if len(delimiter) == 0:
                    delimiter = None
                if keep_header_checkbutton.get() == 1:
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
                    if header_entry.get() != "" and keep_header_checkbutton.get() == 0:
                        df.to_csv(result_filename, index=False, sep=',', header=header_entry.get().split(','))
                    else:
                        df.to_csv(result_filename, index=False, sep=',')
                    mb.showinfo('File successfully converted', 'Displaying file')
                    display_file(result_filename)
                    file_entry.delete(0, END)
                    file_entry.insert(END, result_filename)
            except ValueError:
                mb.showerror("Error while converting file", "Please check if the file and the header are valid")
            except PermissionError:
                mb.showerror('Permission to edit file denied',
                             'Please check if the file is used by another application')

        # GUI Elements
        file_entry = Entry(self, width=config.get('entries', 'entry_width'))

        browse_file_button = Button(self, text="Choose File", command=browse_file)
        browse_file_button.grid(column=1, row=0)

        remove_rows_label = Label(self, text="Number of Lines to Be Removed")
        remove_rows_label.grid(column=0, row=2)

        remove_rows_entry = Entry(self, width=config.get('entries', 'entry_width'))
        remove_rows_entry.grid(column=1, row=2)

        remove_rows_button = Button(self, text="Remove Lines",
                                    command=lambda: [model.remove_lines_from_csv(file_entry.get(),
                                                                                 remove_rows_entry.get()),
                                                     display_file(file_entry.get())])
        remove_rows_button.grid(column=2, row=2)

        add_header_label = Label(self, text="Header")
        add_header_label.grid(column=0, row=3)

        add_header_entry = Entry(self, width=config.get('entries', 'entry_width'))
        add_header_entry.grid(column=1, row=3)

        add_header_button = Button(self, text="Add Header to CSV File", command=lambda: [model.add_header_to_csv(
                                           file_entry.get(), list(add_header_entry.get().split(","))),
                                                    display_file(file_entry.get())])
        add_header_button.grid(column=2, row=3)

        file_displayer_label = Label(self)
        file_displayer_label.grid(column=0, row=8)
        file_displayer = scrolledtext.ScrolledText(self, width=200, height=33)

        date_format_label = Label(self, text="Format Strings of Timestamps")
        date_format_label.grid(column=2, row=4)
        date_format_entry = Entry(self, width=config.get('entries', 'entry_width'))
        date_format_entry.grid(column=3, row=4)
        date_format_entry.insert(END, config.get('entries', 'default_date_format_entry_pft'))

        date_columns_label = Label(self, text="Timestamp Column Indexes")
        date_columns_label.grid(column=0, row=4)
        date_columns_entry = Entry(self, width=config.get('entries', 'entry_width'))
        date_columns_entry.grid(column=1, row=4)

        column_wise_difference_label = Label(self, text="Difference between Columns: Indexes")
        column_wise_difference_label.grid(column=0, row=5)
        column_wise_difference_entry = Entry(self, width=config.get('entries', 'entry_width'))
        column_wise_difference_entry.grid(column=1, row=5)

        column_wise_difference_result_column_label = Label(self, text="Difference between Columns: Result Column Name")
        column_wise_difference_result_column_label.grid(column=2, row=5)
        column_wise_difference_result_column_entry = Entry(self, width=config.get('entries', 'entry_width'))
        column_wise_difference_result_column_entry.grid(column=3, row=5)

        row_wise_difference_label = Label(self, text="Difference over Rows: Column Index")
        row_wise_difference_label.grid(column=0, row=6)
        row_wise_difference_entry = Entry(self, width=config.get('entries', 'entry_width'))
        row_wise_difference_entry.grid(column=1, row=6)

        row_wise_difference_result_column_label = Label(self, text="Difference over Rows: Result Column Name")
        row_wise_difference_result_column_label.grid(column=2, row=6)
        row_wise_difference_result_column_entry = Entry(self, width=config.get('entries', 'entry_width'))
        row_wise_difference_result_column_entry.grid(column=3, row=6)

        calculate_timestamp_button = Button(self, text="Calculate Unix Time",
                                            command=lambda: calculate_timestamp(
                                                file_entry.get(), date_columns_entry.get(), date_format_entry.get()))
        calculate_timestamp_button.grid(column=4, row=4)

        column_wise_difference_button = Button(self, text="Calculate Difference between Columns",
                                               command=lambda: calculate_difference_columns(
                                                   file_entry.get(), column_wise_difference_entry.get()))
        column_wise_difference_button.grid(column=4, row=5)

        row_wise_difference_button = Button(self, text="Calculate Difference over Rows",
                                            command=lambda: calculate_difference_rows(file_entry.get()))
        row_wise_difference_button.grid(column=4, row=6)

        delimiter_label = Label(self, text="Delimiter of the Input File")
        delimiter_label.grid(column=0, row=7)
        delimiter_entry = Entry(self, width=config.get('entries', 'entry_width'))
        delimiter_entry.grid(column=1, row=7)
        header_label = Label(self, text="Header of the New CSV File")
        header_label.grid(column=2, row=7)
        header_entry = Entry(self, width=config.get('entries', 'entry_width'),
                             bg=config.get('entries', 'background_colour_optional_entries'))
        header_entry.grid(column=3, row=7)

        keep_header_checkbutton = IntVar()
        keep_header_checkbutton = Checkbutton(self, text="Use first Line as Header",
                                              variable=keep_header_checkbutton, onvalue=1,
                                              offvalue=0,
                                              selectcolor=config.get('entries','background_colour_optional_entries'))
        keep_header_checkbutton.grid(column=5, row=7)

        transform_filetype_button = Button(self,
                                           text="Convert File to CSV",
                                           command=lambda:
                                           convert_file_to_csv(file_entry.get(), delimiter_entry.get()))
        transform_filetype_button.grid(column=4, row=7)

        # Tooltips
        browse_file_button_tooltip = Hovertip(browse_file_button, config.get('tooltips', 'browse_file_button_pft'))
        remove_rows_label_tooltip = Hovertip(remove_rows_label, config.get('tooltips', 'remove_rows_label_pft'))
        remove_rows_button_tooltip = Hovertip(remove_rows_button, config.get('tooltips', 'remove_rows_button_pft'))
        add_header_label_tooltip = Hovertip(add_header_label, config.get('tooltips', 'add_header_label_pft'))
        add_header_button_tooltip = Hovertip(add_header_button, config.get('tooltips', 'add_header_button_pft'))
        delimiter_tooltip_label = Hovertip(delimiter_label, config.get('tooltips', 'delimiter_label_pft'))
        transform_button_tooltip = Hovertip(transform_filetype_button, config.get('tooltips', 'transform_button_pft'))
        timestamp_format_label_tooltip = Hovertip(date_format_label,
                                                  config.get('tooltips', 'timestamp_format_label_pft'))
        timestamp_columns_label_tooltip = Hovertip(date_columns_label,
                                                   config.get('tooltips', 'timestamp_columns_label_pft'))
        calculate_timestamp_button_tooltip = Hovertip(calculate_timestamp_button,
                                                      config.get('tooltips', 'calculate_timestamp_button_pft'))
        columns_wise_difference_label_tooltip = Hovertip(
            column_wise_difference_label, config.get('tooltips', 'columns_wise_difference_label_pft'))
        columns_wise_difference_result_column_label_tooltip = Hovertip(
            column_wise_difference_result_column_label,
            config.get('tooltips', 'columns_wise_difference_result_column_label_pft'))
        columns_wise_difference_button_tooltip = Hovertip(column_wise_difference_button,
                                                          config.get('tooltips', 'columns_wise_difference_button'))
        row_wise_difference_label_tooltip = Hovertip(row_wise_difference_label,
                                                     config.get('tooltips', 'row_wise_difference_label_pft'))
        row_wise_difference_result_column_tooltip = Hovertip(row_wise_difference_result_column_label,
                                                             config.get('tooltips',
                                                                        'row_wise_difference_result_column_label_pft'))
        row_wise_difference_button_tooltip = Hovertip(row_wise_difference_button,
                                                      config.get('tooltips', 'row_wise_difference_button'))
        header_label_tooltip = Hovertip(header_label, config.get('tooltips', 'header_label_pft'))
        header_checkbutton_tooltip = Hovertip(keep_header_checkbutton,
                                              config.get('tooltips', 'keep_header_checkbutton_pft'))


class ConvertTraceTab(Frame):
    def __init__(self, master):
        """Creates a Convert Trace Tab"""
        ttk.Frame.__init__(self, master)

        def browse_file():
            """Opens file explorer to select a file"""
            original_tracefile_entry.delete(0, END)  # removes previously selected file
            selected_file = fd.askopenfilename(initialdir=config.get('directories', 'raw_traces_dir'),
                                               title="Select a File",
                                               filetypes=(("CSV files", "*.csv*"),))
            if not selected_file:
                mb.showinfo('No file selected', 'Please select a valid file')
            original_tracefile_entry.insert(END, selected_file)
            original_tracefile_entry.grid(row=1, column=1)
            if selected_file:
                display_file(selected_file)

        def show_tracedata_filename_entry():
            """Puts the tracedata_filename_label on the grid if the checkbox is selected"""
            if extract_tracedata_checkbutton_var.get() == 0:
                tracedata_filename_label.grid_forget()
                tracedata_filename_entry.grid_forget()
                float_format_label.grid_forget()
                float_format_entry.grid_forget()
            if extract_tracedata_checkbutton_var.get() == 1:
                tracedata_filename_label.grid(column=4, row=3)
                tracedata_filename_entry.grid(column=4, row=4)
                float_format_label.grid(column=4, row=5)
                float_format_entry.grid(column=4, row=6)

        def convert_trace():
            """Takes the user input from the entry fields and converts the selected trace to the standard format"""
            org_filename = original_tracefile_entry.get()
            write_file = 1
            result_filename = config.get('directories', 'converted_traces_dir') + \
                              '/' + result_filename_entry.get() + config.get('files', 'trace_file_suffix')
            if os.path.isfile(org_filename) and pathlib.Path(org_filename).suffix == ".csv":
                if os.path.exists(result_filename):
                    write_file = mb.askyesno("File already exists",
                                             os.path.basename(result_filename) + " already exists. \n "
                                                                                 "Would you like to overwrite it?")
                try:
                    col = list(map(int, (column_indexes_entry.get().split(";"))))
                except ValueError:
                    mb.showerror("Column indexes invalid",
                                 "Indexes need to be integers seperated by a semicolon [;]")
                    return
                if write_file:
                    model.convert_trace(original_tracefile_entry.get(),
                                        col,
                                        tracedata_description_entry.get().split(";"),
                                        description_entry.get(),
                                        source_entry.get(),
                                        username_entry.get(),
                                        additional_information_entry.get('1.0', 'end-1c').replace("\n", "").split(";"),
                                        statistics_format_entry.get(),
                                        result_filename)
                    if extract_tracedata_checkbutton_var.get() == 1:
                        tracedata_filename = config.get('directories',
                                                        'tracedata_dir') + tracedata_filename_entry.get() + \
                                             config.get('files', 'tracedata_file_suffix')
                        model.extract_tracedata(result_filename, tracedata_filename, float_format_entry.get())
                        mb.showinfo("Trace successfully converted", "Displaying converted Trace")
                        display_file(result_filename)
                else:
                    mb.showinfo("File already exists", "Displaying existing File")
                    # If tracedata checkbox is selected the data will also be extracted
                # Display the created traces
                display_file(result_filename)
            else:
                mb.showinfo('No file selected', 'Please select a valid file')

        def display_file(filename):
            """
            Displays the selected file in the convert tab
            :param filename: File that will be displayed
            """
            with open(filename, 'r') as f:
                file_displayer.config(state=NORMAL)
                file_displayer.delete("1.0", "end")
                file_displayer.insert(INSERT, f.read())
                file_displayer.config(state=DISABLED)
                file_displayer.grid(column=5, row=1, columnspan=12, rowspan=10)

        # GUI Elements
        columns_label = Label(self, text="Tracedata Column Indexes")
        columns_label.grid(row=2)
        tracedata_description_label = Label(self, text="Tracedata Description")
        tracedata_description_label.grid(row=3)
        trace_description_label = Label(self, text="Trace Description")
        trace_description_label.grid(row=4)
        source_label = Label(self, text="Trace Source")
        source_label.grid(row=5)
        username_label = Label(self, text="Username")
        username_label.grid(row=6)
        additional_information_label = Label(self, text="Additional Information")
        additional_information_label.grid(row=7)
        result_filename_label = Label(self, text="Result Filename")
        result_filename_label.grid(row=8)

        tracedata_filename_label = Label(self, text="Filename")
        tracedata_filename_entry = Entry(self)

        float_format_label = Label(self, text="Float Format String")
        float_format_entry = Entry(self,
                                   bg=config.get('entries', 'background_colour_optional_entries'))
        float_format_entry.insert(END, config.get('entries', 'default_float_format_entry_ett'))

        extract_tracedata_checkbutton_var = IntVar()
        extract_tracedata_checkbutton = Checkbutton(self,
                                                    text="Extract Tracedata after Conversion",
                                                    variable=extract_tracedata_checkbutton_var, onvalue=1,
                                                    offvalue=0, command=show_tracedata_filename_entry,
                                                    selectcolor=config.get('entries',
                                                                           'background_colour_optional_entries'))
        extract_tracedata_checkbutton.grid(column=4, row=2)

        statistics_format_label = Label(self, text="Statistic Format String")
        statistics_format_label.grid(row=12, column=0)

        statistics_format_entry = Entry(self, width=config.get('entries', 'entry_width'),
                                        bg=config.get('entries', 'background_colour_optional_entries'))
        statistics_format_entry.grid(row=12, column=1)

        original_tracefile_entry = Entry(self, width=config.get('entries', 'entry_width'))

        # Create entries and set default values
        original_tracefile_button = Button(self, text="Choose File", command=browse_file)

        column_indexes_entry = Entry(self, width=config.get('entries', 'entry_width'))
        column_indexes_entry.insert(END, config.get('entries', 'default_columns_entry_ctt'))

        source_entry = Entry(self, width=config.get('entries', 'entry_width'))
        source_entry.insert(END, config.get('entries', 'default_trace_source_entry_ctt'))

        description_entry = Entry(self, width=config.get('entries', 'entry_width'))
        description_entry.insert(END, config.get('entries', 'default_description_entry_ctt'))

        tracedata_description_entry = Entry(self, width=config.get('entries', 'entry_width'))
        tracedata_description_entry.insert(END, config.get('entries', 'default_tracedata_description_entry_ctt'))

        username_entry = Entry(self, width=config.get('entries', 'entry_width'))
        username_entry.insert(END, config.get('entries', 'default_username_entry_ctt'))

        additional_information_entry = Text(self, width=config.get('entries', 'entry_width'),
                                            height=25,
                                            font=config.get('fonts', 'default_font_text_widget'))
        additional_information_entry.insert(END, config.get('entries', 'default_additional_information_entry_ctt'))

        result_filename_entry = Entry(self, width=config.get('entries', 'entry_width'))
        result_filename_entry.insert(END, config.get('entries', 'default_filename_entry_ctt'))

        original_tracefile_button.grid(row=1, column=0)
        column_indexes_entry.grid(row=2, column=1)
        tracedata_description_entry.grid(row=3, column=1)
        description_entry.grid(row=4, column=1)
        source_entry.grid(row=5, column=1)
        username_entry.grid(row=6, column=1)
        additional_information_entry.grid(row=7, column=1)
        result_filename_entry.grid(row=8, column=1)

        # Text widget to display the converted trace
        file_displayer = scrolledtext.ScrolledText(self, width=105, height=33)

        convert_button = Button(self, text='Convert Trace', command=convert_trace)
        convert_button.grid(row=13, column=1)

        # Tooltips
        columns_label_tooltip = Hovertip(columns_label, config.get('tooltips', 'columns_label_ctt'))
        source_label_tooltip = Hovertip(source_label, config.get('tooltips', 'source_label_ctt'))
        description_label_tooltip = Hovertip(trace_description_label,
                                             config.get('tooltips', 'trace_description_label_ctt'))
        tracedata_description_label_tooltip = Hovertip(tracedata_description_label,
                                                       config.get('tooltips', 'tracedata_description_label_ctt'))
        username_label_tooltip = Hovertip(username_label, config.get('tooltips', 'username_label_ctt'))
        additional_information_label_tooltip = Hovertip(additional_information_label,
                                                        config.get('tooltips', 'additional_information_label_ctt'))
        result_filename_label_tooltip = Hovertip(result_filename_label,
                                                 config.get('tooltips', 'result_filename_label_ctt'))
        tracedata_checkbutton_tooltip = Hovertip(extract_tracedata_checkbutton,
                                                 config.get('tooltips', 'tracedata_checkbutton'))
        tracedata_filename_label_tooltip = Hovertip(tracedata_filename_label,
                                                    config.get('tooltips', 'tracedata_filename_label_ctt'))
        browse_file_button_tooltip = Hovertip(original_tracefile_button,
                                              config.get('tooltips', 'browse_file_button'))
        convert_button_tooltip = Hovertip(convert_button, config.get('tooltips', 'browse_file_button'))
        numerical_format_label_tooltip = Hovertip(statistics_format_label,
                                                  config.get('tooltips', 'statistics_format_string'))
        float_format_label_tooltip = Hovertip(float_format_label, config.get('tooltips', 'float_format_label_ett'))


class FilterTraceTab(Frame):
    def __init__(self, master):
        """Creates a Filter Trace Tab"""
        ttk.Frame.__init__(self, master)

        def browse_files():
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
                browse_button.grid(column=1, row=8)
            except json.decoder.JSONDecodeError:
                mb.showerror("Invalid Trace", "Invalid/corrupted traces were selected")

        def filter_traces(expression):
            """Evaluates the expression for the selected traces"""
            for i in filter_results_treeviw.get_children():
                filter_results_treeviw.delete(i)
            filter_results = model.filter_traces_by_expression(selected_files, expression, selected_filenames)
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
        selected_traces_label = Label(self, text="Selected Traces")
        selected_traces_label.grid(column=1, row=1)

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

        expression_label = Label(self, text="Boolean Expression")
        expression_label.grid(column=3, row=2)

        expression_entry = Entry(self, width=config.get('entries', 'entry_width'))
        expression_entry.grid(column=4, row=2)

        filter_button = Button(self, text="Filter Traces", command=lambda: filter_traces(expression_entry.get()))
        filter_button.grid(column=5, row=2)

        browse_button = Button(self, text="Choose Files", command=browse_files)
        browse_button.grid(column=1, row=2)

        # Tooltips
        selected_traces_label_tooltip = Hovertip(selected_traces_label,
                                                 config.get('tooltips', 'selected_traces_label_ftt'))
        browse_files_button_tooltip = Hovertip(browse_button, config.get('tooltips', 'browse_files_button_ftt'))
        filter_button_tooltip = Hovertip(filter_button, config.get('tooltips', 'filter_button_ftt'))
        expression_label_tooltip = Hovertip(expression_label, config.get('tooltips', 'expression_label_ftt'))


class ExtractTracedataTab(Frame):
    def __init__(self, master):
        """Creates a Extract Tracedata Tab"""
        ttk.Frame.__init__(self, master)

        def browse_file():
            """Opens file explorer to select a file"""
            input_trace_entry.delete(0, END)
            selected_trace = fd.askopenfilename(initialdir=config.get('directories', 'converted_traces_dir'),
                                                title="Select a File",
                                                filetypes=(("JSON files", "*.json*"),))
            if not selected_trace:
                mb.showinfo('No file selected', 'Please select a valid file')
            input_trace_entry.insert(END, selected_trace)
            input_trace_entry.grid(row=0, column=1)
            display_file(selected_trace)

        def display_file(filename):
            """
            Displays the selected file in the extract tracedata tab
            :param filename: File that will be displayed
            """
            with open(filename, 'r') as f:
                trace_column_display.config(state=NORMAL)
                trace_column_display.delete("1.0", "end")
                trace_column_display.insert(INSERT, f.read())
                trace_column_display.config(state=DISABLED)
                trace_column_display.grid(column=0, row=6, columnspan=4)

        def extract_tracedata():
            """Extracts the tracedata so it can be used in ProFiDo"""
            org_filename = input_trace_entry.get()
            if os.path.isfile(org_filename) and pathlib.Path(org_filename).suffix == ".json":
                try:
                    filename = config.get('directories', 'tracedata_dir') + tracedata_filename_entry.get() + \
                               config.get('files', 'tracedata_file_suffix')
                    model.extract_tracedata(input_trace_entry.get(), filename, float_format_entry.get())
                    display_file(filename)
                    mb.showinfo("Data extracted", "Displaying extracted columns")
                except json.decoder.JSONDecodeError:
                    mb.showerror('Invalid Trace', 'The selected file is not a valid Trace')
            else:
                mb.showinfo('No file selected', 'Please select a valid file')

        # GUI Elements
        converted_trace_label = Label(self, text="Trace")
        converted_trace_label.grid(row=0)
        tracedata_filename_label = Label(self, text="Tracedata Filename")
        tracedata_filename_label.grid(row=1, column=0)
        float_format_label = Label(self, text="Float Format String")
        float_format_label.grid(row=2, column=0)
        float_format_entry = Entry(self, width=config.get('entries', 'entry_width'),
                                   bg=config.get('entries', 'background_colour_optional_entries'))
        float_format_entry.grid(row=2, column=1)
        float_format_entry.insert(END, config.get('entries', 'default_float_format_entry_ett'))
        input_trace_entry = Entry(self, width=config.get('entries', 'entry_width'))

        trace_column_display = scrolledtext.ScrolledText(self, width=120, height=33)

        choose_trace_button = Button(self, text="Choose File", command=browse_file)
        choose_trace_button.grid(row=0, column=0)

        tracedata_filename_entry = Entry(self, width=config.get('entries', 'entry_width'))
        tracedata_filename_entry.grid(row=1, column=1)

        extract_columns_button = Button(self, text="Extract Tracedata", command=extract_tracedata)
        extract_columns_button.grid(row=2, column=2)

        # Tooltips
        converted_trace_label_tooltip = Hovertip(converted_trace_label,
                                                 config.get('tooltips', 'converted_trace_label_ett'))
        tracedata_filename_entry_tooltip = Hovertip(tracedata_filename_label,
                                                    config.get('tooltips', 'tracedata_filename_label_ett'))
        browse_trace_button_tooltip = Hovertip(choose_trace_button, config.get('tooltips', 'browse_trace_button_ett'))
        extract_button_tooltip = Hovertip(extract_columns_button,
                                          config.get('tooltips', 'extract_tracedata_button_ett'))
        float_format_label_tooltip = Hovertip(float_format_label, config.get('tooltips', 'float_format_label_ett'))


class ValidateTraceTab(Frame):
    def __init__(self, master):
        """Creates a Validate Trace Tab"""
        ttk.Frame.__init__(self, master)

        def browse_file():
            """Opens file explorer to select a file"""
            file_entry.delete(0, END)
            selected_trace = fd.askopenfilename(initialdir=config.get('directories', 'converted_traces_dir'),
                                                title="Select a File",
                                                filetypes=(("JSON files", "*.json*"),))
            if not selected_trace:
                mb.showinfo('No file selected', 'Please select a valid file')
            file_entry.insert(END, selected_trace)
            file_entry.grid(row=0, column=0)

        # GUI Elements
        file_entry = Entry(self, width=config.get('entries', 'entry_width'))

        relative_tolerance_label = Label(self, text="Relative Tolerance")
        relative_tolerance_label.grid(column=1, row=2)

        relative_tolerance_entry = Entry(self, width=config.get('entries', 'entry_width'))
        relative_tolerance_entry.grid(column=2, row=2)

        browse_file_button = Button(self, text="Choose File", command=browse_file)
        browse_file_button.grid(row=1, column=0)

        validate_statistics_button = Button(self, text="Validate Statistics", command=lambda:
                                            model.verify_statistics(file_entry.get(), relative_tolerance_entry.get()))
        validate_statistics_button.grid(row=2, column=0)

        validate_hash_button = Button(self, text="Validate Hash", command=lambda: model.hash_check(file_entry.get()))
        validate_hash_button.grid(row=3, column=0)

        restore_traceheader_button = Button(self, text="Restore Traceheader", command=lambda: model.restore_traceheader(
                                                file_entry.get(), statistics_format_string_entry.get()))
        restore_traceheader_button.grid(row=4, column=0)

        statistics_format_string_label = Label(self, text="Statistics Format String")
        statistics_format_string_label.grid(column=1, row=4)

        statistics_format_string_entry = Entry(self, width=config.get('entries', 'entry_width'),
                                               bg=config.get('entries', 'background_colour_optional_entries'))
        statistics_format_string_entry.grid(column=2, row=4)

        # Tooltips
        browse_file_button_tooltip = Hovertip(browse_file_button, config.get('tooltips', 'browse_file_button_vtt'))
        validate_statistics_button_tooltip = Hovertip(validate_statistics_button,
                                                      config.get('tooltips', 'validate_statistics_button_vtt'))
        relative_tolerance_tooltip = Hovertip(relative_tolerance_label,
                                              config.get('tooltips', 'relative_tolerance_vtt'))
        validate_hash_button_tooltip = Hovertip(validate_hash_button,
                                                config.get('tooltips', 'validate_hash_button_vtt'))
        restore_traceheader_button_tooltip = Hovertip(restore_traceheader_button,
                                                      config.get('tooltips', 'restore_traceheader_button_vtt'))
        numerical_format_tooltip = Hovertip(statistics_format_string_label,
                                            config.get('tooltips', 'statistics_format_string'))


# Create TCGUI instance and run mainloop
if __name__ == "__main__":
    root = Tk()
    converting_tool_gui = TraceConvertingToolGUI(root)
    root.mainloop()
    sys.exit()
