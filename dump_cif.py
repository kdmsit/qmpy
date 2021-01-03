import pandas as pd
from qmpy import *

# data=pd.read_csv("experimental_prop.csv").values[:,0]
# for i in range(len(data)):
#     composition=data[0]
#     entry=Element.get(composition)
# print(entry)


# s = io.poscar.read('qmpy/io/files/POSCAR_BCC')
s = io.cif.read('qmpy/io/files/fe3o4.cif')
print(s)