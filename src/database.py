import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager


class Database:
    def __init__(self, db_path='whatsapp_bot.db'):
        """Initialize the database"""
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create contacts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create contact groups table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contact_groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create junction table for contacts and groups (many-to-many)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS contact_group_members (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact_id INTEGER NOT NULL,
                    group_id INTEGER NOT NULL,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE,
                    FOREIGN KEY (group_id) REFERENCES contact_groups(id) ON DELETE CASCADE,
                    UNIQUE(contact_id, group_id)
                )
            ''')
            
            # Create message history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS message_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone TEXT NOT NULL,
                    message TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create scheduled messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scheduled_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone TEXT NOT NULL,
                    message TEXT NOT NULL,
                    scheduled_time TIMESTAMP NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    # Contact operations
    def add_contact(self, name, phone):
        """Add a new contact"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO contacts (name, phone) VALUES (?, ?)',
                (name, phone)
            )
            return cursor.lastrowid
    
    def get_all_contacts(self):
        """Get all contacts"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM contacts ORDER BY name')
            return [dict(row) for row in cursor.fetchall()]
    
    def get_contact_by_id(self, contact_id):
        """Get a contact by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def delete_contact(self, contact_id):
        """Delete a contact"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM contacts WHERE id = ?', (contact_id,))
    
    def update_contact(self, contact_id, name, phone):
        """Update a contact"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE contacts SET name = ?, phone = ? WHERE id = ?',
                (name, phone, contact_id)
            )
    
    # Contact Group operations
    def create_group(self, name, description=''):
        """Create a new contact group"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO contact_groups (name, description) VALUES (?, ?)',
                (name, description)
            )
            return cursor.lastrowid
    
    def get_all_groups(self):
        """Get all contact groups with member count"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT g.*, COUNT(cgm.contact_id) as member_count
                FROM contact_groups g
                LEFT JOIN contact_group_members cgm ON g.id = cgm.group_id
                GROUP BY g.id
                ORDER BY g.name
            ''')
            return [dict(row) for row in cursor.fetchall()]
    
    def get_group_by_id(self, group_id):
        """Get a group by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM contact_groups WHERE id = ?', (group_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_group(self, group_id, name, description=''):
        """Update a group"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE contact_groups SET name = ?, description = ? WHERE id = ?',
                (name, description, group_id)
            )
    
    def delete_group(self, group_id):
        """Delete a group and its memberships"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM contact_group_members WHERE group_id = ?', (group_id,))
            cursor.execute('DELETE FROM contact_groups WHERE id = ?', (group_id,))
    
    def add_contact_to_group(self, contact_id, group_id):
        """Add a contact to a group"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    'INSERT INTO contact_group_members (contact_id, group_id) VALUES (?, ?)',
                    (contact_id, group_id)
                )
                return True
            except sqlite3.IntegrityError:
                return False  # Already in group
    
    def remove_contact_from_group(self, contact_id, group_id):
        """Remove a contact from a group"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'DELETE FROM contact_group_members WHERE contact_id = ? AND group_id = ?',
                (contact_id, group_id)
            )
    
    def get_contacts_in_group(self, group_id):
        """Get all contacts in a specific group"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT c.* FROM contacts c
                INNER JOIN contact_group_members cgm ON c.id = cgm.contact_id
                WHERE cgm.group_id = ?
                ORDER BY c.name
            ''', (group_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_groups_for_contact(self, contact_id):
        """Get all groups a contact belongs to"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT g.* FROM contact_groups g
                INNER JOIN contact_group_members cgm ON g.id = cgm.group_id
                WHERE cgm.contact_id = ?
                ORDER BY g.name
            ''', (contact_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_all_contacts_with_groups(self):
        """Get all contacts with their group memberships"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM contacts ORDER BY name')
            contacts = [dict(row) for row in cursor.fetchall()]
            
            for contact in contacts:
                contact['groups'] = self.get_groups_for_contact(contact['id'])
            
            return contacts

    # Message history operations
    def add_message_history(self, phone, message, status='sent'):
        """Add a message to history"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO message_history (phone, message, status) VALUES (?, ?, ?)',
                (phone, message, status)
            )
            return cursor.lastrowid
    
    def get_message_history(self, limit=100):
        """Get message history"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM message_history ORDER BY created_at DESC LIMIT ?',
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def get_message_history_by_phone(self, phone, limit=50):
        """Get message history for a specific phone number"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM message_history WHERE phone = ? ORDER BY created_at DESC LIMIT ?',
                (phone, limit)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    # Scheduled messages operations
    def add_scheduled_message(self, phone, message, scheduled_time):
        """Add a scheduled message"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO scheduled_messages (phone, message, scheduled_time) VALUES (?, ?, ?)',
                (phone, message, scheduled_time)
            )
            return cursor.lastrowid
    
    def get_scheduled_messages(self, status='pending'):
        """Get scheduled messages"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute(
                    'SELECT * FROM scheduled_messages WHERE status = ? ORDER BY scheduled_time',
                    (status,)
                )
            else:
                cursor.execute('SELECT * FROM scheduled_messages ORDER BY scheduled_time')
            return [dict(row) for row in cursor.fetchall()]
    
    def update_scheduled_message_status(self, schedule_id, status):
        """Update the status of a scheduled message"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE scheduled_messages SET status = ? WHERE id = ?',
                (status, schedule_id)
            )
    
    def delete_scheduled_message(self, schedule_id):
        """Delete a scheduled message"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM scheduled_messages WHERE id = ?', (schedule_id,))
    
    # Statistics operations
    def get_statistics(self):
        """Get statistics for the dashboard"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total messages
            cursor.execute('SELECT COUNT(*) as count FROM message_history')
            total_messages = cursor.fetchone()['count']
            
            # Sent messages
            cursor.execute("SELECT COUNT(*) as count FROM message_history WHERE status = 'sent'")
            sent_messages = cursor.fetchone()['count']
            
            # Failed messages
            cursor.execute("SELECT COUNT(*) as count FROM message_history WHERE status = 'failed'")
            failed_messages = cursor.fetchone()['count']
            
            # Total contacts
            cursor.execute('SELECT COUNT(*) as count FROM contacts')
            total_contacts = cursor.fetchone()['count']
            
            # Scheduled messages
            cursor.execute("SELECT COUNT(*) as count FROM scheduled_messages WHERE status = 'pending'")
            scheduled_messages = cursor.fetchone()['count']
            
            return {
                'total_messages': total_messages,
                'sent_messages': sent_messages,
                'failed_messages': failed_messages,
                'total_contacts': total_contacts,
                'scheduled_messages': scheduled_messages
            }
    
    def clear_old_history(self, days=30):
        """Clear message history older than specified days"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM message_history WHERE created_at < datetime('now', '-' || ? || ' days')",
                (days,)
            )
            return cursor.rowcount
