# WhatsApp Automation Bot# 🚀 WhatsApp Message Sender Bot



A professional WhatsApp Web automation tool with a user-friendly web interface. Send messages, attachments, and bulk communications programmatically.A professional web-based WhatsApp automation bot built with Python, Flask, and Selenium. Send individual or bulk messages, schedule messages, and manage contacts through an intuitive web interface.



## ✨ Features![WhatsApp Bot](https://img.shields.io/badge/WhatsApp-Bot-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)

- 📱 **Send Text Messages** - Single or bulk message sending![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)

- 📎 **Send Attachments** - Documents, images, videos with captions![Selenium](https://img.shields.io/badge/Selenium-4.15-43B02A?style=for-the-badge&logo=selenium&logoColor=white)

- 📋 **CSV Import** - Import contacts from CSV files

- 🔄 **Auto-Match** - Automatically match files to contacts by name## ✨ Features

- 📅 **Schedule Messages** - Schedule messages for later delivery

- 🌐 **Unicode Support** - Full support for Gujarati and other languages- 📱 **Send Individual Messages** - Send WhatsApp messages to any phone number

- 🖥️ **Cross-Platform** - Works on macOS, Windows, and Linux- 📢 **Bulk Messaging** - Send the same message to multiple contacts with customizable delays

- 🌍 **Multi-Browser** - Supports Chrome, Brave, Firefox, Edge- 🤖 **Automated Bulk Attachments** - Automatically send files to contacts by matching filenames (FULLY AUTOMATED!)

- ⏰ **Message Scheduling** - Schedule messages to be sent at a specific date and time

## 🚀 Quick Start- 👥 **Contact Management** - Store and manage your contacts in a built-in address book

- 📁 **CSV Import** - Import contacts in bulk from CSV files

### One-Command Setup- 📎 **Send Attachments** - Send images, videos, documents, and other files

- � **Message History** - Track all sent messages with status (sent/failed)

**macOS/Linux:**- 📈 **Dashboard Analytics** - View statistics of messages sent, failed, and scheduled

```bash- 🎨 **Modern UI** - Professional, responsive web interface with dark sidebar

python3 setup.py && ./run.sh- 💾 **SQLite Database** - Persistent storage for contacts, messages, and schedules

```- 🔄 **Persistent Sessions** - Stay logged in to WhatsApp Web between restarts



**Windows:**## 🛠️ Technologies Used

```cmd

python setup.py && run.bat- **Backend**: Python 3.8+, Flask

```- **Automation**: Selenium WebDriver

- **Database**: SQLite3

### Manual Setup- **Frontend**: HTML5, CSS3, JavaScript

- **Scheduling**: APScheduler

1. **Clone the repository:**- **Browser Automation**: Chrome/Chromium/Brave with WebDriver Manager

   ```bash

   git clone https://github.com/dwarkeshkaswala/whatsapp-automation.git## 📋 Prerequisites

   cd whatsapp-automation

   ```Before you begin, ensure you have the following installed:



2. **Run setup:**- Python 3.8 or higher

   ```bash- Google Chrome, Chromium, or Brave browser

   python setup.py- pip (Python package manager)

   ```

## 🚀 Installation

3. **Start the application:**

   ### 1. Clone the Repository

   **macOS/Linux:**

   ```bash```bash

   ./run.shgit clone https://github.com/dwarkeshkaswala/whatsapp-automation.git

   ```cd whatsapp-automation

   ```

   **Windows:**

   ```cmd### 2. Create a Virtual Environment (Recommended)

   run.bat

   ``````bash

# On macOS/Linux

4. **Open in browser:**python3 -m venv venv

   ```source venv/bin/activate

   http://localhost:5001

   ```# On Windows

python -m venv venv

## 📋 Requirementsvenv\Scripts\activate

```

- **Python 3.8+**

- **One of these browsers:**### 3. Install Dependencies

  - Google Chrome

  - Brave Browser```bash

  - Mozilla Firefoxpip install -r requirements.txt

  - Microsoft Edge```



## 🔧 Configuration### 4. Set Up Environment Variables



Edit `.env` file to customize:```bash

# Copy the example environment file

```envcp .env.example .env

# Server Settings

HOST=0.0.0.0# Edit .env and set your configuration

PORT=5001# You can use the default values for development

```

# Browser Settings (chrome, brave, firefox, edge)

BROWSER=chrome### 5. Run the Application

HEADLESS=true

``````bash

python app.py

## 📖 Usage```



### 1. Initialize WhatsAppThe application will start on `http://localhost:5000`



1. Open `http://localhost:5001`## 📖 Usage Guide

2. Click **"Initialize WhatsApp"**

3. Scan the QR code with your phone (WhatsApp > Linked Devices > Link a Device)### Initial Setup

4. Wait for login confirmation

1. **Start the Application**

### 2. Send Messages   ```bash

   python app.py

**Single Message:**   ```

1. Go to **Send Message** page

2. Enter phone number (with country code, e.g., `+1234567890`)2. **Open Your Browser**

3. Enter your message   - Navigate to `http://localhost:5000`

4. Click **Send**

3. **Initialize the Bot**

**With Attachment:**   - Click the "Initialize Bot" button in the sidebar

1. Enter phone number and message   - A Chrome browser window will open with WhatsApp Web

2. Select a file to attach   - Scan the QR code with your WhatsApp mobile app

3. Click **Send with Attachment**   - Once logged in, you're ready to send messages!



### 3. Bulk Sending### Sending Individual Messages



**Import Contacts:**1. Navigate to **Send Message** from the sidebar

1. Go to **Contacts** page2. Select the "Single Message" tab

2. Upload a CSV file with columns: `name`, `phone`3. Enter the recipient's phone number (with country code, e.g., +1234567890)

3. Contacts will be saved to the database4. Type your message

5. Click "Send Message"

**Send to All:**

1. Go to **Send Message** page### Sending Bulk Messages

2. Enter your message

3. Click **Send to All Contacts**1. First, add contacts in the **Contacts** section

2. Navigate to **Send Message** → "Bulk Messages" tab

### 4. Auto-Match Attachments3. Select the contacts you want to message

4. Type your message

1. Place files in the `attachments/` folder5. Set the delay between messages (recommended: 5-10 seconds)

2. Name files to match contact names (e.g., `John.pdf` for contact "John")6. Click "Send Bulk Messages"

3. Go to **Automated** page

4. Click **Auto-Send Attachments**### Sending Messages with Attachments



## 📁 Project Structure1. Navigate to **Send Message** → "With Attachment" tab

2. Enter the recipient's phone number

```3. Type your message (optional caption)

whatsapp-automation/4. Click "Select File" and choose your attachment

├── app.py              # Flask application5. Supported files: Images, Videos, PDFs, Documents (Max 100MB)

├── whatsapp_bot.py     # WhatsApp automation core6. Click "Send with Attachment"

├── database.py         # SQLite database handling

├── setup.py            # Universal setup script### 🤖 Automated Bulk Attachment Sending (NEW!)

├── run.sh              # Mac/Linux run script

├── run.bat             # Windows run script**The ultimate automation feature - NO manual work required!**

├── requirements.txt    # Python dependencies

├── .env                # ConfigurationThis feature automatically matches files in a folder to your contacts and sends them - perfect for bulk operations.

├── attachments/        # Files to send

├── uploads/            # Temporary uploads**How it works:**

├── whatsapp_profile/   # Browser session data1. **Import Contacts** - Use CSV import to add all your contacts

├── static/             # CSS, JS files2. **Name Files to Match Contacts** - Place files in the `attachments/` folder with names matching your contacts

└── templates/          # HTML templates3. **Scan & Preview** - The system shows you what will be sent to whom

```4. **Start Automation** - Click one button and all files are sent automatically!



## 🔒 Security Notes**Example Workflow:**



- WhatsApp session is stored locally in `whatsapp_profile/`1. Import contacts via CSV:

- Never share your session folder   ```csv

- Use on a secure, private network   name,phone

- Respect WhatsApp's Terms of Service   John Doe,+1234567890

   Jane Smith,+9876543210

## 🐛 Troubleshooting   Bob Johnson,+1122334455

   ```

### "No supported browser found"

Install Chrome, Brave, Firefox, or Edge.2. Place files in `attachments/` folder:

   - `John Doe.pdf` → Will be sent to John Doe

### "Could not find attachment button"   - `Jane Smith.jpg` → Will be sent to Jane Smith

WhatsApp Web UI may have changed. Run in visible mode to debug:   - `Bob Johnson.docx` → Will be sent to Bob Johnson

```env

HEADLESS=false3. Navigate to **Automated Bulk** from sidebar

```4. Click **"Scan Attachments"** to preview matches

5. (Optional) Add a message to send with all files

### "QR code not showing"6. Click **"Start Automated Send"**

1. Clear `whatsapp_profile/` folder7. Watch as all files are automatically sent!

2. Restart the application

3. Try again**Features:**

- ✅ Automatic filename-to-contact matching (case-insensitive)

### Session expired- ✅ Partial name matching (e.g., "John.pdf" matches "John Doe")

1. Delete `whatsapp_profile/` folder- ✅ **Full Unicode support** - Gujarati (ગુજરાતી), Hindi (हिंदी), and all languages!

2. Restart and scan QR code again- ✅ Preview before sending - see all matches

- ✅ Progress tracking with real-time updates

## 📝 CSV Format- ✅ Detailed results showing sent/failed/unmatched

- ✅ Configurable delay to avoid spam detection

```csv- ✅ Handles unmatched files and contacts gracefully

name,phone

John Doe,+1234567890**Supported File Types:**

Jane Smith,+0987654321- Images: PNG, JPG, JPEG, GIF

```- Documents: PDF, DOCX, XLSX, TXT

- Archives: ZIP

## 🤝 Contributing

**Best Practices:**

Contributions are welcome! Please feel free to submit a Pull Request.- Use clear, consistent naming (match CSV contact names exactly)

- Set 5-10 second delays between sends

## ⚠️ Disclaimer- Review scan results before starting automation

- Keep files under 100MB (app limit, WhatsApp Web supports up to 2GB but larger files are slower)

This tool is for educational purposes only. Use responsibly and in compliance with WhatsApp's Terms of Service. The authors are not responsible for any misuse or violations.

### Scheduling Messages

## 📄 License

1. Navigate to **Schedule** from the sidebar

MIT License - see LICENSE file for details.2. Select a contact or enter a phone number

3. Type your message
4. Choose the date and time for sending
5. Click "Schedule Message"

The message will be automatically sent at the scheduled time (the app must be running).

### Managing Contacts

**Add Individual Contact:**
1. Navigate to **Contacts** from the sidebar
2. Fill in the contact name and phone number
3. Click "Add Contact"

**Import Contacts from CSV:**
1. Prepare a CSV file with columns: `name` and `phone`
2. See `sample_contacts.csv` for reference format
3. Navigate to **Contacts** → "Import from CSV"
4. Upload your CSV file
5. Click "Import Contacts"

**CSV Format Example:**
```csv
name,phone
John Doe,+1234567890
Jane Smith,+9876543210
```

**Manage Contacts:**
- View all contacts in the table
- Delete contacts using the trash icon

### Viewing Message History

1. Navigate to **History** from the sidebar
2. View all sent messages with their status
3. See timestamps and recipient information

## 🎯 Features in Detail

### CSV Contact Import
- Bulk import contacts from CSV files
- Automatic validation and error handling
- Skips invalid entries and reports statistics
- Supports various CSV column formats (name/Name/NAME, phone/Phone/number)

### Attachment Support
- Send images (JPG, PNG, GIF)
- Send documents (PDF, DOC, DOCX, TXT)
- Send videos (MP4) and audio (MP3)
- Maximum file size: 100MB
- Optional message caption

### Message Scheduling
- Uses APScheduler for reliable background job execution
- Persistent scheduling across application restarts
- Automatic status updates after message delivery

### Contact Management
- SQLite database for persistent storage
- Easy add/delete operations
- Quick contact selection for bulk messaging

### Message History
- Track all messages with timestamps
- Status indicators (sent/failed/pending)
- Searchable and filterable history

### Security Features
- Session persistence using Chrome profile
- No plaintext password storage
- Secure session management with Flask

## 🔧 Configuration

### Environment Variables

Edit the `.env` file to configure:

```env
FLASK_SECRET_KEY=your-secret-key-here
FLASK_ENV=development
DATABASE_PATH=whatsapp_bot.db
```

### Chrome Driver

The application uses `webdriver-manager` to automatically download and manage ChromeDriver. No manual setup required!

## 📁 Project Structure

```
whatsapp-automation/
├── app.py                 # Main Flask application
├── whatsapp_bot.py       # WhatsApp automation logic
├── database.py           # Database operations
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── .gitignore          # Git ignore rules
├── templates/          # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── send.html
│   ├── schedule.html
│   ├── contacts.html
│   └── history.html
├── static/             # Static files
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── main.js
│       ├── send.js
│       ├── schedule.js
│       └── contacts.js
└── session/            # WhatsApp Web session data (auto-generated)
```

## ⚠️ Important Notes

### WhatsApp Terms of Service
- This bot is for **personal and educational use only**
- Do not use for spam or unauthorized marketing
- Respect WhatsApp's Terms of Service
- Be cautious with bulk messaging to avoid account restrictions

### Rate Limiting
- Recommended delay between bulk messages: 5-10 seconds
- Avoid sending too many messages in a short period
- WhatsApp may temporarily ban accounts that send spam

### Browser Session
- Keep the Chrome browser window open while sending messages
- The bot uses your personal WhatsApp account
- Session data is saved in the `session/` folder for persistence

## 🐛 Troubleshooting

### Bot won't initialize
- Ensure Chrome/Chromium is installed
- Check internet connection
- Delete the `session/` folder and try again

### Messages not sending
- Verify you're logged in to WhatsApp Web
- Check if the phone number format is correct (+countrycode + number)
- Ensure the recipient is not blocking you

### Chrome driver errors
- Update Chrome to the latest version
- Clear the webdriver cache: `pip uninstall webdriver-manager && pip install webdriver-manager`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Your Name**
- GitHub: [@dwarkeshkaswala](https://github.com/dwarkeshkaswala)

## 🙏 Acknowledgments

- WhatsApp Web for providing the web interface
- Selenium for browser automation
- Flask for the web framework
- The open-source community

## 📞 Support

If you encounter any issues or have questions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Open an issue on GitHub
3. Contact the maintainer

---

**⚡ Happy Messaging! ⚡**

*Remember to use responsibly and respect WhatsApp's Terms of Service*
