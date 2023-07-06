from datetime import datetime
import logging

from django.conf import settings
from django.forms import model_to_dict
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from auth_and_perms.api.serializers import ValidateUserAccessOrgLabSerializer
from laboratory.api.serializers import BaseShelfObjectSerializer
from rest_framework import serializers
from laboratory.models import ShelfObject, Shelf, Catalog, Object, Laboratory, ShelfObjectLimits, \
    TranferObject, ShelfObjectObservation, Provider, Furniture, LaboratoryRoom, SustanceCharacteristics, REQUESTED
from organilab.settings import DATETIME_INPUT_FORMATS
from reservations_management.models import ReservedProducts
from laboratory.shelfobject.utils import get_available_containers_for_selection, get_containers_for_cloning

logger = logging.getLogger('organilab')


class ContainerSerializer(serializers.Serializer):
    CONTAINER_SELECT_CHOICES = [
        ('clone', _('Create new based on selected')), 
        ('available', _('Use selected')),
    ]
    container_select_option = serializers.ChoiceField(required=True, choices=CONTAINER_SELECT_CHOICES)
    container_for_cloning = serializers.PrimaryKeyRelatedField(many=False, allow_null=True, 
                                                               queryset=Object.objects.none())
    available_container = serializers.PrimaryKeyRelatedField(many=False, allow_null=True, 
                                                             queryset=ShelfObject.objects.none())
       
    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        # allow select only available containers or containers for cloning depending on what the user wants and make the right field not nullable
        container_select_option = self.initial_data.get('container_select_option')
        if container_select_option == 'clone':
            # set queryset to validate that only those in the organization of type material are valid for selection
            fields['container_for_cloning'].queryset = get_containers_for_cloning(self.context['organization_id'])  
            fields['container_for_cloning'].allow_null = False
        elif container_select_option == 'available':
            # set queryset to validate that only those in the laboratory of type material are valid for selection
            fields['available_container'].queryset = get_available_containers_for_selection(self.context['laboratory_id'])
            fields['available_container'].allow_null = False
        return fields

class ReserveShelfObjectSerializer(serializers.ModelSerializer):
    amount_required = serializers.FloatField(min_value=0.1)
    shelf_object = serializers.PrimaryKeyRelatedField(queryset=ShelfObject.objects.using(settings.READONLY_DATABASE))
    initial_date = serializers.DateTimeField(input_formats=DATETIME_INPUT_FORMATS)
    final_date = serializers.DateTimeField(input_formats=DATETIME_INPUT_FORMATS)

    def validate(self, data):
        current_date = now().date()
        initial_date = data['initial_date'].date()
        final_date = data['final_date'].date()

        if initial_date == final_date:
            raise serializers.ValidationError({'final_date':_("Final date can't be equal to initial date")})
        if initial_date >= final_date:
            raise serializers.ValidationError({'initial_date':_("Initial date can't be greater than final date")})
        elif initial_date <= current_date:
            raise serializers.ValidationError({'initial_date':_("Initial date can't be equal or lower to current date")})
        elif initial_date <= current_date:
            raise serializers.ValidationError({'initial_date':_("Initial date can't be lower than current date")})
        elif final_date <= current_date:
            raise serializers.ValidationError({'initial_date': _("Final date can't be lower than current date")})

        return data

    def validate_shelf_object(self, value):
        attr = super().validate(value)
        source_laboratory_id = self.context.get("source_laboratory_id")
        if attr.in_where_laboratory_id != source_laboratory_id:
            logger.debug(
                f'ReservedShelfObjectSerializer --> attr.in_where_laboratory_id ({attr.in_where_laboratory_id}) != source_laboratory_id ({source_laboratory_id})')
            raise serializers.ValidationError(_("Object doesn't exists in this laboratory"))
        return attr

    class Meta:
        model = ReservedProducts
        fields = ['amount_required', 'shelf_object', 'initial_date', 'final_date']


