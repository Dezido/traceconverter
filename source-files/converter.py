import pandas as pd


# Removes unwanted columns from Trace
def relevant_columns_to_csv(file, columns, name):
    df = pd.read_csv(file, header=0, delimiter=',')
    df.drop(df.columns[columns], axis=1, inplace=True)
    df.to_csv(name, float_format="%e", index=False, header=False)


# Extracts the Tracedata into csv for ProFiDo
def extract_tracedata(trace, name):
    df = pd.DataFrame()
    for index in range(len(trace["tracebody"]["tracedata"])):
        df.insert(loc=index, column="col", value=trace["tracebody"]["tracedata"][index], allow_duplicates=True)
    df2 = df.copy()
    df2.to_csv(name, float_format="%e", index=False, header=False)
    return


# Gets the relevant columns and adds each column as a separate list into the result list
def get_tracedata_from_file(file, cols):
    df = pd.read_csv(file, header=0, delimiter=',')
    res_list = []
    df.drop(df.columns[cols], axis=1, inplace=True)
    print(df)
    for column in df:
        res_list.append(df[column].values.reshape(1, -1).ravel().tolist())
    return res_list


def filter_columns(file, cols):
    df = pd.read_csv(file, header=0, delimiter=',')
    df = df.iloc[:, cols]
    return df


def extract_profido_format(file):
    df = pd.read_json(file)
    dictionary = df.to_dict()
    print(dictionary["tracebody"]["tracedata"][0])


trace_template = {"traceheader": {
    "metainformation": {
        "name": "",
        "source": "",
        "description": "",
        "date": "",
        "user": ""
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
        "tracedatadescription": "",
        "tracedata": []
    }
}
