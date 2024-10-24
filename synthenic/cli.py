import click
from models import generate_synthetic_data
from data_handler import read_csv, save_output
from utils import validate_input

@click.command()
@click.option('--input', required=True, type=click.Path(exists=True), help='Path to the input CSV file')
@click.option('--output', required=True, type=click.Path(), help='Path to save the generated synthetic data')
@click.option('--model', type=click.Choice(['gaussian_copula', 'ctgan', 'tvae']), default='gaussian_copula', help='Model to use for synthetic data generation')
@click.option('--samples', default=100, type=int, help='Number of synthetic samples to generate')
@click.option('--output-format', type=click.Choice(['csv', 'json']), default='csv', help='Output format for synthetic data')
def run_cli(input, output, model, samples, output_format):
    """Generate synthetic data based on the input CSV file."""
    try:
        validate_input(input, output, model, samples, output_format)
        
        data = read_csv(input)
        click.echo(f"Loaded input data from {input}")

        synthetic_data = generate_synthetic_data(data, model, samples)
        click.echo(f"Generated {samples} rows of synthetic data using {model} model")

        save_output(synthetic_data, output_format, output)
        click.echo(f"Saved synthetic data to {output} in {output_format} format")

    except Exception as e:
        click.echo(f"An error occurred: {str(e)}", err=True)
        raise click.Abort()

if __name__ == '__main__':
    run_cli()