class IncreaseShelfObjectSerializer(serializers.Serializer):
    amount = serializers.FloatField(min_value=0.1)
    bill = serializers.CharField(required=False, allow_blank=True)
    provider = serializers.PrimaryKeyRelatedField(queryset=Provider.objects.using(settings.READONLY_DATABASE), required=False, allow_null=True)
    shelf_object = serializers.PrimaryKeyRelatedField(queryset=ShelfObject.objects.using(settings.READONLY_DATABASE))

    def validate_shelf_object(self, value):
        attr = super().validate(value)
        source_laboratory_id = self.context.get("source_laboratory_id")
        if attr.in_where_laboratory_id != source_laboratory_id:
            logger.debug(
                f'IncreaseShelfObjectSerializer --> attr.in_where_laboratory_id ({attr.in_where_laboratory_id}) != source_laboratory_id ({source_laboratory_id})')
            raise serializers.ValidationError(_("Object doesn't exists in this laboratory"))
        return attr

    def validate_provider(self, value):
        attr = super().validate(value)
        source_laboratory_id = self.context.get("source_laboratory_id")
        if attr:
            if attr.laboratory_id != source_laboratory_id:
                logger.debug(
                    f'IncreaseShelfObjectSerializer --> attr.laboratory ({attr.laboratory}) != source_laboratory_id ({source_laboratory_id})')
                raise serializers.ValidationError(_("Provider doesn't exists in this laboratory"))
        return attr

    def validate(self, data):
        shelf_object = data['shelf_object']
        shelf = shelf_object.shelf
        shelf_quantity = shelf.quantity
        amount = data['amount']
        total = shelf.get_total_refuse() + amount
        check_measurement_unit = shelf_object.measurement_unit != shelf.measurement_unit and shelf.measurement_unit

        if check_measurement_unit:
            logger.debug(
                f'IncreaseShelfObjectSerializer --> shelf_object.measurement_unit != shelf.measurement_unit and shelf.measurement_unit is'
                f' ({check_measurement_unit})')
            raise serializers.ValidationError({'shelf_object': _("Measurement unit can't different than shelf measurement unit")})

        if total > shelf_quantity and not shelf.infinity_quantity:
            raise serializers.ValidationError({'amount': _("Quantity can't greater than shelf quantity limit %(limit)s") % {
                'limit': shelf_quantity,
            }})
        return data


class DecreaseShelfObjectSerializer(serializers.Serializer):
    amount = serializers.FloatField(min_value=0.1)
    description = serializers.CharField(required=False, allow_blank=True)
    shelf_object = serializers.PrimaryKeyRelatedField(queryset=ShelfObject.objects.using(settings.READONLY_DATABASE))

    def validate_shelf_object(self, value):
        attr = super().validate(value)
        source_laboratory_id = self.context.get("source_laboratory_id")
        if attr.in_where_laboratory_id != source_laboratory_id:
            logger.debug(
                f'DecreaseShelfObjectSerializer --> attr.in_where_laboratory_id ({attr.in_where_laboratory_id}) != source_laboratory_id ({source_laboratory_id})')
            raise serializers.ValidationError(_("Object doesn't exists in this laboratory"))
        return attr

    def validate(self, data):
        amount = data['amount']
        shelf_object = data['shelf_object']

        if shelf_object.quantity < amount:
            raise serializers.ValidationError({'amount': _("Substract amount can't be greater than available shelf amount")})
        return data


class ValidateShelfSerializerCreate(serializers.Serializer):
    # TODO - update this serializer to validate that the shelf belongs to the laboratory, maybe inherit from ValidateShelfSerializer?
    
    OBJTYPE_CHOICES = (
        ("0", 'Reactive'),
        ("1", 'Material'),
        ("2", 'Equipment'))
    shelf = serializers.PrimaryKeyRelatedField(many=False, queryset=Shelf.objects.using(settings.READONLY_DATABASE))
    objecttype = serializers.ChoiceField(choices=OBJTYPE_CHOICES, required=True)

    def get_key_descriptor(self):
        """
        Atención debe llamar a is_valid() primero.
        :return:
        """
        names = {key: value.lower() for key, value in self.OBJTYPE_CHOICES}
        obj_type_name = names[self.validated_data['objecttype']]
        if self.validated_data['shelf'].discard:
            obj_type_name += "_refuse"
        return obj_type_name


