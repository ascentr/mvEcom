from django.db import models
from accounts.models import User, UserProfile
from accounts.utils import send_notification
from datetime import date , time , datetime


class Vendor(models.Model):
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name='userprofile' , on_delete=models.CASCADE )
    vendor_name = models.CharField(max_length=50)
    vendor_slug = models.SlugField(max_length=100, unique=True)
    vendor_logo = models.ImageField(upload_to='vendor/logo')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_At = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.vendor_name
    '''
    Check if is_open for open/close badges on homepage
    '''
    def is_open(self):
        today_date = date.today()
        today = today_date.isoweekday()
        hours_today = OpeningHour.objects.filter(vendor=self, day=today ).order_by('from_hour')
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        
        is_open = None
        
        for i in hours_today:
            if i.is_closed:
                is_open = False
            else:
                start = str(datetime.strptime(i.from_hour, "%I:%M %p").time())
                end = str(datetime.strptime(i.to_hour, "%I:%M %p").time())

                if current_time > start and current_time < end:
                    is_open = True
                    break
                else:
                    is_open = False
        return is_open


    '''
    over ride the default save() method, thus when the vendor is approved or
    disapproved by admin the user can be notified.
    if the is_approved field changes then corresponding email template is used to
    notify the user.
    '''
    def save(self, *args, **kwargs):
        if self.pk is not None:
            #update
            original = Vendor.objects.get(pk=self.pk)
            if original.is_approved != self.is_approved:
                mail_template = 'accounts/emails/admin_approval_email.html'
                context = {
                    'user': self.user,
                    'is_approved':self.is_approved,
                    'to_email' : self.user.email
                }

                if self.is_approved == True:
                    mail_subject = "Congratulation ! Your account has been approved."
                else:
                    mail_subject = "We are Sorry, you are not eligible to create a shop on our platform"

                send_notification(mail_subject, mail_template, context)

        return super(Vendor, self).save(*args, **kwargs)

DAYS = [
    (1, ("Monday")) ,
    (2, ("Tueday")) ,
    (3, ("Wednesday")) ,
    (4, ("Thursday")) ,
    (5, ("Friday")) ,
    (6, ("Saturday")) ,
    (7, ("Sunday")) ,
]

HOURS_OF_DAY24 = [ ( time(h , m).strftime('%I:%M %p'),  time(h , m).strftime('%I:%M %p')) for h in range(0,24) for m in (0,30) ]

class OpeningHour(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField(choices= HOURS_OF_DAY24 , max_length=10 , blank=True)
    to_hour = models.CharField(choices= HOURS_OF_DAY24 , max_length=10 , blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering= ('day' , 'from_hour')
        unique_together = ('vendor', 'day' , 'from_hour' , 'to_hour')
    
    def __str__(self):
        return self.get_day_display()   # built in function to display choice field
