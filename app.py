import os
import csv
import glob
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv
from datetime import datetime
import json
from werkzeug.utils import secure_filename
from whatsapp_bot import WhatsAppBot
from database import Database
from apscheduler.schedulers.background import BackgroundScheduler

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ATTACHMENTS_FOLDER = os.path.join(os.getcwd(), 'attachments')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'csv', 'xlsx', 'mp4', 'mp3', 'zip'}
ALLOWED_CSV_EXTENSIONS = {'csv'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(ATTACHMENTS_FOLDER):
    os.makedirs(ATTACHMENTS_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ATTACHMENTS_FOLDER'] = ATTACHMENTS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB max file size

# Initialize database
db = Database()

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


@app.route('/api/initialize-bot', methods=['POST'])
def initialize_bot():
    """Initialize the WhatsApp bot in headless mode"""
    global whatsapp_bot
    
    try:
        data = request.json or {}
        headless = data.get('headless', False)  # Default to visible browser for debugging
        
        # Close existing bot if any
        if whatsapp_bot is not None:
            try:
                whatsapp_bot.close()
            except:
                pass
        
        whatsapp_bot = WhatsAppBot()
        whatsapp_bot.initialize(headless=headless)
        
        return jsonify({
            'success': True, 
            'message': 'Bot initialized successfully',
            'headless': headless
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
    """API endpoint to send a WhatsApp message"""
    global whatsapp_bot
    
    try:
        data = request.json
        phone = data.get('phone')
        message = data.get('message')
        
        if not phone or not message:
            return jsonify({'success': False, 'error': 'Phone and message are required'}), 400
        
        # Initialize bot if not already done
        if whatsapp_bot is None:
            whatsapp_bot = WhatsAppBot()
            whatsapp_bot.initialize()
        
        # Send message
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
    contacts = db.get_all_contacts()
    return render_template('contacts.html', contacts=contacts)


@app.route('/automated')
def automated_page():
    """Automated bulk send page"""
    return render_template('automated.html')


@app.route('/api/contacts', methods=['POST'])
def add_contact():
    """API endpoint to add a new contact"""
    try:
        data = request.json
        name = data.get('name')
        phone = data.get('phone')
        
        if not name or not phone:
            return jsonify({'success': False, 'error': 'Name and phone are required'}), 400
        
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
                # Support multiple column names
                name = row.get('name') or row.get('Name') or row.get('NAME')
                phone = row.get('phone') or row.get('Phone') or row.get('PHONE') or row.get('number') or row.get('Number')
                
                if name and phone:
                    # Clean phone number
                    phone = phone.strip().replace(' ', '').replace('-', '')
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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

