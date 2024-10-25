# This script was used during development to verify the CRON scheduler is running correctly.
# While it's not used, I've kept it here in case debugging is needed in the future.

from datetime import datetime
from helpers import log

log(f"Running at {datetime.now()}", "print_time") 
