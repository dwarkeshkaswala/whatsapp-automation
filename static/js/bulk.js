/**
 * Bulk Send Page JavaScript
 */

let contacts = [];
let uploadedAttachment = null;
let isSending = false;
let isPaused = false;
let appSettings = { default_country_code: '91' };
let botConnected = false;

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

// Check if bot is initialized and logged in
async function checkBotStatus() {
    const banner = document.getElementById('botStatusBanner');
    const initBtn = document.getElementById('initBotBtn');
    const startBtn = document.getElementById('startSendBtn');
    const warning = document.getElementById('notConnectedWarning');
    
    try {
        const response = await fetch('/api/check-login');
        const data = await response.json();
        
        if (data.logged_in) {
            // Bot is connected
            botConnected = true;
            banner.className = 'bot-status-banner bot-status-connected';
            banner.querySelector('.status-icon').className = 'fas fa-check-circle status-icon';
            banner.querySelector('.status-text').textContent = 'WhatsApp Connected - Ready to send messages';
            initBtn.style.display = 'none';
            startBtn.disabled = false;
            warning.style.display = 'none';
        } else if (data.status === 'waiting_for_scan') {
            // Bot initialized but waiting for QR scan
            botConnected = false;
            banner.className = 'bot-status-banner bot-status-disconnected';
            banner.querySelector('.status-icon').className = 'fas fa-qrcode status-icon';
            banner.querySelector('.status-text').textContent = 'Please scan QR code on Dashboard';
            initBtn.style.display = 'inline-flex';
            initBtn.innerHTML = '<i class="fas fa-qrcode"></i> Scan QR Code';
            startBtn.disabled = true;
            warning.style.display = 'flex';
        } else {
            // Bot not initialized
            botConnected = false;
            banner.className = 'bot-status-banner bot-status-disconnected';
            banner.querySelector('.status-icon').className = 'fas fa-exclamation-circle status-icon';
            banner.querySelector('.status-text').textContent = 'Bot not initialized - Please start the bot first';
            initBtn.style.display = 'inline-flex';
            initBtn.innerHTML = '<i class="fas fa-power-off"></i> Initialize Bot';
            startBtn.disabled = true;
            warning.style.display = 'flex';
        }
    } catch (error) {
        console.error('Error checking bot status:', error);
        botConnected = false;
        banner.className = 'bot-status-banner bot-status-disconnected';
        banner.querySelector('.status-icon').className = 'fas fa-exclamation-triangle status-icon';
        banner.querySelector('.status-text').textContent = 'Could not check bot status';
        initBtn.style.display = 'inline-flex';
        startBtn.disabled = true;
        warning.style.display = 'flex';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    loadAppSettings();
    checkBotStatus();
    initTabSwitching();
    initEventListeners();
    loadSavedContacts();
    updateContactCount();
    
    // Check bot status every 10 seconds
    setInterval(checkBotStatus, 10000);
});

function initTabSwitching() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            
            tabBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === targetTab + '-tab') {
                    content.classList.add('active');
                }
            });
        });
    });
}

function initEventListeners() {
    document.getElementById('addContactsBtn').addEventListener('click', addContactsFromTextarea);
    document.getElementById('csvFile').addEventListener('change', handleCsvUpload);
    document.getElementById('selectAllCheckbox').addEventListener('change', toggleSelectAll);
    document.getElementById('selectAllBtn').addEventListener('click', selectAllContacts);
    document.getElementById('removeSelectedBtn').addEventListener('click', removeSelectedContacts);
    document.getElementById('clearAllBtn').addEventListener('click', clearAllContacts);
    
    // Attachment checkbox toggle
    document.getElementById('hasAttachment').addEventListener('change', toggleAttachmentOptions);
    
    document.getElementById('attachmentFile').addEventListener('change', handleAttachmentUpload);
    document.getElementById('startSendBtn').addEventListener('click', startBulkSend);
    document.getElementById('pauseSendBtn').addEventListener('click', pauseSend);
    document.getElementById('stopSendBtn').addEventListener('click', stopSend);
}

