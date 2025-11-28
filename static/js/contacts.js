// Add contact form
document.getElementById('addContactForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('contactName').value;
    const phone = document.getElementById('contactPhone').value;
    
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
