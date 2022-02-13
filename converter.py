import configparser
import hashlib
import json
import json.decoder
import os
import pathlib
import tkinter
import tkinter.filedialog
import tkinter.messagebox as mb
import time
import datetime

import pandas as pd
from pandas.errors import EmptyDataError

# Load config from file
config = configparser.RawConfigParser()
config.read('config.properties')


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


def date_time_to_epoch(date_time, time_format):
    """
    Transforms a timestamp into unix timestamp
    :param date_time: Original timestamp
    :param time_format: Format of timestamp
    :return: Unix timestamp
    """
    return time.mktime(datetime.datetime.strptime(date_time, time_format).timetuple())


def get_tracedata_from_file(file, keep_cols):
    """
    Gets the relevant columns and adds each column as a separate list into the result list
    :param file: Tracefile the data shall be extracted from
    :param keep_cols: List of column numbers that shall be kept
    :return: Columns of the original trace as lists
    """
    df = pd.read_csv(file, header=0, delimiter=',')
    if columns_valid(keep_cols, len(df.columns)):
        tracedata_list = []
        relevant_column_numbers = list(range(0, len(df.columns)))
        for i in range(len(keep_cols)):
            relevant_column_numbers.remove(keep_cols[i])
        df.drop(df.columns[relevant_column_numbers], axis=1, inplace=True)
        for column in df:
            tracedata_list.append(df[column].values.reshape(1, -1).ravel().tolist())
        print("Tracedata from " + os.path.basename(file) + " successfully retrieved")
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


def verify_statistics(converted_trace_file):
    """
    Checks if the statistics of the trace are valid
    :param converted_trace_file: An already converted trace
    """
    if os.path.isfile(converted_trace_file) and pathlib.Path(converted_trace_file).suffix == ".json":
        try:
            with open(converted_trace_file) as trace_file:
                trace = json.load(trace_file)
                statistics = trace["traceheader"]["statistical characteristics"]
                tracedata = trace["tracebody"]["tracedata"]
                statistics_valid = True
                invalid_statistics = ""
                current_mean = []
                current_median = []
                current_skew = []
                current_kurtosis = []
                current_autocorr = []
                current_variance = []
                for i in range(len(tracedata)):
                    df = pd.DataFrame(tracedata[i])
                    current_mean.append(float(df[0].mean()))
                    current_median.append(float(df[0].median()))
                    current_skew.append(float(df[0].skew()))
                    current_kurtosis.append(float(df[0].kurtosis()))
                    current_autocorr.append(float(df[0].autocorr()))
                    current_variance.append(float(df[0].var()))

                    statistics["mean"][i] = float(statistics["mean"][i])
                    statistics["median"][i] = float(statistics["median"][i])
                    statistics["skew"][i] = float(statistics["skew"][i])
                    statistics["kurtosis"][i] = float(statistics["kurtosis"][i])
                    statistics["autocorrelation"][i] = float(statistics["autocorrelation"][i])
                    statistics["variance"][i] = float(statistics["variance"][i])

                if current_mean != statistics["mean"]:
                    invalid_statistics += ("Mean not correct. Should be: " + str(current_mean) + " but is " +
                                           str(statistics["mean"]) + "\n")
                    statistics_valid = False
                if current_median != statistics["median"]:
                    invalid_statistics += ("Median not correct. Should be: " + str(current_median) + " but is " +
                                           str(statistics["median"]) + "\n")
                    statistics_valid = False
                if current_skew != statistics["skew"]:
                    invalid_statistics += ("Skew not correct. Should be: " + str(current_skew) + " but is " +
                                           str(statistics["skew"]) + "\n")
                    statistics_valid = False
                if current_kurtosis != statistics["kurtosis"]:
                    invalid_statistics += ("Kurtosis not correct. Should be: " + str(current_kurtosis) + " but is " +
                                           str(statistics["kurtosis"]) + "\n")
                    statistics_valid = False
                if current_autocorr != statistics["autocorrelation"]:
                    invalid_statistics += (
                            "Autocorrelation not correct. Should be: " + str(current_autocorr) + " but is " +
                            str(statistics["autocorrelation"]) + "\n")
                    statistics_valid = False
                if current_variance != statistics["variance"]:
                    invalid_statistics += (
                            "Variance not correct. Should be: " + str(current_variance) + " but is " +
                            str(statistics["variance"]) + "\n")
                    statistics_valid = False

                if statistics_valid:
                    print("All statistics are valid")
                    mb.showinfo("Statistic Validation", "All statistics are valid")
                else:
                    print(invalid_statistics)
                    mb.showinfo("Statistic Validation", invalid_statistics)
        except json.decoder.JSONDecodeError:
            mb.showerror("Trace content invalid", "Please check if the trace content is valid")
    else:
        mb.showerror("Trace invalid", "Please check if the file is valid")


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
                mb.showerror('Invalid amount of Rows', 'Please specify a valid amount of rows to remove')
        except ValueError:
            mb.showerror('Integer needed', 'Please enter an integer amount of rows')
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


def hash_from_trace(filename):
    """
    Computes hash value for a given file
    :param filename: Input file
    :return: Computed hash value
    """
    sha256_hash = hashlib.sha256()
    with open(filename, "r") as f:
        for line in f:
            if 'hash' not in line:
                sha256_hash.update(line.encode('UTF-8'))
        return sha256_hash.hexdigest()


def hash_check(filename):
    """
    Computes hash for the input file and compares it to the stored hash inside the file
    :param filename: Input file
    """
    if os.path.isfile(filename) and pathlib.Path(filename).suffix == ".json":
        try:
            with open(filename) as tr:
                tracedata = json.load(tr)
                stored_hash = tracedata["traceheader"]["metainformation"]["hash"]
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


trace_template = {"traceheader": {
    "metainformation": {
        "name": "",
        "source": "",
        "description": "",
        "date": "",
        "user": "",
        "additional information": "",
        "hash": ""
    },
    "statistical characteristics": {
        "mean": [],
        "median": [],
        "skew": [],
        "kurtosis": [],
        "autocorrelation": [],
        "variance": []
    }
},
    "tracebody": {
        "tracedatadescription": [],
        "tracedata": []
    }
}
