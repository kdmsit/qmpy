import pandas as pd
from qmpy import *

data=pd.read_csv("experimental_prop.csv").values[:,0]
composition=data[0]

entry=Element.get(composition)
print(entry)
print("Hello")