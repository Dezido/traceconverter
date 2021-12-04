import pandas as pd
import json


def convert_file(file, columns, name):
    df = pd.read_csv(file, header=0, delimiter=',')
    df.drop(df.columns[columns], axis=1, inplace=True)
    df.to_csv(name, float_format="%e", index=False, header=False)



def print_characteristics(file):
    df = pd.read_csv(file, header=0, delimiter=',')
    mean = df.mean()
    median = df.median()
    skew = df.skew()
    corr = df.corr()
    kurtosis = df.kurtosis()
    mm = mean / median

d=[1.476591e+03,
3.803939e+03,
2.698986e+03,
8.325240e+02,
1.095765e+03,
4.405670e+02,
3.917380e+03,
1.269418e+03,
2.990765e+03,
1.468792e+03]
df = pd.DataFrame(data=d)
print(d)

example_trc = {"traceheader": {
    "metainformation": {
        "name": "oneswarm-timing-attack-trace.csv",
        "source": "UMass Tracerepository",
        "description": "Result of a simple timing attack on the OneSwarm peer-to-peer data sharing network",
        "date": "13.11.2021",
        "user": "Dennis Ziebart"
    },
    "statistical characteristics": {
        "mean": 1817.484124,
        "median": 1633.619,
        "skew": 0.581348,
        "kurtosis": -0.66219,
        "correlation": 1.476591e+03,
    }
},
    "tracebody": {
        "data description": "Shows the delay during the resulting from the timing-attack",
        #"tracedata":  pd.read_csv('result_oneswarm.trace', header=0, delimiter=',')

    }
}

example_trc["tracebody"]["tracedata"] = convert_file('oneswarm-timing-attack-trace.csv', [0], 'result_oneswarm')
print(example_trc["tracebody"]["tracedata"])

# math_on_trace(columns, operation)

# clean traces
# bring entries to

# python -i filename
# function(arguments)

convert_file('oneswarm-timing-attack-trace.csv', [0], 'result_oneswarm.trace')

# convert_file('ask.csv', [0,3,4,5,6,7,8,], 'result_ask.trace')
# print_characteristics('result_oneswarm.trace')
