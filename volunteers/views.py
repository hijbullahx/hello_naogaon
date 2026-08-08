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
            messages.success(request, 'আপনার স্বেচ্ছাসেবক আবেদনটি জমা নেওয়া হয়েছে। আমরা শীঘ্রই যোগাযোগ করব।')
            return redirect('volunteers:apply')
        else:
            messages.error(request, 'দয়া করে নাম ও ফোন নম্বর প্রদান করুন।')
    return render(request, 'volunteers/volunteer_form.html')

