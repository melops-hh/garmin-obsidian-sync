# Garmin to Obsidian Sync  

This Python script fetches sleep and workout data from Garmin and logs it into your Obsidian daily notes automatically.  

## Features  
- Retrieves **sleep data** (score, duration, deep/light/REM sleep, bed/wake time)  
- Fetches **workout activities** (running, lacrosse, yoga, strength training)  
- Formats data into structured Obsidian-friendly markdown  
- Uses environment variables for secure authentication  
- Supports automatic daily logging  

## Installation  

### 1. Clone the Repository  
```sh
git clone https://github.com/your-username/garmin-to-obsidian.git
cd garmin-to-obsidian
```

### 2. Set Up a Virtual Environment
```sh
python3 -m venv venv  
source venv/bin/activate 
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a .env file in the project root and add:
```ini
OBSIDIAN_PATH=~/obsidian/Journal/01\ Daily
GARMIN_EMAIL=your-email@example.com  
GARMIN_PASSWORD=your-secure-password  
```

### 5. Run the Script
```sh
python garmin_to_obsidian.py
```

## Notes
* Ensure your Garmin account credentials are correct in .env
* The script appends data to the correct year/month/day.md file in Obsidian
* Adjust the OBS_PATH based on your Obsidian vault structure
