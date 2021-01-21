import os
import sys
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'venusian==1.2.0',
    'ott.utils',

    'gtfsdb',
    'geoalchemy2',
    'sqlalchemy',
    'zope.sqlalchemy',
    'psycopg2-binary',

    'pyramid',
    'pyramid_tm',
    'pyramid_exclog',
    'waitress==1.4.3',
]

extras_require = dict(
    dev=[],
)


setup(
    name='ott.trafficdb',
    version='0.1.0',
    description='Open Transit Tools - traffic database for speed and congestion data',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
    ],
    author="Open Transit Tools",
    author_email="info@opentransittools.org",
    dependency_links=[
        'git+https://github.com/OpenTransitTools/gtfsdb.git#egg=gtfsdb-1.0.0',
        'git+https://github.com/OpenTransitTools/utils.git#egg=ott.utils-0.1.0',
    ],
    license="Mozilla-derived (http://opentransittools.com)",
    url='http://opentransittools.com',
    keywords='ott, osm, otp, gtfs, vector, tiles, maps, transit',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    extras_require=extras_require,
    tests_require=requires,
    test_suite="ott.trafficdb.tests",
    entry_points="""
        [paste.app_factory]
        main = ott.trafficdb.pyramid.app:main

        [console_scripts]
        inrix_auth_token = ott.trafficdb.control.inrix.get_token:main
        inrix_segment_data = ott.trafficdb.control.inrix.segment_data:main
        inrix_speed_data = ott.trafficdb.control.inrix.speed_data:main

        load_all = ott.trafficdb.control.loader:load_all
        load_gtfsdb = ott.trafficdb.control.loader:load_gtfsdb
        load_stop_segments = ott.trafficdb.control.loader:load_stop_segments
        
        load_speed_data = ott.trafficdb.control.speeds_to_segments:main
        match_segments = ott.trafficdb.control.conflate.match_segments:main

        publisher = ott.trafficdb.view.publisher:main
        printer = ott.trafficdb.view.printer:main
        view_map = ott.trafficdb.view.geojson:main
        bbox = ott.trafficdb.view.bbox:main
    """,
)