class DateFieldWithEmptyString(serializers.DateField):
    def to_internal_value(self, value):
        if not value:
            return None
        return super(DateFieldWithEmptyString, self).to_internal_value(value)


class ShelfObjectLimitsSerializer(serializers.ModelSerializer):
    minimum_limit = serializers.FloatField(min_value=0.0, required=True, initial=0.0)
    maximum_limit = serializers.FloatField(min_value=0.0, required=True, initial=0.0)
    expiration_date = DateFieldWithEmptyString(input_formats=settings.DATE_INPUT_FORMATS, required=False,
                                               allow_null=True)

    class Meta:
        model = ShelfObjectLimits
        fields = '__all__'

    def validate(self, data):
        attr = super().validate(data)
        if attr['minimum_limit'] > attr['maximum_limit']:
            raise serializers.ValidationError(_("Minimum limit can't be greater than maximum limit"))
        return data


def validate_measurement_unit_and_quantity(klass, data, attr):
    errors = {}
    quantity = attr['quantity']
    total = attr['shelf'].get_total_refuse() + quantity
    shelf= attr['shelf']
    obj= attr['object']
    shelf_quantity = attr['shelf'].quantity
    unit = attr['measurement_unit']
    shelf_unit = attr['shelf'].measurement_unit
    shelf_infinity = attr['shelf'].infinity_quantity
    #discard = attr['marked_as_discard'] if 'marked_as_discard' and attr else False

    if unit != shelf_unit and shelf_unit:
        errors.update({'measurement_unit': _("Measurement unit can't different than shelf measurement unit")})
    if total > shelf_quantity and not shelf_infinity:
        errors.update({'quantity': _("Quantity can't greater than shelf quantity limit %(limit)s")%{
            'limit': shelf_quantity,
        }})
    if shelf.limit_only_objects:
        if not shelf.available_objects_when_limit.filter(pk=obj.pk).exists():
            errors.update({'object': _("Object is not available in these shelf")})


    if errors:
        raise serializers.ValidationError(errors)
    return attr


class ReactiveShelfObjectSerializer(serializers.ModelSerializer):
    # TODO - this serializer needs to be updated to also add a field for containers for cloning (or even use the container same one and update the queryset somehow)
    # TODO  - inherit from the container serializer so we dont need to manage the container and get fields method everywhere - delete them from here
    
    object = serializers.PrimaryKeyRelatedField(many=False, queryset=Object.objects.using(settings.READONLY_DATABASE),
                                                required=True)
    shelf = serializers.PrimaryKeyRelatedField(many=False, queryset=Shelf.objects.using(settings.READONLY_DATABASE),
                                               required=True)
    quantity = serializers.FloatField(required=True)
    measurement_unit = serializers.PrimaryKeyRelatedField(many=False,
                                                          queryset=Catalog.objects.using(settings.READONLY_DATABASE),
                                                          required=True)
    marked_as_discard = serializers.BooleanField(default=False, required=False)
    course_name = serializers.CharField(required=False)
    batch = serializers.CharField(required=True)
    container = serializers.PrimaryKeyRelatedField(many=False, required=True, queryset=ShelfObject.objects.none())

    class Meta:
        model = ShelfObject
        fields = ['object', 'shelf', "status", 'quantity', 'measurement_unit', 'limit_quantity', "course_name",
                  'marked_as_discard', 'batch', 'container']

    def validate(self, data):
        attr = super().validate(data)
        return validate_measurement_unit_and_quantity(self, data, attr)
    
    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        # allow select only available containers
        fields['container'].queryset = get_available_containers_for_selection(self.context['lab_pk'])
        return fields

