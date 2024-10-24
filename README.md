# SynthetiQ - Advanced Synthetic Data Generation for Quant Teams

SynthetiQ is a web application that allows quant teams to generate high-quality, statistically accurate synthetic data for financial modeling, risk assessment, and algorithm testing.

## Features

- Advanced synthetic data generation algorithms
- User-friendly web interface
- Secure login system
- Customizable data generation options
- Download synthetic data in CSV or JSON format

## Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <project-directory>
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

To run the Flask application:

```
python app.py
```

The application will start running on `http://127.0.0.1:5000/`. Open this URL in your web browser to access the landing page.

## Using the Web Application

1. Open `http://127.0.0.1:5000/` in your web browser to access the landing page.
2. Explore the various sections of the landing page to learn about SynthetiQ's features and pricing.
3. Click on the "Get Started" or "Start Free Trial" button to open the login modal.
4. Log in using the following credentials:
   - Username: admin
   - Password: password
5. After successful login, you'll be redirected to the generate page.
6. On the generate page:
   - Upload a CSV file using the file input.
   - Select a model from the dropdown menu (Gaussian Copula, CTGAN, or TVAE).
   - Specify the number of samples to generate.
   - Choose the output format (CSV or JSON).
   - Click the "Generate" button to create synthetic data.
7. Once the data is generated, a download link will appear. Click it to download the synthetic data file.

## Project Structure

- `app.py`: Flask application serving the web interface and API endpoints
- `templates/`: Directory containing HTML templates
  - `index.html`: Landing page with various sections and login modal
  - `generate.html`: Data generation page
- `static/`: Directory containing static files
  - `css/landing.css`: CSS styles for the landing page
  - `css/style.css`: CSS styles for the generate page
  - `js/landing.js`: JavaScript functionality for the landing page
  - `js/script.js`: JavaScript functionality for the generate page
- `synthenic/`: Directory containing backend logic
  - `models.py`: Synthetic data generation models
  - `data_handler.py`: File handling and data processing
  - `utils.py`: Utility functions

## Note

This is a basic implementation and may need additional error handling and security measures for production use. The login credentials are hardcoded for demonstration purposes and should be replaced with a proper authentication system in a production environment.
