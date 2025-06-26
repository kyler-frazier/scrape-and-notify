import logging


class LoggingFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    green = "\x1b[32;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    FORMATS = {
        logging.DEBUG: grey,
        logging.INFO: green,
        logging.WARNING: yellow,
        logging.ERROR: red,
        logging.CRITICAL: bold_red,
    }

    def format(self, record):
        log_color = self.FORMATS.get(record.levelno, self.grey)
        log_fmt = f"{log_color}%(levelname)s:{' ' * max(1, 9 - len(record.levelname))}%(message)s{self.reset}"

        # Set the formatter dynamically
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
