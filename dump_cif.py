import pandas as pd
from qmpy import *

data=pd.read_csv("exp_data/experimental_prop.csv").values[:,0]
print("Hello")
for i in range(len(data)):
    composition=data[0]
    entry=Element.objects.get(symbol=composition)
    structure =Structure(entry)
    io.cif.write(structure, "exp_data/"+str(i)+".cif")

