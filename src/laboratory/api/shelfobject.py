from django.conf import settings
from django.contrib.admin.models import CHANGE
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from auth_and_perms.organization_utils import user_is_allowed_on_organization, organization_can_change_laboratory
from laboratory.api import serializers
from laboratory.api.serializers import ShelfLabViewSerializer, ReservedProductsSerializer
from laboratory.logsustances import log_object_change
from laboratory.models import OrganizationStructure, \
    ShelfObject, Laboratory
from rest_framework import status

from laboratory.shelfobject.serializers import AddShelfObjectSerializer, SubstractShelfObjectSerializer
from laboratory.shelfobject.utils import save_shelf_object, get_clean_shelfobject_data, status_shelfobject
from django.utils.translation import gettext_lazy as _

from laboratory.utils import organilab_logentry


class ShelfObjectTableViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ShelfObjectTableSerializer
    queryset = ShelfObject.objects.all()
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ['name', 'last_update', ]  # for the global search
    filterset_class = serializers.ShelfObjectFilterSet
    ordering_fields = ['last_update']
    ordering = ('-last_update',)  # default order

    def get_queryset(self):
        if not self.data['shelf'] :
            return self.queryset.none()
        return self.queryset.filter(
            in_where_laboratory=self.laboratory,
            shelf=self.data['shelf']

        )

    def list(self, request, org_pk, lab_pk, **kwargs):
        self.organization = get_object_or_404(OrganizationStructure.objects.using(settings.READONLY_DATABASE), pk=org_pk)
        self.laboratory = get_object_or_404(Laboratory.objects.using(settings.READONLY_DATABASE), pk=lab_pk)
        user_is_allowed_on_organization(request.user, self.organization)
        organization_can_change_laboratory(self.laboratory, self.organization, raise_exec= True)
        validate_serializer = ShelfLabViewSerializer(data=request.GET, laboratory=self.laboratory)
        validate_serializer.is_valid(raise_exception=True)
        self.data = validate_serializer.data

        queryset = self.filter_queryset(self.get_queryset())
        data = self.paginate_queryset(queryset)
        response = {'data': data, 'recordsTotal': ShelfObject.objects.count(),
                    'recordsFiltered': queryset.count(),
                    'draw': self.request.GET.get('draw', 1)}
        return Response(self.get_serializer(response).data)


