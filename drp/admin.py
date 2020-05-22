from .models import *
from django.contrib import admin
import projects.admin
from import_export import resources
from import_export.fields import Field

drp_search_fields = ('id',
                     'catalog_number',
                     'basis_of_record',
                     'item_type',
                     'barcode',
                     'collection_code',
                     'item_scientific_name',
                     'item_description',
                     'stratigraphic_marker_found',
                     'stratigraphic_marker_likely',
                     'analytical_unit',
                     'finder',
                     'collector',)


###############
# Media Admin #
###############

class ImagesInline(admin.TabularInline):
    model = Image
    extra = 0
    readonly_fields = ("id",)


class FilesInline(admin.TabularInline):
    model = File
    extra = 0
    readonly_fields = ("id",)


#################
# Biology Admin #
#################

occurrence_fieldsets = (
    ('Curatorial', {
        'fields': [('barcode', 'catalog_number', 'id'),
                   ('date_recorded', 'year_collected', 'date_last_modified'),
                   ("collection_code", "paleolocality_number", "item_number", "item_part")]
    }),

    ('Occurrence Details', {
        'fields': [('basis_of_record', 'item_type', 'disposition', 'preparation_status'),
                   ('collecting_method', 'finder', 'collector', 'individual_count'),
                   ('item_description', 'item_scientific_name', 'image'),
                   ('problem', 'problem_comment'),
                   ('remarks',)],
    }),
    ('Provenience', {
        'fields': [('stratigraphic_marker_upper', 'distance_from_upper'),
                   ('stratigraphic_marker_lower', 'distance_from_lower'),
                   ('stratigraphic_marker_found', 'distance_from_found'),
                   ('stratigraphic_marker_likely', 'distance_from_likely'),
                   ('analytical_unit', 'analytical_unit_2', 'analytical_unit_3'),
                   ('in_situ', 'ranked'),
                   ('stratigraphic_member',),
                   ('locality',),
                   ('point_x', 'point_y'),
                   ('easting', 'northing',),
                   ('geom',)]
    }),
)

biology_fieldsets = (
    ('Taxonomy', {'fields': (('taxon',),)
                  }),
)


class BiologyInline(admin.TabularInline):
    model = Biology
    extra = 0
    readonly_fields = ("id",)
    fieldsets = biology_fieldsets


####################
# Occurrence Admin #
####################


###################
# Hydrology Admin #
###################

class HydrologyAdmin(admin.ModelAdmin):
    list_display = ("id", "size",)
    search_fields = ("id",)
    list_filter = ("size",)


class PaleoCoreLocalityAdmin(projects.admin.PaleoCoreLocalityAdminGoogle):
    list_display = ("collection_code", "paleolocality_number", "paleo_sublocality")
    list_filter = ("collection_code",)
    search_fields = ("paleolocality_number",)


class OccurrenceResource(resources.ModelResource):
    locality = Field(attribute='locality')

    class Meta:
        model = Occurrence
        fields = ('id', 'catalog_number', 'barcode')
        # fields = Occurrence().get_all_field_names()


class OccurrenceAdmin(projects.admin.PaleoCoreOccurrenceAdmin):
    """
    OccurrenceAdmin <- PaleoCoreOccurrenceAdmin <- BingGeoAdmin <- OSMGeoAdmin <- GeoModelAdmin
    """
    # change_list_template = 'admin/projects/projects_change_list.html'
    # actions = ['create_data_csv', 'change_xy', 'get_nearest_locality']
    resource_class = OccurrenceResource
    default_read_only_fields = ('id', 'point_x', 'point_y', 'easting', 'northing', 'date_last_modified')
    readonly_fields = default_read_only_fields + ('photo',)
    default_list_display = ('barcode', 'date_recorded', 'catalog_number', 'basis_of_record', 'item_type',
                            'collecting_method', 'collector', 'item_scientific_name', 'item_description',
                            'year_collected',
                            'in_situ', 'problem', 'disposition', 'easting', 'northing')
    list_display = default_list_display + ('thumbnail',)
    fieldsets = occurrence_fieldsets
    default_list_filter = ['basis_of_record', 'item_type', 'collector', 'problem', 'disposition']
    list_filter = default_list_filter + ['collection_code']
    search_fields = drp_search_fields

    # admin action to get nearest locality
    def get_nearest_locality(self, request, queryset):
        # first make sure we are only dealing with one point
        if queryset.count() > 1:
            self.message_user(request, "You can't get the nearest locality for multiple points at once. "
                                       "Please select a single point.", level='error')
            return
        # check if point is within any localities
        matching_localities = []
        for locality in Locality.objects.all():
            if locality.geom.contains(queryset[0].geom):
                matching_localities.append(str(locality.collection_code) + "-" + str(locality.paleolocality_number))
        if matching_localities:
            # warning to user if the point is within multiple localities
            if len(matching_localities) > 1:
                self.message_user(request, "The point falls within multiple localities (localities %s). "
                                           "Please consider redefining your localities so they don't overlap."
                                  % str(matching_localities).replace("[", ""))
                return
            # Message user with the nearest locality
            self.message_user(request, "The point is in %s" % (matching_localities[0]))

        # if the point is not within any locality, get the nearest locality
        distances = {}  # dictionary which will contain {<localityString>:key} entries
        for locality in Locality.objects.all():
            locality_name = str(locality.collection_code) + "-" + str(locality.paleolocality_number)
            #  how are units being dealt with here?
            locality_distance_from_point = locality.geom.distance(queryset[0].geom)
            distances.update({locality_name: locality_distance_from_point})
            closest_locality_key = min(distances, key=distances.get)
        self.message_user(request, "The point is %d meters from locality %s" % (distances.get(closest_locality_key),
                                                                                closest_locality_key))


