# OpenUp WM Registration Project

A Python-based web app designed for William & Mary students to receive notifications when a seat becomes available in a saved course.

## Table of Contents
- [About](#about)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Contact](#contact)

## About

OpenUp WM is a course registration tool built to simplify the process of securing a spot in high-demand classes at William & Mary. By monitoring course availability, the app sends real-time notifications to students when a seat opens in their saved classes, helping them register quickly and efficiently.

## Features

- **Course Monitoring**: Save desired courses and get notified when seats become available.
- **Real-Time Notifications**: Receive alerts via the app when course status changes.
- **User-Friendly Interface**: Simple web-based dashboard for managing saved courses.
- **Built for W&M Students**: Tailored to the William & Mary course registration system.

## Tech Stack

- **Backend**: Python, Django
- **Frontend**: HTML, CSS
- **Database**: SQLite (default for development)
- **Deployment**: Configurable for local or server environments

## Installation

Follow these steps to set up the project locally:

### Prerequisites

- Python 3.8+
- Git
- Virtualenv (recommended)

### Steps

1. Clone the repository and move to appropriate folder:
   ```bash
   git clone https://github.com/marniiii/OpenUp-WM-Registration-Project.git
   cd OpenUp-WM-Registration-Project/MarksApp/src/
2. Create and activate a virtual environment
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
3. Install dependencies:
    ```bash
    pip install -r requirements.txt

4. Set up the database:
    ```bash
    python manage.py migrate
5. Open a new terminal and run celery worker:
   ```bash
   cd OpenUp-WM-Registration-Project/MarksApp/src
   source venv/bin/activate
   celery -A mysite worker --loglevel=info
5. Run the development server:
    ```bash
    python manage.py runserver

Open your browser and navigate to http://127.0.0.1:8000.

## Usage

1. **Login**: Log in to access the dashboard.
2. **Add Courses**: Search for and save courses you want to monitor.
3. **Receive Notifications**: Get alerts when a seat opens in your saved courses.
4. **Register**: Use the notification to quickly register via the W&M system.

> **Note**: Ensure the app is configured to connect to the W&M course registration system (details in [configuration docs](#) if applicable).

## Contact

For questions, suggestions, or support, reach out to:

GitHub: marniiii

Email: markmarni@live.com

