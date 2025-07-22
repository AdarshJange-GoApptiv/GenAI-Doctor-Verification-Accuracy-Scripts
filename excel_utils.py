import pandas as pd

def write_reference_ids(rows, output_path):
    df = pd.DataFrame(rows)
    df.to_excel(output_path, index=False)

def read_image_uuid_and_truth(input_path):
    df = pd.read_excel(input_path)
    return df.to_dict(orient="records")
 