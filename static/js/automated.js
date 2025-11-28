// Automated bulk send functionality

let currentScanData = null;

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Scan attachments folder
document.getElementById('scanBtn').addEventListener('click', async function() {
    const btn = this;
    btn.disabled = true;
    btn.textContent = '🔄 Scanning...';
    
    try {
        const response = await fetch('/api/scan-attachments');
        const data = await response.json();
        
        if (data.success) {
            currentScanData = data;
            displayScanResults(data);
            showAlert('Scan complete!', 'success');
        } else {
            showAlert('Scan failed: ' + data.error, 'error');
        }
    } catch (error) {
        showAlert('Scan error: ' + error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = '📊 Scan Attachments Folder';
    }
});

// Display scan results
function displayScanResults(data) {
    const resultsDiv = document.getElementById('scanResults');
    resultsDiv.style.display = 'block';
    
    // Update statistics
    document.getElementById('totalContacts').textContent = data.statistics.total_contacts;
    document.getElementById('totalFiles').textContent = data.statistics.total_files;
    document.getElementById('matchedCount').textContent = data.statistics.matched;
    document.getElementById('unmatchedContacts').textContent = data.statistics.unmatched_contacts;
    document.getElementById('unmatchedFiles').textContent = data.statistics.unmatched_files;
    
    // Display matched files
    const matchedTable = document.getElementById('matchedTable');
    matchedTable.innerHTML = '';
    
    if (data.matches && data.matches.length > 0) {
        data.matches.forEach(match => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${match.contact}</td>
                <td>${match.phone}</td>
                <td><strong>${match.file}</strong></td>
                <td>${formatFileSize(match.file_size)}</td>
            `;
            matchedTable.appendChild(row);
        });
    } else {
        matchedTable.innerHTML = '<tr><td colspan="4" style="text-align: center;">No matches found</td></tr>';
    }
    
    // Display unmatched contacts
    const unmatchedContactsSection = document.getElementById('unmatchedContactsSection');
    const unmatchedContactsList = document.getElementById('unmatchedContactsList');
    
    if (data.unmatched_contacts && data.unmatched_contacts.length > 0) {
        unmatchedContactsSection.style.display = 'block';
        unmatchedContactsList.innerHTML = '';
        data.unmatched_contacts.forEach(contact => {
            const li = document.createElement('li');
            li.textContent = `${contact.contact} (${contact.phone})`;
            unmatchedContactsList.appendChild(li);
        });
    } else {
        unmatchedContactsSection.style.display = 'none';
    }
    
    // Display unmatched files
    const unmatchedFilesSection = document.getElementById('unmatchedFilesSection');
    const unmatchedFilesList = document.getElementById('unmatchedFilesList');
    
    if (data.unmatched_files && data.unmatched_files.length > 0) {
        unmatchedFilesSection.style.display = 'block';
        unmatchedFilesList.innerHTML = '';
        data.unmatched_files.forEach(file => {
            const li = document.createElement('li');
            li.textContent = file;
            unmatchedFilesList.appendChild(li);
        });
    } else {
        unmatchedFilesSection.style.display = 'none';
    }
}

// Start automated send
document.getElementById('autoSendForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Check if scan was performed
    if (!currentScanData) {
        showAlert('Please scan attachments first!', 'warning');
        return;
    }
    
    if (currentScanData.statistics.matched === 0) {
        showAlert('No matched files found. Cannot start automation.', 'error');
        return;
    }
    
    const message = document.getElementById('message').value;
    const delay = parseInt(document.getElementById('delay').value);
    
    const startBtn = document.getElementById('startBtn');
    const progressSection = document.getElementById('progressSection');
    const resultsSection = document.getElementById('resultsSection');
    
    // Disable form and show progress
    startBtn.disabled = true;
    startBtn.textContent = '⏳ Sending...';
    progressSection.style.display = 'block';
    resultsSection.style.display = 'none';
    
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    
    try {
        // Estimate total time
        const totalMessages = currentScanData.statistics.matched;
        const estimatedTime = totalMessages * delay;
        
        progressText.textContent = `Sending to ${totalMessages} contacts... Estimated time: ${estimatedTime} seconds`;
        
        // Simulate progress (since actual progress isn't real-time)
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += 100 / (estimatedTime / 0.5); // Update every 0.5 seconds
            if (progress > 95) progress = 95; // Stop at 95% until actual completion
            progressBar.style.width = progress + '%';
        }, 500);
        
        // Send request
        const response = await fetch('/api/auto-send-attachments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                delay: delay
            })
        });
        
        const data = await response.json();
        
        // Stop progress simulation
        clearInterval(progressInterval);
        progressBar.style.width = '100%';
        
        if (data.success) {
            // Hide progress, show results
            setTimeout(() => {
                progressSection.style.display = 'none';
                displayResults(data);
                showAlert(data.message, 'success');
            }, 500);
        } else {
            progressSection.style.display = 'none';
            showAlert('Automation failed: ' + data.error, 'error');
        }
        
    } catch (error) {
        progressSection.style.display = 'none';
        showAlert('Automation error: ' + error.message, 'error');
    } finally {
        startBtn.disabled = false;
        startBtn.textContent = '🤖 Start Automated Send';
    }
});

// Display results
function displayResults(data) {
    const resultsSection = document.getElementById('resultsSection');
    const resultsSummary = document.getElementById('resultsSummary');
    const resultsTable = document.getElementById('resultsTable');
    
    resultsSection.style.display = 'block';
    
    // Summary
    resultsSummary.innerHTML = `
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px;">
            <div>
                <strong>Total:</strong> ${data.statistics.total_contacts}
            </div>
            <div style="color: #27ae60;">
                <strong>✅ Sent:</strong> ${data.statistics.sent}
            </div>
            <div style="color: #e74c3c;">
                <strong>❌ Failed:</strong> ${data.statistics.failed}
            </div>
            <div style="color: #f39c12;">
                <strong>⚠️ No Match:</strong> ${data.statistics.no_match}
            </div>
        </div>
    `;
    
    // Results table
    resultsTable.innerHTML = '';
    
    if (data.results && data.results.length > 0) {
        data.results.forEach(result => {
            const row = document.createElement('tr');
            
            let statusBadge = '';
            if (result.status === 'sent') {
                statusBadge = '<span style="color: #27ae60;">✅ Sent</span>';
            } else if (result.status === 'failed') {
                statusBadge = '<span style="color: #e74c3c;">❌ Failed</span>';
            } else if (result.status === 'error') {
                statusBadge = `<span style="color: #e74c3c;">❌ Error: ${result.error || 'Unknown'}</span>`;
            } else if (result.status === 'no_match') {
                statusBadge = '<span style="color: #f39c12;">⚠️ No file match</span>';
            }
            
            row.innerHTML = `
                <td>${result.contact}</td>
                <td>${result.phone}</td>
                <td>${result.file || '-'}</td>
                <td>${statusBadge}</td>
            `;
            resultsTable.appendChild(row);
        });
    }
}