class ReactiveRefuseShelfObjectSerializer(serializers.ModelSerializer):
    # TODO - this serializer needs to be updated to also add a field for containers for cloning (or even use the container same one and update the queryset somehow)
    # TODO  - inherit from the container serializer so we dont need to manage the container and get fields method everywhere - delete them from here
        
    object = serializers.PrimaryKeyRelatedField(many=False, queryset=Object.objects.using(settings.READONLY_DATABASE))
    shelf = serializers.PrimaryKeyRelatedField(many=False, queryset=Shelf.objects.using(settings.READONLY_DATABASE),
                                               required=True)
    status = serializers.PrimaryKeyRelatedField(many=False, queryset=Catalog.objects.using(settings.READONLY_DATABASE),
                                                required=True)
    quantity = serializers.FloatField(required=True)
    measurement_unit = serializers.PrimaryKeyRelatedField(many=False,
                                                          queryset=Catalog.objects.using(settings.READONLY_DATABASE),
                                                          required=True)
    marked_as_discard = serializers.BooleanField(default=True, required=False)
    course_name = serializers.CharField(required=False)
    batch = serializers.CharField(required=True)
    container = serializers.PrimaryKeyRelatedField(many=False, required=True, queryset=ShelfObject.objects.none())

    class Meta:
        model = ShelfObject
        fields = ["object", "shelf", "status", "quantity",
                  "measurement_unit", "marked_as_discard", "course_name", 'batch', 'container']

    def validate(self, data):
        attr = super().validate(data)
        return validate_measurement_unit_and_quantity(self, data, attr)
    
    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        # allow select only available containers
        fields['container'].queryset = get_available_containers_for_selection(self.context['lab_pk'])
        return fields

class MaterialShelfObjectSerializer(serializers.ModelSerializer):
    object = serializers.PrimaryKeyRelatedField(many=False, queryset=Object.objects.using(settings.READONLY_DATABASE))
    shelf = serializers.PrimaryKeyRelatedField(many=False, queryset=Shelf.objects.using(settings.READONLY_DATABASE),
                                               required=True)
    status = serializers.PrimaryKeyRelatedField(many=False, queryset=Catalog.objects.using(settings.READONLY_DATABASE),
                                                required=True)
    quantity = serializers.FloatField(required=True)
    limit_quantity = serializers.FloatField(required=True)
    measurement_unit = serializers.PrimaryKeyRelatedField(many=False,
                                                          queryset=Catalog.objects.using(settings.READONLY_DATABASE),
                                                          required=True)
    marked_as_discard = serializers.BooleanField(default=False, required=False)
    course_name = serializers.CharField(required=False)

    class Meta:
        model = ShelfObject
        fields = ["object", "shelf", "status", "quantity", "limit_quantity", "measurement_unit", "marked_as_discard",
                  "course_name"]

    def validate(self, data):
        attr = super().validate(data)
        return validate_measurement_unit_and_quantity(self, data, attr)

class MaterialRefuseShelfObjectSerializer(serializers.ModelSerializer):
    object = serializers.PrimaryKeyRelatedField(many=False, queryset=Object.objects.using(settings.READONLY_DATABASE))
    shelf = serializers.PrimaryKeyRelatedField(many=False, queryset=Shelf.objects.using(settings.READONLY_DATABASE),
                                               required=True)
    status = serializers.PrimaryKeyRelatedField(many=False, queryset=Catalog.objects.using(settings.READONLY_DATABASE),
                                                required=True)
    quantity = serializers.FloatField(required=True)
    limit_quantity = serializers.FloatField(required=True)
    measurement_unit = serializers.PrimaryKeyRelatedField(many=False,
                                                          queryset=Catalog.objects.using(settings.READONLY_DATABASE),
                                                          required=True)
    marked_as_discard = serializers.BooleanField(default=True, required=False)
    course_name = serializers.CharField(required=False)

    class Meta:
        model = ShelfObject
        fields = ["object", "shelf", "status", "quantity", "limit_quantity", "measurement_unit", "marked_as_discard",
                  "course_name"]

    def validate(self, data):
        attr = super().validate(data)
        return validate_measurement_unit_and_quantity(self, data, attr)

