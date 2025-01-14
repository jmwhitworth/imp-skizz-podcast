
def log(message:str, service:str, type:str='INFO') -> None:
    """Outputs the given message in a nicer format for the CRON logs"""
    print("[%s] [%s] %s" % (service.upper(), type.upper(), message))
