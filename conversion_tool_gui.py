import configparser
import datetime
import json
import os
import pathlib
import tkinter
import tkinter.filedialog as fd
import tkinter.messagebox as mb
from idlelib.tooltip import Hovertip
from tkinter import *
from tkinter import scrolledtext
from tkinter import ttk

import pandas as pd

import converter as cnv
from converter import trace_template

# Load config file
config = configparser.RawConfigParser()
config.read('config.properties')


class TraceConverterGUI:
    def __init__(self, master):
        """Creates a GUI for the tool"""
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
            """Opens file explorer to select a file"""
            file_entry_prt.delete(0, END)  # removes previously selected file
            selected_file = fd.askopenfilename(initialdir=config.get('directories', 'raw_traces_dir'),
                                               title="Select a File",
                                               filetypes=(("CSV files", "*.csv*"), ("all files",
                                                                                    "*.*")))
            if not selected_file:
                mb.showinfo(config.get('browse_file', 'no_file_selected_window'),
                            config.get('browse_file', 'no_file_selected_message'))
            file_entry_prt.insert(END, selected_file)
            file_entry_prt.grid(row=0, column=1)
            file_button_prt.grid(row=0, column=0)
            if selected_file:
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
                                        command=lambda: [cnv.remove_lines_from_csv(file_entry_prt.get(),
                                                                                   remove_rows_entry_prt.get()),
                                                         display_file_prt(file_entry_prt.get())])
        remove_rows_button_prt.grid(column=2, row=2)

        add_header_label_prt = Label(preparation_tab, text="Add header to file")
        add_header_label_prt.grid(column=0, row=3)

        add_header_entry_prt = Entry(preparation_tab, width=config.get('entries', 'entry_width'))
        add_header_entry_prt.grid(column=1, row=3)

        add_header_button_prt = Button(preparation_tab, text="Add Header",
                                       command=lambda: [cnv.add_header_to_csv(file_entry_prt.get(),
                                                                              list(
                                                                                  add_header_entry_prt.get().split(
                                                                                      ","))),
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
                                               convert_file_to_csv_prt(file_entry_prt.get(),
                                                                       delimiter_entry_prt.get(),
                                                                       first_line_is_header_checkbutton_var_prt.get()))
        transform_filetype_button_prt.grid(column=2, row=4)

        def display_file_prt(filename):
            """
            Displays the selected file in the preparation tab
            :param filename: File that will be displayed
            """
            if os.path.isfile(filename) and pathlib.Path(filename).suffix == ".csv":
                with open(filename, 'r') as f:
                    file_displayer_label_prt.configure(text=os.path.basename(filename))
                    file_displayer_prt.grid(column=0, row=5, columnspan=12, rowspan=10)
                    file_displayer_prt.config(state=NORMAL)
                    file_displayer_prt.delete("1.0", "end")
                    file_displayer_prt.insert(INSERT, f.read())
                    file_displayer_prt.config(state=DISABLED)

        def convert_file_to_csv_prt(filename, delimiter, header):
            """
            Converts file to csv format
            :param filename:Input file
            :param delimiter:Delimiter of the file
            :param header:File header
            """
            df = pd.read_csv(filename, sep=delimiter)
            result_filename = \
                config.get('directories', 'raw_traces_dir') + '/' + os.path.basename(filename).split('.')[0] + '.csv'
            dont_overwrite = 0
            if os.path.exists(filename):
                dont_overwrite = not mb.askyesno("File already exists", os.path.basename(filename) +
                                                 " already exists. \n Would you like to overwrite it?")
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
            """Puts the profido_filename_label on the grid if the checkbox is selected"""
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

        numerical_format_label_ct = Label(convert_tab, text="Numerical Format")
        numerical_format_label_ct.grid(row=12, column=0)

        numerical_format_entry_ct = Entry(convert_tab, width=config.get('entries', 'entry_width'))
        numerical_format_entry_ct.grid(row=12, column=1)

        original_tracefile_entry_ct = Entry(convert_tab, width=config.get('entries', 'entry_width'))

        def browse_file_ct():
            """Opens file explorer to select a file"""
            original_tracefile_entry_ct.delete(0, END)  # removes previously selected file
            selected_file = fd.askopenfilename(initialdir=config.get('directories', 'raw_traces_dir'),
                                               title="Select a File",
                                               filetypes=(("CSV files", "*.csv*"),))
            if not selected_file:
                mb.showinfo(config.get('browse_file', 'no_file_selected_window'),
                            config.get('browse_file', 'no_file_selected_message'))
            original_tracefile_entry_ct.insert(END, selected_file)
            original_tracefile_entry_ct.grid(row=1, column=1)
            if selected_file:
                display_file_ct(selected_file)

        # Create entries and set default values
        original_tracefile_button_ct = Button(convert_tab, text="Choose File", command=browse_file_ct)

        columns_entry_ct = Entry(convert_tab, width=config.get('entries', 'entry_width'))
        columns_entry_ct.insert(END, config.get('default_entries', 'default_columns_entry'))

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
            """Takes the user input from the entry fields and converts the selected trace to the standard format"""
            org_filename = original_tracefile_entry_ct.get()
            if os.path.isfile(org_filename) and pathlib.Path(org_filename).suffix == ".csv":
                col = list(map(int, (columns_entry_ct.get().split(";"))))
                trace_template["tracebody"]["tracedata"] = \
                    cnv.get_tracedata_from_file(original_tracefile_entry_ct.get(), col)
                amount_tracedata = len(trace_template["tracebody"]["tracedata"][0])
                trace_template["tracebody"]["tracedatadescription"] = tracedatadescription_entry_ct.get().split(";")
                trace_template["traceheader"]["metainformation"]["name"] = os.path.basename(
                    original_tracefile_entry_ct.get())
                trace_template["traceheader"]["metainformation"]["source"] = source_entry_ct.get()
                trace_template["traceheader"]["metainformation"]["description"] = description_entry_ct.get()
                trace_template["traceheader"]["metainformation"]["date"] = str(datetime.datetime.now())
                trace_template["traceheader"]["metainformation"]["user"] = username_entry_ct.get()
                if len(custom_field_entry_ct.get('1.0', 'end-1c')) != 0:
                    trace_template["traceheader"]["metainformation"]["additional information"] = \
                        custom_field_entry_ct.get('1.0', 'end-1c')
                else:
                    trace_template["traceheader"]["metainformation"].pop("additional information")

                #  Generate statistics and adds them into a list. Each list entry represents one column of the raw trace
                if amount_tracedata > 4:
                    trace = generate_statistic(trace_template, numerical_format_entry_ct.get())
                else:
                    trace = trace_template
                    mb.showinfo("Statistics won't be computed", "Tracedata only contains " + str(amount_tracedata) +
                                " elements per column. Computing statistics requires five or more.")
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
                    add_hash_to_trace(filename)
                    # If profido checkbox is selected the columns will also be extracted for profido use
                    if extract_profido_checkbutton_var_ct.get() == 1:
                        extract_after_conversion(
                            filename)
                    mb.showinfo("Trace converted successfully", "Displaying converted Trace")
                else:
                    mb.showinfo("File already exists", "Displaying existing File")
                # Display the created traces
                display_file_ct(filename)
            else:
                mb.showinfo(config.get('browse_file', 'no_file_selected_window'),
                            config.get('browse_file', 'no_file_selected_message'))

        def generate_statistic(trace, formatstring):
            """
            Computes the statistics for the trace
            :param trace:
            :param formatstring: For formatting the computed values
            """
            # Clear statistic lists so the next trace won't have old values
            trace["traceheader"]["statistical characteristics"]["mean"] = []
            trace["traceheader"]["statistical characteristics"]["median"] = []
            trace["traceheader"]["statistical characteristics"]["skew"] = []
            trace["traceheader"]["statistical characteristics"]["kurtosis"] = []
            trace["traceheader"]["statistical characteristics"]["autocorrelation"] = []
            formatstring = '{' + formatstring + '}'
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
            except TypeError:
                mb.showerror("Type Error", "One of the selected columns does not contain valid data")
                raise
            except (KeyError, IndexError):
                mb.showerror("Format Error", "Invalid Numerical Format entered")
                raise

        def add_hash_to_trace(filename):
            """
            Adds hash value to metainformation
            :param filename: File the hash will be computed for
            """
            with open(filename) as tr:
                tracedata = json.load(tr)
                tracedata["traceheader"]["metainformation"]["hash"] = cnv.hash_from_trace(filename)
            with open(filename, 'w') as fp:
                json.dump(tracedata, fp, indent=4)

        def display_file_ct(filename):
            """
            Displays the selected file in the convert tab
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
            Extracts columns for ProFiDo usage from the trace
            :param filename: Name of the converted tracefile
            """
            with open(filename) as tr:
                tracedata = json.load(tr)["tracebody"]["tracedata"]
                df = pd.DataFrame(tracedata)
                dont_overwrite = 0
                result_filename = config.get('directories', 'profido_traces_dir') + profido_filename_entry_ct.get() + \
                                  '_dat.trace'
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
        numerical_format_tooltip_ct = Hovertip(numerical_format_label_ct,
                                               config.get('tooltips', 'numerical_format'))

        # Filter Tab
        selected_traces_label_ft = Label(filter_tab, text="Selected traces")
        selected_traces_label_ft.grid(column=1, row=1)

        selected_traces_lb = Listbox(filter_tab, width=config.get('listbox', 'listbox_width'),
                                     height=config.get('listbox', 'listbox_height'))

        treeview_columns = ['name', 'mean', 'median', 'skew', 'kurtosis', 'autocorrelation']
        filter_results_tv = ttk.Treeview(filter_tab, columns=treeview_columns, show='headings')
        vsb_filter_results_tv = ttk.Scrollbar(filter_tab, orient="vertical", command=filter_results_tv.yview)
        filter_results_tv.configure(yscrollcommand=vsb_filter_results_tv.set)
        filter_results_tv.heading('name', text='Name')
        filter_results_tv.column('name', width=300)
        filter_results_tv.heading('mean', text='Mean')
        filter_results_tv.heading('median', text='Median')
        filter_results_tv.heading('skew', text='Skew')
        filter_results_tv.heading('kurtosis', text='Kurtosis')
        filter_results_tv.heading('autocorrelation', text='Autocorrelation')

        selected_filenames = []
        selected_files = []
        filter_result = []

        def browse_files_ft():
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
                    mb.showinfo(config.get('browse_file', 'no_files_selected_window'),
                                config.get('browse_file', 'no_files_selected_message'))
                selected_traces_lb.delete(0, 'end')
                selected_files.clear()
                selected_filenames.clear()
                for i in file_tuple:
                    with open(str(i)) as json_file:
                        selected_files.append(json.load(json_file))
                        selected_filenames.append(os.path.basename(os.path.dirname(i)) + '/' + os.path.basename(i))
                for i in range(len(selected_filenames)):
                    selected_traces_lb.insert(i, selected_filenames[i])
                selected_traces_lb.grid(column=1, row=2, rowspan=5)
                browse_button_ft.grid(column=1, row=8)
            except json.decoder.JSONDecodeError:
                mb.showerror("Invalid Trace", "Invalid/corrupted traces were selected")

        def filter_traces(expression):
            """Evaluates the expression for the selected traces"""
            filter_result.clear()
            for i in filter_results_tv.get_children():
                filter_results_tv.delete(i)
            for i in range(len(selected_files)):
                mean_list = selected_files[i]["traceheader"]["statistical characteristics"]["mean"]
                median_list = selected_files[i]["traceheader"]["statistical characteristics"]["median"]
                skew_list = selected_files[i]["traceheader"]["statistical characteristics"]["skew"]
                kurtosis_list = selected_files[i]["traceheader"]["statistical characteristics"]["kurtosis"]
                autocorrelation_list = \
                    selected_files[i]["traceheader"]["statistical characteristics"]["autocorrelation"]
                for j in range(len(selected_files[i]["traceheader"]["statistical characteristics"]["mean"])):
                    mean = float(mean_list[j])
                    median = float(median_list[j])
                    skew = float(skew_list[j])
                    kurtosis = float(kurtosis_list[j])
                    autocorrelation = float(autocorrelation_list[j])
                    try:
                        if eval(expression):
                            trace = [os.path.basename(selected_filenames[i]),
                                     mean,
                                     median,
                                     skew,
                                     kurtosis,
                                     autocorrelation
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
                                                            filter_result[i][5],))
            Label(filter_tab, text="Results").grid(column=1, row=10)
            filter_results_tv.grid(column=1, row=11, columnspan=10)
            vsb_filter_results_tv.grid(column=11, row=11, sticky=N + S)

        expression_label_ft = Label(filter_tab, text="Boolean Expression")
        expression_label_ft.grid(column=3, row=2)

        expression_entry_ft = Entry(filter_tab, width=config.get('entries', 'entry_width'))
        expression_entry_ft.grid(column=4, row=2)

        # Label and Buttons
        filter_button_ft = Button(filter_tab, text="Filter Traces",
                                  command=lambda: filter_traces(expression_entry_ft.get()))
        filter_button_ft.grid(column=5, row=2)

        browse_button_ft = Button(filter_tab, text="Choose Files", command=browse_files_ft)
        browse_button_ft.grid(column=1, row=2)

        # Tooltips
        selected_traces_tooltip_ft = Hovertip(selected_traces_label_ft, config.get('tooltips', 'selected_traces'))
        browse_files_button_tooltip_ft = Hovertip(browse_button_ft, config.get('tooltips', 'browse_files_button'))
        filter_button_tooltip_ft = Hovertip(filter_button_ft, config.get('tooltips', 'filter_button'))
        expression_label_tooltip_ft = Hovertip(expression_label_ft, config.get('tooltips', 'expression_label'))

        # ===ProFiDo format Tab
        converted_trace_label_pt = Label(profido_format_tab, text="Trace")
        converted_trace_label_pt.grid(row=0)
        profido_filename_label_pt = Label(profido_format_tab, text="Result filename")
        profido_filename_label_pt.grid(row=1)
        input_trace_entry_pt = Entry(profido_format_tab, width=config.get('entries', 'entry_width'))

        trace_column_display_pt = scrolledtext.ScrolledText(profido_format_tab, width=45, height=20)

        def browse_file_pt():
            """Opens file explorer to select a file"""
            input_trace_entry_pt.delete(0, END)
            selected_trace = fd.askopenfilename(initialdir=config.get('directories', 'converted_traces_dir'),
                                                title="Select a File",
                                                filetypes=(("JSON files", "*.json*"),))
            if not selected_trace:
                mb.showinfo(config.get('browse_file', 'no_file_selected_window'),
                            config.get('browse_file', 'no_file_selected_message'))
            input_trace_entry_pt.insert(END, selected_trace)
            input_trace_entry_pt.grid(row=0, column=1)

        def extract_columns():
            """Extracts the tracedata so the trace can be used in ProFiDo"""
            org_filename = input_trace_entry_pt.get()
            if os.path.isfile(org_filename) and pathlib.Path(org_filename).suffix == ".json":
                try:
                    with open(input_trace_entry_pt.get()) as trace_in:
                        tracedata = json.load(trace_in)["tracebody"]["tracedata"]
                        df = pd.DataFrame(tracedata)
                        filename = config.get('directories', 'profido_traces_dir') + profido_filename_entry_pt.get() + \
                                   '_dat.trace'
                        dont_overwrite = 0
                        if os.path.exists(filename):
                            dont_overwrite = not mb.askyesno("File already exists", os.path.basename(filename) +
                                                             " already exists. \n Would you like to overwrite it?")
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
                              " result was saved to " + profido_filename_entry_pt.get() + '_dat.trace')
                except json.decoder.JSONDecodeError:
                    mb.showerror('Invalid Trace', 'The selected file is not a valid Trace')
            else:
                mb.showinfo(config.get('browse_file', 'no_file_selected_window'),
                            config.get('browse_file', 'no_file_selected_message'))

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
            """Opens file explorer to select a file"""
            file_entry_vt.delete(0, END)
            selected_trace = fd.askopenfilename(initialdir=config.get('directories', 'converted_traces_dir'),
                                                title="Select a File",
                                                filetypes=(("JSON files", "*.json*"),))
            if not selected_trace:
                mb.showinfo(config.get('browse_file', 'no_file_selected_window'),
                            config.get('browse_file', 'no_file_selected_message'))
            file_entry_vt.insert(END, selected_trace)
            file_entry_vt.grid(row=0, column=0)

        def restore_traceheader(filename):
            """
            (Re)generates statistics and hash for the input trace
            :param filename: Input file
            """
            if os.path.isfile(filename) and pathlib.Path(filename).suffix == ".json":
                try:
                    with open(filename) as tr:
                        tracedata = json.load(tr)
                        trace = generate_statistic(tracedata, numerical_format_entry_vt.get())
                    dont_overwrite = 0
                    if os.path.exists(filename):
                        dont_overwrite = not mb.askyesno("Overwriting File",
                                                         "Restoring the traceheader will overwrite the file. Continue?")
                    if not dont_overwrite:
                        with open(filename, 'w') as fp:
                            json.dump(trace, fp, indent=4)
                    add_hash_to_trace(filename)
                except json.decoder.JSONDecodeError:
                    mb.showerror("Trace content invalid", "Please check if the trace content is valid")
            else:
                mb.showerror("Trace invalid", "Please check if the file is valid")

        file_entry_vt = Entry(validation_tab, width=config.get('entries', 'entry_width'))

        browse_file_button_vt = Button(validation_tab, text="Choose File", command=browse_file_vt)
        browse_file_button_vt.grid(row=1, column=0)

        validate_statistics_button_vt = Button(validation_tab, text="Validate Statistics",
                                               command=lambda: cnv.verify_statistics(file_entry_vt.get()))
        validate_statistics_button_vt.grid(row=2, column=0)

        validate_hash_button_vt = Button(validation_tab, text="Validate Hash",
                                         command=lambda: cnv.hash_check(file_entry_vt.get()))
        validate_hash_button_vt.grid(row=3, column=0)

        restore_traceheader_button_vt = Button(validation_tab, text="Restore Traceheader",
                                               command=lambda: restore_traceheader(file_entry_vt.get()))
        restore_traceheader_button_vt.grid(row=4, column=0)

        numerical_format_label_vt = Label(validation_tab, text="Numerical Format")
        numerical_format_label_vt.grid(column=1, row=2)

        numerical_format_entry_vt = Entry(validation_tab, width=config.get('entries', 'entry_width'))
        numerical_format_entry_vt.grid(column=2, row=2)

        # Tooltips
        browse_file_button_tooltip_vt = Hovertip(browse_file_button_vt, config.get('tooltips', 'browse_file_button_vt'))
        validate_statistics_button_tooltip_vt = Hovertip(validate_statistics_button_vt,
                                                         config.get('tooltips', 'validate_statistics_button'))
        validate_hash_button_tooltip_vt = Hovertip(validate_hash_button_vt,
                                                   config.get('tooltips', 'validate_hash_button'))
        restore_traceheader_button_tooltip_vt = Hovertip(restore_traceheader_button_vt,
                                                         config.get('tooltips', 'restore_traceheader_button'))
        numerical_format_tooltip_vt = Hovertip(numerical_format_label_vt,
                                               config.get('tooltips', 'numerical_format'))


# Create TCGUI instance and run mainloop
root = Tk()
converting_tool_gui = TraceConverterGUI(root)
root.mainloop()
