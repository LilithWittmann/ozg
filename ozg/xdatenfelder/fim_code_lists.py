import untangle
import requests


class FimCodeList(object):
    def __init__(self, urn = None, file_name = None):
        """
        searches for the urn in xrepository and parses the latest version
        :param urn: the urn to search for
        """

        if file_name:
            try:
                self._parse_from_file(file_name)
            except Exception as e:
                print(f"unable to load codelist from file: {file_name}")
                raise e
        elif urn:
            try:
                self._parse_from_xrepository(urn)
            except Exception as e:
                print(f"https://www.xrepository.de/api/codeliste/{urn}/gueltigeVersion")
                print(f"unable to find {urn} in xrepository")
                self._dataset = [(None, f"unable to find {urn} in xrepository")]
                raise e
        else:
            raise AttributeError("no urn and no file_name provided")

    def _parse_from_xrepository(self, urn):
        # try to find the current codelist for the urn
        if urn == 'urn:xoev-de:xunternehmen:codeliste:ihk':
            latest_uri = 'urn:xoev-de:xunternehmen:codeliste:ihk_2021-02-15'
        else:
            self.version_xml = untangle.parse(f"https://www.xrepository.de/api/codeliste/{urn}/gueltigeVersion")
            latest_uri = self.version_xml.dat_VersionCodeliste.dat_kennung.cdata
        self._dataset = []
        # download the codelist and parse (currently always the second value) as a list of enums
        print(f"Downloading https://www.xrepository.de/api/version_codeliste/{latest_uri}/json...")
        result = requests.get(f"https://www.xrepository.de/api/version_codeliste/{latest_uri}/json")
        for item in result.json()["daten"]:
            self._dataset.append((item[0], item[1]))

    def _parse_from_file(self, file_name):
        # parse codelist from file
        print(f"Parsing codelist from file: {file_name}...")
        self._parsed_xml = untangle.parse(file_name)
        self._dataset = []
        if not self._parsed_xml.CodeList.SimpleCodeList.Row:
            raise ValueError(f"cannot parse codelist from file: {file_name}")
        for row in self._parsed_xml.CodeList.SimpleCodeList.Row:
            self._dataset.append((row.Value[0].SimpleValue.cdata, row.Value[1].SimpleValue.cdata))



    @property
    def dataset(self):
        """
        :return: a list of key/value tuples
        """
        return self._dataset
