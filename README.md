# Gratitude — Daily Reflection Tracker

A full-stack wellness app for daily gratitude journaling and mood tracking. Built with Flask, PostgreSQL, and vanilla JavaScript.

**Live app:** [https://web-production-61a76.up.railway.app/](https://web-production-61a76.up.railway.app/)

---

## What it does

Gratitude is a personal daily reflection tool. Each day, users record three things they're grateful for, three things they're praying or hoping for, and a life score out of 10. The app tracks this over time and visualises progress as a line graph.

Key features:

- Multi-step guided form with smooth transitions
- Line graph showing mood score over time (last 30 days or all time view)
- Hover tooltips showing full journal entries on the graph
- Expandable history of all past entries
- Username and PIN authentication with persistent sessions across devices
- Each user's data is completely private and separate
- Fully responsive — works on mobile and desktop

---

## Tech stack

**Backend**

- Python / Flask — web framework and routing
- PostgreSQL — persistent database hosted on Railway
- psycopg2 — Python PostgreSQL adapter
- werkzeug — PIN hashing and security
- gunicorn — production web server

**Frontend**

- Jinja2 — HTML templating
- Vanilla JavaScript — form navigation, AJAX submissions, chart rendering
- Chart.js — line graph visualisation
- CSS custom properties — design system with golden hour colour palette
- Google Fonts — Cormorant Garamond and Jost

**Hosting**

- Railway — app and database hosting
- GitHub — version control and CI/CD (auto-deploys on push)

---

## Project structure

```
wellness-tracker/
├── app.py                  # Flask backend — routes, database, auth
├── Procfile                # Railway deployment config
├── requirements.txt        # Python dependencies
├── .env                    # Local environment variables (not committed)
├── .gitignore
├── templates/
│   ├── base.html           # Shared HTML foundation
│   ├── index.html          # Main app — form and graph
│   └── login.html          # Login and registration page
└── static/
    ├── style.css           # Golden hour aesthetic styling
    └── script.js           # Form navigation, chart, history
```

---

## How it works

### Authentication

Users register with a username and 4-digit PIN. The PIN is hashed using `werkzeug.security` before being stored — plain text PINs are never saved. Sessions persist for 365 days so users stay logged in across devices and browsers.

### Database

Two tables:

`users` — stores username and hashed PIN
`entries` — stores each daily journal entry linked to a user by `user_id`

All queries are parameterised to prevent SQL injection.

### Form flow

The multi-step form uses JavaScript to show and hide steps without page reloads. On submission, the form data is sent via `fetch()` (AJAX) to the `/add` route, avoiding a full page reload. A 2.5 second animation plays before the graph is revealed.

### Graph

Chart.js renders a line graph of the user's life scores over time. A custom external tooltip shows the full journal entry for each data point on hover. Users can toggle between the last 30 days and all-time views.

---

## Running locally

**1. Clone the repo**

```bash
git clone https://github.com/manbows/wellness-tracker.git
cd wellness-tracker
```

**2. Create a virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Set up environment variables**

Create a `.env` file in the project root:

```
DATABASE_URL=your-postgresql-connection-string
```

**5. Run the app**

```bash
python app.py
```

Visit `http://127.0.0.1:5000`

---

## Deployment

The app is deployed on Railway with a PostgreSQL plugin. Every push to the `main` branch on GitHub triggers an automatic redeploy.

Environment variables are set in the Railway dashboard under the service's Variables tab.

---

## What I learned

This project was built as part of a Python and Web Development Skills Bootcamp. Key concepts covered:

- Building a full-stack web app from scratch with Flask
- Designing and querying a relational database with SQL
- Implementing user authentication with hashed credentials
- Using AJAX and the Fetch API to avoid page reloads
- Deploying a production app with a persistent cloud database
- Managing environment variables and keeping secrets out of version control
- Git version control and GitHub workflow

---

## Future features

- Streak counter showing consecutive days of entries
- Ability to backdate missed days
- Weekly summary view
- Email reminders
