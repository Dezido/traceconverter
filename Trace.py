import pandas as pd
import json

from select import error


class Trace:
    def __init__(self, traceheader, tracebody):
        self.traceheader = traceheader
        self.tracebody = tracebody


class Traceheader:
    def __init__(self, metainformation, statistical_information):
        self.metainformation = metainformation
        self.statistical_information = statistical_information


class Tracebody:
    def __init__(self, data_description, tracedata):
        self.data_description = data_description
        self.tracedata = tracedata


tracedata = [1.476591e+03,
             3.803939e+03,
             2.698986e+03,
             1.648804e+03,
             1.062394e+03,
             1.017206e+03]

data_description = "Shows the delay during the resulting from the timing -attack"

metainformation = {"name": "oneswarm-timing-attack-trace.csv",
                   "source": "UMass Tracerepository",
                   "description": "Result of a simple timing attack on the OneSwarm peer -to-peer data sharing network",
                   "date": "13.11.2021",
                   "user": "Dennis Ziebart"
                   }

statistical_information = {"Mittelwert": 1817.484124,
                           "Median": 1633.619,
                           "Schiefe": 0.581348,
                           "Wölbung": -0.66219,
                           "Korrelation": 1.0,
                           "Verhältnis Mittelwert/Median": 0}

statistical_information["Verhältnis Mittelwert/Median"] = statistical_information["Mittelwert"] / \
                                                          statistical_information["Median"]

# print(statistical_information)

tbd = Tracebody(data_description, tracedata)

thd = Traceheader(metainformation, statistical_information)

mytrace = Trace(thd, tbd)

# print(mytrace)

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
        "tracedata": [1, 2, 3, 4, 5]
    }
}

print(example_trc)

with open('result.json', 'w') as fp:
    json.dump(example_trc, fp, indent=4)