class EquipmentShelfObjectSerializer(serializers.ModelSerializer):
    object = serializers.PrimaryKeyRelatedField(many=False, queryset=Object.objects.using(settings.READONLY_DATABASE))
    shelf = serializers.PrimaryKeyRelatedField(many=False, queryset=Shelf.objects.using(settings.READONLY_DATABASE),
                                               required=True)
    status = serializers.PrimaryKeyRelatedField(many=False, queryset=Catalog.objects.using(settings.READONLY_DATABASE),
                                                required=True)
    quantity = serializers.FloatField(required=True)
    limit_quantity = serializers.FloatField(required=True)
    measurement_unit = serializers.PrimaryKeyRelatedField(many=False,
                                                          queryset=Catalog.objects.using(settings.READONLY_DATABASE),
                                                          required=True)
    marked_as_discard = serializers.BooleanField(default=False, required=False)
    course_name = serializers.CharField(required=False)

    class Meta:
        model = ShelfObject
        fields = ["object", "shelf", "status", "quantity", "limit_quantity", "measurement_unit", "marked_as_discard",
                  "course_name"]

    def validate(self, data):
        attr = super().validate(data)
        return validate_measurement_unit_and_quantity(self, data, attr)

class EquipmentRefuseShelfObjectSerializer(serializers.ModelSerializer):
    object = serializers.PrimaryKeyRelatedField(many=False, queryset=Object.objects.using(settings.READONLY_DATABASE))
    shelf = serializers.PrimaryKeyRelatedField(many=False, queryset=Shelf.objects.using(settings.READONLY_DATABASE),
                                               required=True)
    status = serializers.PrimaryKeyRelatedField(many=False, queryset=Catalog.objects.using(settings.READONLY_DATABASE),
                                                required=True)
    quantity = serializers.FloatField(required=True)
    limit_quantity = serializers.FloatField(required=True)
    measurement_unit = serializers.PrimaryKeyRelatedField(many=False,
                                                          queryset=Catalog.objects.using(settings.READONLY_DATABASE),
                                                          required=True)
    marked_as_discard = serializers.BooleanField(default=True, required=False)
    course_name = serializers.CharField(required=False)

    class Meta:
        model = ShelfObject
        fields = ["object", "shelf", "status", "quantity", "limit_quantity", "measurement_unit", "marked_as_discard",
                  "course_name"]

    def validate(self, data):
        attr = super().validate(data)
        return validate_measurement_unit_and_quantity(self, data, attr)


class TransferOutShelfObjectSerializer(serializers.Serializer):
    shelf_object = serializers.PrimaryKeyRelatedField(queryset=ShelfObject.objects.using(settings.READONLY_DATABASE))
    amount_to_transfer = serializers.FloatField(min_value=0.1)
    mark_as_discard = serializers.BooleanField(default=False)
    laboratory = serializers.PrimaryKeyRelatedField(queryset=Laboratory.objects.using(settings.READONLY_DATABASE))

    def validate_shelf_object(self, value):
        attr = super().validate(value)
        source_laboratory_id = self.context.get("source_laboratory_id")
        if attr.in_where_laboratory_id != source_laboratory_id:
            logger.debug(f'TransferOutShelfObjectSerializer --> attr.in_where_laboratory_id '
                         f'({attr.in_where_laboratory_id}) != source_laboratory_id ({source_laboratory_id})')
            raise serializers.ValidationError(_("Object does not exist in the laboratory."))
        return attr


class ShelfObjectDeleteSerializer(serializers.Serializer):
    shelfobj = serializers.PrimaryKeyRelatedField(queryset=ShelfObject.objects.using(settings.READONLY_DATABASE))

    def validate_shelfobj(self, value):
        attr = super().validate(value)
        if attr.in_where_laboratory_id != self.context.get('laboratory_id'):
            logger.debug(f'ShelfObjectDeleteSerializer --> attr.in_where_laboratory_id ({attr.in_where_laboratory_id}) '
                         f'!= laboratory_id ({self.context.get("laboratory_id")})')
            raise serializers.ValidationError(_("Object does not exist in the laboratory."))
        return attr


