from flask import Blueprint, render_template, session, redirect, url_for, g
from database import get_user_projects, get_user_stats

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    
    # Get user's projects
    projects = get_user_projects(g._database, session['user']['user_id'])
    
    # Get user's stats
    stats = get_user_stats(g._database, session['user']['user_id'])
    
    # Convert projects to list of dictionaries for easier template access
    projects_list = []
    for project in projects:
        projects_list.append({
            'id': project['id'],
            'name': project['name'],
            'model': project['model'],
            'samples': project['samples'],
            'format': project['format'],
            'created_at': project['created_at']
        })
    
    return render_template('dashboard.html',
                         user=session['user'],
                         projects=projects_list,
                         total_projects=stats['total_projects'],
                         total_samples=stats['total_samples'],
                         most_used_model=stats['most_used_model'],
                         success_rate=stats['success_rate'])

@main.route('/support')
def support():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    return render_template('support.html', user=session['user'])
