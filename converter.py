import pandas as pd
import json


def convert_file(file, columns, name):
    df = pd.read_csv(file, header=0, delimiter=',')
    df.drop(df.columns[columns], axis=1, inplace=True)
    df.to_csv(name, float_format="%e", index=False, header=False)


def get_df(file):
    df = pd.read_csv(file,  delimiter=' ')
    #df.drop(df.columns[columns], axis=1, inplace=True)
    return df


def get_tracedata(file, columns):
    df = pd.read_csv(file, header=0, delimiter=',')
    df.drop(df.columns[columns], axis=1, inplace=True)
    return df.to_dict()


def print_characteristics(file):
    df = pd.read_csv(file, header=0, delimiter=',')
    mean = df.mean()
    median = df.median()
    skew = df.skew()
    corr = df.corr()
    kurtosis = df.kurtosis()
    mm = mean / median


example_trc = {"traceheader": {
    "metainformation": {
        "name": "oneswarm-timing-attack-trace.csv",
        "source": "UMass Tracerepository",
        "description": "Result of a simple timing attack on the OneSwarm peer-to-peer data sharing network",
        "date": "13.11.2021",
        "user": "Dennis Ziebart"
    },
    "statistical characteristics": {
        "mean": 0,
        "median": 1633.619,
        "skew": 0.581348,
        "kurtosis": -0.66219,
        "correlation": 1.476591e+03,
    }
},
    "tracebody": {
        "data description": "Shows the delay during the resulting from the timing-attack",
        "tracedata": get_tracedata('oneswarm-timing-attack-trace.csv', [0])
    }
}

example_trc["tracebody"]["tracedata"] = open('result_oneswarm.trace', 'r').read().split('\n')
example_trc["traceheader"]["statistical characteristics"]["mean"] = example_trc["tracebody"]["tracedata"]

#print(example_trc["tracebody"]["tracedata"])

get_df('result_oneswarm.trace')

with open('result.json', 'w') as fp:
    json.dump(example_trc, fp, indent=4)

# convert_file('oneswarm-timing-attack-trace.csv', [0], 'result_oneswarm.trace')
# convert_file('ask.csv', [0,3,4,5,6,7,8,], 'result_ask.trace')
# print_characteristics('result_oneswarm.trace')
