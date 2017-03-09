# coding: utf-8

"""Luigi tasks downloading XML files and shapefiles from the Data Grand Lyon
Website https://data.grandlyon.com

You can get the names of available data after downloading the two "capabilities"
XML files from the WFS service.
"""

import os

from lxml import etree

import requests

import luigi
from luigi.format import UTF8, MixedUnicodeBytes

WFS_RDATA_URL = "https://download.data.grandlyon.com/wfs/rdata"
WFS_GRANDLYON_URL = "https://download.data.grandlyon.com/wfs/grandlyon"
DEFAULT_PARAMS = {'SERVICE': 'WFS',
                  'VERSION': '2.0.0',
                  'request': 'GetFeature'}
DATADIR = 'datarepo'


def layers(tree):
    """Get layer names from the XML Capabilities elements
    """
    ns = '{http://www.opengis.net/wms}'
    elements = tree.find(ns+'Capability').find(ns+'Layer').findall(ns+'Layer')
    g = ((x.get('queryable'), x.find(ns+'Name').text) for x in elements)
    return sorted(name for q,name in g if int(q))


def params_factory(projection, output_format, dataname):
    """return a new dict for HTTP query params

    Used for the wfs http query to get some data.
    """
    res = {"SRSNAME": 'EPSG:' + projection,
           "outputFormat": output_format,
           "typename": dataname}
    res.update(DEFAULT_PARAMS)
    return res


def get_all_typenames(source):
    """Get all layer names (i.e. typename) from a specific wfs source: rdata or
    grandlyon.
    """
    fname = os.path.join(DATADIR, '{}-layers.txt'.format(source))
    if source == 'rdata':
        url = WFS_RDATA_URL
    elif source == 'grandlyon':
        url = WFS_GRANDLYON_URL
    else:
        raise Exception("source {} not supported".format(source))
    url = 'https://download.data.grandlyon.com/wms/{}?SERVICE=WMS&REQUEST=GetCapabilities'.format(source)
    if os.path.isfile(fname):
        return open(fname).read().split()
    return layers(etree.fromstring(requests.get(url).content))


class ServiceCapabilitiesTask(luigi.Task):
    """Task to download XML files with some metadata
    """
    source = luigi.Parameter() # can accept rdata and grandlyon
    path = os.path.join(DATADIR, '{source}-capabilities.xml')

    def output(self):
        return luigi.LocalTarget(self.path.format(source=self.source), format=UTF8)

    def run(self):
        url = 'https://download.data.grandlyon.com/wms/{}?SERVICE=WMS&REQUEST=GetCapabilities'.format(self.source)
        resp = requests.get(url)
        with self.output().open("w") as fobj:
            fobj.write(resp.content.decode('utf-8'))


class ExtractLayersTask(luigi.Task):
    """Task to extract layer names (i.e. typename) from a XML file.
    """
    source = luigi.Parameter()
    path = os.path.join(DATADIR, "{source}-layers.txt")

    def output(self):
        return luigi.LocalTarget(self.path.format(source=self.source), format=UTF8)

    def requires(self):
        return ServiceCapabilitiesTask(self.source)

    def run(self):
        with self.input().open() as fobj:
            tree = etree.parse(fobj)
        with self.output().open('w') as fobj:
            fobj.write("\n".join(layers(tree)))


class ExtractAllLayers(luigi.Task):
    """Extract all layer names for the rdata and grandlyon wfs data sources
    """
    def requires(self):
        yield ExtractLayersTask('rdata')
        yield ExtractLayersTask('grandlyon')


class ShapefilesTask(luigi.Task):
    """Task to download a zip files which includes the shapefile

    Need the source: rdata or grandlyon and the layer name (i.e. typename).
    """
    source = luigi.Parameter()
    typename = luigi.Parameter()
    path = os.path.join(DATADIR , '{typename}.zip')
    srid = 4326

    def requires(self):
        return ExtractLayersTask(self.source)

    def output(self):
        return luigi.LocalTarget(self.path.format(typename=self.typename),
                                 format=MixedUnicodeBytes)

    def run(self):
        if self.source == 'rdata':
            url = WFS_RDATA_URL
        elif self.source == 'grandlyon':
            url = WFS_GRANDLYON_URL
        else:
            raise Exception("source {} not supported".format(self.source))
        params = params_factory(str(self.srid), 'SHAPEZIP', self.typename)
        with self.output().open('w') as fobj:
            resp = requests.get(url, params=params)
            resp.raise_for_status()
            fobj.write(resp.content)


class WrapperShapeTask(luigi.Task):
    """A wrapper to download all zip files (including the shapefile) for several
    layers and a specific source: rdata or grandlyon.
    """
    source = luigi.Parameter()

    def requires(self):
        yield ExtractLayersTask(self.source)
        for typename in get_all_typenames(self.source):
            yield ShapefilesTask(self.source, typename)


if __name__ == '__main__':
    t = 'pvo_patrimoine_voirie.pvoparking'
    t = 'pvo_patrimoine_voirie.pvostationvelov'
    p = params_factory('4326', 'SHAPEZIP', t)
    p2 = params_factory('3946', 'SHAPEZIP', t)
    # resp = requests.get(WFS_URL, params=p)
