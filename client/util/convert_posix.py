from datetime import datetime
import pytz

# %Y-%m-%d %H:%M:%S

def convert_posix_to_hours(posix):
    timezone = pytz.timezone('America/Sao_Paulo')
    
    # Convert POSIX timestamp to a UTC datetime object
    utc_time = datetime.fromtimestamp(posix)

    # Convert the datetime object to the São Paulo time zone
    return utc_time.replace(tzinfo=pytz.utc).astimezone(timezone).strftime('%H:%M')