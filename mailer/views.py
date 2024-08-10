import uuid
import csv
import base64
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import EmailMessage
from django.utils.html import escape
from django.urls import reverse
from django.utils.timezone import now
from django.conf import settings
from .forms import EmailForm
from .models import Email, EmailTracking

def home(request):
    return render(request, 'mailer/home.html')

def inbox(request):
    emails = Email.objects.filter(category='inbox').order_by('-sent_at')
    return render(request, 'mailer/inbox.html', {'emails': emails})

def sent_emails(request):
    emails = Email.objects.filter(category='sent').order_by('-sent_at')
    return render(request, 'mailer/sent.html', {'emails': emails})

def draft_emails(request):
    emails = Email.objects.filter(category='draft').order_by('-sent_at')
    return render(request, 'mailer/drafts.html', {'emails': emails})

def trash_emails(request):
    emails = Email.objects.filter(category='trash').order_by('-sent_at')
    return render(request, 'mailer/trash.html', {'emails': emails})

def send_email(request):
    if request.method == 'POST':
        form = EmailForm(request.POST, request.FILES)
        if form.is_valid():
            recipient = form.cleaned_data['recipient']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            attachment = request.FILES.get('attachment')

            # Create email with tracking ID
            tracking_id = str(uuid.uuid4())
            email = Email(
                recipient=recipient,
                subject=subject,
                message=message,
                tracking_id=tracking_id,
                category='sent',
                sent_at=now()
            )
            email.save()

            # Add tracking pixel URL for email opens
            tracking_pixel_url = request.build_absolute_uri(
                reverse('track_email', args=[tracking_id])
            )
            # Add click tracking URL (you can use this URL wherever necessary)
            click_tracking_url = request.build_absolute_uri(
                reverse('track_click', args=[tracking_id, 'http://example.com'])
            )

            # Append tracking pixel to the message (invisible to the user)
            message_with_tracking = f"""
                {escape(message)}
                <div style="display:none;">
                    <img src='{tracking_pixel_url}' width='1' height='1' />
                    <a href='{click_tracking_url}'>Invisible Link</a>
                </div>
            """

            # Create email message
            email_message = EmailMessage(
                subject, message_with_tracking, settings.EMAIL_HOST_USER, [recipient]
            )

            # Add attachment if present
            if attachment:
                email_message.attach(attachment.name, attachment.read(), attachment.content_type)

            # Send the email
            email_message.send()

            return redirect('sent_emails')
    else:
        form = EmailForm()

    return render(request, 'mailer/send_email.html', {'form': form})

def save_draft(request):
    if request.method == 'POST':
        form = EmailForm(request.POST, request.FILES)
        if form.is_valid():
            recipient = form.cleaned_data['recipient']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            email = Email(
                recipient=recipient,
                subject=subject,
                message=message,
                tracking_id=str(uuid.uuid4()),
                category='draft'
            )
            email.save()

            return redirect('draft_emails')
    else:
        form = EmailForm()

    return render(request, 'mailer/send_email.html', {'form': form})

def starred_emails(request):
    emails = Email.objects.filter(starred=True).order_by('-sent_at')
    return render(request, 'mailer/starred.html', {'emails': emails})

def move_to_trash(request, email_id):
    email = get_object_or_404(Email, id=email_id)
    email.category = 'trash'
    email.save()
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def move_to_inbox(request, email_id):
    email = get_object_or_404(Email, id=email_id)
    email.category = 'inbox'
    email.save()
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def star_email(request, email_id):
    email = get_object_or_404(Email, id=email_id)
    email.starred = not email.starred
    email.save()
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def track_email(request, tracking_id):
    email = get_object_or_404(Email, tracking_id=tracking_id)
    tracking, created = EmailTracking.objects.get_or_create(email=email)
    if not tracking.opened:
        tracking.opened = True
        tracking.opened_at = now()
        tracking.save()
    # Return a 1x1 transparent pixel image
    response = HttpResponse(content_type="image/png")
    response.write(base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/wcAAwAB/IX+lwQAAAABJRU5ErkJggg=="
    ))
    return response

def track_click(request, tracking_id, url):
    email = get_object_or_404(Email, tracking_id=tracking_id)
    tracking, created = EmailTracking.objects.get_or_create(email=email)
    if not tracking.clicked:
        tracking.clicked = True
        tracking.clicked_at = now()
        tracking.save()
    return redirect(url)

def email_analytics(request):
    emails = Email.objects.all().select_related('emailtracking')
    return render(request, 'mailer/email_analytics.html', {'emails': emails})

def export_emails_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="email_analytics.csv"'

    writer = csv.writer(response)
    writer.writerow(['Recipient', 'Subject', 'Opened', 'Opened At', 'Clicked', 'Clicked At'])

    emails = Email.objects.all()
    for email in emails:
        for tracking in email.emailtracking_set.all():
            writer.writerow([
                email.recipient, email.subject, tracking.opened, tracking.opened_at,
                tracking.clicked, tracking.clicked_at
            ])

    return response

def delete_forever(request, email_id):
    email = get_object_or_404(Email, id=email_id, category='trash')
    email.delete()
    return redirect('trash_emails')
