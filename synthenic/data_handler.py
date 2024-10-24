import pandas as pd

def read_csv(file):
    return pd.read_csv(file)

def save_output(data, output_format, output_path):
    if output_format == 'csv':
        data.to_csv(output_path, index=False)
    elif output_format == 'json':
        data.to_json(output_path, orient='records', indent=2)
    else:
        raise ValueError(f"Unsupported output format: {output_format}")
