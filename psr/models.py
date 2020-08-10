from django.contrib.gis.db import models
import projects.models
from django.db.models import Manager as GeoManager

app_label = "psr"


class Person(projects.models.Person):
    last_name = models.CharField("Last Name", null=True, blank=True, max_length=256)
    first_name = models.CharField("First Name", null=True, blank=True, max_length=256)

    class Meta:
        verbose_name = f"{app_label.upper()} Person"
        verbose_name_plural = f"{app_label.upper()} People"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        if self.last_name and self.first_name:
            name = self.last_name + ', ' + self.first_name
        else:
            name = self.last_name
        return name


class TaxonRank(projects.models.TaxonRank):
    class Meta:
        verbose_name = f"{app_label.upper()} Taxon Rank"
        verbose_name_plural = f"{app_label.upper()} Taxon Ranks"


class Taxon(projects.models.Taxon):
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    rank = models.ForeignKey(TaxonRank, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = f"{app_label.upper()} Taxon"
        verbose_name_plural = f"{app_label.upper()} Taxa"


class IdentificationQualifier(projects.models.IdentificationQualifier):
    class Meta:
        verbose_name = f"{app_label.upper()} ID Qualifier"
        verbose_name_plural = f"{app_label.upper()} ID Qualifiers"


# Geological Context
class GeologicalContext(projects.models.PaleoCoreContextBaseClass):
    id = models.CharField(primary_key=True, max_length=255)
    name = models.TextField(null=True, blank=True, max_length=255)
    context_type = models.CharField(null=True, blank=True, max_length=255)
    context_number = models.IntegerField(null=True, blank=True)
    collection_code = models.CharField(null=True, blank=True, max_length=10)
    description = models.TextField(null=True, blank=True, max_length=255)

    stratigraphic_section = models.CharField(null=True, blank=True, max_length=50)
    stratigraphic_formation = models.CharField("Formation", max_length=255, blank=True, null=True)
    stratigraphic_member = models.CharField("Member", max_length=255, blank=True, null=True)
    upper_limit_in_section = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    lower_limit_in_section = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    analytical_unit_1 = models.CharField(max_length=255, blank=True, null=True)
    analytical_unit_2 = models.CharField(max_length=255, blank=True, null=True)
    analytical_unit_3 = models.CharField(max_length=255, blank=True, null=True)
    analytical_unit_found = models.CharField(max_length=255, blank=True, null=True)
    analytical_unit_likely = models.CharField(max_length=255, blank=True, null=True)
    analytical_unit_simplified = models.CharField(max_length=255, blank=True, null=True)
    in_situ = models.BooleanField(default=False)
    ranked = models.BooleanField(default=False)
    weathering = models.SmallIntegerField(blank=True, null=True)
    surface_modification = models.CharField("Surface Mod", max_length=255, blank=True, null=True)

    #Cave Attributes
    dip = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    strike = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    color = models.CharField(null=True, blank=True, max_length=255)
    texture = models.CharField(null=True, blank=True, max_length=255)
    height = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    width = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    depth = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    slope_character = models.TextField(null=True, blank=True, max_length=64000)
    sediment_presence = models.BooleanField(default=False)
    sediment_character = models.TextField(null=True, blank=True, max_length=64000)
    cave_mouth_character = models.TextField(null=True, blank=True, max_length=64000)
    rockfall_character = models.TextField(null=True, blank=True, max_length=64000)
    speleothem_character = models.TextField(null=True, blank=True, max_length=64000)

    #Profile Attributes

    context_remarks = models.TextField("Context Remarks", max_length=500, null=True, blank=True)
    error_notes = models.CharField(max_length=255, null=True, blank=True)
    notes = models.CharField(max_length=254, null=True, blank=True)
    geom = models.GeometryField()
    date_last_modified = models.DateTimeField("Date Last Modified", auto_now=True)
    objects = GeoManager()

    def __str__(self):
        nice_name = str(self.collection_code) + " " + str(self.context_number)
        return nice_name.replace("None", "").replace("--", "")

    class Meta:
        verbose_name = f"{app_label.upper()} Geological Context"
        verbose_name_plural = f"{app_label.upper()} Geological Contexts"
        ordering = ["context_number"]


# class Cave(Locality):
#     dip = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
#     strike = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
#     color = models.CharField(null=True, blank=True, max_length=255)
#     texture = models.CharField(null=True, blank=True, max_length=255)
#     height = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
#     width = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
#     depth = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
#     slope_character = models.TextField(null=True, blank=True, max_length=64000)
#     sediment_presence = models.BooleanField(default=False)
#     sediment_character = models.TextField(null=True, blank=True, max_length=64000)
#     cave_mouth_character = models.TextField(null=True, blank=True, max_length=64000)
#     rockfall_character = models.TextField(null=True, blank=True, max_length=64000)
#     speleothem_character = models.TextField(null=True, blank=True, max_length=64000)
#
#     class Meta:
#         verbose_name = f"{app_label.upper()} Cave/Rockshelter"
#         verbose_name_plural = f"{app_label.upper()} Caves/Rockshelters"


class ExcavationUnit(models.Model):
    unit = models.CharField(max_length=6, blank=False)
    extent = models.GeometryField(dim=3, blank=True, null=True)
    geological_context = models.ForeignKey("GeologicalContext", null=True, blank=True, on_delete=models.SET_NULL)
    objects = GeoManager()

    class Meta:
        verbose_name = f"{app_label.upper()} Excavation Unit"
        verbose_name_plural = f"{app_label.upper()} Excavation Units"


# Occurrence Class and Subclasses
class Occurrence(projects.models.PaleoCoreOccurrenceBaseClass):
    """
        Occurrence == Specimen, a general class for things discovered in the field.
        Find's have three subtypes: Archaeology, Biology, Geology
        Fields are grouped by comments into logical sets (i.e. ontological classes)
        """
    basis_of_record = models.CharField("Basis of Record", max_length=50, blank=True, null=False,
                                       help_text='e.g. Observed item or Collected item')
    item_number = models.IntegerField("Item #", null=True, blank=True)
    item_type = models.CharField("Item Type", max_length=255, blank=True, null=False)  # code
    # TODO merge with taxon
    # item_scientific_name = models.CharField("Sci Name", max_length=255, null=True, blank=True)
    # TODO merge with element
    item_description = models.CharField("Description", max_length=255, blank=True, null=True)
    item_count = models.IntegerField("Item Count", blank=True, null=True, default=1)
    collector = models.CharField("Collector", max_length=50, blank=True, null=True)
    recorded_by = models.ForeignKey("Person", null=True, blank=True, related_name="occurrence_recorded_by",
                                    on_delete=models.SET_NULL)
    finder = models.CharField("Finder", null=True, blank=True, max_length=50)  # excavator
    found_by = models.ForeignKey("Person", null=True, blank=True, related_name="occurrence_found_by",
                                 on_delete=models.SET_NULL)
    collecting_method = models.CharField("Collecting Method", max_length=50,
                                         null=True, blank=True)

    geological_context = models.ForeignKey("GeologicalContext", null=True, blank=True, on_delete=models.SET_NULL)
    unit = models.ForeignKey("ExcavationUnit", null=True, blank=True, on_delete=models.SET_NULL)
    field_id = models.CharField("Field ID", max_length=50, null=True, blank=True)
    suffix = models.IntegerField("Suffix", null=True, blank=True)
    cat_number = models.CharField("Cat Number", max_length=255, blank=True, null=True)  # unit + newplot_id
    prism = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    point = models.GeometryField(dim=3, null=True, blank=True, srid=-1)
    objects = GeoManager()

    item_part = models.CharField("Item Part", max_length=10, null=True, blank=True)
    disposition = models.CharField("Disposition", max_length=255, blank=True, null=True)
    preparation_status = models.CharField("Prep Status", max_length=50, blank=True, null=True)
    collection_remarks = models.TextField("Collection Remarks", null=True, blank=True, max_length=255)
    problem = models.BooleanField(default=False)
    problem_remarks = models.TextField(null=True, blank=True, max_length=64000)

    # Location
    collection_code = models.CharField("Collection Code", max_length=20, blank=True, null=True)
    drainage_region = models.CharField("Drainage Region", null=True, blank=True, max_length=255)

    # Media
    image = models.FileField(max_length=255, blank=True, upload_to="uploads/images/hrp", null=True)

    class Meta:
        verbose_name = f"{app_label.upper()} Occurrence"
        verbose_name_plural = f"{app_label.upper()} Occurrences"
        ordering = ["collection_code", "geological_context", "item_number", "item_part"]

    def catalog_number(self):
        """
        Generate a pretty string formatted catalog number from constituent fields
        :return: catalog number as string
        """

        if self.basis_of_record == 'Collection':
            #  Crate catalog number string. Null values become None when converted to string
            if self.item_number:
                if self.item_part:
                    item_text = '-' + str(self.item_number) + str(self.item_part)
                else:
                    item_text = '-' + str(self.item_number)
            else:
                item_text = ''

            catalog_number_string = str(self.collection_code) + " " + str(self.geological_context_id) + item_text
            return catalog_number_string.replace('None', '').replace('- ', '')  # replace None with empty string
        else:
            return None

    @staticmethod
    def fields_to_display():
        fields = ("id", "barcode")
        return fields

    @staticmethod
    def method_fields_to_export():
        """
        Method to store a list of fields that should be added to data exports.
        Called by export admin actions.
        These fields are defined in methods and are not concrete fields in the DB so have to be declared.
        :return:
        """
        return ['longitude', 'latitude', 'easting', 'northing', 'catalog_number', 'photo']

    def get_all_field_names(self):
        """
        Field names from model
        :return: list with all field names
        """
        field_list = self._meta.get_fields()  # produce a list of field objects
        return [f.name for f in field_list]  # return a list of names from each field

    def get_foreign_key_field_names(self):
        """
        Get foreign key fields
        :return: returns a list of for key field names
        """
        field_list = self._meta.get_fields()  # produce a list of field objects
        return [f.name for f in field_list if f.is_relation]  # return a list of names for fk fields

    def get_concrete_field_names(self):
        """
        Get field names that correspond to columns in the DB
        :return: returns a lift
        """
        field_list = self._meta.get_fields()
        return [f.name for f in field_list if f.concrete]


class Biology(Occurrence):
    # Biology
    biology_type = models.CharField(null=True, blank=True, max_length=255)
    sex = models.CharField("Sex", null=True, blank=True, max_length=50)
    life_stage = models.CharField("Life Stage", null=True, blank=True, max_length=50)
    size_class = models.CharField("Size Class", null=True, blank=True, max_length=50)
    # Taxon
    taxon = models.ForeignKey(Taxon,
                              default=0, on_delete=models.SET_DEFAULT,  # prevent deletion when taxa deleted
                              related_name='bio_occurrences')
    identification_qualifier = models.ForeignKey(IdentificationQualifier, null=True, blank=True,
                                                 on_delete=models.SET_NULL,
                                                 related_name='bio_occurrences')
    verbatim_taxon = models.CharField(null=True, blank=True, max_length=1024)
    verbatim_identification_qualifier = models.CharField(null=True, blank=True, max_length=255)
    taxonomy_remarks = models.TextField(max_length=500, null=True, blank=True)
    type_status = models.CharField(null=True, blank=True, max_length=50)
    fauna_notes = models.TextField(null=True, blank=True, max_length=64000)

    def __str__(self):
        return str(self.taxon.__str__())

    class Meta:
        verbose_name = f"{app_label.upper()} Biology"
        verbose_name_plural = f"{app_label.upper()} Biology"


# Archaeology Class and Subclasses
class Archaeology(Occurrence):
    archaeology_type = models.CharField(null=True, blank=True, max_length=255)
    period = models.CharField(null=True, blank=True, max_length=255)
    archaeology_preparation = models.CharField(null=True, blank=True, max_length=255)
    archaeology_remarks = models.TextField(null=True, blank=True, max_length=64000)
    length_mm = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    width_mm = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    thick_mm = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    weight = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    archaeology_notes = models.TextField(null=True, blank=True, max_length=64000)

    class Meta:
        verbose_name = f"{app_label.upper()} Archaeology"
        verbose_name_plural = f"{app_label.upper()} Archaeology"


class Lithic(Archaeology):
    dataclass = models.CharField(null=True, blank=True, max_length=255)
    fbtype = models.SmallIntegerField(blank=True, null=True)
    form = models.CharField(null=True, blank=True, max_length=255)
    technique = models.CharField(null=True, blank=True, max_length=255)
    cortex = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    coretype = models.CharField(null=True, blank=True, max_length=255)
    platsurf = models.CharField(null=True, blank=True, max_length=255)
    scarmorph = models.CharField(null=True, blank=True, max_length=255)
    edgedamage = models.CharField(null=True, blank=True, max_length=255)
    platwidth = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    platthick = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    epa = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    scarlength = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)

    class Meta:
        verbose_name = f"{app_label.upper()} Lithic"
        verbose_name_plural = f"{app_label.upper()} Lithics"


