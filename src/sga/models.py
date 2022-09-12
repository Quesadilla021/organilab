from django.db import models
from django.utils.translation import ugettext_lazy as _
# Create your models here.
from tagging.registry import register
from tagging.fields import TagField
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import User

from sga.managers import OrganilabContextQueryset
from laboratory import catalog

class WarningClass(MPTTModel):
    TYPE = (
        ("typeofdanger", _("Type of danger")),
        ("class", _("Danger class")),
        ("category", _("Danger Category"))
    )
    name = models.CharField(max_length=150, verbose_name=_("Name"))
    danger_type = models.CharField(
        max_length=25, default="category", choices=TYPE,
        verbose_name=_("Danger type"))

    parent = TreeForeignKey('self',
                            on_delete=models.CASCADE, null=True, blank=True,
                            related_name='children')

    def __str__(self):
        name = self.name

        if len(name) < 3 and self.parent:
            name = self.parent.name + " > " + name
        elif WarningClass.objects.filter(name=self.name).count() > 1:
            name = self.parent.name + " > " + name

        """
        if self.danger_type == 'class':
            name = "+ "+name
        elif self.danger_type == 'category':
            name = "# "+name
        """
        return name

    class Meta:
        verbose_name = _('Warning Class')
        verbose_name_plural = _('Warning Classes')


# Pictograma de precaución


class WarningWord(models.Model):
    name = models.CharField(max_length=50, verbose_name=_("Name"))
    weigth = models.SmallIntegerField(default=0, verbose_name=_("Weigth"))
    organilab_context = models.CharField(max_length=25, default="laboratory")  # academic o laboratory
    objects = OrganilabContextQueryset.as_manager()
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Warning Word')
        verbose_name_plural = _('Warning Words')


# Indicación de peligro


class Pictogram(models.Model):
    name = models.CharField(max_length=150, primary_key=True,
                            verbose_name=_("Name"))
    warning_word = models.ForeignKey(WarningWord, on_delete=models.CASCADE)
    organilab_context = models.CharField(max_length=25, default="laboratory")  # academic o laboratory
    objects = OrganilabContextQueryset.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Pictogram')
        verbose_name_plural = _('Pictograms')


# palabras de advertencia


class PrudenceAdvice(models.Model):
    code = models.CharField(max_length=150,
                            verbose_name=_("Code"))
    name = models.CharField(max_length=500, verbose_name=_("Name"))
    prudence_advice_help = models.TextField(
        null=True, blank=True,
        verbose_name=_("Help for prudence advice"))
    organilab_context = models.CharField(max_length=25, default="laboratory")  # academic o laboratory
    objects = OrganilabContextQueryset.as_manager()

    def __str__(self):
        return self.code + ": " + self.name

    class Meta:
        verbose_name = _('Prudence Advice')
        verbose_name_plural = _('Prudence Advices')


class DangerIndication(models.Model):
    code = models.CharField(max_length=150, primary_key=True,
                            verbose_name=_("Code"))
    description = models.TextField(verbose_name=_("Description"))
    warning_words = models.ForeignKey(WarningWord, on_delete=models.DO_NOTHING,
                                      verbose_name=_("Warning words"))
    pictograms = models.ManyToManyField(
        Pictogram, verbose_name=_("Pictograms"))
    warning_class = models.ManyToManyField(WarningClass,
                                           verbose_name=_("Warning class"))

    warning_category = models.ManyToManyField(
        WarningClass,
        related_name='warningcategory',
        verbose_name=_("Warning category"))
    prudence_advice = models.ManyToManyField(
        PrudenceAdvice, verbose_name=_("Prudence advice"))
    organilab_context = models.CharField(max_length=25, default="laboratory")  # academic o laboratory
    objects = OrganilabContextQueryset.as_manager()

    def __str__(self):
        return "(%s) %s" % (self.code, self.description)

    class Meta:
        verbose_name = _('Danger Indication')
        verbose_name_plural = _('Indication of Danger')


class DangerPrudence(models.Model):
    danger_indication = models.ManyToManyField(
        DangerIndication, verbose_name=_("Danger indication"))
    prudence_advice = models.ManyToManyField(
        PrudenceAdvice, verbose_name=_("Prudence advice"))
    organilab_context = models.CharField(max_length=25, default="laboratory")  # academic o laboratory
    objects = OrganilabContextQueryset.as_manager()


