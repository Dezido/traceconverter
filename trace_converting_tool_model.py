import configparser
import datetime
import hashlib
import json
import json.decoder
import math
import os
import pathlib
import time
import tkinter
import tkinter.filedialog
import tkinter.messagebox as mb

import pandas as pd
from pandas.errors import EmptyDataError

# Load config from file
config = configparser.RawConfigParser()
config.read('config.properties')


def remove_lines_from_csv(filename, line_amount):
    """
    Removes rows from the beginning of a file
    :param filename: Input file
    :param line_amount: Amount of lines to be removed from the beginning of the file
    """
    try:
        try:
            line_amount = int(line_amount)
            try:
                df = pd.read_csv(filename, skiprows=line_amount)
                df.to_csv(filename, index=False)
                if line_amount == 1:
                    mb.showinfo('Removing successfully', 'Removed the first row from ' + os.path.basename(filename))
                if line_amount > 1:
                    mb.showinfo('Removing successfully', 'Removed the first ' + str(line_amount) + ' rows from ' +
                                os.path.basename(filename))
            except (EmptyDataError, ValueError):
                mb.showerror('Invalid number of Lines', 'Please specify a valid number of lines to remove')
        except ValueError:
            mb.showerror('Integer needed', 'Please enter an integer number of lines')
    except FileNotFoundError:
        mb.showinfo(config.get('browse_file', 'no_file_selected_window'),
                    config.get('browse_file', 'no_file_selected_message'))


def add_header_to_csv(filename, header):
    """
    Adds new header to csv file
    :param filename: Input file
    :param header: New header
    """
    if os.path.splitext(filename)[1] == ".csv":
        df = pd.read_csv(filename, delimiter=',', header=None)
        if len(header) != len(df.columns):
            mb.showinfo('Invalid header passed', 'The passed header has ' + str(len(header)) + ' elements. \nBut ' +
                        str(len(df.columns)) + ' elements are required!')
        else:
            df.to_csv(filename, header=header, index=False)
            mb.showinfo('Header added ', str(header) + " was added as header to " + filename)
    else:
        mb.showinfo('Please select a csv file', 'You can only add headers to csv files')


def date_time_to_epoch(date_time, time_format):
    """
    Transforms a timestamp into unix timestamp
    :param date_time: Original timestamp
    :param time_format: Format of timestamp
    :return: Unix timestamp
    """
    return time.mktime(datetime.datetime.strptime(date_time, time_format).timetuple())


def df_columns_to_epoch(dataframe, columns, date_time_format):
    """
    Transforms columns in a dataframe to unix timestamp
    :param dataframe: The dataframe
    :param columns: List with column indexes
    :param date_time_format: List with timestamp formats
    :return: Transformed dataframe
    """
    for i in range(len(columns)):
        for j in range(len(dataframe.index)):
            if not pd.isnull(dataframe.at[j, dataframe.columns[columns[i]]]):
                dataframe.at[j, dataframe.columns[columns[i]]] = \
                    date_time_to_epoch(dataframe.at[j, dataframe.columns[columns[i]]], date_time_format[i])
    return dataframe


def get_tracedata_from_file(file, column_indexes):
    """
    Gets the relevant columns and adds each column as a separate list into the result list
    :param file: Tracefile the data shall be extracted from
    :param column_indexes: List of column indexes that shall be kept
    :return: Columns of the original trace as lists
    """
    df = pd.read_csv(file, header=0, delimiter=',')
    if columns_valid(column_indexes, len(df.columns)):
        tracedata_list = []
        column_names = []
        for i in range(len(column_indexes)):
            column_names.append(df.columns[column_indexes[i]])
        df = df[column_names].copy()
        for column in df:
            tracedata_list.append(df[column].values.reshape(1, -1).ravel().tolist())
        return tracedata_list
    else:
        mb.showerror("Columns invalid", "Please specify valid columns")
        raise


def columns_valid(columns, size):
    """
    Checks if passed columns are valid
    :param columns: List with column indexes
    :param size: Size of dataframe the indexes are not allowed to surpass
    :return: True if the columns are valid
    """
    for i in range(len(columns)):
        if not isinstance(columns[i], int) or columns[i] < 0 or columns[i] >= size or len(columns) != len(set(columns)):
            return False
    return True


