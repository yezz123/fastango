from email_validator import EmailNotValidError, EmailSyntaxError, validate_email


def check_email(email):
    """
    Check if email is valid.

    Args:
        email (str): email to check

    Returns:
        bool: True if email is valid, False otherwise
    """
    try:
        validate_email(email, check_deliverability=True)
        return True
    except EmailSyntaxError or EmailNotValidError:
        return False
