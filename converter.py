import configparser
import json
import logging
import os
import hashlib

import pandas as pd

# Load config
config = configparser.RawConfigParser()
config.read('config.properties')

# Logging
logging.basicConfig(format=config.get('logging', 'logging_format'), level=logging.INFO)


def get_tracedata_from_file(file, cols):
    """
    Gets the relevant columns and adds each column as a separate list into the result list
    :param file: Tracefile the data shall be extracted from
    :param cols: List of column numbers that shall be kept
    :return: Columns of the original trace as lists
    """
    df = pd.read_csv(file, header=0, delimiter=',')
    tracedata_list = []
    relevant_column_numbers = list(range(0, len(df.columns)))
    for i in range(len(cols)):
        relevant_column_numbers.remove(cols[i])
    df.drop(df.columns[relevant_column_numbers], axis=1, inplace=True)
    for column in df:
        tracedata_list.append(df[column].values.reshape(1, -1).ravel().tolist())
    print("Tracedata from " + os.path.basename(file) + " successfully retrieved")
    return tracedata_list


def verify_statistics(converted_trace_file):
    """
    Checks if the statistics are valid for the tracedata
    :param converted_trace_file: A tracefile in standard format
    :return:
    """
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
        for i in range(len(tracedata)):
            df = pd.DataFrame(tracedata[i])
            current_mean.append(df[0].mean())
            current_median.append(df[0].median())
            current_skew.append(df[0].skew())
            current_kurtosis.append(df[0].kurtosis())
            current_autocorr.append(df[0].autocorr())

        if current_mean != statistics["mean"]:
            invalid_statistics += ("Mean not correct. Should be: " + str(current_mean) + "\n")
            statistics_valid = False
        if current_median != statistics["median"]:
            invalid_statistics += ("Median not correct. Should be: " + str(current_median) + "\n")
            statistics_valid = False
        if current_skew != statistics["skew"]:
            invalid_statistics += ("Skew not correct. Should be: " + str(current_skew) + "\n")
            statistics_valid = False
        if current_kurtosis != statistics["kurtosis"]:  # np.nan check necessary?
            invalid_statistics += ("Kurtosis not correct. Should be: " + str(current_kurtosis) + "\n")
            statistics_valid = False
        if current_autocorr != statistics["autocorrelation"]:
            invalid_statistics += ("Autocorrelation not correct. Should be: " + str(current_autocorr) + "\n")
            statistics_valid = False
        if statistics_valid:
            return "All statistics are valid"
        else:
            return invalid_statistics


def remove_rows_from_csv(filename, number_of_rows):
    """
    Removes rows from the beginning of a file
    :param filename: Input file
    :param number_of_rows: How many rows shall be removed from the beginning of the file
    """
    df = pd.read_csv(filename, header=1, skiprows=list(range(0, number_of_rows)))
    df.to_csv(filename, index=False, header="Header")
    if number_of_rows == 1:
        print("Removed the first " + str(number_of_rows) + " row from " + filename)
    if number_of_rows > 1:
        print("Removed the first " + str(number_of_rows) + " rows from " + filename)


def add_header_to_csv(filename, header):
    """
    Add a header to a csv file
    :param filename: Input file
    :param header: Header that will be placed on top of the file
    """
    df = pd.read_csv(filename, delimiter=',', header=None)
    if len(header) != len(df.columns):
        print('The passed header has ' + str(len(header)) + ' elements. \nBut ' + str(len(df.columns)) +
              ' elements are required!')
    else:
        df.to_csv(filename, header=header, index=False)
        print(str(header) + " was added as header to " + filename)


def hash_from_trace(filename):
    """
    Computes hash value for a given file
    :param filename: Input file
    :return: hash value
    """
    sha256_hash = hashlib.sha256()
    with open(filename, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


trace_template = {"traceheader": {
    "metainformation": {
        "name": "",
        "source": "",
        "description": "",
        "date": "",
        "user": "",
        "additional information": ""
    },
    "statistical characteristics": {
        "mean": [],
        "median": [],
        "skew": [],
        "kurtosis": [],
        "autocorrelation": [],
    }
},
    "tracebody": {
        "tracedatadescription": [],
        "tracedata": []
    }
}
