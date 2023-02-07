from django.contrib.admin.models import LogEntry
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BaseAuthentication
from rest_framework import status, viewsets, mixins
from django.db.models import Value, DateField

from laboratory.api import serializers
from laboratory.models import CommentInform, Inform, Protocol, OrganizationUserManagement, OrganizationStructure, \
    LabOrgLogEntry, Laboratory, InformsPeriod
from laboratory.utils import get_laboratories_from_organization
from reservations_management.models import ReservedProducts, Reservations
from laboratory.api.serializers import ReservedProductsSerializer, ReservationSerializer, \
    ReservedProductsSerializerUpdate, CommentsSerializer, ProtocolFilterSet, LogEntryFilterSet


class ApiReservedProductsCRUD(APIView):
    def get_object(self, pk):
        try:
            return ReservedProducts.objects.get(pk=pk)
        except ReservedProducts.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        serializer = ReservedProductsSerializer(data=request.data)

        if serializer.is_valid():
            laboratory = get_object_or_404(Laboratory, pk=int(request.data['lab']))
            instance = serializer.save()
            instance.laboratory = laboratory
            instance.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk):
        solicitud = self.get_object(pk)
        serializer = ReservedProductsSerializer(solicitud)
        return Response(serializer.data)

    def put(self, request, pk):
        solicitud = self.get_object(pk)
        serializer = ReservedProductsSerializerUpdate(solicitud, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        solicitud = self.get_object(pk)
        solicitud.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ApiReservationCRUD(APIView):
    def post(self, request):
        serializer = ReservationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentAPI(viewsets.ModelViewSet):

    authentication_classes =[SessionAuthentication,BaseAuthentication]
    permission_classes = [IsAuthenticated]
    queryset= CommentInform.objects.all()
    serializer_class = CommentsSerializer

    def get_comment(self, pk):
        try:
            return self.get_queryset().get(pk=pk)
        except CommentInform.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        serializer = CommentsSerializer(data=request.data)
        if serializer.is_valid():
            inform=Inform.objects.filter(pk=request.data['inform']).first()

            CommentInform.objects.create(
                creator=request.user,
                comment = serializer.data['comment'],
                inform = inform
            )
            comments=self.get_queryset().filter(inform=inform).order_by('pk')
            template = render_to_string('laboratory/comment.html', {'comments':comments, 'user':request.user},request)
            return Response({'data':template}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        pk = None
        if 'pk' in kwargs:
            comments= self.get_queryset().filter(pk=pk)
            return Response(self.get_serializer(comments).data)
        else:

            template = render_to_string('laboratory/comment.html', {'comments': self.get_queryset().filter(inform__pk=int(request.GET.get('inform'))).order_by('pk'), 'user':request.user},request)
            return Response({'data':template})
    def update(self, request, pk=None):
        comment=None
        if pk:
            serializer = CommentsSerializer(data=request.data)
            if serializer.is_valid():
                comment = CommentInform.objects.filter(pk=pk).first()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            if comment:
                comment.comment=request.data['comment']
                comment.save()
                template = render_to_string('laboratory/comment.html',
                                            {'comments': self.get_queryset().filter(inform=comment.inform).order_by('pk'),
                                             'user': request.user},request)

                return Response({'data':template}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        if pk:
            comment = self.get_comment(pk)
            inform=comment.inform
            comment.delete()
            template= render_to_string('laboratory/comment.html', {'comments': self.get_queryset().filter(inform=inform).order_by('pk'), 'user':request.user},request)

            return Response({'data':template},status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ProtocolViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ProtocolDataTableSerializer
    queryset = Protocol.objects.all()
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ['name', 'short_description']
    filterset_class = ProtocolFilterSet
    ordering_fields = ['pk']
    ordering = ('pk', )

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        lab_pk = self.request.GET.get('lab_pk', None)
        if lab_pk:
            queryset = queryset.filter(laboratory__pk=lab_pk)
        else:
            queryset = queryset.none()
        return queryset


    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = self.paginate_queryset(queryset)
        response = {'data': data, 'recordsTotal': Protocol.objects.count(), 'recordsFiltered': queryset.count(),
                    'draw': self.request.GET.get('draw', 1)}
        return Response(self.get_serializer(response).data)


class LogEntryViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.LogEntryDataTableSerializer
    queryset = LogEntry.objects.all()
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ['object_repr', 'action_flag']
    filterset_class =LogEntryFilterSet
    ordering_fields = ['pk']
    ordering = ('pk', )

    def get_queryset(self):
        org = self.request.GET.get('org', None)
        if not org:
            return self.queryset.none()
        else:
            org = OrganizationStructure.objects.filter(pk=org).first()
            if not org:
                return self.queryset.none()
        laboratories = list(get_laboratories_from_organization(org.pk).values_list('pk' , flat=True))

        log_entries = LabOrgLogEntry.objects.filter(
            Q(content_type__app_label='laboratory',
              content_type__model='laboratory',
              object_id__in=laboratories
            ) | Q(
              content_type__app_label='laboratory',
              content_type__model='organizationstructure',
              object_id=org.pk
            )
        ).values_list('log_entry', flat=True)
        return LogEntry.objects.filter(pk__in=log_entries)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        data = self.paginate_queryset(queryset)
        response = {'data': data, 'recordsTotal': LogEntry.objects.count(), 'recordsFiltered': queryset.count(),
                    'draw': self.request.GET.get('draw', 1)}
        return Response(self.get_serializer(response).data)


class InformViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.InformDataTableSerializer
    queryset = Inform.objects.all()
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ['name', 'creation_date', ]  # for the global search
    filterset_class = serializers.InformFilterSet
    ordering_fields = ['creation_date']
    ordering = ('-creation_date',)  # default order

    def get_queryset(self):
        period = self.request.GET.get('period', None)
        if not period:
            return self.queryset.none()
        period = get_object_or_404(InformsPeriod, pk=period)
        queryset = super().get_queryset().filter(pk__in=period.informs.values_list('pk', flat=True),
                                                 organization=self.organization)
        queryset=queryset.annotate(
            start_application_date=Value(period.start_application_date, DateField()),
            close_application_date=Value(period.close_application_date, DateField())
        )
        return queryset

    def retrieve(self, request, pk, **kwargs):
        self.organization = get_object_or_404(OrganizationStructure, pk=pk)
        queryset = self.filter_queryset(self.get_queryset())
        data = self.paginate_queryset(queryset)
        response = {'data': data, 'recordsTotal': Inform.objects.count(),
                    'recordsFiltered': queryset.count(),
                    'draw': self.request.GET.get('draw', 1)}
        return Response(self.get_serializer(response).data)