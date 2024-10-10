from django.contrib import admin
from .models import UserProfile, FileUpload
# admin.site.register(FileUpload)
# admin.site.register(UserProfile)


@admin.register(FileUpload)
class FileUploadadmin(admin.ModelAdmin):
    list_display=['user','file','copies','uploaded_at']

@admin.register(UserProfile)
class UserProfileadmin(admin.ModelAdmin):
    list_display=['name','phone_number']
