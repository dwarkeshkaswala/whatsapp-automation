import os
import csv
import glob
import base64
import requests
import tempfile
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv
from datetime import datetime
import json
from werkzeug.utils import secure_filename
from src.whatsapp_bot import WhatsAppBot
from src.database import Database
from apscheduler.schedulers.background import BackgroundScheduler

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ATTACHMENTS_FOLDER = os.path.join(os.getcwd(), 'attachments')
DATA_FOLDER = os.path.join(os.getcwd(), 'data')
INVITATIONS_FOLDER = os.path.join(os.getcwd(), 'invitations')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'csv', 'xlsx', 'mp4', 'mp3', 'zip'}
ALLOWED_CSV_EXTENSIONS = {'csv'}

# PDF Generator API
PDF_GENERATOR_URL = os.getenv('PDF_GENERATOR_URL', 'http://localhost:5173/api/single/generate')

# Bot Configuration - stored in settings file
SETTINGS_FILE = os.path.join(DATA_FOLDER, 'settings.json')

# Default settings
DEFAULT_SETTINGS = {
    'headless': True,  # Browser hidden by default
    'default_country_code': '91'  # India
}

def load_settings():
    """Load settings from file"""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                import json
                settings = json.load(f)
                return {**DEFAULT_SETTINGS, **settings}
    except:
        pass
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    """Save settings to file"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            import json
            json.dump(settings, f)
        return True
    except:
        return False

def get_headless_mode():
    """Get headless mode from settings"""
    settings = load_settings()
    return settings.get('headless', True)

def get_default_country_code():
    """Get default country code from settings"""
    settings = load_settings()
    return settings.get('default_country_code', '91')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(ATTACHMENTS_FOLDER):
    os.makedirs(ATTACHMENTS_FOLDER)
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)
if not os.path.exists(INVITATIONS_FOLDER):
    os.makedirs(INVITATIONS_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ATTACHMENTS_FOLDER'] = ATTACHMENTS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB max file size

# Initialize database in data folder
db = Database(os.path.join(DATA_FOLDER, 'whatsapp_bot.db'))

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Global WhatsApp bot instance
whatsapp_bot = None


def allowed_file(filename, allowed_extensions=ALLOWED_EXTENSIONS):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


@app.route('/')
def index():
    """Main dashboard"""
    if 'logged_in' not in session:
        session['logged_in'] = True
    
    stats = db.get_statistics()
    return render_template('index.html', stats=stats)


@app.route('/data/<path:filename>')
def serve_data_file(filename):
    """Serve files from the data folder"""
    from flask import send_from_directory
    return send_from_directory(DATA_FOLDER, filename)


@app.route('/api/initialize-bot', methods=['POST'])
def initialize_bot():
    """Initialize the WhatsApp bot"""
    global whatsapp_bot
    
    try:
        # Close existing bot if any
        if whatsapp_bot is not None:
            try:
                whatsapp_bot.close()
            except:
                pass
        
        headless = get_headless_mode()
        whatsapp_bot = WhatsAppBot()
        whatsapp_bot.initialize(headless=headless)
        
        return jsonify({
            'success': True, 
            'message': 'Bot initialized successfully',
            'headless': headless
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/close-bot', methods=['POST'])
def close_bot():
    """Close the WhatsApp bot"""
    global whatsapp_bot
    
    try:
        if whatsapp_bot is not None:
            whatsapp_bot.close()
            whatsapp_bot = None
        
        return jsonify({
            'success': True, 
            'message': 'Bot closed successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/get-qr-code', methods=['GET'])
def get_qr_code():
    """Get QR code for WhatsApp login"""
    global whatsapp_bot
    
    try:
        if whatsapp_bot is None:
            return jsonify({
                'success': False, 
                'status': 'not_initialized',
                'error': 'Bot not initialized. Please initialize first.'
            })
        
        qr_data = whatsapp_bot.get_qr_code_base64()
        
        return jsonify({
            'success': True,
            'status': qr_data['status'],
            'qr': qr_data.get('qr'),
            'error': qr_data.get('error')
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get current settings"""
    settings = load_settings()
    return jsonify({'success': True, 'settings': settings})


