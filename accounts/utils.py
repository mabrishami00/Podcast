from django.conf import settings
from django.core.mail import send_mail

import random
import string





def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    random_password = "".join(random.choice(characters) for _ in range(length))
    return random_password