class Component(models.Model):
    name = models.CharField(max_length=250, verbose_name=_("Name"))
    cas_number = models.CharField(max_length=150, verbose_name=_("CAS number"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Component')
        verbose_name_plural = _('Components')


class Substance(models.Model):
    comercial_name = models.CharField(max_length=250,
                                      verbose_name=_("Comercial name"))
    uipa_name= models.CharField(max_length=250, default="",
                                verbose_name=_("UIPA name"))
    components_sga = models.ManyToManyField(
        "self", verbose_name=_("Components"))
    danger_indications = models.ManyToManyField(
        DangerIndication,
        verbose_name=_("Danger indications"))
    synonymous = TagField(verbose_name=_("Synonymous"))
    agrochemical = models.BooleanField(default=False,
                                       verbose_name=_("Agrochemical"))
    creator = models.ForeignKey(User, verbose_name=_("Creator"), on_delete=models.DO_NOTHING, null=True)
    organilab_context = models.CharField(max_length=25, default="laboratory")  # academic o laboratory
    objects = OrganilabContextQueryset.as_manager()


    @property
    def warning_word(self):
        last_word = ""
        last_num = -1
        for dindic in self.danger_indications.all():
            if dindic.warning_words.weigth > last_num:
                last_num = dindic.warning_words.weigth
                last_word = dindic.warning_words.name
        return last_word

    def __str__(self):
        return self.comercial_name

    class Meta:
        verbose_name = _('Sustance')
        verbose_name_plural = _('Sustances')


register(Substance)

class SustanceCharacteristics(models.Model):
    substance = models.OneToOneField(Substance, on_delete=models.CASCADE)
    iarc = catalog.GTForeignKey("laboratory.Catalog", related_name="gt_iarcrel_sga", on_delete=models.DO_NOTHING,
                                null=True, blank=True, key_name="key", key_value="IARC")
    imdg = catalog.GTForeignKey("laboratory.Catalog", related_name="gt_imdg_sga", on_delete=models.DO_NOTHING,
                                null=True, blank=True, key_name="key", key_value="IDMG")
    white_organ = catalog.GTManyToManyField("laboratory.Catalog", related_name="gt_white_organ_sga", key_name="key",
                                            key_value="white_organ", blank=True)
    bioaccumulable = models.BooleanField(null=True)
    molecular_formula = models.CharField(_('Molecular formula'), max_length=255, null=True, blank=True)
    cas_id_number = models.CharField(
        _('Cas ID Number'), max_length=255, null=True, blank=True)
    security_sheet = models.FileField(
        _('Security sheet'), upload_to='security_sheets/', null=True, blank=True)
    is_precursor = models.BooleanField(_('Is precursor'), default=False)
    precursor_type = catalog.GTForeignKey("laboratory.Catalog", related_name="gt_precursor_sga", on_delete=models.SET_NULL,
                                          null=True, blank=True, key_name="key", key_value="Precursor")

    h_code = models.ManyToManyField(DangerIndication, related_name="sga_h_code", verbose_name=_("Danger Indication"), blank=True)
    valid_molecular_formula = models.BooleanField(default=False)
    ue_code = catalog.GTManyToManyField("laboratory.Catalog", related_name="gt_ue_sga", key_name="key",
                                        key_value="ue_code", blank=True, verbose_name=_('UE codes'))
    nfpa = catalog.GTManyToManyField("laboratory.Catalog", related_name="gt_nfpa_sga", key_name="key",
                                     key_value="nfpa", blank=True, verbose_name=_('NFPA codes'))
    storage_class = catalog.GTManyToManyField("laboratory.Catalog", related_name="gt_storage_class_sga", key_name="key",
                                              key_value="storage_class", blank=True, verbose_name=_('Storage class'))
    seveso_list = models.BooleanField(verbose_name=_('Is Seveso list III?'), default=False)

    class Meta:
        verbose_name = _('Sustance characteristic SGA')
        verbose_name_plural = _('Sustance characteristics SGA')

# build information


class BuilderInformation(models.Model):
    name = models.CharField(max_length=150, verbose_name=_("Name"))
    phone = models.TextField(max_length=15, verbose_name=_("Phone"))
    address = models.TextField(max_length=100, verbose_name=_("Address"))
    user = models.ForeignKey(User, verbose_name=_("User"),on_delete=models.DO_NOTHING, null=True)
    community_share = models.BooleanField(default=False,blank=True, verbose_name=_("Share with community"))
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Builder Information')
        verbose_name_plural = _('Information of Builders')


# labels


class RecipientSize(models.Model):
    CHOICES = (
        ('mm', _('Milimeters')),
        ('cm', _('Centimeters')),
        ('inch', _('inch')),
    )
    name = models.CharField(max_length=150, verbose_name=_("Name"))
    height = models.FloatField(default=10, verbose_name=_("Height"))
    height_unit = models.CharField(max_length=5, default="cm",
                                   verbose_name=_("Height Unit"),
                                   choices=CHOICES)
    width = models.FloatField(default=10, verbose_name=_("Width"))
    width_unit = models.CharField(max_length=5, default="cm",
                                  verbose_name=_("Width Unit"),
                                  choices=CHOICES)

    def __str__(self):
        return 'name={0} | height={1}, height_unit={2}, width={3}, width_unit={4}'.format(self.name, self.height,
                                                                                          self.height_unit, self.width,
                                                                                          self.width_unit)

    class Meta:
        verbose_name = _('Recipient Size')
        verbose_name_plural = _('Size of recipients')


class Label(models.Model):
    sustance = models.ForeignKey(Substance,
                                 verbose_name=_("Sustance"),
                                 on_delete=models.CASCADE)
    builderInformation = models.ForeignKey(
        BuilderInformation, verbose_name=_("Builder Information"),
        on_delete=models.CASCADE)
    commercial_information = models.TextField(
        null=True, blank=True,
        verbose_name=_("Commercial Information"))

    def __str__(self):
        return str(self.sustance)

    class Meta:
        verbose_name = _('Label')
        verbose_name_plural = _('Labels')


class TemplateSGA(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=150, verbose_name=_("Name"))
    recipient_size = models.ForeignKey(RecipientSize, verbose_name=_("Recipient Size"), on_delete=models.CASCADE)
    json_representation = models.TextField()
    community_share = models.BooleanField(default=True, verbose_name=_("Share with community"))
    preview = models.TextField(help_text="B64 preview image", null=True)
    organilab_context = models.CharField(max_length=25, default="laboratory")  # academic o laboratory
    objects = OrganilabContextQueryset.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Template SGA')
        verbose_name_plural = _('Templates SGA')

class PersonalTemplateSGA(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, verbose_name=_("Name"))
    json_representation = models.TextField()
    template = models.ForeignKey(TemplateSGA, verbose_name=_("Template SGA"), on_delete=models.DO_NOTHING)
    preview = models.TextField(help_text="B64 preview image", null=True)
    label = models.ForeignKey(Label, verbose_name=_("Label"), on_delete=models.DO_NOTHING)
    barcode = models.CharField(max_length=150, verbose_name=_("Barcode"), null=True, blank=True)
    logo = models.FileField(_('Logo'), upload_to='sga/logo/', null=True, blank=True)
    organilab_context = models.CharField(max_length=25, default="laboratory")  # academic o laboratory
    objects = OrganilabContextQueryset.as_manager()

    def __str__(self):
        recipient=RecipientSize.objects.get(pk=self.template.recipient_size.pk)
        return self.name+" Height {0}{1} x Width {2}{3}".format(recipient.height,recipient.height_unit,recipient.width,recipient.width_unit)

    class Meta:
        verbose_name = _('Personal Template SGA')
        verbose_name_plural = _('Personal Templates SGA')


class Donation(models.Model):
    name = models.CharField(max_length=200, verbose_name=_("Name"))
    email = models.CharField(max_length=100, verbose_name=_("Email"))
    amount = models.CharField(max_length=10, verbose_name=_("Amount"))
    details = models.TextField(max_length=255, verbose_name=_("Details"))
    is_donator = models.BooleanField(default=True, verbose_name=_("Add me to the donators list"))
    is_paid = models.BooleanField(default=False, verbose_name=_("Is paid?"))
    donation_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Donation date'))

    class Meta:
        verbose_name = _("Donation")
        verbose_name_plural = _("Donations")

    def __str__(self):
        return f'{self.name}: ${self.amount}'
