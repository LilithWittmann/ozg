import untangle
import requests


class FimCodeList(object):
    def __init__(self, urn):
        """
        searches for the urn in xrepository and parses the latest version
        :param urn: the urn to search for
        """

        if not urn:
            self._dataset = [(None, f"no urn provided")]

        try:
            # try to find the current codelist for the urn
            self.version_xml = untangle.parse(f"https://www.xrepository.de/api/codeliste/{urn}/gueltigeVersion")
            self._dataset = []
            latest_uri = self.version_xml.dat_VersionCodeliste.dat_kennung.cdata
            # download the codelist and parse (currently always the second value) as a list of enums
            result = requests.get(f"https://www.xrepository.de/api/version_codeliste/{latest_uri}/genericode-daten")
            for item in result.json()["daten"]:
                self._dataset.append((item["zelle"][0]["wert"], item["zelle"][1]["wert"]))
        except Exception as e:
            print(f"https://www.xrepository.de/api/codeliste/{urn}/gueltigeVersion")
            print(f"unable to find {urn} in xrepository")
            self._dataset = [(None, f"unable to find {urn} in xrepository")]

    @property
    def dataset(self):
        """
        :return: a list of key/value tuples
        """
        return self._dataset
