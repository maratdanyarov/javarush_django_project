from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .models import Order


def send_order_confirmation_email(order: Order) -> bool:
    """Send order confirmation email to customer.

    Args:
        order: The Order instance to send confirmation for.

    Returns:
        True if email was sent successfully, False otherwise.
    """
    subject = f"Order Confirmation - #{order.id}"
    context = {'order': order}

    text_context = render_to_string("emails/order_confirmation.txt.", context)
    html_context = render_to_string("emails/order_confirmation.html", context)

    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_context,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.user.email]
        )
        email.attach_alternative(html_context, "text/html")
        email.send(fail_silently=False)
        return True
    except Exception:
        return False


def send_order_admin_notification(order: Order, request=None) -> bool:
    """Send new order notification to admin.

    Args:
        order: The Order instance to notify about.
        request: Optional HTTP request for building admin URL.

    Returns:
        True if email was sent successfully, False otherwise.
    """
    subject = f'New Order #{order.id} - Hop & Barley'

    # Build admin URL
    admin_url = ''
    if request:
        admin_url = request.build_absolute_uri(
            f'/admin/orders/order/{order.id}/change/'
        )

    context = {
        'order': order,
        'admin_url': admin_url,
    }

    text_content = render_to_string('emails/order_admin_notification.txt', context)

    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.ADMIN_EMAIL],
        )
        email.send(fail_silently=False)
        return True
    except Exception:
        return False