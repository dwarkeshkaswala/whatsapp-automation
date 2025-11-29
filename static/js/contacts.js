// Global settings
let appSettings = { default_country_code: '91' };

// Load settings on page load
async function loadAppSettings() {
    try {
        const response = await fetch('/api/settings');
        const data = await response.json();
        if (data.success) {
            appSettings = data.settings;
        }
    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

// Prepend country code if phone doesn't have one
function normalizePhone(phone) {
    phone = phone.trim().replace(/[^0-9]/g, '');
    // If phone is less than 10 digits or starts with 0, prepend country code
    if (phone.length <= 10 || phone.startsWith('0')) {
        phone = phone.replace(/^0+/, ''); // Remove leading zeros
        phone = appSettings.default_country_code + phone;
    }
    return phone;
}

// Load settings on page load
loadAppSettings();

// Add contact form
document.getElementById('addContactForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('contactName').value;
    let phone = document.getElementById('contactPhone').value;
    phone = normalizePhone(phone);
    
    try {
        const response = await fetch('/api/contacts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, phone })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('Contact added successfully!', 'success');
            document.getElementById('addContactForm').reset();
            
            // Reload page to show new contact
            setTimeout(() => location.reload(), 1500);
        } else {
            showAlert(data.error, 'error');
        }
    } catch (error) {
        showAlert('Failed to add contact: ' + error.message, 'error');
    }
});

// Delete contact
document.querySelectorAll('.delete-contact').forEach(btn => {
    btn.addEventListener('click', async () => {
        const contactId = btn.dataset.id;
        
        if (!confirm('Are you sure you want to delete this contact?')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/contacts/${contactId}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (data.success) {
                showAlert('Contact deleted successfully!', 'success');
                
                // Remove row from table
                btn.closest('tr').remove();
            } else {
                showAlert(data.error, 'error');
            }
        } catch (error) {
            showAlert('Failed to delete contact: ' + error.message, 'error');
        }
    });
});

// Edit contact
document.querySelectorAll('.edit-contact').forEach(btn => {
    btn.addEventListener('click', () => {
        const row = btn.closest('tr');
        const contactId = row.dataset.id;
        const name = row.dataset.name;
        const phone = row.dataset.phone;
        
        // Parse country code and phone number
        const phoneStr = phone.toString();
        let countryCode = '';
        let phoneNumber = phoneStr;
        
        if (phoneStr.length >= 10) {
            countryCode = phoneStr.substring(0, 2);
            phoneNumber = phoneStr.substring(2);
        }
        
        document.getElementById('editContactId').value = contactId;
        document.getElementById('editContactName').value = name;
        document.getElementById('editContactCountryCode').value = countryCode;
        document.getElementById('editContactPhone').value = phoneNumber;
        document.getElementById('editContactModal').style.display = 'flex';
    });
});

function closeEditContactModal() {
    document.getElementById('editContactModal').style.display = 'none';
}

async function saveEditedContact() {
    const contactId = document.getElementById('editContactId').value;
    const name = document.getElementById('editContactName').value.trim();
    const countryCode = document.getElementById('editContactCountryCode').value.trim();
    const phoneNumber = document.getElementById('editContactPhone').value.trim();
    
    if (!name || !countryCode || !phoneNumber) {
        showAlert('Please fill in all fields', 'warning');
        return;
    }
    
    const fullPhone = countryCode + phoneNumber;
    
    try {
        const response = await fetch(`/api/contacts/${contactId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, phone: fullPhone })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('Contact updated successfully!', 'success');
            closeEditContactModal();
            setTimeout(() => location.reload(), 1500);
        } else {
            showAlert(data.error, 'error');
        }
    } catch (error) {
        showAlert('Failed to update contact: ' + error.message, 'error');
    }
}

// Import CSV form
document.getElementById('importCsvForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const fileInput = document.getElementById('csvFile');
    const file = fileInput.files[0];
    
    if (!file) {
        showAlert('Please select a CSV file', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showAlert('Importing contacts...', 'info');
        
        const response = await fetch('/api/import-contacts', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert(data.message, 'success');
            document.getElementById('importCsvForm').reset();
            
            // Reload page to show new contacts
            setTimeout(() => location.reload(), 2000);
        } else {
            showAlert(data.error, 'error');
        }
    } catch (error) {
        showAlert('Failed to import contacts: ' + error.message, 'error');
    }
});

// ==================== GROUP MANAGEMENT ====================

// Create group form
document.getElementById('createGroupForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('groupName').value.trim();
    const description = document.getElementById('groupDescription').value.trim();
    
    if (!name) {
        showAlert('Please enter a group name', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api/groups', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, description })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('Group created successfully!', 'success');
            document.getElementById('createGroupForm').reset();
            setTimeout(() => location.reload(), 1500);
        } else {
            showAlert(data.error, 'error');
        }
    } catch (error) {
        showAlert('Failed to create group: ' + error.message, 'error');
    }
});

// Delete group
document.querySelectorAll('.delete-group').forEach(btn => {
    btn.addEventListener('click', async () => {
        const groupId = btn.dataset.id;
        
        if (!confirm('Are you sure you want to delete this group? Contacts will not be deleted.')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/groups/${groupId}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (data.success) {
                showAlert('Group deleted successfully!', 'success');
                btn.closest('.group-item').remove();
            } else {
                showAlert(data.error, 'error');
            }
        } catch (error) {
            showAlert('Failed to delete group: ' + error.message, 'error');
        }
    });
});

// View group contacts
document.querySelectorAll('.view-group').forEach(btn => {
    btn.addEventListener('click', async () => {
        const groupId = btn.dataset.id;
        const groupName = btn.dataset.name;
        
        document.getElementById('viewGroupId').value = groupId;
        document.getElementById('viewGroupName').textContent = groupName;
        document.getElementById('viewGroupModal').style.display = 'flex';
        
        // Load group contacts
        try {
            const response = await fetch(`/api/groups/${groupId}/contacts`);
            const data = await response.json();
            
            const container = document.getElementById('groupContactsList');
            
            if (data.success && data.contacts.length > 0) {
                let html = '<table class="table"><thead><tr><th>Name</th><th>Phone</th><th>Action</th></tr></thead><tbody>';
                data.contacts.forEach(contact => {
                    html += `<tr>
                        <td>${escapeHtml(contact.name)}</td>
                        <td>${escapeHtml(contact.phone)}</td>
                        <td><button class="btn btn-sm btn-danger" onclick="removeFromGroup(${groupId}, ${contact.id})">
                            <i class="fas fa-times"></i> Remove
                        </button></td>
                    </tr>`;
                });
                html += '</tbody></table>';
                container.innerHTML = html;
            } else {
                container.innerHTML = '<p class="text-muted text-center">No contacts in this group</p>';
            }
        } catch (error) {
            showAlert('Failed to load group contacts: ' + error.message, 'error');
        }
    });
});

function closeViewGroupModal() {
    document.getElementById('viewGroupModal').style.display = 'none';
}

async function removeFromGroup(groupId, contactId) {
    try {
        const response = await fetch(`/api/groups/${groupId}/contacts/${contactId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('Contact removed from group', 'success');
            // Refresh the group view
            document.querySelector(`.view-group[data-id="${groupId}"]`).click();
            // Update the member count
            setTimeout(() => location.reload(), 1500);
        } else {
            showAlert(data.error, 'error');
        }
    } catch (error) {
        showAlert('Failed to remove contact: ' + error.message, 'error');
    }
}

// Manage groups for contact
document.querySelectorAll('.manage-groups').forEach(btn => {
    btn.addEventListener('click', async () => {
        const contactId = btn.dataset.id;
        const contactName = btn.dataset.name;
        
        document.getElementById('modalContactId').value = contactId;
        document.getElementById('contactNameInModal').textContent = contactName;
        document.getElementById('manageGroupsModal').style.display = 'flex';
        
        // Uncheck all checkboxes first
        document.querySelectorAll('.group-checkbox').forEach(cb => cb.checked = false);
        
        // Load current groups for contact
        try {
            const response = await fetch(`/api/contacts/${contactId}/groups`);
            const data = await response.json();
            
            if (data.success) {
                data.groups.forEach(group => {
                    const checkbox = document.querySelector(`.group-checkbox[value="${group.id}"]`);
                    if (checkbox) checkbox.checked = true;
                });
            }
        } catch (error) {
            showAlert('Failed to load contact groups: ' + error.message, 'error');
        }
    });
});

function closeManageGroupsModal() {
    document.getElementById('manageGroupsModal').style.display = 'none';
}

async function saveContactGroups() {
    const contactId = document.getElementById('modalContactId').value;
    const checkboxes = document.querySelectorAll('.group-checkbox');
    
    try {
        // Get current groups
        const currentResponse = await fetch(`/api/contacts/${contactId}/groups`);
        const currentData = await currentResponse.json();
        const currentGroupIds = currentData.success ? currentData.groups.map(g => g.id) : [];
        
        // Get selected groups
        const selectedGroupIds = [];
        checkboxes.forEach(cb => {
            if (cb.checked) selectedGroupIds.push(parseInt(cb.value));
        });
        
        // Add to new groups
        for (const groupId of selectedGroupIds) {
            if (!currentGroupIds.includes(groupId)) {
                await fetch(`/api/groups/${groupId}/contacts/${contactId}`, {
                    method: 'POST'
                });
            }
        }
        
        // Remove from unselected groups
        for (const groupId of currentGroupIds) {
            if (!selectedGroupIds.includes(groupId)) {
                await fetch(`/api/groups/${groupId}/contacts/${contactId}`, {
                    method: 'DELETE'
                });
            }
        }
        
        showAlert('Groups updated successfully!', 'success');
        closeManageGroupsModal();
        setTimeout(() => location.reload(), 1500);
        
    } catch (error) {
        showAlert('Failed to update groups: ' + error.message, 'error');
    }
}

// Filter contacts by group
document.getElementById('groupFilter')?.addEventListener('change', function() {
    const groupId = this.value;
    const rows = document.querySelectorAll('#contactsTable tr[data-id]');
    
    rows.forEach(row => {
        if (!groupId) {
            row.style.display = '';
        } else {
            const contactGroups = row.dataset.groups.split(',');
            if (contactGroups.includes(groupId)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        }
    });
});

// Close modals when clicking outside
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal')) {
        e.target.style.display = 'none';
    }
});

// Utility function
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
