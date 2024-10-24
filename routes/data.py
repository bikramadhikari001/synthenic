from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, send_file, current_app, g
from werkzeug.utils import secure_filename
import os
import pandas as pd
import numpy as np
from database import add_project, get_project, get_user_projects, delete_project, get_project_details
from synthenic.models import generate_synthetic_data
from synthenic.data_handler import read_csv, save_output
import json
import math
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

data = Blueprint('data', __name__)

def clean_for_json(obj):
    """Clean data structure to ensure JSON serialization works"""
    if isinstance(obj, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64,
                       np.uint8, np.uint16, np.uint32, np.uint64)):
        return int(obj)
    elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return clean_for_json(obj.tolist())
    elif isinstance(obj, (list, tuple)):
        return [clean_for_json(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: clean_for_json(value) for key, value in obj.items()}
    elif pd.isna(obj):
        return None
    return obj

def calculate_data_quality_score(df, column):
    """Calculate data quality metrics"""
    try:
        # Completeness
        completeness = 1 - (df[column].isnull().sum() / len(df))
        
        # Consistency (check for values within expected range)
        q1, q3 = df[column].quantile([0.25, 0.75])
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        consistency = (df[column].between(lower_bound, upper_bound).sum() / len(df))
        
        # Overall quality score
        quality_score = (completeness * 0.5 + consistency * 0.5)
        
        return {
            'completeness': round(completeness * 100, 2),
            'consistency': round(consistency * 100, 2),
            'quality_score': round(quality_score * 100, 2)
        }
    except Exception as e:
        logger.error(f"Error calculating quality score for column {column}: {str(e)}")
        return {
            'completeness': 0,
            'consistency': 0,
            'quality_score': 0
        }

def calculate_correlation_score(df):
    """Calculate overall correlation score"""
    try:
        corr_matrix = df.corr()
        # Calculate average absolute correlation
        score = np.abs(corr_matrix.values).mean()
        return round(score * 100, 2)
    except Exception as e:
        logger.error(f"Error calculating correlation score: {str(e)}")
        return 0

@data.route('/upload-csv', methods=['POST'])
def upload_csv():
    logger.info("Entering upload_csv function")
    if 'user' not in session:
        logger.warning("User not in session, redirecting to login")
        return redirect(url_for('auth.login'))
    
    if 'file' not in request.files:
        logger.error("No file part in the request")
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        logger.error("No selected file")
        return jsonify({"error": "No selected file"}), 400
    
    if file and file.filename.endswith('.csv'):
        filename = secure_filename(file.filename)
        session['project_name'] = os.path.splitext(filename)[0]
        
        temp_dir = os.path.join(current_app.root_path, 'temp')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        file_path = os.path.join(temp_dir, filename)
        file.save(file_path)
        
        try:
            df = pd.read_csv(file_path)
            analysis = analyze_data(df)
            session['csv_analysis'] = analysis
            session['csv_file_path'] = file_path
            
            logger.info(f"Redirecting to data_overview with analysis: {analysis}")
            return redirect(url_for('data.data_overview'))
        except Exception as e:
            logger.error(f"Error processing CSV file: {str(e)}")
            return jsonify({"error": "Error processing CSV file"}), 400
    else:
        logger.error("Invalid file format")
        return jsonify({"error": "Invalid file format. Please upload a CSV file."}), 400

@data.route('/data-overview')
def data_overview():
    logger.info("Entering data_overview function")
    if 'user' not in session:
        logger.warning("User not in session, redirecting to login")
        return redirect(url_for('auth.login'))
    
    if 'csv_analysis' not in session:
        logger.warning("csv_analysis not in session, redirecting to dashboard")
        return redirect(url_for('main.dashboard'))
    
    analysis = session['csv_analysis']
    project_name = session.get('project_name', '')
    logger.info(f"Rendering data_overview.html with analysis: {analysis}")
    return render_template('data_overview.html', 
                         user=session['user'], 
                         analysis=analysis,
                         project_name=project_name)

@data.route('/generate', methods=['POST'])
def generate_data():
    logger.info("Entering generate_data function")
    if 'user' not in session:
        logger.error("User not in session")
        return jsonify({"error": "Unauthorized"}), 401
    
    if 'csv_file_path' not in session:
        logger.error("No CSV file path in session")
        return jsonify({"error": "No CSV file uploaded"}), 400
    
    project_name = request.form.get('project_name')
    model_name = request.form.get('model')
    samples = request.form.get('samples')
    selected_columns = json.loads(request.form.get('selected_columns'))
    model_params = json.loads(request.form.get('model_params', '{}'))

    if not all([project_name, model_name, samples, selected_columns]):
        logger.error("Missing required parameters")
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        samples = int(samples)
    except ValueError:
        logger.error("Invalid sample size")
        return jsonify({"error": "Invalid sample size"}), 400

    try:
        data = read_csv(session['csv_file_path'])
        data = data[selected_columns]
        
        synthetic_data = generate_synthetic_data(data, model_name, samples, model_params)
        
        output_dir = os.path.join(current_app.root_path, 'output')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        output_path = os.path.join(output_dir, f'synthetic_data_{project_name}.csv')
        save_output(synthetic_data, 'csv', output_path)
        
        project_id = add_project(g._database, session['user']['user_id'], project_name, model_name, samples, 'csv', output_path)
        
        if project_id is None:
            logger.error("Failed to save project to database")
            return jsonify({"error": "Failed to save project"}), 500
        
        project = get_project(g._database, project_id)
        if not project:
            logger.error(f"Project {project_id} not found after saving")
            return jsonify({"error": "Project not found after saving"}), 500
            
        session.pop('csv_file_path', None)
        session.pop('csv_analysis', None)
        session.pop('project_name', None)
        
        logger.info(f"Successfully generated data, redirecting to insights for project {project_id}")
        return redirect(url_for('data.data_insights', project_id=project_id))
    except Exception as e:
        logger.error(f"Error generating data: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@data.route('/data-insights/<int:project_id>')
def data_insights(project_id):
    logger.info(f"Accessing data insights for project_id: {project_id}")
    
    if 'user' not in session:
        logger.warning("User not in session, redirecting to login")
        return redirect(url_for('auth.login'))
    
    project = get_project_details(g._database, project_id)
    logger.info(f"Retrieved project details: {project}")
    
    if not project:
        logger.error(f"Project not found for project_id: {project_id}")
        return redirect(url_for('main.dashboard'))
    
    try:
        logger.info(f"Reading synthetic data from: {project['file_path']}")
        synthetic_data = pd.read_csv(project['file_path'])
        numeric_cols = synthetic_data.select_dtypes(include=[np.number]).columns
        logger.info(f"Found numeric columns: {list(numeric_cols)}")
        
        stats = {
            'column_stats': {},
            'correlations': {},
            'distributions': {},
            'quality_metrics': {},
            'overall_metrics': {}
        }
        
        # Calculate metrics for each numeric column
        for col in numeric_cols:
            logger.info(f"Calculating metrics for column: {col}")
            # Basic statistics
            stats['column_stats'][col] = {
                'mean': float(synthetic_data[col].mean()),
                'median': float(synthetic_data[col].median()),
                'std': float(synthetic_data[col].std()),
                'min': float(synthetic_data[col].min()),
                'max': float(synthetic_data[col].max())
            }
            
            # Distribution data
            hist, bins = np.histogram(synthetic_data[col].dropna(), bins='auto')
            stats['distributions'][col] = {
                'histogram': hist.tolist(),
                'bins': bins.tolist()
            }
            
            # Quality metrics
            stats['quality_metrics'][col] = calculate_data_quality_score(
                synthetic_data, col
            )
        
        # Calculate correlation matrices
        if len(numeric_cols) > 1:
            logger.info("Calculating correlation matrix")
            synth_corr = synthetic_data[numeric_cols].corr()
            logger.info(f"Correlation matrix:\n{synth_corr}")
            
            # Filter significant correlations (abs value > 0.1 to show more relationships)
            significant_correlations = {}
            for col1 in numeric_cols:
                significant_correlations[col1] = {}
                for col2 in numeric_cols:
                    if col1 != col2:  # Only store correlations between different columns
                        corr_value = float(synth_corr.loc[col1, col2])
                        if abs(corr_value) > 0.1:  # Only store significant correlations
                            significant_correlations[col1][col2] = corr_value
            
            logger.info(f"Significant correlations: {significant_correlations}")
            stats['correlations'] = significant_correlations
        
        # Model-specific insights
        model_insights = {
            'gaussian_copula': "Preserves linear correlations and marginal distributions",
            'ctgan': "Handles multi-modal distributions and captures complex patterns",
            'tvae': "Balances privacy and utility through variational encoding"
        }
        
        # Calculate overall correlation score
        correlation_score = calculate_correlation_score(synthetic_data[numeric_cols])
        logger.info(f"Overall correlation score: {correlation_score}")
        
        stats['overall_metrics'] = {
            'model_type': project['model'],
            'model_insights': model_insights.get(project['model'], ""),
            'samples_generated': project['samples'],
            'correlation_preservation': correlation_score,
            'data_quality': round(np.mean([
                stats['quality_metrics'][col]['quality_score'] 
                for col in numeric_cols
            ]), 2)
        }
        
        # Clean data for JSON serialization
        stats = clean_for_json(stats)
        logger.info("Successfully prepared all statistics")
        logger.info(f"Final correlations structure: {stats['correlations']}")
        
        return render_template('data_insights.html', 
                             user=session['user'],
                             project=project,
                             stats=stats)
    except Exception as e:
        logger.error(f"Error in data_insights: {str(e)}", exc_info=True)
        return redirect(url_for('main.dashboard'))

@data.route('/download-project/<int:project_id>')
def download_project(project_id):
    logger.info(f"Attempting to download project {project_id}")
    if 'user' not in session:
        logger.warning("User not in session")
        return jsonify({"error": "Unauthorized"}), 401
    
    project = get_project(g._database, project_id)
    if project and project['user_id'] == session['user']['user_id']:
        logger.info(f"Sending file: {project['file_path']}")
        return send_file(project['file_path'], as_attachment=True)
    else:
        logger.error(f"Project not found or unauthorized: {project_id}")
        return jsonify({"error": "Project not found"}), 404

@data.route('/delete-project/<int:project_id>', methods=['POST'])
def delete_project_route(project_id):
    logger.info(f"Attempting to delete project {project_id}")
    if 'user' not in session:
        logger.warning("User not in session")
        return jsonify({"error": "Unauthorized"}), 401
    
    project = get_project(g._database, project_id)
    if not project or project['user_id'] != session['user']['user_id']:
        logger.error(f"Project not found or unauthorized: {project_id}")
        return jsonify({"error": "Project not found"}), 404
    
    try:
        delete_project(g._database, project_id)
        if os.path.exists(project['file_path']):
            os.remove(project['file_path'])
        logger.info(f"Successfully deleted project {project_id}")
        return jsonify({"success": True, "message": "Project deleted successfully"}), 200
    except Exception as e:
        logger.error(f"Error deleting project: {str(e)}")
        return jsonify({"error": "Failed to delete project"}), 500

def analyze_data(df):
    """Analyze the uploaded CSV data"""
    analysis = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'columns': []
    }
    
    for column in df.columns:
        col_type = str(df[column].dtype)
        unique_values = df[column].nunique()
        missing_values = df[column].isnull().sum()
        
        col_analysis = {
            'name': column,
            'type': col_type,
            'unique_values': int(unique_values),
            'missing_values': int(missing_values)
        }
        
        if col_type in ['int64', 'float64']:
            col_analysis.update({
                'min': float(df[column].min()),
                'max': float(df[column].max()),
                'mean': float(df[column].mean()),
                'std': float(df[column].std())
            })
        
        analysis['columns'].append(col_analysis)
    
    return clean_for_json(analysis)
