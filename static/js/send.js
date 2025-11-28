// Character counter for single message
const messageInput = document.getElementById('message');
const charCount = document.getElementById('charCount');

if (messageInput && charCount) {
    messageInput.addEventListener('input', () => {
        charCount.textContent = messageInput.value.length;
    });
}

// Single message form
document.getElementById('singleMessageForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const phone = document.getElementById('phone').value;
    const message = document.getElementById('message').value;
    
    try {
        const response = await fetch('/api/send-message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ phone, message })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('Message sent successfully!', 'success');
            document.getElementById('singleMessageForm').reset();
            charCount.textContent = '0';
        } else {
            showAlert(data.error, 'error');
        }
    } catch (error) {
        showAlert('Failed to send message: ' + error.message, 'error');
    }
});

// Bulk message form
document.getElementById('bulkMessageForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const checkboxes = document.querySelectorAll('input[name="contacts"]:checked');
    const contacts = Array.from(checkboxes).map(cb => cb.value);
    const message = document.getElementById('bulkMessage').value;
    const delay = parseInt(document.getElementById('delay').value);
    
    if (contacts.length === 0) {
        showAlert('Please select at least one contact', 'error');
        return;
    }
    
    try {
        showAlert('Sending bulk messages... This may take a while.', 'info');
        
        const response = await fetch('/api/send-bulk', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ contacts, message, delay })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert(data.message, 'success');
            document.getElementById('bulkMessageForm').reset();
        } else {
            showAlert(data.error, 'error');
        }
    } catch (error) {
        showAlert('Failed to send bulk messages: ' + error.message, 'error');
    }
});

// Attachment form
document.getElementById('attachmentForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const phone = document.getElementById('attachmentPhone').value;
    const message = document.getElementById('attachmentMessage').value;
    const fileInput = document.getElementById('attachment');
    const file = fileInput.files[0];
    
    if (!file) {
        showAlert('Please select a file to send', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('phone', phone);
    formData.append('message', message);
    formData.append('file', file);
    
    try {
        showAlert('Sending message with attachment...', 'info');
        
        const response = await fetch('/api/send-with-attachment', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('Message with attachment sent successfully!', 'success');
            document.getElementById('attachmentForm').reset();
            document.getElementById('filePreview').innerHTML = '';
        } else {
            showAlert(data.error, 'error');
        }
    } catch (error) {
        showAlert('Failed to send message: ' + error.message, 'error');
    }
});

// File preview
document.getElementById('attachment')?.addEventListener('change', (e) => {
    const file = e.target.files[0];
    const preview = document.getElementById('filePreview');
    
    if (file) {
        const fileSize = (file.size / 1024 / 1024).toFixed(2);
        preview.innerHTML = `
            <div class="file-info">
                <i class="fas fa-file"></i>
                <span>${file.name} (${fileSize} MB)</span>
            </div>
        `;
    } else {
        preview.innerHTML = '';
    }
});
