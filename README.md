# Gratitude — Daily Reflection Tracker

A full-stack wellness app for daily gratitude journaling and mood tracking. Built with Flask, PostgreSQL, and vanilla JavaScript.

**Live app:** [https://wellness-tracker-25qrzhro8-emma-bowmans-projects.vercel.app/](https://wellness-tracker-25qrzhro8-emma-bowmans-projects.vercel.app/)

---

## Preview

![Login](static/images/login.png)
![Add Gratitude Points](static/images/gratitude.png)
![Add Prayer Points](static/images/prayers.png)
![Rating](static/images/rating.png)
![Results/Journey](static/images/results.png)
![Missed Day](static/images/missedday.png)

---

## What it does

Gratitude is a personal daily reflection tool. Each day, users record three things they're grateful for, three things they're praying or hoping for, and a life score out of 10. The app tracks this over time and visualises progress as a line graph.

Key features:

- Multi-step guided form with smooth transitions
- Line graph showing mood score over time (last 30 days or all time view)
- Hover tooltips showing full journal entries on the graph
- Expandable history of all past entries
- Ability to backdate and add missing entries from previous days
- Username and PIN authentication with persistent sessions across devices
- Each user's data is completely private and separate
- Fully responsive — works on mobile and desktop

---

## Tech stack

**Backend**

- Python / Flask — web framework and routing
- PostgreSQL — persistent database hosted on Supabase
- psycopg2 — Python PostgreSQL adapter
- werkzeug — PIN hashing and security
- gunicorn — production web server

**Frontend**

- Jinja2 — HTML templating
- Vanilla JavaScript — form navigation, AJAX submissions, chart rendering
- Chart.js — line graph visualisation
- CSS custom properties — design system with warm cream colour palette
- Google Fonts — Cormorant Garamond and Jost

**Hosting**

- Vercel — app hosting with automatic deploys on push
- Supabase — managed PostgreSQL database
- GitHub — version control and CI/CD

---

## Project structure

```
wellness-tracker/
├── app.py                  # Flask backend — routes, database, auth
├── vercel.json             # Vercel deployment config
├── requirements.txt        # Python dependencies
├── .env                    # Local environment variables (not committed)
├── .gitignore
├── templates/
│   ├── base.html           # Shared HTML foundation
│   ├── index.html          # Main app — form and graph
│   ├── login.html          # Login and registration page
│   └── backdate.html       # Add a missing past entry
└── static/
    ├── style.css           # Warm cream aesthetic styling
    └── script.js           # Form navigation, chart, history
```

---

## How it works

### Authentication

Users register with a username and 4-digit PIN. The PIN is hashed using `werkzeug.security` before being stored — plain text PINs are never saved. Sessions persist for 365 days so users stay logged in across devices and browsers. The app secret key is loaded from an environment variable and never hardcoded.

### Database

Two tables:

`users` — stores username and hashed PIN  
`entries` — stores each daily journal entry linked to a user by `user_id`

All queries are parameterised to prevent SQL injection. Delete operations verify `user_id` ownership before removing any record.

### Form flow

The multi-step form uses JavaScript to show and hide steps without page reloads. On submission, the form data is sent via `fetch()` (AJAX) to the `/add` route, avoiding a full page reload. A 2.5 second animation plays before the graph is revealed.

### Graph

Chart.js renders a line graph of the user's life scores over time. A custom external tooltip shows the full journal entry for each data point on hover. Users can toggle between the last 30 days and all-time views.

### Backdating

Users can add entries for days they missed via the `/backdate` route. The form prevents duplicate entries for the same date and blocks future dates. Accessible via the "+ Add a missing entry" link on the journey view.

---

## Running locally

**1. Clone the repo**

```bash
git clone https://github.com/emma-bowman/wellness-tracker.git
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
DATABASE_URL=your-supabase-postgresql-connection-string
SECRET_KEY=your-secret-key
```

**5. Run the app**

```bash
python app.py
```

Visit `http://127.0.0.1:5000`

---

## Deployment

The app is deployed on Vercel with a Supabase PostgreSQL database. Every push to the `main` branch on GitHub triggers an automatic redeploy via Vercel's GitHub integration.

Environment variables (`DATABASE_URL` and `SECRET_KEY`) are set in the Vercel dashboard under the project's Settings → Environment Variables tab.

The database uses Supabase's transaction pooler connection (port 6543) for compatibility with Vercel's serverless functions.

---

## What I learned

This project was built as part of a Python and Web Development Skills Bootcamp. Key concepts covered:

- Building a full-stack web app from scratch with Flask
- Designing and querying a relational database with SQL
- Implementing user authentication with hashed credentials and secure session management
- Using AJAX and the Fetch API to avoid page reloads
- Deploying a production app with Vercel and a managed cloud database (Supabase)
- Migrating a live database from Railway to Supabase using pg_dump and pg_restore
- Managing environment variables and keeping secrets out of version control
- Git version control and GitHub workflow
- Securing routes against unauthorised data access (ownership checks on delete)

---

## Future features

- Streak counter showing consecutive days of entries
- Weekly summary view
- Email reminders