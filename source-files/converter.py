import pandas as pd


# Gets the relevant columns and adds each column as a separate list into the result list
def get_tracedata_from_file(file, cols):
    df = pd.read_csv(file, header=0, delimiter=',')
    res_list = []
    df.drop(df.columns[cols], axis=1, inplace=True)
    for column in df:
        res_list.append(df[column].values.reshape(1, -1).ravel().tolist())
    return res_list


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
