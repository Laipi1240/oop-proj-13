import pandas as pd

df = pd.read_csv(".txt", delimiter=':')
print(df.sort_values(by='Skin', ascending=True))
print(df.iloc[1:5])