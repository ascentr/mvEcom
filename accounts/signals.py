from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import User, UserProfile


    
@receiver(post_save, sender=User)
def post_Save_create_profile_receiver(sender, instance,  created, **kwargs):
    print(created)
    if created:
        UserProfile.objects.create(user=instance)
        print('User profile created')
    else:
        try:
            profile = UserProfile.objects.get(user=instance)
            profile.save()
            print('Profile is updated')
        except:
            #create user profile if not not existing
            UserProfile.objects.create(user=instance)
            print('User profile could not be found, User Profile Created')

@receiver(pre_save , sender=User)
def pre_save_profile_receiver(sender, instance,  **kwargs):
    print(instance.username, 'New created user is being saved')
