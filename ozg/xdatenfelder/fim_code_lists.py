import untangle
import requests

class FimCodeList(object):
    def __init__(self, urn):
        """
        searches for the urn in xrepository and parses the latest version
        :param urn: the urn to search for
        """
        print(urn)
        try:
            self.version_xml = untangle.parse(f"https://www.xrepository.de/api/codeliste/{urn}/gueltigeVersion")
            self._dataset = []
            latest_uri = self.version_xml.dat_VersionCodeliste.dat_kennung.cdata
            #self.xml = untangle.parse(f"https://www.xrepository.de/api/version_codeliste//genericode")
            result = requests.get(f"https://www.xrepository.de/api/version_codeliste/{latest_uri}/genericode-daten")
            for item in result.json()["daten"]:
                self._dataset.append((item["zelle"][0]["wert"], item["zelle"][1]["wert"]))
        except Exception as e:
            print(f"https://www.xrepository.de/api/codeliste/{urn}/gueltigeVersion")
            print(f"unable to find {urn} in xrepository")
            self._dataset = [(None, f"unable to find {urn} in xrepository")]


    @property
    def dataset(self):
        return self._dataset