function toggleAttachmentOptions() {
    const hasAttachment = document.getElementById('hasAttachment').checked;
    const attachmentOptions = document.getElementById('attachmentOptions');
    
    if (hasAttachment) {
        attachmentOptions.style.display = 'block';
    } else {
        attachmentOptions.style.display = 'none';
        clearAttachment();
    }
}

function loadSavedContacts() {
    const saved = localStorage.getItem('bulkContacts');
    if (saved) {
        try {
            contacts = JSON.parse(saved);
            renderContacts();
        } catch (e) {
            console.error('Error loading contacts:', e);
        }
    }
}

function saveContactsToStorage() {
    localStorage.setItem('bulkContacts', JSON.stringify(contacts));
}

// Parse phone number to extract country code and local number
function parsePhoneNumber(phone) {
    phone = phone.replace(/[^\d]/g, ''); // Remove non-digits
    
    // Common country codes (2-3 digits)
    // India: 91, US/Canada: 1, UK: 44, etc.
    let countryCode = '';
    let localNumber = phone;
    
    if (phone.length > 10) {
        // Assume country code is the digits before the last 10
        const extraDigits = phone.length - 10;
        countryCode = phone.substring(0, extraDigits);
        localNumber = phone.substring(extraDigits);
    }
    
    return { countryCode, localNumber };
}

// Normalize phone number - add country code if missing
function normalizePhone(phone) {
    phone = phone.replace(/[^\d]/g, ''); // Remove non-digits
    // If phone is 10 digits or less or starts with 0, prepend country code
    if (phone.length <= 10 || phone.startsWith('0')) {
        phone = phone.replace(/^0+/, ''); // Remove leading zeros
        phone = appSettings.default_country_code + phone;
    }
    return phone;
}

function addContactsFromTextarea() {
    const textarea = document.getElementById('phoneNumbers');
    const text = textarea.value.trim();
    
    if (!text) {
        showAlert('Please enter phone numbers', 'warning');
        return;
    }
    
    const lines = text.split(/[\n,]+/);
    let added = 0;
    
    lines.forEach(line => {
        let phone = line.trim().replace(/[^\d+]/g, '');
        phone = phone.replace(/^\+/, ''); // Remove leading +
        phone = normalizePhone(phone); // Apply default country code
        
        if (phone && phone.length >= 10) {
            if (!contacts.find(c => c.phone === phone)) {
                const parsed = parsePhoneNumber(phone);
                contacts.push({
                    phone: phone,
                    countryCode: parsed.countryCode,
                    localNumber: parsed.localNumber,
                    name: '',
                    status: 'pending',
                    selected: false
                });
                added++;
            }
        }
    });
    
    if (added > 0) {
        renderContacts();
        saveContactsToStorage();
        updateContactCount();
        showAlert('Added ' + added + ' contact(s)', 'success');
        textarea.value = '';
    } else {
        showAlert('No valid phone numbers found', 'warning');
    }
}

function handleCsvUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        const text = e.target.result;
        const lines = text.split('\n');
        let added = 0;
        let isFirstLine = true;
        
        lines.forEach(line => {
            line = line.trim();
            if (!line) return;
            
            if (isFirstLine) {
                isFirstLine = false;
                if (line.toLowerCase().includes('phone') || line.toLowerCase().includes('name') || line.toLowerCase().includes('number')) {
                    return;
                }
            }
            
            const parts = line.split(',').map(p => p.trim().replace(/^["']|["']$/g, ''));
            let phone = '';
            let name = '';
            
            if (parts.length >= 2) {
                if (/^\+?\d{10,}$/.test(parts[0].replace(/[\s-]/g, ''))) {
                    phone = parts[0].replace(/[\s-+]/g, '');
                    name = parts[1];
                } else {
                    name = parts[0];
                    phone = parts[1].replace(/[\s-+]/g, '');
                }
            } else if (parts.length === 1) {
                phone = parts[0].replace(/[\s-+]/g, '');
            }
            
            // Normalize phone with default country code
            phone = normalizePhone(phone);
            
            if (phone && phone.length >= 10) {
                if (!contacts.find(c => c.phone === phone)) {
                    const parsed = parsePhoneNumber(phone);
                    contacts.push({
                        phone: phone,
                        countryCode: parsed.countryCode,
                        localNumber: parsed.localNumber,
                        name: name,
                        status: 'pending',
                        selected: false
                    });
                    added++;
                }
            }
        });
        
        if (added > 0) {
            renderContacts();
            saveContactsToStorage();
            updateContactCount();
            showAlert('Imported ' + added + ' contact(s) from CSV', 'success');
        } else {
            showAlert('No valid contacts found in CSV', 'warning');
        }
        
        event.target.value = '';
    };
    reader.readAsText(file);
}

// Country code to flag emoji mapping
const countryCodeFlags = {
    '1': '🇺🇸', '7': '🇷🇺', '20': '🇪🇬', '27': '🇿🇦', '30': '🇬🇷', '31': '🇳🇱', '32': '🇧🇪', '33': '🇫🇷',
    '34': '🇪🇸', '36': '🇭🇺', '39': '🇮🇹', '40': '🇷🇴', '41': '🇨🇭', '43': '🇦🇹', '44': '🇬🇧', '45': '🇩🇰',
    '46': '🇸🇪', '47': '🇳🇴', '48': '🇵🇱', '49': '🇩🇪', '51': '🇵🇪', '52': '🇲🇽', '53': '🇨🇺', '54': '🇦🇷',
    '55': '🇧🇷', '56': '🇨🇱', '57': '🇨🇴', '58': '🇻🇪', '60': '🇲🇾', '61': '🇦🇺', '62': '🇮🇩', '63': '🇵🇭',
    '64': '🇳🇿', '65': '🇸🇬', '66': '🇹🇭', '81': '🇯🇵', '82': '🇰🇷', '84': '🇻🇳', '86': '🇨🇳', '90': '🇹🇷',
    '91': '🇮🇳', '92': '🇵🇰', '93': '🇦🇫', '94': '🇱🇰', '95': '🇲🇲', '98': '🇮🇷', '212': '🇲🇦', '213': '🇩🇿',
    '216': '🇹🇳', '218': '🇱🇾', '220': '🇬🇲', '221': '🇸🇳', '223': '🇲🇱', '224': '🇬🇳', '225': '🇨🇮',
    '226': '🇧🇫', '227': '🇳🇪', '228': '🇹🇬', '229': '🇧🇯', '230': '🇲🇺', '231': '🇱🇷', '232': '🇸🇱',
    '233': '🇬🇭', '234': '🇳🇬', '235': '🇹🇩', '236': '🇨🇫', '237': '🇨🇲', '238': '🇨🇻', '239': '🇸🇹',
    '240': '🇬🇶', '241': '🇬🇦', '242': '🇨🇬', '243': '🇨🇩', '244': '🇦🇴', '245': '🇬🇼', '246': '🇮🇴',
    '248': '🇸🇨', '249': '🇸🇩', '250': '🇷🇼', '251': '🇪🇹', '252': '🇸🇴', '253': '🇩🇯', '254': '🇰🇪',
    '255': '🇹🇿', '256': '🇺🇬', '257': '🇧🇮', '258': '🇲🇿', '260': '🇿🇲', '261': '🇲🇬', '262': '🇷🇪',
    '263': '🇿🇼', '264': '🇳🇦', '265': '🇲🇼', '266': '🇱🇸', '267': '🇧🇼', '268': '🇸🇿', '269': '🇰🇲',
    '290': '🇸🇭', '291': '🇪🇷', '297': '🇦🇼', '298': '🇫🇴', '299': '🇬🇱', '350': '🇬🇮', '351': '🇵🇹',
    '352': '🇱🇺', '353': '🇮🇪', '354': '🇮🇸', '355': '🇦🇱', '356': '🇲🇹', '357': '🇨🇾', '358': '🇫🇮',
    '359': '🇧🇬', '370': '🇱🇹', '371': '🇱🇻', '372': '🇪🇪', '373': '🇲🇩', '374': '🇦🇲', '375': '🇧🇾',
    '376': '🇦🇩', '377': '🇲🇨', '378': '🇸🇲', '380': '🇺🇦', '381': '🇷🇸', '382': '🇲🇪', '383': '🇽🇰',
    '385': '🇭🇷', '386': '🇸🇮', '387': '🇧🇦', '389': '🇲🇰', '420': '🇨🇿', '421': '🇸🇰', '423': '🇱🇮',
    '500': '🇫🇰', '501': '🇧🇿', '502': '🇬🇹', '503': '🇸🇻', '504': '🇭🇳', '505': '🇳🇮', '506': '🇨🇷',
    '507': '🇵🇦', '508': '🇵🇲', '509': '🇭🇹', '590': '🇬🇵', '591': '🇧🇴', '592': '🇬🇾', '593': '🇪🇨',
    '594': '🇬🇫', '595': '🇵🇾', '596': '🇲🇶', '597': '🇸🇷', '598': '🇺🇾', '599': '🇨🇼', '670': '🇹🇱',
    '672': '🇳🇫', '673': '🇧🇳', '674': '🇳🇷', '675': '🇵🇬', '676': '🇹🇴', '677': '🇸🇧', '678': '🇻🇺',
    '679': '🇫🇯', '680': '🇵🇼', '681': '🇼🇫', '682': '🇨🇰', '683': '🇳🇺', '685': '🇼🇸', '686': '🇰🇮',
    '687': '🇳🇨', '688': '🇹🇻', '689': '🇵🇫', '690': '🇹🇰', '691': '🇫🇲', '692': '🇲🇭', '850': '🇰🇵',
    '852': '🇭🇰', '853': '🇲🇴', '855': '🇰🇭', '856': '🇱🇦', '880': '🇧🇩', '886': '🇹🇼', '960': '🇲🇻',
    '961': '🇱🇧', '962': '🇯🇴', '963': '🇸🇾', '964': '🇮🇶', '965': '🇰🇼', '966': '🇸🇦', '967': '🇾🇪',
    '968': '🇴🇲', '970': '🇵🇸', '971': '🇦🇪', '972': '🇮🇱', '973': '🇧🇭', '974': '🇶🇦', '975': '🇧🇹',
    '976': '🇲🇳', '977': '🇳🇵', '992': '🇹🇯', '993': '🇹🇲', '994': '🇦🇿', '995': '🇬🇪', '996': '🇰🇬',
    '998': '🇺🇿'
};

function getCountryFlag(countryCode) {
    if (!countryCode) return '';
    // Remove + prefix if present
    const code = countryCode.replace(/^\+/, '');
    return countryCodeFlags[code] || '🏳️';
}

function renderContacts() {
    const tbody = document.getElementById('contactTableBody');
    
    if (contacts.length === 0) {
        tbody.innerHTML = '<tr class="empty-row"><td colspan="6">No contacts added yet</td></tr>';
        return;
    }
    
    let html = '';
    contacts.forEach((contact, index) => {
        // Parse country code if not already parsed
        if (!contact.countryCode && !contact.localNumber) {
            const parsed = parsePhoneNumber(contact.phone);
            contact.countryCode = parsed.countryCode;
            contact.localNumber = parsed.localNumber;
        }
        
        const flag = getCountryFlag(contact.countryCode);
        const isNonIndian = contact.countryCode && contact.countryCode.replace(/^\+/, '') !== '91';
        
        html += '<tr data-index="' + index + '"' + (isNonIndian ? ' class="non-indian-contact"' : '') + '>';
        html += '<td class="checkbox-col"><input type="checkbox" ' + (contact.selected ? 'checked' : '') + ' onchange="toggleContactSelection(' + index + ')"></td>';
        html += '<td class="country-code-col"><span class="country-flag">' + flag + '</span> ' + escapeHtml(contact.countryCode || '-') + '</td>';
        html += '<td>' + escapeHtml(contact.localNumber || contact.phone) + '</td>';
        html += '<td>' + escapeHtml(contact.name || '-') + '</td>';
        html += '<td><span class="status-badge status-' + contact.status + '">' + contact.status + '</span></td>';
        html += '<td class="actions-col">';
        html += '<button class="btn btn-sm btn-success send-single-btn" onclick="sendToSingle(' + index + ')" title="Send to this contact"><i class="fas fa-paper-plane"></i></button> ';
        html += '<button class="btn btn-sm btn-primary" onclick="openEditModal(' + index + ')" title="Edit"><i class="fas fa-edit"></i></button> ';
        html += '<button class="btn btn-sm btn-danger" onclick="removeContact(' + index + ')" title="Delete"><i class="fas fa-trash"></i></button>';
        html += '</td>';
        html += '</tr>';
    });
    tbody.innerHTML = html;
}

function updateContactCount() {
    document.getElementById('contactCount').textContent = contacts.length;
}

function toggleContactSelection(index) {
    contacts[index].selected = !contacts[index].selected;
    saveContactsToStorage();
    updateSelectAllCheckbox();
}

function toggleSelectAll() {
    const checked = document.getElementById('selectAllCheckbox').checked;
    contacts.forEach(c => c.selected = checked);
    renderContacts();
    saveContactsToStorage();
}

function selectAllContacts() {
    contacts.forEach(c => c.selected = true);
    document.getElementById('selectAllCheckbox').checked = true;
    renderContacts();
    saveContactsToStorage();
}

function updateSelectAllCheckbox() {
    const allSelected = contacts.length > 0 && contacts.every(c => c.selected);
    document.getElementById('selectAllCheckbox').checked = allSelected;
}

function updateContactName(index, name) {
    contacts[index].name = name;
    saveContactsToStorage();
}

function removeContact(index) {
    contacts.splice(index, 1);
    renderContacts();
    saveContactsToStorage();
    updateContactCount();
}

function removeSelectedContacts() {
    const selected = contacts.filter(c => c.selected);
    if (selected.length === 0) {
        showAlert('No contacts selected', 'warning');
        return;
    }
    
    if (confirm('Remove ' + selected.length + ' selected contact(s)?')) {
        contacts = contacts.filter(c => !c.selected);
        renderContacts();
        saveContactsToStorage();
        updateContactCount();
        showAlert('Removed ' + selected.length + ' contact(s)', 'success');
    }
}

function clearAllContacts() {
    if (contacts.length === 0) {
        showAlert('No contacts to clear', 'warning');
        return;
    }
    
    if (confirm('Clear all contacts?')) {
        contacts = [];
        renderContacts();
        saveContactsToStorage();
        updateContactCount();
        showAlert('All contacts cleared', 'success');
    }
}

function updateAttachmentAccept() {
    // No longer needed - accept all types
}

// Auto-detect file type from MIME type or extension
function detectFileType(file) {
    const mimeType = file.type.toLowerCase();
    const fileName = file.name.toLowerCase();
    const ext = fileName.split('.').pop();
    
    // Check MIME type first
    if (mimeType.startsWith('image/')) return 'image';
    if (mimeType.startsWith('video/')) return 'video';
    if (mimeType.startsWith('audio/')) return 'audio';
    
    // Check extension for documents
    const imageExts = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'];
    const videoExts = ['mp4', 'mov', 'avi', 'mkv', 'webm', '3gp'];
    const audioExts = ['mp3', 'wav', 'ogg', 'm4a', 'aac', 'flac'];
    
    if (imageExts.includes(ext)) return 'image';
    if (videoExts.includes(ext)) return 'video';
    if (audioExts.includes(ext)) return 'audio';
    
    // Everything else is a document
    return 'document';
}

// Get icon for file type
function getFileTypeIcon(type) {
    const icons = {
        'image': 'fa-image',
        'video': 'fa-video',
        'audio': 'fa-music',
        'document': 'fa-file-alt'
    };
    return icons[type] || 'fa-file';
}

// Get color for file type
function getFileTypeColor(type) {
    const colors = {
        'image': '#4CAF50',
        'video': '#2196F3',
        'audio': '#9C27B0',
        'document': '#FF9800'
    };
    return colors[type] || '#666';
}

function handleAttachmentUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    uploadedAttachment = file;
    
    // Auto-detect file type
    const detectedType = detectFileType(file);
    document.getElementById('detectedFileType').value = detectedType;
    
    const preview = document.getElementById('attachmentPreview');
    const icon = getFileTypeIcon(detectedType);
    const color = getFileTypeColor(detectedType);
    
    let html = '<div class="preview-item" style="border-left: 4px solid ' + color + ';">';
    html += '<div class="preview-type-badge" style="background: ' + color + ';">';
    html += '<i class="fas ' + icon + '"></i> ' + detectedType.toUpperCase();
    html += '</div>';
    
    // Show image preview for images
    if (detectedType === 'image' && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = function(e) {
            let imgHtml = '<div class="preview-item" style="border-left: 4px solid ' + color + ';">';
            imgHtml += '<div class="preview-type-badge" style="background: ' + color + ';">';
            imgHtml += '<i class="fas ' + icon + '"></i> ' + detectedType.toUpperCase();
            imgHtml += '</div>';
            imgHtml += '<img src="' + e.target.result + '" class="preview-image" alt="Preview" style="max-width: 200px; max-height: 150px; margin: 10px 0;">';
            imgHtml += '<div class="preview-info">';
            imgHtml += '<span class="preview-name">' + escapeHtml(file.name) + '</span>';
            imgHtml += '<span class="preview-size">(' + formatFileSize(file.size) + ')</span>';
            imgHtml += '</div>';
            imgHtml += '<button class="btn btn-sm btn-danger" onclick="clearAttachment()"><i class="fas fa-times"></i> Remove</button>';
            imgHtml += '</div>';
            preview.innerHTML = imgHtml;
        };
        reader.readAsDataURL(file);
    } else {
        html += '<div class="preview-info" style="margin: 10px 0;">';
        html += '<span class="preview-name"><strong>' + escapeHtml(file.name) + '</strong></span><br>';
        html += '<span class="preview-size" style="color: #666;">' + formatFileSize(file.size) + '</span>';
        html += '</div>';
        html += '<button class="btn btn-sm btn-danger" onclick="clearAttachment()"><i class="fas fa-times"></i> Remove</button>';
        html += '</div>';
        preview.innerHTML = html;
    }
}