class Bone(Archaeology):
    cutmarks = models.BooleanField(default=False)
    burning = models.BooleanField(default=False)
    part = models.CharField(null=True, blank=True, max_length=255)

    class Meta:
        verbose_name = f"{app_label.upper()} Archaeological Fauna"
        verbose_name_plural = f"{app_label.upper()} Archaeological Fauna"


class Ceramic(Archaeology):
    type = models.CharField(null=True, blank=True, max_length=255)
    decorated = models.BooleanField(default=False)

    class Meta:
        verbose_name = f"{app_label.upper()} Ceramic"
        verbose_name_plural = f"{app_label.upper()} Ceramic"


class Geology(Occurrence):  # need to think about a possible subclass for Locality that is cave
    geology_type = models.CharField(null=True, blank=True, max_length=255)
    dip = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    strike = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    color = models.CharField(null=True, blank=True, max_length=255)
    texture = models.CharField(null=True, blank=True, max_length=255)

    class Meta:
        verbose_name = f"{app_label.upper()} Geology"
        verbose_name_plural = f"{app_label.upper()} Geology"


class Aggregate(Occurrence):
    screen_size = models.CharField(null=True, blank=True, max_length=255)
    burning = models.BooleanField(default=False)
    bone = models.BooleanField(default=False)
    microfauna = models.BooleanField(default=False)
    pebbles = models.BooleanField(default=False)
    smallplatforms = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    smalldebris = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    tinyplatforms = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    tinydebris = models.DecimalField(max_digits=38, decimal_places=8, null=True, blank=True)
    counts = models.IntegerField(null=True, blank=True)
    weights = models.IntegerField(null=True, blank=True)
    bull_find_remarks = models.TextField(null=True, blank=True, max_length=64000)

    class Meta:
        verbose_name = f"{app_label.upper()} Bulk Find"
        verbose_name_plural = f"{app_label.upper()} Bulk Finds"


# Media Classes
class Image(models.Model):
    occurrence = models.ForeignKey("Occurrence", related_name='psr_occurrences', on_delete=models.CASCADE)
    image = models.ImageField(upload_to="uploads/images", null=True, blank=True)
    description = models.TextField(null=True, blank=True)


class File(models.Model):
    occurrence = models.ForeignKey("Occurrence", on_delete=models.CASCADE)
    file = models.FileField(upload_to="uploads/files", null=True, blank=True)
    description = models.TextField(null=True, blank=True)
