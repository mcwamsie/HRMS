import os
from datetime import date
from shutil import copyfile
from uuid import UUID

from dateutil.relativedelta import relativedelta
from django.utils import timezone

from HRMS import settings


def uuid_convert(o):
    if isinstance(o, UUID):
        return o.hex


def stripAndUpperCase(value):
    value = value.strip()
    value = value.title()
    return value


def cleanNumber(idNumber):
    idNumber = idNumber.upper()
    idNumber = idNumber.replace(' ', '')
    idNumber = idNumber.replace('-', '')
    idNumber = idNumber.replace('/', '')
    return idNumber


def movefile(new_file_name):
    base_dir = settings.BASE_DIR
    media_dir = os.path.join(base_dir, 'media')
    old_file_path = os.path.join(media_dir, "upload_temp/" + new_file_name)
    new_file_path = os.path.join(media_dir, "profiles/" + new_file_name)
    copyfile(old_file_path, new_file_path)
    # os.rename(old_file_path, new_file_path)


def calculateAge(dateOfBirth, date=None) -> int:
    if not date:
        return (timezone.now().date() - dateOfBirth).days // 365
    return (date - dateOfBirth).days // 365


def mask_email(email):
    """
    Mask an email address, showing the first character and domain.
    Example: john.doe@example.com -> j****e@example.com
    """
    try:
        local_part, domain = email.split('@')
        if len(local_part) <= 2:
            return email  # If local part is too short, return the original email
        masked_email = f"{local_part[0]}{'*' * (len(local_part) - 2)}{local_part[-1]}@{domain}"
        return masked_email
    except Exception as e:
        print(f"Error masking email: {e}")
        return None


def mask_phone(phone):
    """
    Mask a phone number, showing only the last 3 digits.
    Example: 1234567890 -> ******7890
    """
    try:
        if len(phone) < 4:
            return phone  # If phone number is too short, return the original number
        masked_phone = f"{phone[:7]}{'*' * (len(phone) - 7)}{phone[-2:]}"
        return masked_phone
    except Exception as e:
        print(f"Error masking phone number: {e}")
        return None


def append_contact(contact_list, contact_type: str, value: str):
    print(contact_type, "--", value)
    maskedValue = mask_phone(value) if contact_type.startswith("Mobile") else mask_email(value)
    contact_list.append({
        "type": contact_type,
        # "contact_value": value,
        "contact_display": maskedValue
    })
    return contact_list

def calculate_age(birthdate):
    """
    Calculate the age from the given birthdate to today in years, months, and days.
    """
    today = date.today()
    age_difference = relativedelta(today, birthdate)

    age_str=""
    years = age_difference.years
    months = age_difference.months
    days = age_difference.days

    if years >= 1:
        age_str += f"{years} yrs"

    if months >= 1:
        if years >= 1:
            age_str += f", {months} months"
        else:
            age_str += f"{months} months"

    if days >= 1:
        if years >= 1 or (months >= 1):
            age_str += f", {days} days"
        else:
            age_str += f"{days} days"
    return age_str
def calculate_age_in_year(birthdate):
    today = date.today()
    age_difference = relativedelta(today, birthdate)
    return age_difference.years
