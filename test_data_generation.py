import pandas as pd
from sdv.metadata import SingleTableMetadata
from sdv.single_table import GaussianCopulaSynthesizer, CTGANSynthesizer, TVAESynthesizer

def test_gaussian_copula():
    print("\nTesting Gaussian Copula...")
    # Create sample data
    data = pd.DataFrame({
        'id': range(1, 7),
        'name': ['John'] * 6,
        'age': [28, 32, 35, 37, 39, 30],
        'city': ['New York', 'London', 'Paris', 'Tokyo', 'Berlin', 'Sydney']
    })
    print("Original Data:")
    print(data)

    # Create metadata
    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(data)

    # Initialize and fit the model
    synthesizer = GaussianCopulaSynthesizer(
        metadata,
        enforce_min_max_values=True
    )
    synthesizer.fit(data)

    # Generate synthetic data
    synthetic_data = synthesizer.sample(num_rows=10)
    print("\nSynthetic Data:")
    print(synthetic_data)
    return True

def test_ctgan():
    print("\nTesting CTGAN...")
    data = pd.DataFrame({
        'id': range(1, 7),
        'name': ['John'] * 6,
        'age': [28, 32, 35, 37, 39, 30],
        'city': ['New York', 'London', 'Paris', 'Tokyo', 'Berlin', 'Sydney']
    })
    print("Original Data:")
    print(data)

    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(data)

    synthesizer = CTGANSynthesizer(
        metadata,
        epochs=10,  # Using smaller number for testing
        batch_size=100
    )
    synthesizer.fit(data)

    synthetic_data = synthesizer.sample(num_rows=10)
    print("\nSynthetic Data:")
    print(synthetic_data)
    return True

def test_tvae():
    print("\nTesting TVAE...")
    data = pd.DataFrame({
        'id': range(1, 7),
        'name': ['John'] * 6,
        'age': [28, 32, 35, 37, 39, 30],
        'city': ['New York', 'London', 'Paris', 'Tokyo', 'Berlin', 'Sydney']
    })
    print("Original Data:")
    print(data)

    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(data)

    synthesizer = TVAESynthesizer(
        metadata,
        epochs=10,  # Using smaller number for testing
        batch_size=100
    )
    synthesizer.fit(data)

    synthetic_data = synthesizer.sample(num_rows=10)
    print("\nSynthetic Data:")
    print(synthetic_data)
    return True

if __name__ == "__main__":
    try:
        print("Starting tests...")
        
        # Test Gaussian Copula
        gc_success = test_gaussian_copula()
        print(f"Gaussian Copula Test: {'Passed' if gc_success else 'Failed'}")
        
        # Test CTGAN
        ctgan_success = test_ctgan()
        print(f"CTGAN Test: {'Passed' if ctgan_success else 'Failed'}")
        
        # Test TVAE
        tvae_success = test_tvae()
        print(f"TVAE Test: {'Passed' if tvae_success else 'Failed'}")
        
        print("\nAll tests completed!")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
