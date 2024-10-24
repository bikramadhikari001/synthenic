import sqlitecloud
from datetime import datetime

def get_db_connection(db_path=None):
    # SQLite Cloud connection string
    connection_string = "sqlitecloud://nujaxhhmhk.sqlite.cloud:8860?apikey=qoGc7qTB8j3ojaVCn1MPCxilBfXwpSpFuj1Tl59AoyM"
    
    try:
        db = sqlitecloud.connect(connection_string)
        cursor = db.cursor()
        
        # Create database if it doesn't exist
        try:
            cursor.execute("CREATE DATABASE synthenic")
        except Exception as e:
            print(f"Note: {e}")
            
        # Use the database
        cursor.execute("USE DATABASE synthenic")
        
        db.row_factory = lambda cursor, row: {
            column[0]: row[idx] for idx, column in enumerate(cursor.description)
        }
        return db
    except Exception as e:
        print(f"Error connecting to SQLite Cloud: {e}")
        raise

def init_db(db):
    cursor = db.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create projects table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        name TEXT NOT NULL,
        model TEXT NOT NULL,
        samples INTEGER NOT NULL,
        format TEXT NOT NULL,
        file_path TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    db.commit()

def migrate_db(db):
    """Add any new columns or tables here"""
    cursor = db.cursor()
    
    # Example migration: Add a new column to projects table
    try:
        cursor.execute('ALTER TABLE projects ADD COLUMN file_path TEXT')
    except Exception:
        # Column already exists
        pass
    
    db.commit()

def add_user(db, user_id, name, email):
    cursor = db.cursor()
    try:
        cursor.execute(
            'INSERT OR IGNORE INTO users (id, name, email) VALUES (?, ?, ?)',
            (user_id, name, email)
        )
        db.commit()
        return True
    except Exception as e:
        print(f"Error adding user: {e}")
        return False

def get_user(db, user_id):
    cursor = db.cursor()
    try:
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error getting user: {e}")
        return None

def add_project(db, user_id, name, model, samples, format, file_path):
    cursor = db.cursor()
    try:
        cursor.execute('''
            INSERT INTO projects (user_id, name, model, samples, format, file_path)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, name, model, samples, format, file_path))
        db.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Error adding project: {e}")
        return None

def get_project(db, project_id):
    cursor = db.cursor()
    try:
        cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error getting project: {e}")
        return None

def get_project_details(db, project_id):
    cursor = db.cursor()
    try:
        cursor.execute('''
            SELECT 
                projects.id,
                projects.name,
                projects.model,
                projects.samples,
                projects.format,
                projects.file_path,
                projects.created_at,
                users.name as user_name
            FROM projects
            JOIN users ON projects.user_id = users.id
            WHERE projects.id = ?
        ''', (project_id,))
        project = cursor.fetchone()
        if project:
            return project
        return None
    except Exception as e:
        print(f"Error getting project details: {e}")
        return None

def get_user_projects(db, user_id):
    cursor = db.cursor()
    try:
        cursor.execute('SELECT * FROM projects WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting user projects: {e}")
        return []

def delete_project(db, project_id):
    cursor = db.cursor()
    try:
        cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
        db.commit()
        return True
    except Exception as e:
        print(f"Error deleting project: {e}")
        return False

def get_user_stats(db, user_id):
    cursor = db.cursor()
    try:
        # Get total projects
        cursor.execute('SELECT COUNT(*) as count FROM projects WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        total_projects = result['count'] if result else 0

        # Get total samples
        cursor.execute('SELECT SUM(samples) as total FROM projects WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        total_samples = result['total'] if result and result['total'] is not None else 0

        # Get most used model
        cursor.execute('''
            SELECT model, COUNT(*) as count 
            FROM projects 
            WHERE user_id = ? 
            GROUP BY model 
            ORDER BY count DESC 
            LIMIT 1
        ''', (user_id,))
        most_used = cursor.fetchone()
        most_used_model = most_used['model'] if most_used else 'None'

        return {
            'total_projects': total_projects,
            'total_samples': total_samples,
            'most_used_model': most_used_model,
            'success_rate': 100  # Placeholder for now
        }
    except Exception as e:
        print(f"Error getting user stats: {e}")
        return {
            'total_projects': 0,
            'total_samples': 0,
            'most_used_model': 'None',
            'success_rate': 0
        }