class ShelfObjectViewSet(viewsets.GenericViewSet):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    # This is not an API.
    def _check_permission_on_laboratory(self,request, org_pk, lab_pk):
        self.organization = get_object_or_404(OrganizationStructure.objects.using(settings.READONLY_DATABASE), pk=org_pk)
        self.laboratory = get_object_or_404(Laboratory.objects.using(settings.READONLY_DATABASE), pk=lab_pk)
        user_is_allowed_on_organization(request.user, self.organization)
        organization_can_change_laboratory(self.laboratory, self.organization, raise_exec= True)

    @action(detail=False, methods=['post'])
    def create_shelfobject(self, request, org_pk, lab_pk, **kwargs):
        self._check_permission_on_laboratory(request, org_pk, lab_pk)

    @action(detail=False, methods=['post'])
    def fill_increase_shelobject(self, request, org_pk, lab_pk, **kwargs):
        self._check_permission_on_laboratory(request, org_pk, lab_pk)

    @action(detail=False, methods=['post'])
    def fill_decrease_shelobject(self, request, org_pk, lab_pk, **kwargs):
        self._check_permission_on_laboratory(request, org_pk, lab_pk)

    @action(detail=False, methods=['post'])
    def reserve(self, request, org_pk, lab_pk, **kwargs):
        self._check_permission_on_laboratory(request, org_pk, lab_pk)
        self.serializer_class = ReservedProductsSerializer
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            laboratory = get_object_or_404(Laboratory, pk=lab_pk)
            instance = serializer.save()
            instance.laboratory = laboratory
            instance.save()

            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def add(self, request, org_pk, lab_pk, **kwargs):
        self._check_permission_on_laboratory(request, org_pk, lab_pk)
        self.serializer_class = AddShelfObjectSerializer
        serializer = self.serializer_class(data=request.data)
        errors = {'amount': [_('The quantity is more than the shelf has')]}
        status_code = status.HTTP_200_OK
        changed_data = ["amount"]

        if serializer.is_valid():
            bill, amount, shelfobject, provider = get_clean_shelfobject_data(serializer, changed_data, lab_pk)
            shelf = shelfobject.shelf

            if shelf.discard:
                total = shelf.get_total_refuse()
                new_total = total + amount
                if shelf.quantity >= new_total or not shelf.quantity:
                    status_code = save_shelf_object(shelfobject, request.user, shelfobject.pk, amount, provider, bill, changed_data)
                else:
                    errors.update({'amount': [_('The quantity is much larger than the shelf limit %(limit)s')]})
            else:
                status_shelf_obj = status_shelfobject(shelfobject, shelf, amount)

                if status_shelf_obj:
                    status_code = save_shelf_object(shelfobject, request.user, shelfobject.pk, amount, provider, bill, changed_data)
        else:
            errors = serializer.errors

        if status_code == 201:
            return Response(status=status_code)
        return Response(errors, status=status_code)

    @action(detail=False, methods=['post'])
    def substract(self, request, org_pk, lab_pk, **kwargs):
        self._check_permission_on_laboratory(request, org_pk, lab_pk)
        self.serializer_class = SubstractShelfObjectSerializer
        serializer = self.serializer_class(data=request.data)
        errors = {'discount': [_('The amount to be subtracted is more than the shelf has')]}
        status_code = status.HTTP_200_OK
        changed_data = ["discount"]

        if serializer.is_valid():
            shelfobject = get_object_or_404(ShelfObject, pk=serializer.data['shelf_object'])
            old = shelfobject.quantity
            discount = serializer.data['discount']
            description = serializer.data.get('description', '')

            if description:
                changed_data.append("description")

            if old >= discount:
                new = old - discount
                shelfobject.quantity = new
                shelfobject.save()
                log_object_change(request.user, shelfobject.pk, shelfobject, old, new, description, 2, "Substract", create=False)
                organilab_logentry(request.user, shelfobject, CHANGE, 'shelfobject', changed_data=changed_data)
                status_code = status.HTTP_201_CREATED
        else:
            errors = serializer.errors

        if status_code == 201:
            return Response(status=status_code)
        return Response(errors, status=status_code)

    @action(detail=True, methods=['get'])
    def detail(self, request, org_pk, lab_pk, **kwargs):
        self._check_permission_on_laboratory(request, org_pk, lab_pk)

    @action(detail=False, methods=['post'])
    def tag(self, request, org_pk, lab_pk, **kwargs):
        """
        Devuelve la etiqueta en formato svg
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        self._check_permission_on_laboratory(request, org_pk, lab_pk)

    @action(detail=False, methods=['post'])
    def transfer_out(self, request, org_pk, lab_pk, **kwargs):
        self._check_permission_on_laboratory(request, org_pk, lab_pk)

    @action(detail=False, methods=['post'])
    def transfer_in(self, request, org_pk, lab_pk, **kwargs):
        self._check_permission_on_laboratory(request, org_pk, lab_pk)

    @action(detail=False, methods=['post'])
    def transfer_available_list(self, request, org_pk, lab_pk, **kwargs):
        self._check_permission_on_laboratory(request, org_pk, lab_pk)

    @action(detail=False, methods=['get'])
    def detail_pdf(self, request, org_pk, lab_pk, **kwargs):
        self._check_permission_on_laboratory(request, org_pk, lab_pk)

    @action(detail=False, methods=['delete'])
    def delete(self, request, org_pk, lab_pk, **kwargs):
        self._check_permission_on_laboratory(request, org_pk, lab_pk)

    @action(detail=False, methods=['get'])
    def chart_graphic(self, request, org_pk, lab_pk, **kwargs):
        """
            def get(self, request):
        queryset = ShelfObject.objects.filter(shelf__pk=request.GET['shelf'])
        labels = []
        data = []
        if queryset:
            self.show_chart = True
            for obj in queryset:
               data.append(obj.quantity)
               labels.append(obj.object.name)

        return Response({'labels':labels,'data':data})
        :return:
        """
        self._check_permission_on_laboratory(request, org_pk, lab_pk)


    @action(detail=False, methods=['post'])
    def create_observation(self, request, org_pk, lab_pk, **kwargs):
        self._check_permission_on_laboratory(request, org_pk, lab_pk)
        pass

    @action(detail=False, methods=['post'])
    def list_observations(self, request, org_pk, lab_pk, **kwargs):
        self._check_permission_on_laboratory(request, org_pk, lab_pk)
        pass

    @action(detail=False, methods=['put'])
    def update_status(self, request, org_pk, lab_pk, **kwargs):
        self._check_permission_on_laboratory(request, org_pk, lab_pk)
        pass


    # maybe we move observations to other class