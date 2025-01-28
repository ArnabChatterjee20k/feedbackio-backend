import logging

def get_logger():
    """
    Configures a custom logger for the FastAPI application.
    Logs to both console and file.
    """
    # Create a custom logger
    logger = logging.getLogger("app_logger")
    
    # Only configure the logger if it hasn't been configured before
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # Create a formatter for log messages
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Create a console handler for logging to the console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Create a file handler for logging to a file
        file_handler = logging.FileHandler('app_logs.log')
        file_handler.setFormatter(formatter)

        # Set the log level for the file handler
        file_handler.setLevel(logging.DEBUG)

        # Add the handlers to the logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        # Prevent logging from being propagated to the root logger
        logger.propagate = False

    return logger