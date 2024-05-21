from django.conf import settings
from django.core.management import BaseCommand
from django.contrib.auth import get_user_model
from dateutil.relativedelta import relativedelta
from django.utils.timezone import now
from django.contrib.sites.models import Site
from django.test import RequestFactory

from auth_and_perms.models import DeleteUserList
from auth_and_perms.users import delete_user
from auth_and_perms.users import send_email_user_management


class Command(BaseCommand):

    def enqueue_users(self):
        User=get_user_model()
        User.objects.all()
        year_ago = now() - relativedelta(years=1)
        deletelist = []
        for user in User.objects.exclude(username="soporte@organilab.org").filter(
            deleteuserlist__isnull=True,
            last_login__lte=year_ago):
            deletelist.append(DeleteUserList(user=user))
        if deletelist:
            DeleteUserList.objects.bulk_create(deletelist)

        print("Actual: ", User.objects.all().count())
        print("Remove: ", len(deletelist))

    def delete_users(self):
        User = get_user_model()
        site = Site.objects.all().last()
        if site.domain not in settings.ALLOWED_HOSTS:
            settings.ALLOWED_HOSTS.append(site.domain)
        request = RequestFactory().get('/')

        request.META['HTTP_HOST'] = site.domain
        request.META['SERVER_PORT'] = "80" if settings.DEBUG else "443"
        user_base = User.objects.filter(username="soporte@organilab.org").first()
        del_count = 0
        for user_delete in DeleteUserList.objects.filter(expiration_date__lte=now()):
            send_email_user_management(request, user_base, user_delete, "delete")
            delete_user(user_delete.user, user_base)
            del_count += 1
        print("Delete users", del_count)
        print("Actual to users delete ", DeleteUserList.objects.all().count())
        print("Actual to users ", User.objects.all().count())

    def handle(self, *args, **options):
        self.enqueue_users()
        self.delete_users()


