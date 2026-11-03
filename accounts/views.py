from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .forms import CorporateRegistrationForm, ProfileUpdateForm, VerificationSubmissionForm
from .models import UserProfile, EmployeeVerification
from cart.models import Order


def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')

    if request.method == 'POST':
        form = CorporateRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['corporate_email']
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Configure profile
            profile = user.profile
            profile.company_name = form.cleaned_data['company_name']
            profile.employee_id = form.cleaned_data['employee_id']
            profile.corporate_email = form.cleaned_data['corporate_email']
            profile.verification_status = 'PENDING'
            profile.is_corporate_verified = False
            profile.save()

            # Record verification request
            EmployeeVerification.objects.create(
                user=user,
                company_name=profile.company_name,
                corporate_email=profile.corporate_email,
                employee_id=profile.employee_id,
                status='PENDING',
                admin_notes='Initial registration verification submitted automatically.'
            )

            # Log user in
            login(request, user)
            messages.success(
                request,
                f"Welcome to PerkCart, {user.first_name or user.username}! Your corporate employee account has been created. Status: PENDING verification (Simulated demonstration workflow)."
            )
            return redirect('accounts:profile')
    else:
        form = CorporateRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')

    next_url = request.GET.get('next', 'core:home')

    if request.method == 'POST':
        username_or_email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username_or_email, password=password)
        if not user:
            # Try authentication via email
            from django.contrib.auth.models import User
            try:
                user_obj = User.objects.get(email__iexact=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                user = None

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect(next_url if next_url.startswith('/') else 'core:home')
        else:
            messages.error(
                request,
                "Invalid corporate email/username or password. Refer to troubleshooting code AUTH-001 if issues persist."
            )

    return render(request, 'accounts/login.html', {'next': next_url})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out securely from PerkCart Corporate Portal.")
    return redirect('core:home')


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    recent_orders = Order.objects.filter(user=request.user)[:5]
    verification_requests = EmployeeVerification.objects.filter(user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            # Update user first and last name if provided
            user = request.user
            user.first_name = form.cleaned_data.get('first_name', user.first_name)
            user.last_name = form.cleaned_data.get('last_name', user.last_name)
            user.save()
            messages.success(request, "Your corporate profile has been updated successfully.")
            return redirect('accounts:profile')
    else:
        initial = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        }
        form = ProfileUpdateForm(instance=profile, initial=initial)

    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'form': form,
        'recent_orders': recent_orders,
        'verification_requests': verification_requests,
    })


@login_required
def submit_verification_view(request):
    profile = request.user.profile

    if request.method == 'POST':
        form = VerificationSubmissionForm(request.POST)
        if form.is_valid():
            req_obj = form.save(commit=False)
            req_obj.user = request.user
            req_obj.status = 'PENDING'
            req_obj.save()

            profile.company_name = req_obj.company_name
            profile.corporate_email = req_obj.corporate_email
            profile.employee_id = req_obj.employee_id
            profile.verification_status = 'PENDING'
            profile.is_corporate_verified = False
            profile.save()

            messages.success(
                request,
                "Employee verification request submitted successfully! An administrator can approve it via the Admin panel."
            )
            return redirect('accounts:profile')
    else:
        initial = {
            'company_name': profile.company_name,
            'corporate_email': profile.corporate_email or request.user.email,
            'employee_id': profile.employee_id,
        }
        form = VerificationSubmissionForm(initial=initial)

    return render(request, 'accounts/submit_verification.html', {'form': form, 'profile': profile})


@login_required
def admin_verification_dashboard(request):
    """
    Demonstration management dashboard allowing evaluators and admins
    to review and approve or reject employee verification workflows easily.
    """
    if not request.user.is_staff:
        messages.error(request, "Access restricted. Staff privileges required (Code: SEC-001).")
        return redirect('accounts:profile')

    verifications = EmployeeVerification.objects.all().select_related('user')
    return render(request, 'accounts/admin_verifications.html', {
        'verifications': verifications,
    })


@login_required
def admin_update_verification(request, pk, action):
    """
    Action endpoint for admin to Approve or Reject a verification request.
    """
    if not request.user.is_staff:
        messages.error(request, "Access denied. Admin credentials required.")
        return redirect('core:home')

    verification = get_object_or_404(EmployeeVerification, pk=pk)
    profile = verification.user.profile

    if action == 'approve':
        verification.status = 'APPROVED'
        verification.reviewed_at = timezone.now()
        verification.reviewed_by = request.user
        verification.admin_notes = "Approved by administrator in demonstration portal."
        verification.save()

        profile.verification_status = 'APPROVED'
        profile.is_corporate_verified = True
        profile.save()
        messages.success(request, f"Employee '{verification.user.username}' has been APPROVED for corporate privileges.")

    elif action == 'reject':
        verification.status = 'REJECTED'
        verification.reviewed_at = timezone.now()
        verification.reviewed_by = request.user
        verification.rejection_reason = "Demonstration rejection: Corporate email domain could not be verified."
        verification.save()

        profile.verification_status = 'REJECTED'
        profile.is_corporate_verified = False
        profile.save()
        messages.warning(request, f"Employee '{verification.user.username}' verification marked REJECTED.")

    return redirect('accounts:admin_verifications')
