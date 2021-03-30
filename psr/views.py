from django.shortcuts import render
import os
from fastkml import kml, Placemark, Folder, Document
from lxml import etree
from datetime import datetime
from django.contrib.gis.geos import GEOSGeometry
from pygeoif import geometry
from zipfile import ZipFile

# Django Libraries
from django.conf import settings
from django.views import generic
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib import messages
from dateutil.parser import parse
from django.core.files.base import ContentFile

# App Libraries
from .models import Occurrence, Biology, Archaeology, Geology, Taxon, IdentificationQualifier
from .forms import UploadKMLForm, DownloadKMLForm, ChangeXYForm, Occurrence2Biology, DeleteAllForm
from .utilities import html_escape, get_finds
from .ontologies import *  # import vocabularies and choice lists

# Create your views here.
class ImportKMZ(generic.FormView):
    template_name = 'admin/projects/import_kmz.html'
    form_class = UploadKMLForm
    context_object_name = 'upload'
    success_url = '../?last_import__exact=1'

    # Define a routine for importing Placemarks from a list of placemark elements

    def get_import_file(self):
        return self.request.FILES['kmlfileUpload']  # get a handle on the file

    def get_import_file_extension(self):
        import_file = self.get_import_file()
        import_file_name = import_file.name
        return import_file_name[import_file_name.rfind('.') + 1:]  # get the file extension

    def get_kmz_file(self):
        import_file = self.get_import_file()
        return ZipFile(import_file, 'r')

    def get_kml_file(self):
        """
        read the form and fetch the kml or kmz file
        :return: return a kml.KML() object
        """
        # need to parse the kml file more smartly to locate the first placemark and work from there.
        import_file = self.get_import_file()
        #kml_file_upload_name = kml_file_upload.name  # get the file name
        # kml_file_name = kml_file_upload_name[:kml_file_upload_name.rfind('.')]  # get the file name no extension
        kml_file_extension = self.get_import_file_extension()  # get the file extension

        kml_file_path = os.path.join(settings.MEDIA_ROOT)

        kml_file = kml.KML()
        if kml_file_extension == "kmz":
            kmz_file = self.get_kmz_file()
            kml_document = kmz_file.open('doc.kml', 'r').read()
        else:
            # read() loads entire file as one string
            kml_document = open(kml_file_path + "/" + import_file.name, 'r').read()

        kml_file.from_string(kml_document)  # pass contents of kml string to kml document instance for parsing
        return kml_file

    def import_placemarks(self, kml_placemark_list):
        """
        A procedure that reads a KML placemark list and saves the data into the django database
        :param kml_placemark_list:
        :return:
        """
        message_string = ''
        occurrence_count, archaeology_count, biology_count, geology_count = [0, 0, 0, 0]
        Occurrence.objects.all().update(last_import=False)  # Toggle off all last imports
        for o in kml_placemark_list:

            # Check to make sure that the object is a Placemark, filter out folder objects
            if type(o) is Placemark:
                # Step 1 - parse the xml and copy placemark attributes to a dictionary
                escaped_description = html_escape(o.description)  # escape &
                table = etree.fromstring(escaped_description)  # get the table element the data from the xml.
                attributes = table.xpath("//text()|//img")  # get all text values and image tags from xml string

                # Create a dictionary from the attribute list. The list has key value pairs as alternating
                # elements in the list, the line below takes the first and every other elements and adds them
                # as keys, then the second and every other element and adds them as values.
                # e.g.
                # attributes[0::2] = ["Basis of Record", "Time", "Item Type" ...]
                # attributes[1::2] = ["Collection", "May 27, 2017, 10:12 AM", "Faunal" ...]
                # zip creates a list of tuples  = [("Basis of Record", "Collection), ...]
                # which is converted to a dictionary.
                if len(attributes) % 2 == 0:  # attributes list should be even length
                    attributes_dict = dict(zip(attributes[0::2], attributes[1::2]))
                else:
                    raise KeyError
                # Step 2 - Create a new Occurrence object (or subtype)
                lgrp_occ = None
                # Determine the appropriate subtype and initialize
                item_type = attributes_dict.get("Item Type")
                occurrence_count += 1
                # variables imported from .ontologies
                if item_type in (ontologies.artifactual, "Artifactual", "Archeology", "Archaeological"):
                    lgrp_occ = Archaeology()
                    archaeology_count += 1
                elif item_type in (ontologies.faunal, "Fauna", "Floral", "Flora"):
                    lgrp_occ = Biology()
                    biology_count += 1
                elif item_type in (ontologies.geological, "Geology"):
                    lgrp_occ = Geology()
                    geology_count += 1

                # Step 3 - Copy attributes from dictionary to Occurrence object, validate as we go.
                # Improve by checking each field to see if it has a choice list. If so validate against choice
                # list.

                # Verbatim Data - save a verbatim copy of the original kml placemark coordinates and attributes.
                if o.geometry.wkt:
                    geom = ['geom', o.geometry.wkt]
                else:
                    geom = ['geom', 'No coordinates']
                lgrp_occ.verbatim_kml_data = attributes + geom

                # Validate Basis of Record
                if attributes_dict.get("Basis Of Record") in (ontologies.fossil_specimen, "Fossil", "Collection"):
                    # need to update basis_of_record vocab, change Fossil Specimen to Collection
                    lgrp_occ.basis_of_record = ontologies.fossil_specimen  # from .ontologies
                elif attributes_dict.get("Basis Of Record") in (ontologies.human_observation, "Observation"):
                    lgrp_occ.basis_of_record = ontologies.human_observation  # from .ontologies

                # Validate Item Type
                item_type = attributes_dict.get("Item Type")
                if item_type in (ontologies.artifactual, "Artifact", "Archeology", "Archaeological"):
                    lgrp_occ.item_type = ontologies.artifactual
                elif item_type in (ontologies.faunal, "Fauna"):
                    lgrp_occ.item_type = ontologies.faunal
                elif item_type in (ontologies.floral, "Flora"):
                    lgrp_occ.item_type = ontologies.floral
                elif item_type in (ontologies.geological, "Geology"):
                    lgrp_occ.item_type = ontologies.geological

                # Date Recorded
                error_string = ''
                try:
                    # parse the time
                    lgrp_occ.date_recorded = parse(attributes_dict.get("Time"))
                    # set the year collected form field number
                    lgrp_occ.year_collected = lgrp_occ.date_recorded.year
                except ValueError:
                    # If there's a problem getting the fieldnumber, use the current date time and set the
                    # problem flag to True.
                    lgrp_occ.date_recorded = datetime.now()
                    lgrp_occ.problem = True
                    try:
                        error_string = "Upload error, missing field number, using current date and time instead."
                        lgrp_occ.problem_comment = lgrp_occ.problem_comment + " " + error_string
                    except TypeError:
                        lgrp_occ.problem_comment = error_string

                # Process point, comes in as well known text string
                # Assuming point is in GCS WGS84 datum = SRID 4326
                #GEOSGeometry is generic, this is how to create the point
                #need to pull in the coordinates, and the correct SRID (need to ask about this)
                pnt = GEOSGeometry("POINT (" + str(o.geometry.x) + " " + str(o.geometry.y) + ")", 4326)  # WKT
                lgrp_occ.geom = pnt

                scientific_name_string = attributes_dict.get("Scientific Name")
                lgrp_occ.item_scientific_name = scientific_name_string
                # Next step only applies to Biology objects
                if lgrp_occ.item_scientific_name and lgrp_occ.__class__ is Biology:
                    match, match_count, match_list = lgrp_occ.match_taxon()
                    if match and match_count == 1:
                        lgrp_occ.taxon = match_list[0]

                lgrp_occ.item_description = attributes_dict.get("Description")
                # if lgrp_occ.item_description:
                #     match, match_count, match_list = match_element(lgrp_occ)
                #     if match and match_count ==1:
                #         lgrp_occ.element = lgrp_occ.item_description.lower()

                #######################
                # NON-REQUIRED FIELDS #
                #######################
                lgrp_occ.barcode = attributes_dict.get("Barcode")
                lgrp_occ.item_number = lgrp_occ.barcode
                lgrp_occ.collection_remarks = attributes_dict.get("Collecting Remarks")
                lgrp_occ.geology_remarks = attributes_dict.get("Geology Remarks")

                lgrp_occ.collecting_method = attributes_dict.get("Collection Method")
                finder_string = attributes_dict.get("Finder")
                lgrp_occ.finder = finder_string
                # import person object, validated against look up data in Person table
                # lgrp_occ.finder_person, created = Person.objects.get_or_create(name=finder_string)

                collector_string = attributes_dict.get("Collector")
                lgrp_occ.collector = collector_string
                # import person object, validated against look up data in Person table
                # lgrp_occ.collector_person, created = Person.objects.get_or_create(name=collector_string)

                lgrp_occ.individual_count = attributes_dict.get("Count")

                if attributes_dict.get("In Situ") in ('No', "NO", 'no'):
                    lgrp_occ.in_situ = False
                elif attributes_dict.get("In Situ") in ('Yes', "YES", 'yes'):
                    lgrp_occ.in_situ = True

                if attributes_dict.get("Ranked Unit") in ('No', "NO", 'no'):
                    lgrp_occ.ranked = False
                elif attributes_dict.get("Ranked Unit") in ('Yes', "YES", 'yes'):
                    lgrp_occ.ranked = True

                unit_found_string = attributes_dict.get("Unit Found")
                unit_likely_string = attributes_dict.get("Unit Likely")
                lgrp_occ.analytical_unit_found = unit_found_string
                lgrp_occ.analytical_unit_likely = unit_likely_string
                lgrp_occ.analytical_unit_1 = attributes_dict.get("Unit 1")
                lgrp_occ.analytical_unit_2 = attributes_dict.get("Unit 2")
                lgrp_occ.analytical_unit_3 = attributes_dict.get("Unit 3")

                # import statigraphy object, validate against look up data in Stratigraphy table
                # lgrp_occ.unit_found, created = StratigraphicUnit.objects.get_or_create(name=unit_found_string)
                # lgrp_occ.unit_likly, created = StratigraphicUnit.objects.get_or_create(name=unit_likely_string)

                # Save Occurrence before saving media. Need id to rename media files
                lgrp_occ.last_import = True
                lgrp_occ.save()

                # Save image
                kmz_file = self.get_kmz_file()
                if self.get_import_file_extension().lower() == "kmz":
                    # grab image names from XML
                    image_names = table.xpath("//img/@src")
                    # grab the name of the first image
                    # Future: add functionality to import multiple images
                    if image_names and len(image_names) == 1:  # This will break if image_names is None
                        image_name = image_names[0]
                        # Check that the image name is in the kmz file list
                        kmz_file.filenames = [f.orig_filename for f in kmz_file.filelist]
                        if image_name in kmz_file.filenames:
                            # etch the kmz image file object, this is a ZipInfo object not a File object
                            image_file_obj = next(f for f in kmz_file.filelist if f.orig_filename == image_name)
                            # fetch the upload directory from the model definition
                            upload_dir = Biology._meta.get_field('image').upload_to
                            # update image name to include upload path and occurrence id
                            # e.g. /uploads/images/lgrp/14775_188.jpg
                            new_image_name = os.path.join(upload_dir, str(lgrp_occ.id) + '_' + image_name)
                            # Save the image
                            lgrp_occ.image.save(new_image_name, ContentFile(kmz_file.read(image_file_obj)))

            elif type(o) is not Placemark:
                raise IOError("KML File is badly formatted")
        if occurrence_count == 1:
            message_string = '1 occurrence'
        if occurrence_count > 1:
            message_string = '{} occurrences'.format(occurrence_count)
        messages.add_message(self.request, messages.INFO,
                             'Successfully imported {} occurrences'.format(message_string))

