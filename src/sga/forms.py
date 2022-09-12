from django import forms
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from djgentelella.widgets import core as genwidgets
from djgentelella.widgets.selects import AutocompleteSelect
from djgentelella.forms.forms import GTForm
from sga.models import Substance, RecipientSize, TemplateSGA, DangerIndication, DangerPrudence, PersonalTemplateSGA, \
    BuilderInformation, Label


class RecipientInformationForm(forms.Form):
    substance = forms.ModelChoiceField(queryset=Substance.objects.all())
    name = forms.CharField(max_length=150, required=True )
    phone = forms.CharField(max_length=15, required=True )
    address = forms.CharField(max_length=100, required=True )
    commercial_information = forms.Textarea( )


class SGAEditorForm(GTForm,forms.ModelForm):
    class Meta:
        model = DangerPrudence
        fields = ('prudence_advice','danger_indication')
        exclude = ['']
        widgets = {
            'prudence_advice':AutocompleteSelect('prudencesearch'),
            'danger_indication': AutocompleteSelect('dangersearch')
        }

class EditorForm(GTForm, forms.ModelForm):
    preview = forms.CharField(widget=forms.HiddenInput())
    json_representation = forms.CharField(widget=forms.HiddenInput())
    class Meta:
        model = TemplateSGA
        fields = ('name', 'recipient_size', 'json_representation', 'community_share', 'preview')
        widgets={
            'name': genwidgets.TextInput,
            'recipient_size': genwidgets.Select,
            'community_share': genwidgets.YesNoInput
        }


class SearchDangerIndicationForm(GTForm, forms.Form):

    codes = forms.ModelMultipleChoiceField(queryset=DangerIndication.objects.all().exclude(code="Ninguno"), widget=genwidgets.SelectMultiple, required=True)

class PersonalForm(GTForm, forms.Form):
    name = forms.CharField(max_length=100, required=True, widget=genwidgets.TextInput)
    company_name = forms.CharField(max_length=150, required=True, widget=genwidgets.TextInput)
    address = forms.CharField(widget=genwidgets.Textarea)
    phone = forms.CharField(max_length=50, required=True, widget=genwidgets.TextInput)
    json_representation = forms.CharField(widget=forms.HiddenInput())
    preview = forms.CharField(widget=forms.HiddenInput())
    template = forms.ModelChoiceField(queryset=TemplateSGA.objects.none(), required=False, widget=genwidgets.HiddenInput)
    substance = forms.ModelChoiceField(queryset=Substance.objects.all(), widget=genwidgets.Select)
    commercial_information = forms.CharField(widget=genwidgets.Textarea)
    barcode = forms.CharField(widget=genwidgets.TextInput, max_length=150, required=False)
    logo = forms.FileField(widget=genwidgets.FileInput, required=False)
    logo_upload_id = forms.CharField(widget=forms.HiddenInput(), required=False)


    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(PersonalForm, self).__init__(*args, **kwargs)
        filter = Q(community_share=True) | Q(creator=user)
        self.fields['template'].queryset = TemplateSGA.objects.filter(filter)


class PersonalSGAForm(forms.ModelForm):
    logo_upload_id = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = PersonalTemplateSGA
        fields = ['name', 'logo', 'barcode', 'template', 'logo_upload_id', 'json_representation', 'preview']
        exclude = ['template', 'user']
        widgets = {
            'logo': genwidgets.FileInput,
        }


class BuilderInformationForm(forms.ModelForm):
    class Meta:
        model = BuilderInformation
        fields = "__all__"


class LabelForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ['sustance', 'commercial_information']
        exclude = ['builderInformation']
        widgets = {
            'sustance': genwidgets.Select
        }


class DonateForm(GTForm, forms.Form):
    name = forms.CharField(
        label=_('Name'), max_length=200, required=True,
        widget=genwidgets.TextInput)
    amount = forms.CharField(
        label=_('Amount'), required=True, widget=genwidgets.NumberInput,
        help_text=_("*Type the amount in dollars"))
    email = forms.CharField(
        label=_('Email'), required=True, widget=genwidgets.EmailMaskInput)
    is_donator = forms.BooleanField(
        label=_('Add me to the donators list'), widget=genwidgets.YesNoInput,
        initial=True)


class PersonalTemplatesForm(GTForm, forms.Form):
    name = forms.CharField(max_length=100, required=True)
    json_data = forms.CharField(widget=forms.TextInput)

class SubstanceForm(GTForm,forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(SubstanceForm, self).__init__(*args, **kwargs)
        self.fields['uipa_name'].label= _('UIPA name')
    class Meta:
        model = Substance
        fields= '__all__'
        widgets = {
            'comercial_name':genwidgets.TextInput,
            'uipa_name': genwidgets.TextInput,
            'components': genwidgets.SelectMultiple(),
            'danger_indications': genwidgets.SelectMultiple(),
            'synonymous': genwidgets.TextInput,
            'agrochemical': genwidgets.YesNoInput
        }

class RecipientSizeForm(GTForm,forms.ModelForm):

    class Meta:
        model = RecipientSize
        fields= '__all__'
        widgets = {
            'name':genwidgets.TextInput,
            'height': genwidgets.NumberInput,
            'height_unit': genwidgets.Select,
            'width': genwidgets.NumberInput,
            'width_unit': genwidgets.Select,

        }