"""
Burme AI - Flask Application
Multi-provider AI API rotation engine with admin dashboard
"""

import json
import os
import uuid
import bcrypt
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, session, redirect, url_for, render_template, jsonify, g
from flask_cors import CORS
import markdown
import requests

# ============================================================================
# CONFIGURATION
# ============================================================================

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'burme-ai-secret-key-change-in-production')

# Enable CORS
CORS(app, supports_credentials=True)

# Data file path - use absolute path for Vercel compatibility
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data.json')

# Provider configuration
PROVIDERS = [
    {
        'name': 'Groq',
        'env_key': 'GROQ_API_KEY',
        'base_url': 'https://api.groq.com/openai/v1/chat/completions',
        'model': 'llama-3.3-70b-versatile',
        'headers': lambda key: {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
    },
    {
        'name': 'Cerebras',
        'env_key': 'CEREBRAS_API_KEY',
        'base_url': 'https://api.cerebras.ai/v1/chat/completions',
        'model': 'llama-3.3-70b',
        'headers': lambda key: {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
    },
    {
        'name': 'OpenRouter',
        'env_key': 'OPENROUTER_API_KEY',
        'base_url': 'https://openrouter.ai/api/v1/chat/completions',
        'model': 'meta-llama/llama-3.3-70b-instruct',
        'headers': lambda key: {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json', 'HTTP-Referer': 'https://burme.ai', 'X-Title': 'Burme AI'}
    },
    {
        'name': 'NVIDIA',
        'env_key': 'NVIDIA_API_KEY',
        'base_url': 'https://api.nvidia.com/v1/chat/completions',
        'model': 'nvidia/llama-3.3-nemoir-70b-instruct',
        'headers': lambda key: {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
    },
    {
        'name': 'HuggingFace',
        'env_key': 'HUGGINGFACE_API_KEY',
        'base_url': 'https://api-inference.huggingface.co/meta-llama/Llama-3.3-70B-Instruct',
        'model': 'meta-llama/Llama-3.3-70B-Instruct',
        'headers': lambda key: {'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'}
    }
]


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def load_data():
    """Load data from JSON file"""
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {'admin': {}, 'users': [], 'logs': []}


def save_data(data):
    """Save data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def generate_id(prefix='id'):
    """Generate unique ID"""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def log_action(action, user='system', details=''):
    """Log an action to data.json"""
    data = load_data()
    data['logs'].append({
        'id': generate_id('log'),
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'action': action,
        'user': user,
        'details': details
    })
    # Keep only last 1000 logs
    if len(data['logs']) > 1000:
        data['logs'] = data['logs'][-1000:]
    save_data(data)


def get_api_keys(env_key):
    """Get API keys from environment variable (supports comma-separated)"""
    keys = os.environ.get(env_key, '')
    if not keys:
        return []
    return [k.strip() for k in keys.split(',') if k.strip()]


def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password, password_hash):
    """Verify password against hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False


def login_required(f):
    """Decorator requiring authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator requiring admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# API ROTATION ENGINE
# ============================================================================

class APIRotationEngine:
    """Multi-provider API rotation with failover"""
    
    def __init__(self):
        self.provider_status = {}
        for provider in PROVIDERS:
            self.provider_status[provider['name']] = {
                'status': 'inactive',
                'last_success': None,
                'failure_count': 0,
                'last_error': None
            }
    
    def call_api(self, messages, model=None):
        """Call API with automatic failover"""
        errors = []
        
        for provider in PROVIDERS:
            keys = get_api_keys(provider['env_key'])
            if not keys:
                self.provider_status[provider['name']]['status'] = 'no_keys'
                continue
            
            for key in keys:
                try:
                    result = self._call_provider(provider, key, messages, model)
                    if result:
                        self.provider_status[provider['name']]['status'] = 'active'
                        self.provider_status[provider['name']]['last_success'] = datetime.utcnow().isoformat()
                        self.provider_status[provider['name']]['failure_count'] = 0
                        
                        # Log successful call
                        log_action(
                            'api_call',
                            session.get('username', 'anonymous'),
                            f'Success: {provider["name"]}'
                        )
                        
                        return {
                            'success': True,
                            'provider': provider['name'],
                            'response': result
                        }
                except Exception as e:
                    error_msg = str(e)
                    errors.append(f"{provider['name']}: {error_msg}")
                    self.provider_status[provider['name']]['failure_count'] += 1
                    self.provider_status[provider['name']]['last_error'] = error_msg
                    self.provider_status[provider['name']]['status'] = 'error'
                    
                    log_action(
                        'api_error',
                        session.get('username', 'anonymous'),
                        f'{provider["name"]}: {error_msg}'
                    )
                    continue
            
            # All keys for this provider failed, move to next
            self.provider_status[provider['name']]['status'] = 'failed'
        
        return {
            'success': False,
            'error': 'All providers failed',
            'details': errors
        }
    
    def _call_provider(self, provider, key, messages, model=None):
        """Make API call to a specific provider"""
        target_model = model or provider['model']
        headers = provider['headers'](key)
        
        payload = {
            'model': target_model,
            'messages': messages,
            'temperature': 0.7,
            'max_tokens': 2048,
            'stream': False
        }
        
        # Different handling for certain providers
        if provider['name'] == 'HuggingFace':
            # HuggingFace uses different endpoint structure
            payload = {
                'inputs': messages[-1]['content'] if messages else '',
                'parameters': {
                    'max_new_tokens': 2048,
                    'temperature': 0.7
                }
            }
        
        try:
            response = requests.post(
                provider['base_url'],
                headers=headers,
                json=payload,
                timeout=60
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                raise Exception('Rate limited (429)')
            
            # Handle auth errors
            if response.status_code in [401, 403]:
                raise Exception(f'Auth error ({response.status_code})')
            
            # Handle server errors
            if response.status_code >= 500:
                raise Exception(f'Server error ({response.status_code})')
            
            # Handle success
            if response.status_code == 200:
                data = response.json()
                
                # Parse response based on provider
                if provider['name'] == 'Groq':
                    return data['choices'][0]['message']['content']
                elif provider['name'] == 'OpenRouter':
                    return data['choices'][0]['message']['content']
                elif provider['name'] == 'Cerebras':
                    return data['choices'][0]['message']['content']
                elif provider['name'] == 'NVIDIA':
                    return data['choices'][0]['message']['content']
                elif provider['name'] == 'HuggingFace':
                    return data.get('generated_text', '')
                
                return str(data)
            
            return None
            
        except requests.exceptions.RequestException as e:
            raise Exception(f'Request failed: {str(e)}')
    
    def test_provider(self, provider_name):
        """Test a specific provider"""
        for provider in PROVIDERS:
            if provider['name'] == provider_name:
                keys = get_api_keys(provider['env_key'])
                if not keys:
                    return {'success': False, 'error': 'No API keys configured'}
                
                try:
                    result = self._call_provider(
                        provider,
                        keys[0],
                        [{'role': 'user', 'content': 'Hello'}]
                    )
                    
                    self.provider_status[provider['name']]['status'] = 'active'
                    self.provider_status[provider['name']]['last_success'] = datetime.utcnow().isoformat()
                    self.provider_status[provider['name']]['failure_count'] = 0
                    
                    return {'success': True, 'response': result}
                except Exception as e:
                    self.provider_status[provider['name']]['status'] = 'error'
                    self.provider_status[provider['name']]['last_error'] = str(e)
                    return {'success': False, 'error': str(e)}
        
        return {'success': False, 'error': 'Provider not found'}


# Initialize API engine
api_engine = APIRotationEngine()


# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Get Started / Login page"""
    if 'admin' in session or 'user_id' in session:
        return redirect(url_for('chat'))
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    """Process login"""
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    
    if not username or not password:
        return render_template('login.html', error='Please enter username and password')
    
    data = load_data()
    
    # Check admin login
    if data.get('admin', {}).get('username') == username:
        if verify_password(password, data['admin']['password_hash']):
            session['admin'] = username
            session['username'] = username
            log_action('admin_login', username, 'Admin logged in')
            return redirect(url_for('dashboard'))
        else:
            log_action('login_failed', username, 'Admin login failed')
            return render_template('login.html', error='Invalid credentials')
    
    # Check user login
    for user in data.get('users', []):
        if user['username'] == username and user.get('active', True):
            if verify_password(password, user['password_hash']):
                session['user_id'] = user['id']
                session['username'] = username
                log_action('user_login', username, 'User logged in')
                return redirect(url_for('chat'))
            else:
                log_action('login_failed', username, 'User login failed')
                return render_template('login.html', error='Invalid credentials')
    
    log_action('login_failed', username, 'User not found')
    return render_template('login.html', error='Invalid credentials')


@app.route('/logout')
def logout():
    """Logout"""
    username = session.get('username', 'unknown')
    session.clear()
    log_action('logout', username, 'Logged out')
    return redirect(url_for('index'))


@app.route('/chat')
@login_required
def chat():
    """Chat interface"""
    return render_template('chat.html', username=session.get('username', 'User'))


@app.route('/api/chat', methods=['POST'])
def api_chat():
    """AI Chat API endpoint"""
    data = request.get_json()
    message = data.get('message', '')
    model = data.get('model')
    history = data.get('history', [])
    
    if not message:
        return jsonify({'success': False, 'error': 'Empty message'})
    
    # Build messages from history + new message
    messages = history + [{'role': 'user', 'content': message}]
    
    # Call API with rotation
    result = api_engine.call_api(messages, model)
    
    return jsonify(result)


@app.route('/dashboard')
@admin_required
def dashboard():
    """Dashboard with user management"""
    data = load_data()
    return render_template(
        'dashboard.html',
        users=data.get('users', []),
        logs=data.get('logs', []),
        username=session.get('username', 'Admin')
    )


@app.route('/api/users', methods=['GET', 'POST', 'PUT', 'DELETE'])
@admin_required
def users_api():
    """User CRUD API"""
    data = load_data()
    
    if request.method == 'GET':
        return jsonify(data.get('users', []))
    
    if request.method == 'POST':
        # Add new user
        user_data = request.get_json()
        username = user_data.get('username', '').strip()
        password = user_data.get('password', '')
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password required'})
        
        # Check if username exists
        for user in data['users']:
            if user['username'] == username:
                return jsonify({'success': False, 'error': 'Username already exists'})
        
        new_user = {
            'id': generate_id('user'),
            'username': username,
            'password_hash': hash_password(password),
            'created_at': datetime.utcnow().isoformat() + 'Z',
            'active': True
        }
        data['users'].append(new_user)
        save_data(data)
        
        log_action('user_created', session.get('username', 'admin'), f'Created user: {username}')
        return jsonify({'success': True, 'user': new_user})
    
    if request.method == 'PUT':
        # Update user
        user_data = request.get_json()
        user_id = user_data.get('id')
        
        for user in data['users']:
            if user['id'] == user_id:
                if 'username' in user_data:
                    user['username'] = user_data['username']
                if 'password' in user_data:
                    user['password_hash'] = hash_password(user_data['password'])
                if 'active' in user_data:
                    user['active'] = user_data['active']
                
                save_data(data)
                log_action('user_updated', session.get('username', 'admin'), f'Updated user: {user["username"]}')
                return jsonify({'success': True, 'user': user})
        
        return jsonify({'success': False, 'error': 'User not found'})
    
    if request.method == 'DELETE':
        # Delete (deactivate) user
        user_id = request.args.get('id')
        
        for user in data['users']:
            if user['id'] == user_id:
                user['active'] = False
                save_data(data)
                log_action('user_deleted', session.get('username', 'admin'), f'Deleted user: {user["username"]}')
                return jsonify({'success': True})
        
        return jsonify({'success': False, 'error': 'User not found'})


@app.route('/api/logs', methods=['GET'])
@admin_required
def logs_api():
    """Get logs API"""
    data = load_data()
    return jsonify(data.get('logs', []))


@app.route('/api-status')
def api_status():
    """API status page"""
    status = api_engine.provider_status
    return render_template('status.html', status=status)


@app.route('/api/test-provider', methods=['POST'])
def test_provider_api():
    """Test a specific provider"""
    data = request.get_json()
    provider_name = data.get('provider')
    
    result = api_engine.test_provider(provider_name)
    return jsonify(result)


@app.route('/docs')
def docs():
    """Documentation page"""
    return render_template('docs.html')


@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')


# ============================================================================
# STATIC FILES (for Vercel)
# ============================================================================

@app.route('/static/favicon.svg')
def favicon():
    """Serve favicon"""
    import os
    favicon_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'favicon.svg')
    from flask import send_file
    return send_file(favicon_path, mimetype='image/svg+xml')


@app.route('/static/manifest.json')
def manifest():
    """Serve PWA manifest"""
    import os
    manifest_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'manifest.json')
    from flask import send_file, json
    return send_file(manifest_path, mimetype='application/json')


@app.route('/static/sw.js')
def service_worker():
    """Serve service worker"""
    import os
    sw_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'sw.js')
    from flask import send_file
    return send_file(sw_path, mimetype='application/javascript')


# ============================================================================
# MARKDOWN FILTER
# ============================================================================

@app.template_filter('markdown')
def markdown_filter(text):
    """Convert markdown to HTML"""
    if not text:
        return ''
    return markdown.markdown(text, extensions=['fenced_code', 'tables'])


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)