def convert_trace(input_file, indexes, data_desc, desc, source, user, additional_info, stat_format, result_filename):
    """
    Converts the input trace to standard format
    :param input_file: input trace
    :param indexes: column indexes with tracedata
    :param data_desc: tracedata description
    :param desc: trace description
    :param source: trace source
    :param user: username
    :param additional_info: additional information about the trace
    :param stat_format: format string for statistical characteristics
    :param result_filename: result filename
    :return: converted trace
    """
    trace_template["tracebody"]["tracedata"] = \
        get_tracedata_from_file(input_file, indexes)
    amount_tracedata = len(trace_template["tracebody"]["tracedata"][0])
    trace_template["tracebody"]["tracedata description"] = data_desc
    trace_template["traceheader"]["metainformation"]["original name"] = os.path.basename(input_file)
    trace_template["traceheader"]["metainformation"]["description"] = desc
    trace_template["traceheader"]["metainformation"]["source"] = source
    trace_template["traceheader"]["metainformation"]["user"] = user
    trace_template["traceheader"]["metainformation"]["additional information"] = additional_info
    trace_template["traceheader"]["metainformation"]["creation time"] = str(datetime.datetime.now())
    # Generates statistics and adds them into a list. Each list entry represents one column of the raw trace
    if amount_tracedata > 4:
        trace = generate_statistic(trace_template, stat_format)
    else:
        trace = trace_template
        mb.showinfo("Statistics won't be computed", "Tracedata only contains " + str(amount_tracedata) +
                    " elements per column. Computing statistics requires five or more.")
    # Save trace to file
    with open(result_filename, 'w') as fp:
        json.dump(trace, fp, indent='\t')
    add_hash_value_to_trace(result_filename)


def extract_tracedata(tracename, result_filename, float_format_string):
    """
    Extracts tracedata from the file can be used for ProFiDo
    :param float_format_string: Format string for tracedata
    :param result_filename: Name for the tracedata file
    :param tracename: Name of the converted tracefile
    """
    try:
        with open(tracename) as tr:
            tracedata = json.load(tr)["tracebody"]["tracedata"]
            df = pd.DataFrame(tracedata)
            write_file = 1
            if os.path.exists(result_filename):
                write_file = mb.askyesno("File already exists", os.path.basename(result_filename) +
                                         " already exists. \n Would you like to overwrite it?")
            if write_file:
                try:
                    df = df.transpose().dropna()
                    if len(float_format_string) > 0:
                        df.to_csv(result_filename, sep='\t', float_format=float_format_string, index=False,
                                  header=False)
                    if len(float_format_string) == 0:
                        df.to_csv(result_filename, sep='\t', index=False, header=False)
                except TypeError:
                    mb.showerror('Invalid float format string', 'Please enter a valid format string')
                except ValueError:
                    mb.showerror('Invalid float format string', 'Please enter a valid format string')
                except FileNotFoundError:
                    mb.showerror('Invalid Path or Filename', 'Please check if the result path and filename are valid')
    except json.decoder.JSONDecodeError:
        mb.showerror('Invalid Trace', 'The selected file is not a valid Trace')
    except FileNotFoundError:
        mb.showerror('Could not find trace', 'Please check if path and filename are valid')


def generate_statistic(trace, formatstring):
    """
    Computes the statistics for the trace
    :param trace: Tracefile to compute from and add the statistics to
    :param formatstring: For formatting the computed values
    """
    # Clear statistic lists so the next trace won't have old values
    statistics = trace["traceheader"]["statistical characteristics"]
    for statistic in trace["traceheader"]["statistical characteristics"]:
        trace["traceheader"]["statistical characteristics"][statistic] = []
    try:
        for i in range(len(trace["tracebody"]["tracedata"])):
            df = pd.DataFrame(trace["tracebody"]["tracedata"][i])
            statistics["mean"].append(format(df[0].mean(), formatstring))
            statistics["median"].append(format(df[0].median(), formatstring))
            statistics["skewness"].append(format(df[0].skew(), formatstring))
            statistics["kurtosis"].append(format(df[0].kurtosis(), formatstring))
            statistics["autocorrelation"].append(format(df[0].autocorr(), formatstring))
            statistics["variance"].append(format(df[0].var(), formatstring))
        return trace
    except TypeError:
        mb.showerror("Type Error", "One of the selected columns does not contain valid data")
        raise
    except (KeyError, IndexError):
        mb.showerror("Format Error", "Invalid Numerical Format entered")
        raise