class ValidateShelfSerializer(serializers.Serializer):
    shelf = serializers.PrimaryKeyRelatedField(queryset=Shelf.objects.using(settings.READONLY_DATABASE))

    def validate_shelf(self, value):
        attr = super().validate(value)
        laboratory_id = self.context.get("laboratory_id")
        if attr.furniture.labroom.laboratory_id != laboratory_id:
            logger.debug(f'ValidateShelfSerializer --> attr.furniture.labroom.laboratory_id '
                         f'({attr.furniture.labroom.laboratory_id}) != laboratory_id ({laboratory_id})')
            raise serializers.ValidationError(_("Object doesn't exists in this laboratory"))
        return attr


class CatalogDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Catalog
        fields = ['description']


class SubstanceCharacteristicsDetailSerializer(serializers.ModelSerializer):
    iarc = CatalogDetailSerializer()
    imdg = CatalogDetailSerializer()
    precursor_type = CatalogDetailSerializer()
    white_organ = CatalogDetailSerializer(many=True)
    storage_class = CatalogDetailSerializer(many=True)
    ue_code = CatalogDetailSerializer(many=True)
    nfpa = CatalogDetailSerializer(many=True)

    class Meta:
        model = SustanceCharacteristics
        fields = '__all__'


class ShelfObjectDetailSerializer(BaseShelfObjectSerializer, serializers.ModelSerializer):
    object_detail = serializers.SerializerMethodField()
    object_name = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()
    object_inst = serializers.SerializerMethodField()
    object_features = serializers.SerializerMethodField(required=False, allow_null=True)
    substance_characteristics = serializers.SerializerMethodField(required=False, allow_null=True)

    class Meta:
        model = ShelfObject
        fields = '__all__'

    def get_substance_characteristics(self, obj):
        if hasattr(obj.object, 'sustancecharacteristics'):
            characteristics = SubstanceCharacteristicsDetailSerializer(obj.object.sustancecharacteristics)
            return characteristics.data

    def get_object_detail(self, obj):
        return obj.get_object_detail()

    def get_object_features(self, obj):
        if obj.object.features.exists():
            return list(obj.object.features.all().values('name'))

    def get_object_inst(self, obj):
        object_d = model_to_dict(obj.object)
        del object_d['features']
        return object_d


class ShelfSerializer(serializers.ModelSerializer):

    type = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()
    quantity_storage_status = serializers.SerializerMethodField()
    percentage_storage_status = serializers.SerializerMethodField()
    shelf_info = serializers.SerializerMethodField()

    def get_type(self, obj):
        return str(obj.type) if obj.type else ""

    def get_quantity(self, obj):
        quantity = obj.quantity
        if quantity == -1:
            quantity = _("Unlimited storage")
        return quantity

    def get_measurement_unit(self, obj):
        return obj.get_measurement_unit_display()

    def get_quantity_storage_status(self, obj):
        return f'{obj.get_total_refuse()} {_("of")} {obj.quantity}'

    def get_percentage_storage_status(self, obj):
        return f'{obj.get_refuse_porcentage()}% {_("of")} 100%'

    def get_shelf_info(self, obj):
        shelf = {
            'name': obj.name,
            'type': self.get_type(obj),
            'quantity': self.get_quantity(obj),
            'discard': obj.discard,
            'measurement_unit': self.get_measurement_unit(obj),
            'quantity_storage_status': self.get_quantity_storage_status(obj),
            'percentage_storage_status': self.get_percentage_storage_status(obj)
        }
        return render_to_string(
            'laboratory/shelfobject/shelf_availability_information.html',
            context={'shelf': shelf}
        )

    class Meta:
        model = Shelf
        fields = ['name', 'type', 'quantity', 'discard', 'measurement_unit', 'quantity_storage_status', 'shelf_info',
                  'percentage_storage_status']


class ShelfObjectStatusSerializer(serializers.Serializer):
    description = serializers.CharField(allow_blank=False, required=True)


