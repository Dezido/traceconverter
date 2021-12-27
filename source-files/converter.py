import pandas as pd


# Gets the relevant columns and adds each column as a separate list into the result list
def get_tracedata_from_file(file, cols):
    df = pd.read_csv(file, header=0, delimiter=',')
    tracedata_list = []
    relevant_column_numbers = list(range(0, len(df.columns)))
    for i in range(len(cols)):
        relevant_column_numbers.remove(cols[i])
    df.drop(df.columns[relevant_column_numbers], axis=1, inplace=True)
    for column in df:
        tracedata_list.append(df[column].values.reshape(1, -1).ravel().tolist())
    return tracedata_list


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
