// Schedule message form
document.getElementById('scheduleForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const phone = document.getElementById('schedulePhone').value;
    const message = document.getElementById('scheduleMessage').value;
    const scheduledTime = document.getElementById('scheduledTime').value;
    
    // Validate scheduled time is in the future
    const scheduledDate = new Date(scheduledTime);
    const now = new Date();
    
    if (scheduledDate <= now) {
        showAlert('Scheduled time must be in the future', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/schedule-message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ phone, message, scheduled_time: scheduledTime })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('Message scheduled successfully!', 'success');
            document.getElementById('scheduleForm').reset();
            
            // Reload page to show new scheduled message
            setTimeout(() => location.reload(), 1500);
        } else {
            showAlert(data.error, 'error');
        }
    } catch (error) {
        showAlert('Failed to schedule message: ' + error.message, 'error');
    }
});

// Set minimum datetime to current time
const scheduledTimeInput = document.getElementById('scheduledTime');
if (scheduledTimeInput) {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    
    scheduledTimeInput.min = `${year}-${month}-${day}T${hours}:${minutes}`;
}