function clearAttachment() {
    uploadedAttachment = null;
    document.getElementById('attachmentFile').value = '';
    document.getElementById('attachmentPreview').innerHTML = '';
    document.getElementById('detectedFileType').value = '';
}

async function startBulkSend() {
    // Check bot status first
    if (!botConnected) {
        showAlert('Bot not connected! Please initialize the bot and scan QR code first.', 'error');
        checkBotStatus();
        return;
    }
    
    // Filter out contacts with invalid/empty phone numbers
    const validContacts = contacts.filter(c => c.phone && c.phone.trim().length >= 10);
    
    if (validContacts.length === 0) {
        showAlert('Please add valid contacts first', 'warning');
        return;
    }
    
    const message = document.getElementById('messageTemplate').value.trim();
    const hasAttachment = document.getElementById('hasAttachment').checked;
    // Get auto-detected file type instead of radio button
    const attachmentType = hasAttachment ? document.getElementById('detectedFileType').value : null;
    
    // Validation: need either message or attachment
    if (!message && (!hasAttachment || !uploadedAttachment)) {
        showAlert('Please enter a message or select an attachment', 'warning');
        return;
    }
    
    // If attachment is checked but no file selected
    if (hasAttachment && !uploadedAttachment) {
        showAlert('Please select an attachment file', 'warning');
        return;
    }
    
    const delay = parseInt(document.getElementById('messageDelay').value) || 5;
    
    isSending = true;
    isPaused = false;
    updateSendUI();
    
    const progressSection = document.querySelector('.progress-section');
    const progressFill = document.querySelector('.progress-fill');
    const sentCount = document.querySelector('.sent-count');
    const totalCount = document.querySelector('.total-count');
    const logContent = document.getElementById('sendLogContent');
    
    progressSection.style.display = 'block';
    totalCount.textContent = validContacts.length;
    logContent.innerHTML = '';
    
    let sent = 0;
    let failed = 0;
    
    let attachmentPath = null;
    if (hasAttachment && uploadedAttachment) {
        try {
            const formData = new FormData();
            formData.append('file', uploadedAttachment);
            
            addLogEntry(logContent, 'Uploading attachment...', 'info');
            
            const uploadRes = await fetch('/api/upload-attachment', {
                method: 'POST',
                body: formData
            });
            
            const uploadResult = await uploadRes.json();
            if (!uploadResult.success) {
                throw new Error(uploadResult.error || 'Upload failed');
            }
            attachmentPath = uploadResult.path;
            addLogEntry(logContent, 'Attachment uploaded successfully', 'success');
        } catch (error) {
            addLogEntry(logContent, 'Attachment upload failed: ' + error.message, 'error');
            isSending = false;
            updateSendUI();
            return;
        }
    }
    
    for (let i = 0; i < validContacts.length; i++) {
        if (!isSending) break;
        
        while (isPaused && isSending) {
            await sleep(500);
        }
        
        if (!isSending) break;
        
        const contact = validContacts[i];
        const personalizedMessage = message.replace(/{name}/gi, contact.name || 'there');
        
        addLogEntry(logContent, 'Sending to ' + contact.phone + '...', 'info');
        
        try {
            const response = await fetch('/api/send-message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    phone: contact.phone,
                    message: personalizedMessage,
                    attachment_path: attachmentPath,
                    file_type: attachmentType
                })
            });
            
            const result = await response.json();
            
            // Find original index to update status
            const originalIndex = contacts.findIndex(c => c.phone === contact.phone);
            
            if (result.success) {
                if (originalIndex !== -1) contacts[originalIndex].status = 'sent';
                sent++;
                addLogEntry(logContent, 'Sent to ' + contact.phone, 'success');
            } else {
                if (originalIndex !== -1) contacts[originalIndex].status = 'failed';
                failed++;
                addLogEntry(logContent, 'Failed: ' + contact.phone + ' - ' + result.error, 'error');
            }
        } catch (error) {
            const originalIndex = contacts.findIndex(c => c.phone === contact.phone);
            if (originalIndex !== -1) contacts[originalIndex].status = 'failed';
            failed++;
            addLogEntry(logContent, 'Error: ' + contact.phone + ' - ' + error.message, 'error');
        }
        
        sentCount.textContent = sent + failed;
        progressFill.style.width = ((sent + failed) / validContacts.length * 100) + '%';
        renderContacts();
        saveContactsToStorage();
        
        if (i < validContacts.length - 1 && isSending) {
            await sleep(delay * 1000);
        }
    }
    
    isSending = false;
    updateSendUI();
    addLogEntry(logContent, 'Completed! Sent: ' + sent + ', Failed: ' + failed, sent > 0 ? 'success' : 'error');
    showAlert('Bulk send complete. Sent: ' + sent + ', Failed: ' + failed, sent > 0 ? 'success' : 'error');
}

