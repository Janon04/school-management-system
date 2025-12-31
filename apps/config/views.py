from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import SchoolInfo
from .forms import SchoolInfoForm

def is_admin_or_staff(user):
    return user.is_superuser or user.is_staff

@login_required
@user_passes_test(is_admin_or_staff)
def school_info_update_view(request):
    school_info, created = SchoolInfo.objects.get_or_create(pk=1)
    if request.method == 'POST':
        form = SchoolInfoForm(request.POST, request.FILES, instance=school_info)
        if form.is_valid():
            form.save()
            messages.success(request, 'School information updated successfully!')
            return redirect('school_info_update')
    else:
        form = SchoolInfoForm(instance=school_info)
    return render(request, 'config/school_info_form.html', {'form': form, 'school_info': school_info})