class BiologyResource(resources.ModelResource):

    class Meta:
        model = Biology
        # fields = ('id', 'catalog_number', 'barcode', 'taxon__name', 'taxon__rank__name')
        fields = ('id', 'barcode', 'field_number', 'field_number_orig',
                  'catalog_number', 'collection_code', 'item_number', 'item_part',
                  'date_recorded', 'year_collected',
                  'basis_of_record', 'item_type',
                  'individual_count',
                  'item_description', 'side', 'element', 'element_modifier',
                  'item_scientific_name', 'taxon__name', 'taxon__rank__name', 'identification_qualifier__name',
                  'fauna_notes',
                  'problem', 'problem_comment',
                  'remarks',
                  'geom', 'georeference_remarks',

                  'collecting_method', 'related_catalog_items',
                  'collector', 'finder', 'disposition',  'preparation_status',
                  'stratigraphic_marker_upper', 'distance_from_upper',
                  'stratigraphic_marker_lower', 'distance_from_lower',
                  'stratigraphic_marker_found', 'distance_from_found',
                  'stratigraphic_marker_likely', 'distance_from_likely',
                  'stratigraphic_member',
                  'analytical_unit', 'analytical_unit_2', 'analytical_unit_3',
                  'in_situ', 'ranked', 'image',
                  'weathering', 'surface_modification',
                  'paleolocality_number', 'paleo_sublocality',
                  'locality_text', 'verbatim_coordinates', 'verbatim_coordinate_system',
                  'geodetic_datum', 'collection_remarks', 'stratigraphic_section',
                  'stratigraphic_height_in_meters', 'locality', 'occurrence_ptr',
                  'infraspecific_epithet', 'infraspecific_rank', 'author_year_of_scientific_name',
                  'nomenclatural_code', 'identified_by', 'date_identified', 'type_status', 'sex',
                  'life_stage', 'preparations', 'morphobank_number',
                  'attributes',
                  'tooth_upper_or_lower', 'tooth_number', 'tooth_type',
                  'um_tooth_row_length_mm', 'um_1_length_mm', 'um_1_width_mm',
                  'um_2_length_mm', 'um_2_width_mm', 'um_3_length_mm', 'um_3_width_mm',
                  'lm_tooth_row_length_mm', 'lm_1_length', 'lm_1_width', 'lm_2_length',
                  'lm_2_width', 'lm_3_length', 'lm_3_width',

                  'uli1', 'uli2', 'uli3', 'uli4', 'uli5', 'uri1', 'uri2', 'uri3', 'uri4',
                  'uri5', 'ulc', 'urc', 'ulp1', 'ulp2', 'ulp3', 'ulp4', 'urp1', 'urp2', 'urp3',
                  'urp4', 'ulm1', 'ulm2', 'ulm3', 'urm1', 'urm2', 'urm3', 'lli1', 'lli2', 'lli3',
                  'lli4', 'lli5', 'lri1', 'lri2', 'lri3', 'lri4', 'lri5', 'llc', 'lrc', 'llp1',
                  'llp2', 'llp3', 'llp4', 'lrp1', 'lrp2', 'lrp3', 'lrp4', 'llm1', 'llm2', 'llm3',
                  'lrm1', 'lrm2', 'lrm3',
                  )
        export_order =  fields


class BiologyAdmin(OccurrenceAdmin):
    model = Biology
    resource_class = BiologyResource
    fieldsets = occurrence_fieldsets + biology_fieldsets

##########################
# Register Admin Classes #
##########################

admin.site.register(Biology, BiologyAdmin)
admin.site.register(Hydrology, HydrologyAdmin)
admin.site.register(Locality, PaleoCoreLocalityAdmin)
admin.site.register(Occurrence, OccurrenceAdmin)
admin.site.register(Taxon, projects.admin.TaxonomyAdmin)

