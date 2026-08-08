from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Volunteer, TeamMember, BloodDonor

def blood_donors_list(request):
    blood_group = request.GET.get('group', '')
    donors = BloodDonor.objects.filter(is_available=True)
    if blood_group:
        donors = donors.filter(blood_group=blood_group)
    context = {
        'donors': donors,
        'selected_group': blood_group,
        'groups': ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
    }
    return render(request, 'volunteers/blood_donors.html', context)

def apply_volunteer(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        if full_name and phone:
            Volunteer.objects.create(
                full_name=full_name,
                email=email,
                phone=phone,
                address=address
            )
            messages.success(request, 'আপনার স্বেচ্ছাসেবক আবেদনটি সফলভাবে জমা নেওয়া হয়েছে। আমাদের টিম আপনার সাথে শীঘ্রই যোগাযোগ করবে।')
            return redirect('volunteers:apply')
        else:
            messages.error(request, 'দয়া করে আপনার নাম ও ফোন নম্বর সঠিকভাবে প্রদান করুন।')

    team_members = TeamMember.objects.all()
    volunteers_list = Volunteer.objects.all().order_by('-id')

    context = {
        'team_members': team_members,
        'volunteers_list': volunteers_list,
    }
    return render(request, 'volunteers/volunteer_form.html', context)

