# The Nostalgia Time Machine 🚀

A web application that allows users to travel back in time and explore music, events, and cultural highlights from any year between 1980 and the present.

## Features ✨

- **Year Selection**: Choose any year to explore its cultural highlights
- **Music Discovery**: Get top songs from Billboard charts for selected years
- **Historical Events**: View significant events from Wikipedia
- **Archived Websites**: Explore old versions of popular websites via Internet Archive
- **User Authentication**: Secure login/registration system
- **Favorites System**: Save and manage your favorite memories
- **Admin Panel**: User management for administrators
- **Activity Tracking**: Monitor user interactions
- **Responsive Design**: Works perfectly on all devices

## Tech Stack 🛠️

### Backend

- **Flask**: Python web framework
- **MongoDB**: NoSQL database for data persistence
- **BeautifulSoup4**: Web scraping for external data
- **Flask-Session**: Session management
- **Werkzeug**: Security utilities

### Frontend

- **HTML5/CSS3**: Modern, responsive design
- **JavaScript**: Interactive functionality
- **Bootstrap**: UI components and styling
- **Font Awesome**: Icons
- **Google Fonts**: Typography

## Installation & Setup 📦

### Prerequisites

- Python 3.7+
- MongoDB
- Node.js (for package management)

### Backend Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd s
```

2. Create and activate virtual environment:

```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

3. Install Python dependencies:

```bash
cd backend
pip install -r requirements.txt
```

4. Set up MongoDB:

```bash
# Start MongoDB service
mongod

# Create database (optional - will be created automatically)
mongo
use nostalgia_db
```

5. Set environment variables:

```bash
# Create .env file in backend directory
SECRET_KEY=your_secret_key_here
FLASK_DEBUG=False
```

6. Run the application:

```bash
python app.py
```

The backend will be available at `http://localhost:5001`

### Frontend Setup

1. Install Node.js dependencies:

```bash
npm install
```

2. The frontend is served by Flask, so no additional setup is needed.

## Project Structure 📁

```
s/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── requirements.txt    # Python dependencies
│   ├── sessions/          # Session storage
│   └── flask_session/     # Flask session files
├── templates/
│   ├── index.html         # Landing page
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   ├── dashboard.html     # User dashboard
│   ├── admin.html         # Admin panel
│   └── contact.html       # Contact page
├── static/
│   ├── styles.css         # Main stylesheet
│   ├── dashboard.js       # Dashboard functionality
│   ├── auth.js           # Authentication scripts
│   └── *.png             # Images
├── package.json          # Node.js dependencies
└── README.md            # This file
```

## API Endpoints 🔌

### Authentication

- `POST /login` - User login
- `POST /register` - User registration
- `GET /logout` - User logout

### User Management

- `GET /dashboard` - User dashboard
- `GET /get_user_data` - Get user profile data
- `POST /update_profile` - Update user profile
- `GET /get_favorites` - Get user favorites
- `POST /toggle_favorite` - Add/remove favorites

### Nostalgia Data

- `GET /get_nostalgia_data/<year>` - Get nostalgia data for specific year
- `POST /log_activity` - Log user activity
- `GET /get_activity` - Get user activity history

### Admin

- `GET /admin_panel` - Admin dashboard
- `POST /delete_user/<user_id>` - Delete user

### Contact

- `GET /contact` - Contact page
- `POST /submit_contact` - Submit contact form

## Security Features 🔒

- Password hashing with Werkzeug
- Session-based authentication
- Rate limiting (10 requests per minute per user)
- Input validation and sanitization
- CSRF protection via Flask-Session
- Secure headers and configurations

## Contributing 🤝

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License 📄

This project is licensed under the ISC License.

## Support 💬

For support, email support@nostalgiatimemachine.com or create an issue in the repository.

## Acknowledgments 🙏

- Billboard for music chart data
- Wikipedia for historical events
- Internet Archive for website snapshots
- Flask and MongoDB communities for excellent documentation

---

**Made with ❤️ for nostalgia lovers everywhere**