// Send to a single contact from the table
async function sendToSingle(index) {
    // Check bot status first
    if (!botConnected) {
        showAlert('Bot not connected! Please initialize the bot and scan QR code first.', 'error');
        checkBotStatus();
        return;
    }
    
    const contact = contacts[index];
    if (!contact || !contact.phone || contact.phone.trim().length < 10) {
        showAlert('Invalid contact phone number', 'error');
        return;
    }
    
    const message = document.getElementById('messageTemplate').value.trim();
    const hasAttachment = document.getElementById('hasAttachment').checked;
    const attachmentType = hasAttachment ? document.getElementById('detectedFileType').value : null;
    
    // Validation: need either message or attachment
    if (!message && (!hasAttachment || !uploadedAttachment)) {
        showAlert('Please enter a message or select an attachment first', 'warning');
        return;
    }
    
    // If attachment is checked but no file selected
    if (hasAttachment && !uploadedAttachment) {
        showAlert('Please select an attachment file first', 'warning');
        return;
    }
    
    // Disable the send button for this contact
    const btn = document.querySelector(`tr[data-index="${index}"] .send-single-btn`);
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    }
    
    const personalizedMessage = message.replace(/{name}/gi, contact.name || 'there');
    
    try {
        let attachmentPath = null;
        
        // Upload attachment if needed
        if (hasAttachment && uploadedAttachment) {
            const formData = new FormData();
            formData.append('file', uploadedAttachment);
            
            const uploadRes = await fetch('/api/upload-attachment', {
                method: 'POST',
                body: formData
            });
            
            const uploadResult = await uploadRes.json();
            if (!uploadResult.success) {
                throw new Error(uploadResult.error || 'Attachment upload failed');
            }
            attachmentPath = uploadResult.path;
        }
        
        // Send the message
        const response = await fetch('/api/send-message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                phone: contact.phone,
                message: personalizedMessage,
                attachment_path: attachmentPath,
                file_type: attachmentType
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            contacts[index].status = 'sent';
            showAlert(`Message sent to ${contact.name || contact.phone}`, 'success');
        } else {
            contacts[index].status = 'failed';
            showAlert(`Failed to send to ${contact.name || contact.phone}: ${result.error}`, 'error');
        }
    } catch (error) {
        contacts[index].status = 'failed';
        showAlert(`Error sending to ${contact.name || contact.phone}: ${error.message}`, 'error');
    }
    
    renderContacts();
    saveContactsToStorage();
}

