from datetime import datetime
# --- imports go above here ---

# --- functions go below here ---
def play_music():
    return 'Playing music...'

def tell_joke():
    return 'Why don\'t scientists trust atoms? Because they make up everything!'

def get_time():
    return f'Currently, it\'s {datetime.now().strftime('%H:%M:%S')}'

def get_date():
    return f'Today is {datetime.now().strftime('%Y-%m-%d')} (YYYY-MM-DD)'

