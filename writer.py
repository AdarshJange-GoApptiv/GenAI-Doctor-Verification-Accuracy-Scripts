import pandas as pd

def write_accuracy_report(data, path):
    df = pd.DataFrame(data)
    df.to_excel(path, index=False)