@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Update settings"""
    try:
        data = request.json
        settings = load_settings()
        
        if 'headless' in data:
            settings['headless'] = bool(data['headless'])
        
        if 'default_country_code' in data:
            settings['default_country_code'] = str(data['default_country_code']).strip().replace('+', '')
        
        if save_settings(settings):
            return jsonify({'success': True, 'message': 'Settings saved'})
        else:
            return jsonify({'success': False, 'error': 'Failed to save settings'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/check-login', methods=['GET'])
def check_login():
    """Check if user is logged in to WhatsApp"""
    global whatsapp_bot
    
    try:
        if whatsapp_bot is None:
            return jsonify({
                'logged_in': False, 
                'status': 'not_initialized',
                'message': 'Bot not initialized'
            })
        
        logged_in = whatsapp_bot.is_logged_in()
        
        return jsonify({
            'logged_in': logged_in,
            'status': 'logged_in' if logged_in else 'waiting_for_scan',
            'message': 'Connected to WhatsApp' if logged_in else 'Please scan QR code'
        })
        
    except Exception as e:
        return jsonify({
            'logged_in': False, 
            'status': 'error',
            'message': str(e)
        })


@app.route('/api/close-bot', methods=['POST'])
def close_bot():
    """Close the WhatsApp bot"""
    global whatsapp_bot
    
    try:
        if whatsapp_bot is not None:
            whatsapp_bot.close()
            whatsapp_bot = None
        
        return jsonify({'success': True, 'message': 'Bot closed successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/send')
def send_page():
    """Send message page"""
    contacts = db.get_all_contacts()
    return render_template('send.html', contacts=contacts)


@app.route('/api/send-message', methods=['POST'])
def send_message():
    """API endpoint to send a WhatsApp message with optional attachment"""
    global whatsapp_bot
    
    try:
        data = request.json
        phone = data.get('phone')
        message = data.get('message', '')
        attachment_path = data.get('attachment_path')
        file_type = data.get('file_type', 'image')  # image, video, audio, document
        
        if not phone:
            return jsonify({'success': False, 'error': 'Phone is required'}), 400
        
        if not message and not attachment_path:
            return jsonify({'success': False, 'error': 'Message or attachment is required'}), 400
        
        # Initialize bot if not already done
        if whatsapp_bot is None:
            whatsapp_bot = WhatsAppBot()
            whatsapp_bot.initialize()
        
        # Send message with or without attachment
        if attachment_path and os.path.exists(attachment_path):
            success = whatsapp_bot.send_message_with_attachment(phone, message, attachment_path, file_type)
        else:
            success = whatsapp_bot.send_message(phone, message)
        
        if success:
            # Save to database
            db.add_message_history(phone, message, 'sent')
            return jsonify({'success': True, 'message': 'Message sent successfully'})
        else:
            db.add_message_history(phone, message, 'failed')
            return jsonify({'success': False, 'error': 'Failed to send message'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/send-bulk', methods=['POST'])
def send_bulk_messages():
    """API endpoint to send bulk messages"""
    global whatsapp_bot
    
    try:
        data = request.json
        contacts = data.get('contacts', [])
        message = data.get('message')
        delay = data.get('delay', 5)  # Delay between messages in seconds
        
        if not contacts or not message:
            return jsonify({'success': False, 'error': 'Contacts and message are required'}), 400
        
        # Initialize bot if not already done
        if whatsapp_bot is None:
            whatsapp_bot = WhatsAppBot()
            whatsapp_bot.initialize()
        
        results = whatsapp_bot.send_bulk_messages(contacts, message, delay)
        
        # Save to database
        for result in results:
            status = 'sent' if result['success'] else 'failed'
            db.add_message_history(result['phone'], message, status)
        
        success_count = sum(1 for r in results if r['success'])
        
        return jsonify({
            'success': True,
            'message': f'Sent {success_count} out of {len(contacts)} messages',
            'results': results
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/history')
def history_page():
    """Message history page"""
    history = db.get_message_history(limit=100)
    return render_template('history.html', history=history)


@app.route('/contacts')
def contacts_page():
    """Contacts management page"""
    contacts = db.get_all_contacts_with_groups()
    groups = db.get_all_groups()
    return render_template('contacts.html', contacts=contacts, groups=groups)


@app.route('/bulk')
def bulk_page():
    """Bulk message send page"""
    return render_template('bulk.html')


@app.route('/api/contacts', methods=['POST'])
def add_contact():
    """API endpoint to add a new contact"""
    try:
        data = request.json
        name = data.get('name', '')
        phone = data.get('phone')
        
        if not phone:
            return jsonify({'success': False, 'error': 'Phone number is required'}), 400
        
        # Clean phone number
        phone = phone.strip().replace(' ', '').replace('-', '').replace('+', '')
        
        # Use phone as name if name is empty
        if not name:
            name = phone
        
        db.add_contact(name, phone)
        return jsonify({'success': True, 'message': 'Contact added successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    """API endpoint to delete a contact"""
    try:
        db.delete_contact(contact_id)
        return jsonify({'success': True, 'message': 'Contact deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/contacts/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    """API endpoint to update a contact"""
    try:
        data = request.json
        name = data.get('name')
        phone = data.get('phone')
        
        if not name or not phone:
            return jsonify({'success': False, 'error': 'Name and phone are required'}), 400
        
        db.update_contact(contact_id, name, phone)
        return jsonify({'success': True, 'message': 'Contact updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/import-contacts', methods=['POST'])
def import_contacts():
    """API endpoint to import contacts from CSV file"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename, ALLOWED_CSV_EXTENSIONS):
            return jsonify({'success': False, 'error': 'Only CSV files are allowed'}), 400
        
        # Read CSV file
        csv_data = file.read().decode('utf-8').splitlines()
        csv_reader = csv.DictReader(csv_data)
        
        imported_count = 0
        skipped_count = 0
        
        for row in csv_reader:
            try:
                # Support multiple column names - name is optional
                name = row.get('name') or row.get('Name') or row.get('NAME') or ''
                phone = row.get('phone') or row.get('Phone') or row.get('PHONE') or row.get('number') or row.get('Number') or row.get('mobile') or row.get('Mobile')
                
                # If no phone column found, try first column value
                if not phone:
                    for key, value in row.items():
                        if value and value.strip().replace('+', '').replace('-', '').replace(' ', '').isdigit():
                            phone = value
                            break
                
                if phone:
                    # Clean phone number
                    phone = phone.strip().replace(' ', '').replace('-', '').replace('+', '')
                    
                    # If name is empty, use phone number as name
                    if not name:
                        name = phone
                    
                    db.add_contact(name.strip(), phone)
                    imported_count += 1
                else:
                    skipped_count += 1
            except Exception as row_error:
                skipped_count += 1
                print(f"Error importing row: {str(row_error)}")
        
        return jsonify({
            'success': True,
            'message': f'Imported {imported_count} contacts. Skipped {skipped_count} invalid entries.',
            'imported': imported_count,
            'skipped': skipped_count
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Contact Groups API endpoints
@app.route('/api/groups', methods=['GET'])
def get_groups():
    """Get all contact groups"""
    try:
        groups = db.get_all_groups()
        return jsonify({'success': True, 'groups': groups})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/groups', methods=['POST'])
def create_group():
    """Create a new contact group"""
    try:
        data = request.json
        name = data.get('name')
        description = data.get('description', '')
        
        if not name:
            return jsonify({'success': False, 'error': 'Group name is required'}), 400
        
        group_id = db.create_group(name, description)
        return jsonify({'success': True, 'message': 'Group created successfully', 'group_id': group_id})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/groups/<int:group_id>', methods=['PUT'])
def update_group(group_id):
    """Update a contact group"""
    try:
        data = request.json
        name = data.get('name')
        description = data.get('description', '')
        
        if not name:
            return jsonify({'success': False, 'error': 'Group name is required'}), 400
        
        db.update_group(group_id, name, description)
        return jsonify({'success': True, 'message': 'Group updated successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/groups/<int:group_id>', methods=['DELETE'])
def delete_group(group_id):
    """Delete a contact group"""
    try:
        db.delete_group(group_id)
        return jsonify({'success': True, 'message': 'Group deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/groups/<int:group_id>/contacts', methods=['GET'])
def get_group_contacts(group_id):
    """Get all contacts in a group"""
    try:
        contacts = db.get_contacts_in_group(group_id)
        return jsonify({'success': True, 'contacts': contacts})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/groups/<int:group_id>/contacts/<int:contact_id>', methods=['POST'])
def add_contact_to_group(group_id, contact_id):
    """Add a contact to a group"""
    try:
        result = db.add_contact_to_group(contact_id, group_id)
        if result:
            return jsonify({'success': True, 'message': 'Contact added to group'})
        else:
            return jsonify({'success': False, 'error': 'Contact already in group'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/groups/<int:group_id>/contacts/<int:contact_id>', methods=['DELETE'])
def remove_contact_from_group(group_id, contact_id):
    """Remove a contact from a group"""
    try:
        db.remove_contact_from_group(contact_id, group_id)
        return jsonify({'success': True, 'message': 'Contact removed from group'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/contacts/<int:contact_id>/groups', methods=['GET'])
def get_contact_groups(contact_id):
    """Get all groups a contact belongs to"""
    try:
        groups = db.get_groups_for_contact(contact_id)
        return jsonify({'success': True, 'groups': groups})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/send-with-attachment', methods=['POST'])
def send_with_attachment():
    """API endpoint to send message with attachment"""
    global whatsapp_bot
    
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        phone = request.form.get('phone')
        message = request.form.get('message', '')
        
        if not phone:
            return jsonify({'success': False, 'error': 'Phone number is required'}), 400
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'File type not allowed'}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Initialize bot if not already done
        if whatsapp_bot is None:
            whatsapp_bot = WhatsAppBot()
            whatsapp_bot.initialize()
        
        # Send message with attachment
        success = whatsapp_bot.send_message_with_attachment(phone, message, filepath)
        
        # Clean up file after sending
        try:
            os.remove(filepath)
        except:
            pass
        
        if success:
            db.add_message_history(phone, f"{message} [Attachment: {filename}]", 'sent')
            return jsonify({'success': True, 'message': 'Message with attachment sent successfully'})
        else:
            db.add_message_history(phone, f"{message} [Attachment: {filename}]", 'failed')
            return jsonify({'success': False, 'error': 'Failed to send message'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/auto-send-attachments', methods=['POST'])
def auto_send_attachments():
    """Fully automated: Match attachments in folder to contacts by name and send"""
    global whatsapp_bot
    
    try:
        data = request.json
        message = data.get('message', '')  # Optional message to send with attachments
        delay = data.get('delay', 5)  # Delay between sends
        
        # Get all contacts from database
        contacts = db.get_all_contacts()
        
        if not contacts:
            return jsonify({'success': False, 'error': 'No contacts found in database'}), 400
        
        # Get all files from attachments folder
        attachments_path = app.config['ATTACHMENTS_FOLDER']
        all_files = []
        
        for ext in ALLOWED_EXTENSIONS:
            all_files.extend(glob.glob(os.path.join(attachments_path, f'*.{ext}')))
            all_files.extend(glob.glob(os.path.join(attachments_path, f'*.{ext.upper()}')))
        
        if not all_files:
            return jsonify({'success': False, 'error': f'No files found in {attachments_path}'}), 400
        
        # Initialize bot if needed
        if whatsapp_bot is None:
            whatsapp_bot = WhatsAppBot()
            try:
                whatsapp_bot.initialize()
            except Exception as init_error:
                whatsapp_bot = None
                return jsonify({'success': False, 'error': f'Failed to initialize bot: {str(init_error)}'}), 500
        
        # Match files to contacts by name
        results = []
        matched_count = 0
        sent_count = 0
        failed_count = 0
        
        for contact in contacts:
            # Preserve Unicode characters (Gujarati, Hindi, etc.)
            contact_name = contact['name'].strip()
            contact_name_lower = contact_name.lower()
            matched_file = None
            
            # Find file that matches contact name
            for file_path in all_files:
                # Get filename without extension, preserve Unicode
                filename = Path(file_path).stem
                filename_lower = filename.lower()
                
                # Match if contact name is in filename or vice versa (case-insensitive for ASCII, exact for Unicode)
                if (contact_name_lower in filename_lower or filename_lower in contact_name_lower or
                    contact_name in filename or filename in contact_name):
                    matched_file = file_path
                    break
            
            if matched_file:
                matched_count += 1
                try:
                    # Send the attachment
                    import time
                    time.sleep(delay)
                    
                    # Ensure absolute path
                    abs_file_path = os.path.abspath(matched_file)
                    
                    success = whatsapp_bot.send_message_with_attachment(
                        contact['phone'], 
                        message, 
                        abs_file_path
                    )
                    
                    if success:
                        sent_count += 1
                        db.add_message_history(
                            contact['phone'], 
                            f"{message} [Auto-sent: {Path(matched_file).name}]", 
                            'sent'
                        )
                        results.append({
                            'contact': contact['name'],
                            'phone': contact['phone'],
                            'file': Path(matched_file).name,
                            'status': 'sent'
                        })
                    else:
                        failed_count += 1
                        db.add_message_history(
                            contact['phone'], 
                            f"{message} [Auto-sent: {Path(matched_file).name}]", 
                            'failed'
                        )
                        results.append({
                            'contact': contact['name'],
                            'phone': contact['phone'],
                            'file': Path(matched_file).name,
                            'status': 'failed'
                        })
                        
                except Exception as send_error:
                    failed_count += 1
                    results.append({
                        'contact': contact['name'],
                        'phone': contact['phone'],
                        'file': Path(matched_file).name,
                        'status': 'error',
                        'error': str(send_error)
                    })
            else:
                results.append({
                    'contact': contact['name'],
                    'phone': contact['phone'],
                    'file': None,
                    'status': 'no_match'
                })
        
        return jsonify({
            'success': True,
            'message': f'Automation complete: {sent_count} sent, {failed_count} failed, {matched_count} matched out of {len(contacts)} contacts',
            'statistics': {
                'total_contacts': len(contacts),
                'matched': matched_count,
                'sent': sent_count,
                'failed': failed_count,
                'no_match': len(contacts) - matched_count
            },
            'results': results
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/scan-attachments', methods=['GET'])
def scan_attachments():
    """Scan attachments folder and return preview of what will be sent"""
    try:
        # Get all contacts
        contacts = db.get_all_contacts()
        
        # Get all files from attachments folder
        attachments_path = app.config['ATTACHMENTS_FOLDER']
        all_files = []
        
        for ext in ALLOWED_EXTENSIONS:
            all_files.extend(glob.glob(os.path.join(attachments_path, f'*.{ext}')))
            all_files.extend(glob.glob(os.path.join(attachments_path, f'*.{ext.upper()}')))
        
        # Match files to contacts
        matches = []
        unmatched_contacts = []
        unmatched_files = list(all_files)
        
        for contact in contacts:
            # Preserve Unicode characters (Gujarati, Hindi, etc.)
            contact_name = contact['name'].strip()
            contact_name_lower = contact_name.lower()
            matched_file = None
            
            for file_path in all_files:
                # Get filename without extension, preserve Unicode
                filename = Path(file_path).stem
                filename_lower = filename.lower()
                
                # Match if contact name is in filename or vice versa
                if (contact_name_lower in filename_lower or filename_lower in contact_name_lower or
                    contact_name in filename or filename in contact_name):
                    matched_file = file_path
                    if file_path in unmatched_files:
                        unmatched_files.remove(file_path)
                    break
            
            if matched_file:
                matches.append({
                    'contact': contact['name'],
                    'phone': contact['phone'],
                    'file': Path(matched_file).name,
                    'file_size': os.path.getsize(matched_file),
                    'matched': True
                })
            else:
                unmatched_contacts.append({
                    'contact': contact['name'],
                    'phone': contact['phone'],
                    'matched': False
                })
        
        return jsonify({
            'success': True,
            'statistics': {
                'total_contacts': len(contacts),
                'total_files': len(all_files),
                'matched': len(matches),
                'unmatched_contacts': len(unmatched_contacts),
                'unmatched_files': len(unmatched_files)
            },
            'matches': matches,
            'unmatched_contacts': unmatched_contacts,
            'unmatched_files': [Path(f).name for f in unmatched_files],
            'attachments_folder': attachments_path
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/schedule')
def schedule_page():
    """Scheduled messages page"""
    scheduled = db.get_scheduled_messages()
    contacts = db.get_all_contacts()
    return render_template('schedule.html', scheduled=scheduled, contacts=contacts)


@app.route('/api/schedule-message', methods=['POST'])
def schedule_message():
    """API endpoint to schedule a message"""
    try:
        data = request.json
        phone = data.get('phone')
        message = data.get('message')
        scheduled_time = data.get('scheduled_time')
        
        if not phone or not message or not scheduled_time:
            return jsonify({'success': False, 'error': 'All fields are required'}), 400
        
        # Save scheduled message to database
        schedule_id = db.add_scheduled_message(phone, message, scheduled_time)
        
        # Schedule the job
        def send_scheduled_message():
            global whatsapp_bot
            if whatsapp_bot is None:
                whatsapp_bot = WhatsAppBot()
                whatsapp_bot.initialize()
            
            success = whatsapp_bot.send_message(phone, message)
            status = 'sent' if success else 'failed'
            db.update_scheduled_message_status(schedule_id, status)
            db.add_message_history(phone, message, status)
        
        scheduled_datetime = datetime.strptime(scheduled_time, '%Y-%m-%dT%H:%M')
        scheduler.add_job(send_scheduled_message, 'date', run_date=scheduled_datetime, id=f'msg_{schedule_id}')
        
        return jsonify({'success': True, 'message': 'Message scheduled successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/statistics')
def get_statistics():
    """Get statistics for the dashboard"""
    try:
        stats = db.get_statistics()
        return jsonify({'success': True, 'statistics': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============== BULK MESSAGE SEND ==============

@app.route('/api/upload-attachment', methods=['POST'])
def upload_attachment():
    """Upload an attachment file for bulk sending"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to avoid conflicts
            import time
            timestamp = int(time.time())
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{timestamp}{ext}"
            
            # Organize by extension subfolder
            ext_folder = ext.lstrip('.').lower() if ext else 'other'
            ext_folder_map = {
                'jpg': 'images', 'jpeg': 'images', 'png': 'images', 'gif': 'images', 'webp': 'images',
                'mp4': 'videos', 'avi': 'videos', 'mov': 'videos', 'mkv': 'videos',
                'mp3': 'audio', 'wav': 'audio', 'ogg': 'audio', 'm4a': 'audio',
                'pdf': 'documents', 'doc': 'documents', 'docx': 'documents', 
                'xls': 'documents', 'xlsx': 'documents', 'ppt': 'documents', 'pptx': 'documents',
                'txt': 'documents', 'csv': 'documents',
                'zip': 'archives', 'rar': 'archives', '7z': 'archives',
            }
            subfolder = ext_folder_map.get(ext_folder, 'other')
            upload_subfolder = os.path.join(UPLOAD_FOLDER, subfolder)
            os.makedirs(upload_subfolder, exist_ok=True)
            
            filepath = os.path.join(upload_subfolder, filename)
            file.save(filepath)
            
            return jsonify({
                'success': True,
                'filename': filename,
                'path': filepath,
                'folder': subfolder
            })
        else:
            return jsonify({'success': False, 'error': 'File type not allowed'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/bulk-send', methods=['POST'])
def bulk_send():
    """Send bulk messages with optional attachment"""
    global whatsapp_bot
    
    try:
        if not whatsapp_bot or not whatsapp_bot.is_logged_in():
            return jsonify({'success': False, 'error': 'WhatsApp not initialized. Please initialize first.'}), 400
        
        data = request.get_json()
        contacts = data.get('contacts', [])
        message = data.get('message', '')
        attachment_path = data.get('attachment_path')
        attachment_type = data.get('attachment_type', 'document')  # image, document, audio, video
        delay = int(data.get('delay', 5))
        
        if not contacts:
            return jsonify({'success': False, 'error': 'No contacts provided'}), 400
        
        if not message and not attachment_path:
            return jsonify({'success': False, 'error': 'Please provide a message or attachment'}), 400
        
        print(f"[BULK SEND] Starting bulk send to {len(contacts)} contacts")
        print(f"[BULK SEND] Message: {message[:50]}..." if message else "[BULK SEND] No message")
        print(f"[BULK SEND] Attachment: {attachment_path}" if attachment_path else "[BULK SEND] No attachment")
        
        results = []
        import time
        
        for i, contact in enumerate(contacts):
            name = contact.get('name', '')
            number = contact.get('number', '')
            
            if not number:
                results.append({
                    'name': name,
                    'number': number,
                    'status': 'failed',
                    'error': 'No phone number'
                })
                continue
            
            try:
                print(f"[BULK SEND] Processing {i+1}/{len(contacts)}: {name} -> {number}")
                
                # Personalize message with name
                personalized_message = message.replace('{name}', name) if message else ''
                
                if attachment_path and os.path.exists(attachment_path):
                    # Send with attachment (pass file_type for correct WhatsApp option)
                    success = whatsapp_bot.send_message_with_attachment(number, personalized_message, attachment_path, attachment_type)
                else:
                    # Send text only
                    success = whatsapp_bot.send_message(number, personalized_message)
                
                status = 'sent' if success else 'failed'
                print(f"[BULK SEND] Result: {status}")
                
                # Log to history
                msg_log = f"{personalized_message}"
                if attachment_path:
                    msg_log = f"[Attachment: {os.path.basename(attachment_path)}] {personalized_message}"
                db.add_message_history(number, msg_log, status)
                
                results.append({
                    'name': name,
                    'number': number,
                    'status': status
                })
                
                # Delay between messages (except for last one)
                if i < len(contacts) - 1:
                    print(f"[BULK SEND] Waiting {delay} seconds...")
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"[BULK SEND] ERROR for {name}: {str(e)}")
                results.append({
                    'name': name,
                    'number': number,
                    'status': 'failed',
                    'error': str(e)
                })
        
        sent_count = sum(1 for r in results if r['status'] == 'sent')
        failed_count = sum(1 for r in results if r['status'] == 'failed')
        
        print(f"[BULK SEND] Complete! Sent: {sent_count}, Failed: {failed_count}")
        
        return jsonify({
            'success': True,
            'message': f'Sent {sent_count}/{len(contacts)} messages',
            'sent': sent_count,
            'failed': failed_count,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============== INVITATION BULK SEND ==============

@app.route('/invitations')
def invitations_page():
    """Render the invitations page"""
    return render_template('invitations.html')


@app.route('/api/invitations/upload-csv', methods=['POST'])
def upload_invitation_csv():
    """Upload CSV file with invitation data (name, number, sangeet, jaan)"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename, ALLOWED_CSV_EXTENSIONS):
            return jsonify({'success': False, 'error': 'Only CSV files are allowed'}), 400
        
        # Save the file
        filename = secure_filename(file.filename)
        filepath = os.path.join(DATA_FOLDER, 'invitations.csv')
        file.save(filepath)
        
        # Parse CSV and return preview
        invitations = []
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Handle both English and potential variations
                invitation = {
                    'name': row.get('name', '').strip(),
                    'number': row.get('number', '').strip(),
                    'sangeet': row.get('sangeet', '').strip(),
                    'jaan': row.get('jaan', '').strip()
                }
                if invitation['name'] and invitation['number']:
                    invitations.append(invitation)
        
        return jsonify({
            'success': True,
            'message': f'Loaded {len(invitations)} invitations',
            'invitations': invitations
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/invitations/list')
def list_invitations():
    """List all invitations from the uploaded CSV"""
    try:
        filepath = os.path.join(DATA_FOLDER, 'invitations.csv')
        if not os.path.exists(filepath):
            return jsonify({'success': True, 'invitations': []})
        
        invitations = []
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                invitation = {
                    'name': row.get('name', '').strip(),
                    'number': row.get('number', '').strip(),
                    'sangeet': row.get('sangeet', '').strip(),
                    'jaan': row.get('jaan', '').strip()
                }
                if invitation['name'] and invitation['number']:
                    invitations.append(invitation)
        
        return jsonify({'success': True, 'invitations': invitations})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/invitations/generate-pdf', methods=['POST'])
def generate_invitation_pdf():
    """Generate PDF for a single invitation using the external API"""
    try:
        data = request.get_json()
        name = data.get('name')
        sangeet = data.get('sangeet')
        jaan = data.get('jaan')
        
        if not all([name, sangeet, jaan]):
            return jsonify({'success': False, 'error': 'Missing required fields: name, sangeet, jaan'}), 400
        
        # Call the PDF generator API
        response = requests.post(PDF_GENERATOR_URL, json={
            'name': name,
            'sangeet': sangeet,
            'jaan': jaan
        }, timeout=30)
        
        if response.status_code != 200:
            return jsonify({'success': False, 'error': f'PDF generator returned status {response.status_code}'}), 500
        
        result = response.json()
        if not result.get('success'):
            return jsonify({'success': False, 'error': 'PDF generation failed'}), 500
        
        # Save PDF to uploads/documents folder
        pdf_data = base64.b64decode(result['pdf_base64'])
        pdf_filename = f"{name}.pdf"
        pdf_subfolder = os.path.join(UPLOAD_FOLDER, 'documents')
        os.makedirs(pdf_subfolder, exist_ok=True)
        pdf_path = os.path.join(pdf_subfolder, pdf_filename)
        
        with open(pdf_path, 'wb') as f:
            f.write(pdf_data)
        
        return jsonify({
            'success': True,
            'filename': pdf_filename,
            'path': pdf_path
        })
        
    except requests.exceptions.ConnectionError:
        return jsonify({'success': False, 'error': 'Cannot connect to PDF generator. Make sure it is running on localhost:5173'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/invitations/send-single', methods=['POST'])
def send_single_invitation():
    """Generate PDF and send to a single contact"""
    global whatsapp_bot
    
    try:
        if not whatsapp_bot or not whatsapp_bot.is_logged_in():
            return jsonify({'success': False, 'error': 'WhatsApp not initialized. Please initialize first.'}), 400
        
        data = request.get_json()
        name = data.get('name')
        number = data.get('number')
        sangeet = data.get('sangeet')
        jaan = data.get('jaan')
        message = data.get('message', '')  # Optional message/caption
        
        if not all([name, number, sangeet, jaan]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Generate PDF
        response = requests.post(PDF_GENERATOR_URL, json={
            'name': name,
            'sangeet': sangeet,
            'jaan': jaan
        }, timeout=30)
        
        if response.status_code != 200:
            return jsonify({'success': False, 'error': 'PDF generation failed'}), 500
        
        result = response.json()
        if not result.get('success'):
            return jsonify({'success': False, 'error': 'PDF generation failed'}), 500
        
        # Save PDF to uploads/documents folder
        pdf_data = base64.b64decode(result['pdf_base64'])
        pdf_filename = f"{name}.pdf"
        pdf_subfolder = os.path.join(UPLOAD_FOLDER, 'documents')
        os.makedirs(pdf_subfolder, exist_ok=True)
        pdf_path = os.path.join(pdf_subfolder, pdf_filename)
        
        with open(pdf_path, 'wb') as f:
            f.write(pdf_data)
        
        # Send via WhatsApp (PDF = document type)
        success = whatsapp_bot.send_message_with_attachment(number, message, pdf_path, 'document')
        status = 'sent' if success else 'failed'
        
        # Log to history
        db.add_message_history(number, f"[Invitation PDF: {pdf_filename}] {message}", status)
        
        return jsonify({
            'success': success,
            'message': f'Invitation {"sent" if success else "failed"} to {name}',
            'status': status
        })
        
    except requests.exceptions.ConnectionError:
        return jsonify({'success': False, 'error': 'Cannot connect to PDF generator'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/invitations/send-bulk', methods=['POST'])
def send_bulk_invitations():
    """Send invitations to all contacts in the CSV"""
    global whatsapp_bot
    
    try:
        if not whatsapp_bot or not whatsapp_bot.is_logged_in():
            return jsonify({'success': False, 'error': 'WhatsApp not initialized. Please initialize first.'}), 400
        
        data = request.get_json()
        message = data.get('message', '')  # Optional caption for all
        delay = int(data.get('delay', 5))  # Delay between messages in seconds
        
        # Load invitations from CSV
        filepath = os.path.join(DATA_FOLDER, 'invitations.csv')
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'No invitation CSV uploaded'}), 400
        
        invitations = []
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                invitation = {
                    'name': row.get('name', '').strip(),
                    'number': row.get('number', '').strip(),
                    'sangeet': row.get('sangeet', '').strip(),
                    'jaan': row.get('jaan', '').strip()
                }
                if invitation['name'] and invitation['number']:
                    invitations.append(invitation)
        
        if not invitations:
            return jsonify({'success': False, 'error': 'No valid invitations found in CSV'}), 400
        
        print(f"[INVITATIONS] Found {len(invitations)} invitations to send")
        
        results = []
        import time
        
        for i, inv in enumerate(invitations):
            try:
                print(f"[INVITATIONS] Processing {i+1}/{len(invitations)}: {inv['name']} -> {inv['number']}")
                
                # Generate PDF
                print(f"[INVITATIONS] Calling PDF API: {PDF_GENERATOR_URL}")
                response = requests.post(PDF_GENERATOR_URL, json={
                    'name': inv['name'],
                    'sangeet': inv['sangeet'],
                    'jaan': inv['jaan']
                }, timeout=30)
                
                print(f"[INVITATIONS] PDF API response status: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"[INVITATIONS] PDF generation failed for {inv['name']}")
                    results.append({
                        'name': inv['name'],
                        'number': inv['number'],
                        'status': 'failed',
                        'error': 'PDF generation failed'
                    })
                    continue
                
                # Check if response is JSON or raw PDF
                content_type = response.headers.get('Content-Type', '')
                
                if 'application/json' in content_type:
                    # JSON response with base64 PDF
                    result = response.json()
                    if not result.get('success'):
                        print(f"[INVITATIONS] PDF API returned error for {inv['name']}")
                        results.append({
                            'name': inv['name'],
                            'number': inv['number'],
                            'status': 'failed',
                            'error': 'PDF generation failed'
                        })
                        continue
                    pdf_data = base64.b64decode(result['pdf_base64'])
                else:
                    # Raw PDF response
                    pdf_data = response.content
                
                # Save PDF to uploads/documents
                print(f"[INVITATIONS] Saving PDF for {inv['name']}")
                pdf_filename = f"{inv['name']}.pdf"
                pdf_subfolder = os.path.join(UPLOAD_FOLDER, 'documents')
                os.makedirs(pdf_subfolder, exist_ok=True)
                pdf_path = os.path.join(pdf_subfolder, pdf_filename)
                
                with open(pdf_path, 'wb') as f:
                    f.write(pdf_data)
                
                print(f"[INVITATIONS] PDF saved to {pdf_path}")
                
                # Send via WhatsApp (PDF = document type)
                print(f"[INVITATIONS] Sending WhatsApp to {inv['number']}")
                success = whatsapp_bot.send_message_with_attachment(inv['number'], message, pdf_path, 'document')
                status = 'sent' if success else 'failed'
                print(f"[INVITATIONS] WhatsApp send result: {status}")
                
                # Log to history
                db.add_message_history(inv['number'], f"[Invitation PDF: {pdf_filename}] {message}", status)
                
                results.append({
                    'name': inv['name'],
                    'number': inv['number'],
                    'status': status
                })
                
                # Delay between messages (except for last one)
                if i < len(invitations) - 1:
                    print(f"[INVITATIONS] Waiting {delay} seconds...")
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"[INVITATIONS] ERROR for {inv['name']}: {str(e)}")
                results.append({
                    'name': inv['name'],
                    'number': inv['number'],
                    'status': 'failed',
                    'error': str(e)
                })
        
        sent_count = sum(1 for r in results if r['status'] == 'sent')
        failed_count = sum(1 for r in results if r['status'] == 'failed')
        
        print(f"[INVITATIONS] Complete! Sent: {sent_count}, Failed: {failed_count}")
        
        return jsonify({
            'success': True,
            'message': f'Sent {sent_count}/{len(invitations)} invitations',
            'sent': sent_count,
            'failed': failed_count,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

