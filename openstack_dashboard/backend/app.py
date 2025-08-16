from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import openstack
import os
from dotenv import load_dotenv
from datetime import datetime
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['OPENSTACK_AUTH_URL'] = os.getenv('OPENSTACK_AUTH_URL')
app.config['OPENSTACK_PROJECT_NAME'] = os.getenv('OPENSTACK_PROJECT_NAME')
app.config['OPENSTACK_USERNAME'] = os.getenv('OPENSTACK_USERNAME')
app.config['OPENSTACK_PASSWORD'] = os.getenv('OPENSTACK_PASSWORD')

CORS(app, supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins="*")

class OpenStackManager:
    def __init__(self):
        self.conn = None
        self.authenticated = False
    
    def authenticate(self, auth_url, username, password, project_name):
        try:
            self.conn = openstack.connect(
                auth_url=auth_url,
                username=username,
                password=password,
                project_name=project_name
            )
            self.authenticated = True
            return True
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False
    
    def get_instances(self):
        if not self.authenticated:
            return []
        try:
            instances = []
            for server in self.conn.compute.servers():
                instances.append({
                    'id': server.id,
                    'name': server.name,
                    'status': server.status,
                    'flavor': server.flavor['id'] if server.flavor else None,
                    'image': server.image['id'] if server.image else None,
                    'created': server.created,
                    'networks': list(server.addresses.keys())
                })
            return instances
        except Exception as e:
            print(f"Error getting instances: {e}")
            return []
    
    def get_networks(self):
        if not self.authenticated:
            return []
        try:
            networks = []
            for network in self.conn.network.networks():
                networks.append({
                    'id': network.id,
                    'name': network.name,
                    'status': network.status,
                    'admin_state_up': network.admin_state_up,
                    'shared': network.shared,
                    'subnets': [subnet.id for subnet in self.conn.network.subnets(network_id=network.id)]
                })
            return networks
        except Exception as e:
            print(f"Error getting networks: {e}")
            return []
    
    def get_volumes(self):
        if not self.authenticated:
            return []
        try:
            volumes = []
            for volume in self.conn.block_storage.volumes():
                volumes.append({
                    'id': volume.id,
                    'name': volume.name,
                    'size': volume.size,
                    'status': volume.status,
                    'volume_type': volume.volume_type,
                    'attachments': volume.attachments
                })
            return volumes
        except Exception as e:
            print(f"Error getting volumes: {e}")
            return []
    
    def get_images(self):
        if not self.authenticated:
            return []
        try:
            images = []
            for image in self.conn.image.images():
                images.append({
                    'id': image.id,
                    'name': image.name,
                    'status': image.status,
                    'size': image.size,
                    'created': image.created,
                    'visibility': image.visibility
                })
            return images
        except Exception as e:
            print(f"Error getting images: {e}")
            return []
    
    def create_instance(self, name, image_id, flavor_id, network_id):
        if not self.authenticated:
            return None
        try:
            server = self.conn.compute.create_server(
                name=name,
                image_id=image_id,
                flavor_id=flavor_id,
                networks=[{'uuid': network_id}]
            )
            return server
        except Exception as e:
            print(f"Error creating instance: {e}")
            return None

# Global OpenStack manager
openstack_mgr = OpenStackManager()

@app.route('/api/auth', methods=['POST'])
def authenticate():
    data = request.get_json()
    auth_url = data.get('auth_url')
    username = data.get('username')
    password = data.get('password')
    project_name = data.get('project_name')
    
    if openstack_mgr.authenticate(auth_url, username, password, project_name):
        session['authenticated'] = True
        return jsonify({'success': True, 'message': 'Authentication successful'})
    else:
        return jsonify({'success': False, 'message': 'Authentication failed'}), 401

@app.route('/api/instances', methods=['GET'])
def get_instances():
    if not session.get('authenticated'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    instances = openstack_mgr.get_instances()
    return jsonify(instances)

@app.route('/api/networks', methods=['GET'])
def get_networks():
    if not session.get('authenticated'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    networks = openstack_mgr.get_networks()
    return jsonify(networks)

@app.route('/api/volumes', methods=['GET'])
def get_volumes():
    if not session.get('authenticated'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    volumes = openstack_mgr.get_volumes()
    return jsonify(volumes)

@app.route('/api/images', methods=['GET'])
def get_images():
    if not session.get('authenticated'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    images = openstack_mgr.get_images()
    return jsonify(images)

@app.route('/api/instances', methods=['POST'])
def create_instance():
    if not session.get('authenticated'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    name = data.get('name')
    image_id = data.get('image_id')
    flavor_id = data.get('flavor_id')
    network_id = data.get('network_id')
    
    server = openstack_mgr.create_instance(name, image_id, flavor_id, network_id)
    if server:
        return jsonify({'success': True, 'server_id': server.id})
    else:
        return jsonify({'success': False, 'message': 'Failed to create instance'}), 500

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    if not session.get('authenticated'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        instances = openstack_mgr.get_instances()
        networks = openstack_mgr.get_networks()
        volumes = openstack_mgr.get_volumes()
        images = openstack_mgr.get_images()
        
        dashboard_data = {
            'instances': {
                'total': len(instances),
                'running': len([i for i in instances if i['status'] == 'ACTIVE']),
                'stopped': len([i for i in instances if i['status'] == 'SHUTOFF']),
                'error': len([i for i in instances if i['status'] == 'ERROR'])
            },
            'networks': {
                'total': len(networks),
                'active': len([n for n in networks if n['admin_state_up']])
            },
            'volumes': {
                'total': len(volumes),
                'available': len([v for v in volumes if v['status'] == 'available']),
                'in_use': len([v for v in volumes if v['status'] == 'in-use'])
            },
            'images': {
                'total': len(images),
                'active': len([i for i in images if i['status'] == 'active'])
            }
        }
        
        return jsonify(dashboard_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'data': 'Connected to OpenStack Dashboard'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
