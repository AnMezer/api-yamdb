from django.conf import settings
from django.core.mail import send_mail


def sender_mail(confirmation_code, recipient):
    send_mail(
        subject='Код подтверждения',
        message=f'confirmation_code: {confirmation_code}',
        from_email=settings.SENDERS_EMAIL,
        recipient_list=[f'{recipient}'],
        fail_silently=True,
    )
