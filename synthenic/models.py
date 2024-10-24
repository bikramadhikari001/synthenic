import numpy as np
from sdv.metadata import SingleTableMetadata
from sdv.single_table import GaussianCopulaSynthesizer, CTGANSynthesizer, TVAESynthesizer

def create_metadata(data):
    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(data)
    return metadata

def generate_synthetic_data(data, model_name, samples, model_params=None):
    metadata = create_metadata(data)
    model_params = model_params or {}
    
    if model_name == 'gaussian_copula':
        model = GaussianCopulaSynthesizer(
            metadata,
            enforce_min_max_values=True
        )
    elif model_name == 'ctgan':
        epochs = int(model_params.get('ctgan-epochs', 300))
        batch_size = int(model_params.get('ctgan-batch', 500))
        model = CTGANSynthesizer(
            metadata,
            epochs=epochs,
            batch_size=batch_size,
            cuda=False  # Set to True if GPU is available
        )
    elif model_name == 'tvae':
        epochs = int(model_params.get('tvae-epochs', 300))
        batch_size = int(model_params.get('tvae-batch', 500))
        model = TVAESynthesizer(
            metadata,
            epochs=epochs,
            batch_size=batch_size,
            cuda=False  # Set to True if GPU is available
        )
    else:
        raise ValueError(f"Unsupported model: {model_name}")
    
    # Log training parameters
    print(f"Training {model_name} with parameters: {model_params}")
    
    # Fit the model
    model.fit(data)
    
    # Generate synthetic data
    synthetic_data = model.sample(num_rows=samples)
    
    # Post-processing for numeric columns
    numeric_columns = data.select_dtypes(include=[np.number]).columns
    for column in numeric_columns:
        if column in synthetic_data.columns:
            # Round to the same number of decimal places as in the original data
            decimals = data[column].apply(lambda x: str(x).split('.')[-1]).str.len().max()
            synthetic_data[column] = synthetic_data[column].round(decimals)
            
            # Clip to the range of the original data
            synthetic_data[column] = synthetic_data[column].clip(data[column].min(), data[column].max())
    
    return synthetic_data