function pauseSend() {
    isPaused = !isPaused;
    const pauseBtn = document.getElementById('pauseSendBtn');
    pauseBtn.innerHTML = isPaused ? '<i class="fas fa-play"></i> Resume' : '<i class="fas fa-pause"></i> Pause';
}

function stopSend() {
    if (confirm('Stop sending messages?')) {
        isSending = false;
        isPaused = false;
        updateSendUI();
    }
}

function updateSendUI() {
    const startBtn = document.getElementById('startSendBtn');
    const pauseBtn = document.getElementById('pauseSendBtn');
    const stopBtn = document.getElementById('stopSendBtn');
    
    if (isSending) {
        startBtn.style.display = 'none';
        pauseBtn.style.display = 'inline-flex';
        stopBtn.style.display = 'inline-flex';
    } else {
        startBtn.style.display = 'inline-flex';
        pauseBtn.style.display = 'none';
        stopBtn.style.display = 'none';
    }
}

function addLogEntry(container, message, type) {
    const entry = document.createElement('div');
    entry.className = 'log-entry log-' + type;
    entry.innerHTML = '<span class="log-time">' + new Date().toLocaleTimeString() + '</span> ' + message;
    container.appendChild(entry);
    container.scrollTop = container.scrollHeight;
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function showAlert(message, type) {
    const container = document.getElementById('alertContainer');
    if (container) {
        container.innerHTML = '<div class="alert alert-' + type + '">' + message + '</div>';
        setTimeout(function() {
            container.innerHTML = '';
        }, 5000);
    } else {
        alert(message);
    }
}

// Edit Contact Modal Functions
function openEditModal(index) {
    const contact = contacts[index];
    document.getElementById('editContactIndex').value = index;
    document.getElementById('editCountryCode').value = contact.countryCode || '';
    document.getElementById('editPhone').value = contact.localNumber || contact.phone;
    document.getElementById('editName').value = contact.name || '';
    document.getElementById('editContactModal').style.display = 'flex';
}

function closeEditModal() {
    document.getElementById('editContactModal').style.display = 'none';
}

function saveContactEdit() {
    const index = parseInt(document.getElementById('editContactIndex').value);
    const countryCode = document.getElementById('editCountryCode').value.trim().replace(/[^\d]/g, '');
    const localNumber = document.getElementById('editPhone').value.trim().replace(/[^\d]/g, '');
    const name = document.getElementById('editName').value.trim();
    
    if (!localNumber || localNumber.length < 10) {
        showAlert('Please enter a valid phone number (at least 10 digits)', 'warning');
        return;
    }
    
    // Combine country code and local number for full phone
    const fullPhone = countryCode + localNumber;
    
    contacts[index].countryCode = countryCode;
    contacts[index].localNumber = localNumber;
    contacts[index].phone = fullPhone;
    contacts[index].name = name;
    
    renderContacts();
    saveContactsToStorage();
    closeEditModal();
    showAlert('Contact updated successfully', 'success');
}

// Close modal when clicking outside
document.addEventListener('click', function(e) {
    const modal = document.getElementById('editContactModal');
    if (e.target === modal) {
        closeEditModal();
    }
});
