import pandas as pd

def read_reference_ids(filepath):
    df = pd.read_excel(filepath)
    return df.to_dict(orient="records")
