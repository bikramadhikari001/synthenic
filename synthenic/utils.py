import os

def validate_input(input_file, output_file, model, samples, output_format):
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    if not input_file.lower().endswith('.csv'):
        raise ValueError("Input file must be a CSV file")
    
    if samples <= 0:
        raise ValueError("Number of samples must be greater than 0")
    
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        raise FileNotFoundError(f"Output directory does not exist: {output_dir}")
    
    if model not in ['gaussian_copula', 'ctgan', 'tvae']:
        raise ValueError(f"Unsupported model: {model}")
    
    if output_format not in ['csv', 'json']:
        raise ValueError(f"Unsupported output format: {output_format}")
