# encoding: utf-8
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.shortcuts import render
from laboratory.forms import OrganizationUserManagementForm, SearchUserForm
from laboratory.models import Laboratory, OrganizationStructure, OrganizationUserManagement, Profile
from laboratory.decorators import has_lab_assigned


#FIXME to manage add separately bootstrap, we need a workaround to to this.
@permission_required(['laboratory.view_organizationusermanagement', 'laboratory.add_organizationusermanagement'])
def access_management(request):
    context = {}
    context['labs'] = request.user.profile.laboratories.all()
    context['orgs'] = OrganizationUserManagement.objects.filter(users=request.user)
    return render(request, 'laboratory/access_management.html', context=context)


@has_lab_assigned(lab_pk='pk')
@permission_required('laboratory.view_organizationusermanagement')
def users_management(request, pk):
    if request.method == 'POST':
        users_list = Profile.objects.filter(laboratories__pk=pk).all()
        form = SearchUserForm(request.POST, users_list=users_list)
        if form.is_valid():
            user = User.objects.get(username=form.cleaned_data['user'])
            lab = Laboratory.objects.get(pk=pk)
            if not hasattr(user, 'profile'):
                profile = Profile(user=user)
                profile.save()
            user.profile.laboratories.add(lab)
        return redirect('laboratory:users_management', pk=pk)

    users_pk = User.objects.filter(profile__laboratories__pk=pk).values_list('pk', flat=True)
    context = {
        'users_list': Profile.objects.filter(laboratories__pk=pk).all(),
        'organization': Laboratory.objects.get(pk=pk),
        'form': SearchUserForm(users_list=users_pk)
    }
    return render(request, 'laboratory/users_management.html', context=context)


@has_lab_assigned(lab_pk='pk')
@permission_required('laboratory.delete_organizationusermanagement')
def delete_user(request, pk, user_pk):
    user_orga_management = OrganizationUserManagement.objects.filter(organization__pk=pk).first()
    if user_orga_management:
        user_orga_management.users.remove(user_pk)
    return redirect('laboratory:users_management', pk=pk)