class TransferObjectSerializer(serializers.ModelSerializer):
    object = serializers.SerializerMethodField()
    laboratory_send = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()

    def get_object(self, obj):
        return {"name": obj.object.object.name, "type": obj.object.object.get_type_display()}

    def get_laboratory_send(self, obj):
        return obj.laboratory_send.name

    def get_quantity(self, obj):
        return f"{obj.quantity} {obj.object.get_measurement_unit_display()}"

    class Meta:
        model = TranferObject
        fields = ("id", "object", "quantity", "laboratory_send", "update_time", "mark_as_discard")


class TransferObjectDataTableSerializer(serializers.Serializer):
    data = serializers.ListField(child=TransferObjectSerializer(), required=True)
    draw = serializers.IntegerField(required=True)
    recordsFiltered = serializers.IntegerField(required=True)
    recordsTotal = serializers.IntegerField(required=True)


class ShelfObjectObservationSerializer(serializers.ModelSerializer):
    creator_name = serializers.SerializerMethodField()

    class Meta:
        model = ShelfObjectObservation
        fields = ['id', 'action_taken', 'description', 'creator_name', 'creation_date']

    def get_creator_name(self, obj):
        if obj.creator:
            name = obj.creator.get_full_name()
            if name:
                return name
            else:
                return obj.creator.username
        return "No creator"


class ShelfObjectObservationDataTableSerializer(serializers.Serializer):
    data = serializers.ListField(child=ShelfObjectObservationSerializer(), required=True)
    draw = serializers.IntegerField(required=True)
    recordsFiltered = serializers.IntegerField(required=True)
    recordsTotal = serializers.IntegerField(required=True)

class UpdateShelfObjectStatusSerializer(serializers.Serializer):
    shelf_object = serializers.PrimaryKeyRelatedField(many=False,
                                                      queryset=ShelfObject.objects.using(settings.READONLY_DATABASE),
                                                      required=True)
    status = serializers.PrimaryKeyRelatedField(many=False, queryset=Catalog.objects.filter(key='shelfobject_status'),
                                                required=True)
    description = serializers.CharField(required=True)

    def validate_shelf_object(self, value):
        attr = super().validate(value)
        if attr.in_where_laboratory_id != self.context.get('laboratory_id'):
            logger.debug(f'UpdateShelfObjectStatusSerializer --> attr.in_where_laboratory_id ({attr.in_where_laboratory_id}) '
                         f'!= laboratory_id ({self.context.get("laboratory_id")})')
            raise serializers.ValidationError(_("Object does not exist in the laboratory."))
        return attr


