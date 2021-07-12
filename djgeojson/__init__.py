#: Module version, as defined in PEP-0396.
# from pkg_resources import DistributionNotFound
#
# pkg_resources = __import__('pkg_resources')
# try:
#     distribution = pkg_resources.get_distribution('django-geojson')
#     __version__ = distribution.version
# except (AttributeError, DistributionNotFound):
#     __version__ = 'unknown'
#     import warnings
#     warnings.warn('No distribution found.')

# Simple version info. pkg_resources is blacklisted!!
VERSION = (3, 2, 0)
__version__ = '.'.join(map(str, VERSION))
GEOJSON_DEFAULT_SRID = 4326
