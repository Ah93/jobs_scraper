<img width="1251" height="554" alt="img1" src="https://github.com/user-attachments/assets/fcf70b1c-98ac-4260-b12b-080edd201cf4" />

<img width="1187" height="540" alt="img2" src="https://github.com/user-attachments/assets/1f8b39e5-d181-4733-85ab-f3639e281cc3" />

# 🚀 Job Scraper Pro

A powerful Django-based web application for scraping job listings from multiple platforms including Indeed and Glassdoor. Built with modern web technologies and featuring a beautiful, responsive UI.

![Job Scraper Pro](https://img.shields.io/badge/Job%20Scraper-Pro-blue)
![Django](https://img.shields.io/badge/Django-5.2.6-green)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Selenium](https://img.shields.io/badge/Selenium-4.15.2-orange)

## ✨ Features

### 🔍 Multi-Platform Job Scraping
- **Indeed** - Scrape job listings with location-based filtering
- **Glassdoor** - Extract job data with company insights
- **Extensible** - Easy to add new platforms (LinkedIn support coming soon)

### 📊 Smart Data Management
- **Duplicate Prevention** - Intelligent fingerprinting system prevents duplicate entries
- **Company Tracking** - Automatic company database management
- **Source Attribution** - Track which platform each job was found on
- **Real-time Updates** - Live job count and progress tracking

### 🎨 Modern User Interface
- **Responsive Design** - Works perfectly on desktop, tablet, and mobile
- **Dark Theme** - Beautiful gradient design with modern aesthetics
- **Real-time Progress** - Live updates during scraping operations
- **Interactive Dashboard** - Clean, intuitive job browsing experience

### 📈 Advanced Functionality
- **CSV Export** - Download scraped data for analysis
- **Bulk Operations** - Clear all jobs with one click
- **Progress Tracking** - Real-time scraping progress with detailed status
- **Error Handling** - Robust error management and user feedback

## 🛠️ Technology Stack

- **Backend**: Django 5.2.6
- **Web Scraping**: Selenium 4.15.2, BeautifulSoup4
- **Database**: SQLite (easily configurable for PostgreSQL/MySQL)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Browser Automation**: Chrome WebDriver with anti-detection features

## 📋 Prerequisites

- Python 3.8 or higher
- Google Chrome browser
- Virtual environment (recommended)
- Windows/macOS/Linux

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd job_scrape
```

### 2. Set Up Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Database
```bash
cd jobsuite
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Admin User (Optional)
```bash
python manage.py createsuperuser
```

### 6. Run the Application
```bash
python manage.py runserver
```

### 7. Access the Dashboard
Open your browser and navigate to: **http://127.0.0.1:8000/**

## 📖 How to Use

### Basic Job Scraping

1. **Select Platform**: Choose between Indeed or Glassdoor
2. **Enter Job Role**: Specify the position you're looking for (e.g., "Data Scientist", "Software Engineer")
3. **Set Location**: Enter the desired location (e.g., "New York, NY", "San Francisco, CA", "Remote")
4. **Choose Limit**: Set how many jobs to scrape (1-100)
5. **Click "Run Scraper"**: Watch the magic happen!

### Advanced Features

#### Real-time Progress Tracking
- Live progress updates during scraping
- Detailed status messages
- Automatic error handling and recovery

#### Data Management
- **View Results**: Browse scraped jobs in the beautiful table interface
- **Export Data**: Download results as CSV for further analysis
- **Clear Database**: Reset all data with one click (with confirmation)

#### Platform-Specific Features

**Indeed Scraping:**
- Location-based job filtering
- Anti-detection measures
- Automatic pagination handling

**Glassdoor Scraping:**
- Company insights and ratings
- Advanced job filtering
- Robust error handling

## 🗂️ Project Structure

```
job_scrape/
├── jobsuite/                    # Django project
│   ├── jobs/                   # Main app
│   │   ├── scraper/           # Scraping modules
│   │   │   ├── indeed_scraper.py
│   │   │   ├── glassdoor.py
│   │   │   ├── pipeline.py
│   │   │   └── ...
│   │   ├── templates/         # HTML templates
│   │   ├── models.py          # Database models
│   │   ├── views.py           # View logic
│   │   └── forms.py           # Form definitions
│   ├── manage.py
│   └── settings.py
├── requirements.txt
└── README.md
```

## 🔧 Configuration

### Database Settings
The app uses SQLite by default. To use PostgreSQL or MySQL:

1. Update `DATABASES` in `jobsuite/settings.py`
2. Install the appropriate database adapter
3. Run migrations

### Scraping Limits
- Default job limit: 20
- Maximum job limit: 100
- Rate limiting: Built-in delays to prevent blocking

### Browser Settings
- Chrome WebDriver automatically managed
- Anti-detection features enabled
- Headless mode available for server deployment

## 📊 Data Models

### Job Model
- **Title**: Job position title
- **Company**: Foreign key to Company model
- **Location**: Job location
- **Description**: Full job description
- **Source URL**: Original job posting URL
- **Sources**: List of platforms where job was found
- **Fingerprint**: Unique identifier for deduplication
- **Posted At**: When the job was originally posted
- **Scraped At**: When we scraped the job

### Company Model
- **Name**: Company name
- **Website**: Company website URL
- **Email**: Contact email (if found)
- **Created At**: When company was added to database

## 🚨 Troubleshooting

### Common Issues

**Chrome Driver Problems:**
- The app automatically downloads and manages ChromeDriver
- Ensure Chrome browser is installed and up-to-date

**Scraping Failures:**
- Check your internet connection
- Some platforms may have rate limiting
- Try reducing the job limit

**Database Issues:**
- Run `python manage.py migrate` to update database schema
- Check file permissions for SQLite database

**Memory Issues:**
- Reduce the job limit for large scrapes
- Clear old data using the "Clear All Jobs" button

### Getting Help

1. Check the console output for detailed error messages
2. Ensure all dependencies are installed correctly
3. Verify your Python version (3.8+ required)
4. Check that Chrome browser is installed

## 🔮 Future Enhancements

- [ ] LinkedIn scraping support
- [ ] Scheduled scraping with cron jobs
- [ ] Advanced filtering and search
- [ ] Email notifications for new jobs
- [ ] Job application tracking
- [ ] Company analysis dashboard
- [ ] API endpoints for external integration
- [ ] Docker containerization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Legal Notice

This tool is for educational and personal use only. Please respect the terms of service of the platforms you're scraping from. Use responsibly and consider the impact on the target websites.

## 🙏 Acknowledgments

- Django community for the excellent framework
- Selenium team for browser automation capabilities
- BeautifulSoup for HTML parsing
- All contributors and users of this project

---

**Happy Job Hunting! 🎯**

*Built with ❤️ for job seekers and recruiters everywhere*