class MoveShelfObjectSerializer(serializers.Serializer):
    lab_room = serializers.PrimaryKeyRelatedField(queryset=LaboratoryRoom.objects.using(settings.READONLY_DATABASE))
    furniture = serializers.PrimaryKeyRelatedField(queryset=Furniture.objects.using(settings.READONLY_DATABASE))
    shelf = serializers.PrimaryKeyRelatedField(queryset=Shelf.objects.using(settings.READONLY_DATABASE))
    shelf_object = serializers.PrimaryKeyRelatedField(queryset=ShelfObject.objects.using(settings.READONLY_DATABASE))

    def validate_lab_room(self, value):
        attr = super().validate(value)
        source_laboratory_id = self.context.get("source_laboratory_id")
        if attr:
            if attr.laboratory_id != source_laboratory_id:
                logger.debug(
                    f'MoveShelfObjectSerializer --> attr.laboratory_id ({attr.laboratory_id}) != source_laboratory_id ({source_laboratory_id})')
                raise serializers.ValidationError(_("Laboratory room doesn't exists in this laboratory"))
        return attr

    def validate_furniture(self, value):
        attr = super().validate(value)
        source_laboratory_id = self.context.get("source_laboratory_id")
        if attr:
            if attr.labroom.laboratory_id != source_laboratory_id:
                logger.debug(
                    f'MoveShelfObjectSerializer --> attr.labroom.laboratory_id ({attr.labroom.laboratory_id}) != source_laboratory_id ({source_laboratory_id})')
                raise serializers.ValidationError(_("Furniture doesn't exists in this laboratory"))
        return attr

    def validate_shelf(self, value):
        attr = super().validate(value)
        source_laboratory_id = self.context.get("source_laboratory_id")
        if attr:
            if attr.furniture.labroom.laboratory_id != source_laboratory_id:
                logger.debug(
                    f'MoveShelfObjectSerializer --> attr.furniture.labroom.laboratory_id ({attr.furniture.labroom.laboratory_id}) != source_laboratory_id ({source_laboratory_id})')
                raise serializers.ValidationError(_("Shelf doesn't exists in this laboratory"))
        return attr

    def validate_shelf_object(self, value):
        attr = super().validate(value)
        source_laboratory_id = self.context.get("source_laboratory_id")
        if attr.in_where_laboratory_id != source_laboratory_id:
            logger.debug(
                f'MoveShelfObjectSerializer --> attr.in_where_laboratory_id ({attr.in_where_laboratory_id}) != source_laboratory_id ({source_laboratory_id})')
            raise serializers.ValidationError(_("Object doesn't exists in this laboratory"))
        return attr

    def validate(self, data):
        shelf_object = data['shelf_object']
        shelf = data['shelf']

        if shelf.pk == shelf_object.shelf.pk:
            logger.debug(
                f'MoveShelfObjectSerializer --> shelf ({shelf.pk}) == shelf_object.shelf.pk ({shelf_object.shelf.pk})')
            raise serializers.ValidationError({'shelf': _("Object can't be moved to same shelf")})

        if shelf.measurement_unit != shelf_object.measurement_unit:
            logger.debug(
                f'MoveShelfObjectSerializer --> shelf ({shelf.pk}) == shelf_object.shelf.pk ({shelf_object.shelf.pk})')
            raise serializers.ValidationError({'shelf': _("Object can't be moved to shelf with different measurement unit")})

        return data


class ValidateUserAccessShelfSerializer(ValidateUserAccessOrgLabSerializer):
    shelf = serializers.PrimaryKeyRelatedField(queryset=Shelf.objects.using(settings.READONLY_DATABASE))


class ValidateUserAccessShelfTypeSerializer(ValidateUserAccessOrgLabSerializer):
    OBJTYPE_CHOICES = (
        ("0", 'Reactive'),
        ("1", 'Material'),
        ("2", 'Equipment'))
    shelf = serializers.PrimaryKeyRelatedField(many=False, queryset=Shelf.objects.using(settings.READONLY_DATABASE), required=True)
    objecttype = serializers.ChoiceField(choices=OBJTYPE_CHOICES, required=True)


class TransferInSerializer(ValidateShelfSerializer):
    # inherits the shelf field and its validation from parent serializer
    
    transfer_object = serializers.PrimaryKeyRelatedField(queryset=TranferObject.objects.using(settings.READONLY_DATABASE).filter(status=REQUESTED))

    def validate_transfer_object(self, value):
        attr = super().validate(value)
        if attr.laboratory_received_id != self.context.get('laboratory_id'):
            logger.debug(f'TransferInSerializer --> attr.laboratory_received ({attr.laboratory_received}) '
                         f'!= laboratory_id ({self.context.get("laboratory_id")})')
            raise serializers.ValidationError(_("Transfer was not sent to the laboratory."))
        return attr


class TransferInApproveWithContainerSerializer(TransferInSerializer, ContainerSerializer):
    TRANSFER_IN_CONTAINER_SELECT_CHOICES = [
        ('clone', _('Create new based on selected')), 
        ('available', _('Use selected')),
        ('use_source', _('Move the container from the source laboratory')),
        ('new_based_source', _('Create new based on current container in the source laboratory'))
    ]
    container_select_option = serializers.ChoiceField(required=True, choices=TRANSFER_IN_CONTAINER_SELECT_CHOICES)

    def validate(self, data):
        container_select_option = data['container_select_option']
        transfer_object = data['transfer_object']
        if container_select_option == 'use_source' and transfer_object.quantity != transfer_object.object.quantity:
            raise serializers.ValidationError({"container_select_option": 
                _("Source container cannot be moved since the entire quantity available for the object was not transferred in.")})
        return data
    