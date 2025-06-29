# roommate match example

This repository is used as a practice example and may be converted to a private repository in the future.

## Project Structure
  
```
/project-root
│
├── backend/
│   ├── app.py                 # Flask app entry point
│   ├── requirements.txt       # Python dependencies
│   ├── models/
│   │   ├── user.py           # User model
│   │   └── match.py          # Match engine
│   ├── routes/
│   │   ├── auth.py           # Authentication endpoints
│   │   ├── profiles.py       # Profile management
│   │   ├── preferences.py    # User preferences
│   │   ├── matches.py        # Matching logic
│   │   └── chats.py          # Chat function
│   └── services/
│       ├── estimator.py      # Feasibility calculator
│       ├── regression.py     # (future) ML model
│       └── chat_labeler.py   # (future) Chat analysis
│
└── frontend/
    ├── index.html            # application
    ├── css/
    │   └── style.css         # Custom styles
    ├── js/
    │   ├── api.js            # API communication
    │   ├── ui.js             # UI management
    │   └── realtime.js       # Real-time updates
    └── assets/
```


### Environment Variables
Create a `.env` file in the backend directory:
