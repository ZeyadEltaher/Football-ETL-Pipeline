<<<<<<< HEAD
# Football-Data-Engine
Advanced Python scraper for football match data from Soccerway and Transfermarkt, storing results in MySQL.
=======
# Football Data Engine

Football Data Engine is an advanced Python project designed to scrape detailed football match data from websites like Soccerway and Transfermarkt, and store it in a well-structured MySQL database.

---

## Features

- Collect detailed match information including teams, scores, match status, date, round, league, and more.  
- Supports scraping data for specified gameweeks or date ranges.  
- Automatically creates necessary database tables if they do not exist.  
- Securely manages database credentials using a `.env` environment file.  
- Handles errors gracefully to ensure continuous scraping.  
- Uses Selenium and BeautifulSoup to handle dynamic websites and parse HTML content efficiently.

---

## Requirements

- Python 3.7 or higher  
- A running and accessible MySQL server  
- The following Python packages:  
  - selenium  
  - beautifulsoup4  
  - python-dotenv  
  - mysql-connector-python  
  - requests  

---

## Setup Instructions

1. **Clone or download** this repository.  

2. **Create a `.env` file** in the root project directory with your database credentials (modify the values accordingly):

   ```env
   DB_HOST=your_database_host
   DB_USER=your_database_username
   DB_PASSWORD=your_database_password
   DB_NAME=your_database_name
3. **Install the required Python packages** by running:

   pip install -r requirements.txt

4. **Run the script and invoke the appropriate functions in main.py or functions.py to scrape data for your desired gameweeks or date ranges.**


## How It Works
- The project uses Selenium to navigate dynamic websites such as Soccerway and Transfermarkt.

- It parses HTML content with BeautifulSoup to extract detailed match and team information.

- Data is inserted into structured MySQL tables like matches and teams.

- If the required tables do not exist, they are created automatically by the script.

- Database connection details are securely loaded from a .env file.

## Project Structure
```
/Football_Data_Engine
│
├── sample.env             # Environment variables for DB credentials
├── main.py                # Main Python script to run the scraper
├── functions.py           # Helper functions for scraping and processing data
├── queries.py             # SQL queries for creating and manipulating tables
├── database.py            # Database connection and data insertion logic
├── constants.py           # Constants like URLs and mappings
├── requirements.txt       # Required Python packages
└── README.md              # This documentation file
>>>>>>> 4f3d934 (Initial commit: Add FootballDataEngine project files)
