from django.conf import settings
from django.core.mail import send_mail

import random
import string





def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    random_password = "".join(random.choice(characters) for _ in range(length))
    return random_password


def sending_email(
    recipient_list,
    subject,
    message,
    from_email=settings.EMAIL_HOST_USER,
    fail_silently=False,
    **kwargs
):
    recipient_list = recipient_list
    subject = subject
    message = message
    from_email = from_email

    if kwargs:
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=fail_silently,
            **kwargs
        )
    else:
        send_mail(
            subject, message, from_email, recipient_list, fail_silently=fail_silently
        )



