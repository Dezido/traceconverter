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

        prepare_file_tab = ttk.Frame(tab_parent)
        convert_trace_tab = ttk.Frame(tab_parent)
        filter_traces_tab = ttk.Frame(tab_parent)
        extract_tracedata_tab = ttk.Frame(tab_parent)
        validate_trace_tab = ttk.Frame(tab_parent)

        # Add tabs to master
        tab_parent.add(prepare_file_tab, text="Prepare File")
        tab_parent.add(convert_trace_tab, text="Convert Trace")
        tab_parent.add(filter_traces_tab, text="Filter Traces")
        tab_parent.add(extract_tracedata_tab, text="Extract Tracedata for Usage in ProFiDo")
        tab_parent.add(validate_trace_tab, text="Validate Trace")
        tab_parent.pack(expand=1, fill='both')

        # Prepare File Tab
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

        file_entry_pft = Entry(prepare_file_tab, width=config.get('entries', 'entry_width'))

        browse_file_button_pft = Button(prepare_file_tab, text="Choose File", command=browse_file_pft)
        browse_file_button_pft.grid(column=1, row=0)

        remove_rows_label_pft = Label(prepare_file_tab, text="Amount of Rows")
        remove_rows_label_pft.grid(column=0, row=2)

        remove_rows_entry_pft = Entry(prepare_file_tab, width=config.get('entries', 'entry_width'))
        remove_rows_entry_pft.grid(column=1, row=2)

        remove_rows_button_pft = Button(prepare_file_tab, text="Remove Rows",
                                        command=lambda: [model.remove_lines_from_csv(file_entry_pft.get(),
                                                                                     remove_rows_entry_pft.get()),
                                                         display_file_pft(file_entry_pft.get())])
        remove_rows_button_pft.grid(column=2, row=2)

        add_header_label_pft = Label(prepare_file_tab, text="Header")
        add_header_label_pft.grid(column=0, row=3)

        add_header_entry_pft = Entry(prepare_file_tab, width=config.get('entries', 'entry_width'))
        add_header_entry_pft.grid(column=1, row=3)

        add_header_button_pft = Button(prepare_file_tab, text="Add Header to CSV",
                                       command=lambda: [model.add_header_to_csv(file_entry_pft.get(),
                                                                                list(
                                                                                    add_header_entry_pft.get().split(
                                                                                        ","))),
                                                        display_file_pft(file_entry_pft.get())])
        add_header_button_pft.grid(column=2, row=3)

        file_displayer_label_pft = Label(prepare_file_tab)
        file_displayer_label_pft.grid(column=0, row=8)
        file_displayer_pft = scrolledtext.ScrolledText(prepare_file_tab, width=200, height=33)

        date_format_label_pft = Label(prepare_file_tab, text="Timestamp Format Strings")
        date_format_label_pft.grid(column=2, row=4)
        date_format_entry_pft = Entry(prepare_file_tab, width=config.get('entries', 'entry_width'))
        date_format_entry_pft.grid(column=3, row=4)
        date_format_entry_pft.insert(END, config.get('entries', 'default_date_format_entry_pft'))

        date_columns_label_pft = Label(prepare_file_tab, text="Column Indexes")
        date_columns_label_pft.grid(column=0, row=4)
        date_columns_entry_pft = Entry(prepare_file_tab, width=config.get('entries', 'entry_width'))
        date_columns_entry_pft.grid(column=1, row=4)

        column_wise_difference_label_pft = Label(prepare_file_tab, text="Column Indexes")
        column_wise_difference_label_pft.grid(column=0, row=5)
        column_wise_difference_entry_pft = Entry(prepare_file_tab, width=config.get('entries', 'entry_width'))
        column_wise_difference_entry_pft.grid(column=1, row=5)

        column_wise_difference_result_column_label_pft = Label(prepare_file_tab, text="Result Column Name")
        column_wise_difference_result_column_label_pft.grid(column=2, row=5)
        column_wise_difference_result_column_entry_pft = Entry(prepare_file_tab,
                                                               width=config.get('entries', 'entry_width'))
        column_wise_difference_result_column_entry_pft.grid(column=3, row=5)

        row_wise_difference_label_pft = Label(prepare_file_tab, text="Column Index")
        row_wise_difference_label_pft.grid(column=0, row=6)
        row_wise_difference_entry_pft = Entry(prepare_file_tab, width=config.get('entries', 'entry_width'))
        row_wise_difference_entry_pft.grid(column=1, row=6)

        row_wise_difference_result_column_label_pft = Label(prepare_file_tab, text="Result Column Name")
        row_wise_difference_result_column_label_pft.grid(column=2, row=6)
        row_wise_difference_result_column_entry_pft = Entry(prepare_file_tab,
                                                            width=config.get('entries', 'entry_width'))
        row_wise_difference_result_column_entry_pft.grid(column=3, row=6)

        calculate_timestamp_button_pft = Button(prepare_file_tab, text="Calculate Unix Time",
                                                command=lambda: calculate_timestamp_pft(
                                                    file_entry_pft.get(),
                                                    date_columns_entry_pft.get(),
                                                    date_format_entry_pft.get()))
        calculate_timestamp_button_pft.grid(column=4, row=4)

        column_wise_difference_button_pft = Button(prepare_file_tab, text="Calculate column-wise Difference",
                                                   command=lambda: calculate_difference_columns_pft(
                                                       file_entry_pft.get(),
                                                       column_wise_difference_entry_pft.get()))
        column_wise_difference_button_pft.grid(column=4, row=5)

        row_wise_difference_button_pft = Button(prepare_file_tab, text="Calculate row-wise Difference",
                                                command=lambda: calculate_difference_rows_pft(
                                                    file_entry_pft.get()))
        row_wise_difference_button_pft.grid(column=4, row=6)

        delimiter_label_pft = Label(prepare_file_tab, text="Delimiter")
        delimiter_label_pft.grid(column=0, row=7)
        delimiter_entry_pft = Entry(prepare_file_tab, width=config.get('entries', 'entry_width'))
        delimiter_entry_pft.grid(column=1, row=7)
        header_label_pft = Label(prepare_file_tab, text="Header")
        header_label_pft.grid(column=2, row=7)
        header_entry_pft = Entry(prepare_file_tab, width=config.get('entries', 'entry_width'))
        header_entry_pft.grid(column=3, row=7)

        keep_header_checkbutton_var_pft = IntVar()
        keep_header_checkbutton_pft = Checkbutton(prepare_file_tab, text="Use first Line as Header",
                                                  variable=keep_header_checkbutton_var_pft, onvalue=1,
                                                  offvalue=0)
        keep_header_checkbutton_pft.grid(column=5, row=7)

        transform_filetype_button_pft = Button(prepare_file_tab,
                                               text="Convert to CSV",
                                               command=lambda:
                                               convert_file_to_csv_pft(file_entry_pft.get(),
                                                                       delimiter_entry_pft.get()))
        transform_filetype_button_pft.grid(column=4, row=7)

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
            try:
                if keep_header_checkbutton_var_pft.get() == 1:
                    df = pd.read_csv(filename, header=0, sep=delimiter)
                else:
                    df = pd.read_csv(filename, header=None, sep=delimiter)
                result_filename = filename.split('.')[0] + '.csv'
                dont_overwrite = 0
            except ValueError:
                mb.showerror("Error while reading file", "Please check if the file and the delimiter are valid")
            if os.path.exists(result_filename):
                dont_overwrite = not mb.askyesno("File already exists", result_filename +
                                                 " already exists. \n Would you like to overwrite it?")
            try:
                if not dont_overwrite:
                    if header_entry_pft.get() == "":
                        df.to_csv(result_filename, index=False, sep=',')
                    else:
                        df.to_csv(result_filename, index=False, sep=',', header=header_entry_pft.get().split(','))
                    mb.showinfo('File successfully converted', 'Displaying file')
                    display_file_pft(result_filename)
                    file_entry_pft.delete(0, END)
                    file_entry_pft.insert(END, result_filename)
            except ValueError:
                mb.showerror("Error while converting file", "Please check if the file and the header are valid")

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

        # Converting Tab
        columns_label_ctt = Label(convert_trace_tab, text="Column Indexes for Tracedata")
        columns_label_ctt.grid(row=2)
        source_label_ctt = Label(convert_trace_tab, text="Tracesource")
        source_label_ctt.grid(row=3)
        tracedescription_label_ctt = Label(convert_trace_tab, text="Tracedescription")
        tracedescription_label_ctt.grid(row=4)
        tracedatadescription_label_ctt = Label(convert_trace_tab, text="Tracedatadescription")
        tracedatadescription_label_ctt.grid(row=5)
        username_label_ctt = Label(convert_trace_tab, text="Username")
        username_label_ctt.grid(row=6)
        additional_information_label_ctt = Label(convert_trace_tab, text="Additional Information")
        additional_information_label_ctt.grid(row=7)
        result_filename_label_ctt = Label(convert_trace_tab, text="Result Filename")
        result_filename_label_ctt.grid(row=8)

        tracedata_filename_label_ctt = Label(convert_trace_tab, text="Filename")
        tracedata_filename_entry_ctt = Entry(convert_trace_tab)

        float_format_label_ctt = Label(convert_trace_tab, text="Float Format String")
        float_format_entry_ctt = Entry(convert_trace_tab)
        float_format_entry_ctt.insert(END, config.get('entries', 'default_float_format_entry_ett'))

        def show_name_entry():
            """Puts the tracedata_filename_label on the grid if the checkbox is selected"""
            if extract_tracedata_checkbutton_var_ctt.get() == 0:
                tracedata_filename_label_ctt.grid_forget()
                tracedata_filename_entry_ctt.grid_forget()
            if extract_tracedata_checkbutton_var_ctt.get() == 1:
                tracedata_filename_label_ctt.grid(column=4, row=3)
                tracedata_filename_entry_ctt.grid(column=4, row=4)
                float_format_label_ctt.grid(column=4, row=5)
                float_format_entry_ctt.grid(column=4, row=6)

        extract_tracedata_checkbutton_var_ctt = IntVar()
        extract_tracedata_checkbutton_ctt = Checkbutton(convert_trace_tab,
                                                        text="Extract Tracedata for Usage in ProFiDo after Conversion",
                                                        variable=extract_tracedata_checkbutton_var_ctt, onvalue=1,
                                                        offvalue=0, command=show_name_entry)
        extract_tracedata_checkbutton_ctt.grid(column=4, row=2)

        statistics_format_label_ctt = Label(convert_trace_tab, text="Statistics Format String")
        statistics_format_label_ctt.grid(row=12, column=0)

        statistics_format_entry_ctt = Entry(convert_trace_tab, width=config.get('entries', 'entry_width'))
        statistics_format_entry_ctt.grid(row=12, column=1)

        original_tracefile_entry_ctt = Entry(convert_trace_tab, width=config.get('entries', 'entry_width'))

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

        # Create entries and set default values
        original_tracefile_button_ctt = Button(convert_trace_tab, text="Choose File", command=browse_file_ctt)

        columns_entry_ctt = Entry(convert_trace_tab, width=config.get('entries', 'entry_width'))
        columns_entry_ctt.insert(END, config.get('entries', 'default_columns_entry'))

        source_entry_ctt = Entry(convert_trace_tab, width=config.get('entries', 'entry_width'))
        source_entry_ctt.insert(END, config.get('entries', 'default_source_entry'))

        description_entry_ctt = Entry(convert_trace_tab, width=config.get('entries', 'entry_width'))
        description_entry_ctt.insert(END, config.get('entries', 'default_description_entry'))

        tracedatadescription_entry_ctt = Entry(convert_trace_tab, width=config.get('entries', 'entry_width'))
        tracedatadescription_entry_ctt.insert(END, config.get('entries', 'default_tracedatadescription_entry'))

        username_entry_ctt = Entry(convert_trace_tab, width=config.get('entries', 'entry_width'))
        username_entry_ctt.insert(END, config.get('entries', 'default_username_entry'))

        additional_information_entry_ctt = Text(convert_trace_tab, width=config.get('entries', 'entry_width'),
                                                height=25,
                                                font=config.get('fonts', 'default_font_text_widget'))
        additional_information_entry_ctt.insert(END, config.get('entries', 'default_additional_information_entry'))

        result_filename_entry_ctt = Entry(convert_trace_tab, width=config.get('entries', 'entry_width'))
        result_filename_entry_ctt.insert(END, config.get('entries', 'default_filename_entry'))

        # Place Entries
        original_tracefile_button_ctt.grid(row=1, column=0)
        columns_entry_ctt.grid(row=2, column=1)
        source_entry_ctt.grid(row=3, column=1)
        description_entry_ctt.grid(row=4, column=1)
        tracedatadescription_entry_ctt.grid(row=5, column=1)
        username_entry_ctt.grid(row=6, column=1)
        additional_information_entry_ctt.grid(row=7, column=1)
        result_filename_entry_ctt.grid(row=8, column=1)

        # Text widget to display the converted trace
        file_displayer_ctt = scrolledtext.ScrolledText(convert_trace_tab, width=100, height=33)

        def convert_trace():
            """Takes the user input from the entry fields and converts the selected trace to the standard format"""
            org_filename = original_tracefile_entry_ctt.get()
            if os.path.isfile(org_filename) and pathlib.Path(org_filename).suffix == ".csv":
                try:
                    col = list(map(int, (columns_entry_ctt.get().split(";"))))
                except ValueError:
                    mb.showerror("Columns to keep entry invalid",
                                 "Columns need to be integers seperated by a semicolon [;]")
                trace_template["tracebody"]["tracedata"] = \
                    model.get_tracedata_from_file(original_tracefile_entry_ctt.get(), col)
                amount_tracedata = len(trace_template["tracebody"]["tracedata"][0])
                trace_template["tracebody"]["tracedatadescription"] = tracedatadescription_entry_ctt.get().split(";")
                trace_template["traceheader"]["metainformation"]["name"] = os.path.basename(
                    original_tracefile_entry_ctt.get())
                trace_template["traceheader"]["metainformation"]["source"] = source_entry_ctt.get()
                trace_template["traceheader"]["metainformation"]["description"] = description_entry_ctt.get()
                trace_template["traceheader"]["metainformation"]["creation timestamp"] = str(datetime.datetime.now())
                trace_template["traceheader"]["metainformation"]["user"] = username_entry_ctt.get()
                if len(additional_information_entry_ctt.get('1.0', 'end-1c')) != 0:
                    trace_template["traceheader"]["metainformation"]["additional information"] = \
                        additional_information_entry_ctt.get('1.0', 'end-1c').replace("\n", "").split(";")
                else:
                    trace_template["traceheader"]["metainformation"].pop("additional information", None)

                #  Generate statistics and adds them into a list. Each list entry represents one column of the raw trace
                if amount_tracedata > 4:
                    trace = generate_statistic(trace_template, statistics_format_entry_ctt.get())
                else:
                    trace = trace_template
                    mb.showinfo("Statistics won't be computed", "Tracedata only contains " + str(amount_tracedata) +
                                " elements per column. Computing statistics requires five or more.")
                # Save trace to file
                filename = config.get('directories', 'converted_traces_dir') + '/' + result_filename_entry_ctt.get() + \
                           config.get('files', 'trace_file_suffix')
                dont_overwrite = 0
                if os.path.exists(filename):
                    dont_overwrite = not mb.askyesno("File already exists",
                                                     os.path.basename(filename) + " already exists. \n "
                                                                                  "Would you like to overwrite it?")
                if not dont_overwrite:
                    with open(filename, 'w') as fp:
                        json.dump(trace, fp, indent=4)
                    add_hash_value_to_trace(filename)
                    # If tracedata checkbox is selected the data will also be extracted
                    if extract_tracedata_checkbutton_var_ctt.get() == 1:
                        extract_tracedata_after_conversion(
                            filename)
                    mb.showinfo("Trace successfully converted", "Displaying converted Trace")
                else:
                    mb.showinfo("File already exists", "Displaying existing File")
                # Display the created traces
                display_file_ctt(filename)
            else:
                mb.showinfo('No file selected', 'Please select a valid file')

        def generate_statistic(trace, formatstring):
            """
            Computes the statistics for the trace
            :param trace: Tracefile to compute from and add the statistics to
            :param formatstring: For formatting the computed values
            """
            # Clear statistic lists so the next trace won't have old values
            trace["traceheader"]["statistical characteristics"]["mean"] = []
            trace["traceheader"]["statistical characteristics"]["median"] = []
            trace["traceheader"]["statistical characteristics"]["skew"] = []
            trace["traceheader"]["statistical characteristics"]["kurtosis"] = []
            trace["traceheader"]["statistical characteristics"]["autocorrelation"] = []
            trace["traceheader"]["statistical characteristics"]["variance"] = []
            # formatstring = '{' + formatstring + '}'
            try:
                for i in range(len(trace["tracebody"]["tracedata"])):
                    df = pd.DataFrame(trace["tracebody"]["tracedata"][i])
                    trace["traceheader"]["statistical characteristics"]["mean"].append(
                        format(df[0].mean(), formatstring))
                    trace["traceheader"]["statistical characteristics"]["median"].append(
                        format(df[0].median(), formatstring))
                    trace["traceheader"]["statistical characteristics"]["skew"].append(
                        format(df[0].skew(), formatstring))
                    trace["traceheader"]["statistical characteristics"]["kurtosis"].append(
                        format(df[0].kurtosis(), formatstring))
                    trace["traceheader"]["statistical characteristics"]["autocorrelation"].append(
                        format(df[0].autocorr(), formatstring))
                    trace["traceheader"]["statistical characteristics"]["variance"].append(
                        format(df[0].var(), formatstring))
                return trace
            except TypeError:
                mb.showerror("Type Error", "One of the selected columns does not contain valid data")
                raise
            except (KeyError, IndexError):
                mb.showerror("Format Error", "Invalid Numerical Format entered")
                raise

        def add_hash_value_to_trace(filename):
            """
            Adds hash value to metainformation
            :param filename: File the hash will be computed for
            """
            with open(filename) as tr:
                tracedata = json.load(tr)
                tracedata["traceheader"]["metainformation"]["hash value"] = model.hash_from_trace(filename)
            with open(filename, 'w') as fp:
                json.dump(tracedata, fp, indent=4)

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

        def extract_tracedata_after_conversion(filename):
            """
            Extracts tracedata from the file can be used for ProFiDo
            :param filename: Name of the converted tracefile
            """
            with open(filename) as tr:
                tracedata = json.load(tr)["tracebody"]["tracedata"]
                df = pd.DataFrame(tracedata)
                dont_overwrite = 0
                result_filename = config.get('directories', 'profido_traces_dir') + tracedata_filename_entry_ctt.get() + \
                                  config.get('files', 'tracedata_file_suffix')
                if os.path.exists(result_filename):
                    dont_overwrite = not mb.askyesno("File already exists",
                                                     os.path.basename(result_filename) +
                                                     " already exists. "
                                                     "\n Would you like to overwrite it?")
                if not dont_overwrite:
                    try:
                        if len(float_format_entry_ctt.get()) > 0:
                            df.transpose().to_csv(result_filename,
                                                  sep='\t',
                                                  float_format=float_format_entry_ctt.get(),
                                                  index=False, header=False)
                        if len(float_format_entry_ctt.get()) == 0:
                            df.transpose().to_csv(result_filename,
                                                  sep='\t',
                                                  index=False, header=False)
                    except TypeError:
                        mb.showerror('Invalid float format string', 'Please enter a valid format string')
                    except ValueError:
                        mb.showerror('Invalid float format string', 'Please enter a valid format string')

        convert_button_ctt = Button(convert_trace_tab, text='Convert Trace', command=convert_trace)
        convert_button_ctt.grid(row=13, column=1)

        # Tooltips
        columns_label_tooltip_ctt = Hovertip(columns_label_ctt, config.get('tooltips', 'columns_label_ctt'))
        source_label_tooltip_ctt = Hovertip(source_label_ctt, config.get('tooltips', 'source_label_ctt'))
        description_label_tooltip_ctt = Hovertip(tracedescription_label_ctt, config.get('tooltips', 'tracedescription_label_ctt'))
        tracedatadescription_label_tooltip_ctt = Hovertip(tracedatadescription_label_ctt,
                                                          config.get('tooltips', 'tracedatadescription_label_ctt'))
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

        # Filter Tab
        selected_traces_label_ftt = Label(filter_traces_tab, text="Selected Traces")
        selected_traces_label_ftt.grid(column=1, row=1)

        selected_traces_lb = Listbox(filter_traces_tab, width=config.get('listbox', 'listbox_width'),
                                     height=config.get('listbox', 'listbox_height'))

        treeview_columns = ['name', 'mean', 'median', 'skew', 'kurtosis', 'autocorrelation', 'variance']
        filter_results_tv = ttk.Treeview(filter_traces_tab, columns=treeview_columns, show='headings',
                                         height=config.get('treeview', 'filter_treeview_height'))
        vsb_filter_results_tv = ttk.Scrollbar(filter_traces_tab, orient="vertical", command=filter_results_tv.yview)
        filter_results_tv.configure(yscrollcommand=vsb_filter_results_tv.set)
        filter_results_tv.heading('name', text='Name')
        filter_results_tv.column('name', width=300)
        filter_results_tv.heading('mean', text='Mean')
        filter_results_tv.heading('median', text='Median')
        filter_results_tv.heading('skew', text='Skew')
        filter_results_tv.heading('kurtosis', text='Kurtosis')
        filter_results_tv.heading('autocorrelation', text='Autocorrelation')
        filter_results_tv.heading('variance', text='Variance')

        selected_filenames = []
        selected_files = []
        filter_result = []

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
            filter_result.clear()
            for i in filter_results_tv.get_children():
                filter_results_tv.delete(i)
            for i in range(len(selected_files)):
                mean_list = selected_files[i]["mean"]
                median_list = selected_files[i]["median"]
                skew_list = selected_files[i]["skew"]
                kurtosis_list = selected_files[i]["kurtosis"]
                autocorrelation_list = selected_files[i]["autocorrelation"]
                variance_list = selected_files[i]["variance"]
                for j in range(len(selected_files[i]["mean"])):
                    mean = float(mean_list[j])
                    median = float(median_list[j])
                    skew = float(skew_list[j])
                    kurtosis = float(kurtosis_list[j])
                    autocorrelation = float(autocorrelation_list[j])
                    variance = float(variance_list[j])
                    try:
                        if eval(expression):
                            trace = [os.path.basename(selected_filenames[i]),
                                     mean,
                                     median,
                                     skew,
                                     kurtosis,
                                     autocorrelation,
                                     variance
                                     ]
                            filter_result.append(trace)
                    except (NameError, SyntaxError):
                        mb.showerror("Expression invalid", "Please enter a valid expression")
                        raise
            for i in range(len(filter_result)):
                filter_results_tv.insert('', 'end', values=(filter_result[i][0],
                                                            filter_result[i][1],
                                                            filter_result[i][2],
                                                            filter_result[i][3],
                                                            filter_result[i][4],
                                                            filter_result[i][5],
                                                            filter_result[i][6]))
            Label(filter_traces_tab, text="Results").grid(column=1, row=10)
            filter_results_tv.grid(column=1, row=11, columnspan=10)
            vsb_filter_results_tv.grid(column=11, row=11, sticky=N + S)

        expression_label_ftt = Label(filter_traces_tab, text="Boolean Expression")
        expression_label_ftt.grid(column=3, row=2)

        expression_entry_ftt = Entry(filter_traces_tab, width=config.get('entries', 'entry_width'))
        expression_entry_ftt.grid(column=4, row=2)

        # Label and Buttons
        filter_button_ftt = Button(filter_traces_tab, text="Filter Traces",
                                   command=lambda: filter_traces_ftt(expression_entry_ftt.get()))
        filter_button_ftt.grid(column=5, row=2)

        browse_button_ftt = Button(filter_traces_tab, text="Choose Files", command=browse_files_ftt)
        browse_button_ftt.grid(column=1, row=2)

        # Tooltips
        selected_traces_label_tooltip_ftt = Hovertip(selected_traces_label_ftt,
                                                     config.get('tooltips', 'selected_traces_label_ftt'))
        browse_files_button_tooltip_ftt = Hovertip(browse_button_ftt, config.get('tooltips', 'browse_files_button_ftt'))
        filter_button_tooltip_ftt = Hovertip(filter_button_ftt, config.get('tooltips', 'filter_button_ftt'))
        expression_label_tooltip_ftt = Hovertip(expression_label_ftt, config.get('tooltips', 'expression_label_ftt'))

        # Extract tracedata Tab
        converted_trace_label_ett = Label(extract_tracedata_tab, text="Trace")
        converted_trace_label_ett.grid(row=0)
        tracedata_filename_label_ett = Label(extract_tracedata_tab, text="Result Filename")
        tracedata_filename_label_ett.grid(row=1, column=0)
        float_format_label_ett = Label(extract_tracedata_tab, text="Float Format String")
        float_format_label_ett.grid(row=2, column=0)
        float_format_entry_ett = Entry(extract_tracedata_tab, width=config.get('entries', 'entry_width'))
        float_format_entry_ett.grid(row=2, column=1)
        float_format_entry_ett.insert(END, config.get('entries', 'default_float_format_entry_ett'))
        input_trace_entry_ett = Entry(extract_tracedata_tab, width=config.get('entries', 'entry_width'))

        trace_column_display_ett = scrolledtext.ScrolledText(extract_tracedata_tab, width=100, height=33)

        def browse_file_ett():
            """Opens file explorer to select a file"""
            input_trace_entry_ett.delete(0, END)
            selected_trace = fd.askopenfilename(initialdir=config.get('directories', 'converted_traces_dir'),
                                                title="Select a File",
                                                filetypes=(("JSON files", "*.json*"),))
            if not selected_trace:
                mb.showinfo('No file selected', 'Please select a valid file')
            input_trace_entry_ett.insert(END, selected_trace)
            input_trace_entry_ett.grid(row=0, column=1)
            display_file_ett(selected_trace)

        def display_file_ett(filename):
            """
            Displays the selected file in the extract tracedata tab
            :param filename: File that will be displayed
            """
            with open(filename, 'r') as f:
                trace_column_display_ett.config(state=NORMAL)
                trace_column_display_ett.delete("1.0", "end")
                trace_column_display_ett.insert(INSERT, f.read())
                trace_column_display_ett.config(state=DISABLED)
                trace_column_display_ett.grid(column=0, row=6, columnspan=4)

        def extract_tracedata_ett():
            """Extracts the tracedata so it can be used in ProFiDo"""
            org_filename = input_trace_entry_ett.get()
            if os.path.isfile(org_filename) and pathlib.Path(org_filename).suffix == ".json":
                try:
                    with open(input_trace_entry_ett.get()) as trace_in:
                        tracedata = json.load(trace_in)["tracebody"]["tracedata"]
                        df = pd.DataFrame(tracedata)
                        filename = config.get('directories', 'profido_traces_dir') \
                                   + tracedata_filename_entry_ett.get() + '_dat.trace'
                        dont_overwrite = 0
                        if os.path.exists(filename):
                            dont_overwrite = not mb.askyesno("File already exists", os.path.basename(filename) +
                                                             " already exists. \n Would you like to overwrite it?")
                        if not dont_overwrite:
                            df = df.transpose().dropna()
                            try:
                                if len(float_format_entry_ett.get()) > 0:
                                    df.to_csv(filename, sep='\t', float_format=float_format_entry_ett.get(),
                                              index=False, header=False)
                                if len(float_format_entry_ett.get()) == 0:
                                    df.to_csv(filename, sep='\t', index=False, header=False)
                            except TypeError:
                                mb.showerror('Invalid float format string', 'Please enter a valid format string')
                            except ValueError:
                                mb.showerror('Invalid float format string', 'Please enter a valid format string')
                        display_file_ett(filename)
                        mb.showinfo("Data extracted", "Displaying extracted columns")
                except json.decoder.JSONDecodeError:
                    mb.showerror('Invalid Trace', 'The selected file is not a valid Trace')

            else:
                mb.showinfo('No file selected', 'Please select a valid file')

        choose_trace_button_ett = Button(extract_tracedata_tab, text="Choose File", command=browse_file_ett)
        choose_trace_button_ett.grid(row=0, column=0)

        tracedata_filename_entry_ett = Entry(extract_tracedata_tab, width=config.get('entries', 'entry_width'))
        tracedata_filename_entry_ett.grid(row=1, column=1)

        extract_columns_button_ett = Button(extract_tracedata_tab, text="Extract Tracedata for Usage in ProFiDo",
                                            command=extract_tracedata_ett)
        extract_columns_button_ett.grid(row=2, column=2)

        # Tooltips
        converted_trace_label_tooltip_ett = Hovertip(converted_trace_label_ett,
                                                     config.get('tooltips', 'converted_trace_label_ett'))
        tracedata_filename_entry_tooltip_ett = Hovertip(tracedata_filename_label_ett,
                                                        config.get('tooltips', 'tracedata_filename_label_ett'))
        browse_trace_button_tooltip_ett = Hovertip(choose_trace_button_ett,
                                                   config.get('tooltips', 'browse_trace_button_ett'))
        extract_button_tooltip_ett = Hovertip(extract_columns_button_ett,
                                              config.get('tooltips', 'extract_tracedata_button_ett'))
        float_format_label_tooltip_ett = Hovertip(float_format_label_ett,
                                                  config.get('tooltips', 'float_format_label_ett'))

        # Validation tab

        def browse_file_vtt():
            """Opens file explorer to select a file"""
            file_entry_vtt.delete(0, END)
            selected_trace = fd.askopenfilename(initialdir=config.get('directories', 'converted_traces_dir'),
                                                title="Select a File",
                                                filetypes=(("JSON files", "*.json*"),))
            if not selected_trace:
                mb.showinfo('No file selected', 'Please select a valid file')
            file_entry_vtt.insert(END, selected_trace)
            file_entry_vtt.grid(row=0, column=0)

        def restore_traceheader(filename):
            """
            (Re)generates statistics and hash for the input trace
            :param filename: Input file
            """
            if os.path.isfile(filename) and pathlib.Path(filename).suffix == ".json":
                try:
                    with open(filename) as tr:
                        tracedata = json.load(tr)
                        trace = generate_statistic(tracedata, statistics_format_string_entry_vtt.get())
                    dont_overwrite = 0
                    if os.path.exists(filename):
                        dont_overwrite = not mb.askyesno("Overwriting File",
                                                         "Restoring the traceheader will overwrite the file. Continue?")
                    if not dont_overwrite:
                        with open(filename, 'w') as fp:
                            json.dump(trace, fp, indent=4)
                    add_hash_value_to_trace(filename)
                except json.decoder.JSONDecodeError:
                    mb.showerror("Trace content invalid", "Please check if the trace content is valid")
            else:
                mb.showerror("Trace invalid", "Please check if the file is valid")

        file_entry_vtt = Entry(validate_trace_tab, width=config.get('entries', 'entry_width'))

        relative_tolerance_label_vtt = Label(validate_trace_tab, text="Relative Tolerance")
        relative_tolerance_label_vtt.grid(column=1, row=2)

        relative_tolerance_entry_vtt = Entry(validate_trace_tab, width=config.get('entries', 'entry_width'))
        relative_tolerance_entry_vtt.grid(column=2, row=2)

        browse_file_button_vtt = Button(validate_trace_tab, text="Choose File", command=browse_file_vtt)
        browse_file_button_vtt.grid(row=1, column=0)

        validate_statistics_button_vtt = Button(validate_trace_tab, text="Validate Statistics",
                                                command=lambda: model.verify_statistics(file_entry_vtt.get(),
                                                                                        relative_tolerance_entry_vtt.get()))
        validate_statistics_button_vtt.grid(row=2, column=0)

        validate_hash_button_vtt = Button(validate_trace_tab, text="Validate Hash",
                                          command=lambda: model.hash_check(file_entry_vtt.get()))
        validate_hash_button_vtt.grid(row=3, column=0)

        restore_traceheader_button_vtt = Button(validate_trace_tab, text="Restore Traceheader",
                                                command=lambda: restore_traceheader(file_entry_vtt.get()))
        restore_traceheader_button_vtt.grid(row=4, column=0)

        statistics_format_string_label_vtt = Label(validate_trace_tab, text="Statistics Format String")
        statistics_format_string_label_vtt.grid(column=1, row=4)

        statistics_format_string_entry_vtt = Entry(validate_trace_tab, width=config.get('entries', 'entry_width'))
        statistics_format_string_entry_vtt.grid(column=2, row=4)

        # Tooltips
        browse_file_button_tooltip_vtt = Hovertip(browse_file_button_vtt,
                                                  config.get('tooltips', 'browse_file_button_vtt'))
        validate_statistics_button_tooltip_vtt = Hovertip(validate_statistics_button_vtt,
                                                          config.get('tooltips', 'validate_statistics_button_vtt'))
        relative_tolerance_tooltip_vtt = Hovertip(relative_tolerance_label_vtt,
                                                  config.get('tooltips', 'relative_tolerance_vtt'))
        validate_hash_button_tooltip_vtt = Hovertip(validate_hash_button_vtt,
                                                    config.get('tooltips', 'validate_hash_button_vtt'))
        restore_traceheader_button_tooltip_vtt = Hovertip(restore_traceheader_button_vtt,
                                                          config.get('tooltips', 'restore_traceheader_button_vtt'))
        numerical_format_tooltip_vtt = Hovertip(statistics_format_string_label_vtt,
                                                config.get('tooltips', 'statistics_format_string'))


# Create TCGUI instance and run mainloop
root = Tk()
converting_tool_gui = TraceConvertingToolGUI(root)
root.mainloop()
sys.exit()