def filter_traces_by_expression(selected_files, expression, selected_filenames):
    """
    filters the selected files with the expression
    :param selected_files: set of files to filter from
    :param expression: expression to filter by
    :param selected_filenames: names of selected files
    :return: results of filtering
    """
    filter_results = []
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
                    trace = [os.path.basename(os.path.dirname((selected_filenames[i]))) +
                             '/' + os.path.basename((selected_filenames[i])),
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
    return filter_results


def hash_from_trace(filename):
    """
    Computes hash value for a given file
    :param filename: Input file
    :return: Computed hash value
    """
    sha256_hash = hashlib.sha256()
    with open(filename, "r") as file:
        for line in file:
            if 'hash value' not in line:
                sha256_hash.update(line.encode('UTF-8'))
        return sha256_hash.hexdigest()


def hash_check(filename):
    """
    Computes hash for the input file and compares it to the stored hash inside the file
    :param filename: Input file
    """
    if os.path.isfile(filename) and pathlib.Path(filename).suffix == ".json":
        try:
            with open(filename) as file:
                tracedata = json.load(file)
                stored_hash = tracedata["traceheader"]["metainformation"]["hash value"]
                computed_hash = hash_from_trace(filename)
            if stored_hash == computed_hash:
                tkinter.messagebox.showinfo("Hash check result", "Hashes are equal")
            else:
                tkinter.messagebox.showinfo("Hash check result", "Stored Hash: " + stored_hash + "\n" +
                                            "Computed Hash: " + hash_from_trace(filename))
        except json.decoder.JSONDecodeError:
            mb.showerror("Trace content invalid", "Please check if the trace content is valid")
    else:
        mb.showerror("Trace invalid", "Please check if the file is valid")


def add_hash_value_to_trace(filename):
    """
    Adds hash value to metainformation
    :param filename: File the hash will be computed for
    """
    with open(filename) as tr:
        tracedata = json.load(tr)
        tracedata["traceheader"]["metainformation"]["hash value"] = hash_from_trace(filename)
    with open(filename, 'w', newline='\n') as fp:
        json.dump(tracedata, fp, indent='\t')


def verify_statistics(converted_trace_file, tolerance):
    """
    Checks if the statistics of the trace are valid
    :param tolerance: relative tolerance
    :param converted_trace_file: An already converted trace
    """
    if os.path.isfile(converted_trace_file) and pathlib.Path(converted_trace_file).suffix == ".json":
        try:
            try:
                tolerance = float(tolerance)
                if tolerance < 0 or tolerance > 1:
                    mb.showerror('Tolerance must be between 0 and 1', 'Please enter a value between 0 and 1')
                    return
            except ValueError:
                mb.showerror('Tolerance Entry invalid', 'Please enter a valid float')
                return
            with open(converted_trace_file) as trace_file:
                input_trace = json.load(trace_file)
                saved = input_trace["traceheader"]["statistical characteristics"]
            with open(converted_trace_file) as trace_file:
                input_trace = json.load(trace_file)
                comp = generate_statistic(input_trace, '')["traceheader"]["statistical characteristics"]
            statistics_valid = True
            invalid_statistics = ""
            for i in range(len(comp["mean"])):
                for statistic in saved:
                    if not math.isclose(float(comp[statistic][i]), float(saved[statistic][i]), rel_tol=tolerance):
                        invalid_statistics += (
                                str(statistic) + " [" + str(i) + "] not equal. Should be: " + str(comp[statistic][i]) +
                                " but is " + str(saved[statistic][i]) + "\n")
                        statistics_valid = False
            if statistics_valid:
                mb.showinfo("Statistic Validation",
                            "All statistics are close considering the passed relative tolerance")
            else:
                mb.showinfo("Statistic Validation", invalid_statistics)
        except json.decoder.JSONDecodeError:
            mb.showerror("Trace content invalid", "Please check if the trace content is valid")
        except ValueError:
            mb.showerror('Invalid Trace', 'Trace contains invalid statistics')
            return
    else:
        mb.showerror("Trace invalid", "Please check if the file is valid")


def restore_traceheader(filename, stat_format_string):
    """
    (Re)generates statistics and hash for the input trace
    :param stat_format_string: format string for statistical characteristics
    :param filename: Input file
    """
    if os.path.isfile(filename) and pathlib.Path(filename).suffix == ".json":
        try:
            with open(filename) as tr:
                tracedata = json.load(tr)
                trace = generate_statistic(tracedata, stat_format_string)
            write_file = 1
            if os.path.exists(filename):
                write_file = mb.askyesno("Overwriting File",
                                         "Restoring the traceheader will overwrite the file. Continue?")
            if write_file:
                with open(filename, 'w') as fp:
                    json.dump(trace, fp, indent='\t')
                    add_hash_value_to_trace(filename)
                    mb.showinfo('Traceheader restored', 'Statistics and has value restored successfully')
        except json.decoder.JSONDecodeError:
            mb.showerror("Trace content invalid", "Please check if the trace content is valid")
    else:
        mb.showerror("Trace invalid", "Please check if the file is valid")


trace_template = {"traceheader": {
    "metainformation": {
        "original name": "",
        "description": "",
        "source": "",
        "user": "",
        "additional information": "",
        "creation time": "",
        "hash value": ""
    },
    "statistical characteristics": {
        "mean": [],
        "median": [],
        "skewness": [],
        "kurtosis": [],
        "autocorrelation": [],
        "variance": []
    }
},
    "tracebody": {
        "tracedata description": [],
        "tracedata": []
    }
}
