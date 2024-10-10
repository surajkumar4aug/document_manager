from django.shortcuts import render, redirect
from .models import UserProfile, FileUpload
from django.contrib import messages
from django.core.paginator import Paginator
import os
from django.conf import settings
# def manage_profile_and_files_view(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         phone_number = request.POST.get('phone_number')

#         if name and phone_number:
#             # Check if a user profile with the given phone number already exists
#             profile, created = UserProfile.objects.get_or_create(
#                 phone_number=phone_number,
#                 defaults={'name': name}
#             )

#             # If the profile was not created (i.e., it already existed), update the name
#             if not created:
#                 profile.name = name
#                 profile.save()

#             try:
#                 # Handle file uploads with their respective number of copies
#                 file_inputs = request.FILES.getlist('files')
#                 copies = [int(request.POST.get(f'copies{i+1}', 1)) for i in range(len(file_inputs))]

#                 for file, copy, i in zip(file_inputs, copies, range(len(file_inputs))):
#                     if not request.POST.get(f'delete{i+1}'):  # Check if delete checkbox is not checked
#                         FileUpload.objects.create(user=profile, file=file, copies=copy)

#                 messages.success(request, "Profile and files successfully uploaded!")
#                 return redirect('/')
#             except Exception as e:
#                 # In case of any error during file upload, show an error message
#                 messages.error(request, f"File upload failed. Error: {str(e)}")
#                 return redirect('/')

#         else:
#             # Handle missing name or phone number
#             messages.error(request, "Please provide both name and phone number.")

#     return render(request, 'uploads.html')

from django.core.files.storage import default_storage
from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserProfile, FileUpload 

def manage_profile_and_files_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone_number = request.POST.get('phone_number')

        if not name or not phone_number:
            messages.error(request, "Please provide both name and phone number.")
            return redirect('/')  # or render the form again with error message

        try:
            with transaction.atomic():
                # Get or create the user profile
                profile, created = UserProfile.objects.get_or_create(
                    phone_number=phone_number,
                    defaults={'name': name}
                )

                if not created and profile.name != name:
                    profile.name = name
                    profile.save()

                # Handle file uploads
                file_inputs = request.FILES.getlist('files')
                if not file_inputs:
                    messages.error(request, "Please upload at least one file.")
                    return redirect('/')

                # Process each file upload and save it
                for i, file in enumerate(file_inputs):
                    if not request.POST.get(f'delete{i+1}'):  # Check if the delete checkbox is unchecked
                        copies = int(request.POST.get(f'copies{i+1}', 1))
                        import os
                        file_name = os.path.basename(file.name)  # Get the file name without the path
                        # Use default_storage to upload the file to Dropbox
                        file_name = default_storage.save(file_name, file)
                        print(f"File uploaded to Dropbox with path: {file_name}")  # Upload the file to Dropbox
                        FileUpload.objects.create(user=profile, file=file_name, copies=copies)                
                messages.success(request, "Profile and files successfully uploaded!")
                return redirect('/')

        except Exception as e:
            messages.error(request, f"File upload failed. Error: {str(e)}")
            return redirect('/')

    return render(request, 'uploads.html')

# def dashboard_view(request):
#     if request.method == 'POST':
#         file_ids = request.POST.getlist('delete_files')
#         if file_ids:
#             # Retrieve files to delete
#             files_to_delete = FileUpload.objects.filter(id__in=file_ids)

#             # Delete each file from the filesystem
#             for file in files_to_delete:
#                 if file.file:
#                     file_path = os.path.join(settings.MEDIA_ROOT, file.file.name)
#                     if os.path.isfile(file_path):
#                         os.remove(file_path)

#             # Now delete the records from the database
#             files_to_delete.delete()

#             # Redirect with a message after deletion
#             messages.success(request, 'Selected files deleted successfully.')
#             return redirect('dashboard')

#     # Group files by user
#     user_files = {}
#     files = FileUpload.objects.select_related('user').all().order_by('-uploaded_at')
#     paginator = Paginator(files, 10)  # Show 10 files per page
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#     user_files = {}
#     for file in page_obj:
#         user = file.user
#         if user not in user_files:
#             user_files[user] = []
#         file.cleaned_file_name = file.file.name.replace('uploads/', '', 1)
#         user_files[user].append(file)

#     # Pagination
#     paginator = Paginator(files, 10)  # Show 10 files per page
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)

#     return render(request, 'dashboards.html', {'user_files': user_files, 'page_obj': page_obj})


from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
@login_required
def dashboard_view(request):
    if request.method == 'POST':
        file_ids = request.POST.getlist('delete_files')
        if file_ids:
            # Retrieve files to delete
            files_to_delete = FileUpload.objects.filter(id__in=file_ids)

            # Delete each file from Dropbox
            for file in files_to_delete:
                if file.file:
                    # Delete the file from Dropbox using the file field's delete method
                    file.file.delete()

            # Now delete the records from the database
            files_to_delete.delete()

            # Redirect with a message after deletion
            messages.success(request, 'Selected files deleted successfully.')
            return redirect('dashboard')

    # Group files by user
    files = FileUpload.objects.select_related('user').all().order_by('-id')
    paginator = Paginator(files, 10)  # Show 10 files per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    user_files = {}
    for file in page_obj:
        user = file.user
        if user not in user_files:
            user_files[user] = []
        file.cleaned_file_name = file.file.name.replace('uploads/', '', 1)
        user_files[user].append(file)

    return render(request, 'dashboards.html', {'user_files': user_files, 'page_obj': page_obj})


from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
class CustomLoginView(LoginView):
    template_name = 'login.html'
    success_url = reverse_lazy('dashboard')
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid email or password. Please try again.')
        return super().form_invalid(form)




@login_required
def custom_password_change(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
        elif new_password != confirm_password:
            messages.error(request, 'New password and confirm password do not match.')
        else:
            request.user.set_password(new_password)
            request.user.save()
            # Keep the user logged in after password change
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('dashboard')
    
    return render(request, 'password_change.html')

from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('login') 


