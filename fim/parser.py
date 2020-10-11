import abc
import untangle
from typing import List, Any, Union
from abc import ABC


class FIMParserError(Exception):
    pass


class FIMHeaderMixin(object):

    def _parse_header(self, element):
        # required fields by FIM standard
        base_schema = element
        if self._version == FIMParser.FIM_VERSION_2:
            self._id = base_schema.xdf_identifikation.xdf_id.cdata
        elif self._version == FIMParser.FIM_VERSION_1:
            self._id = base_schema.xdf_id.cdata
        self._name = base_schema.xdf_name.cdata
        self._description = base_schema.xdf_beschreibung.cdata
        self._input_name = base_schema.xdf_bezeichnungEingabe.cdata
        self._internal_definition = base_schema.xdf_definition.cdata
        self._relation = base_schema.xdf_bezug.cdata

        # optional fields by fim standard
        if len(element.get_elements("xdf_bezeichnungAusgabe")) > 0:
            self._output_name = base_schema.xdf_bezeichnungAusgabe
        else:
            self._output_name = None

        # TODO: parse status gueltigAb gueltigBis fachlicherErsteller versionshinweis freigabedatum veroeffentlichungsdatum
        # in FimParser itself

    @property
    def id(self) -> str:
        """
        :return: the FIM id of the described process as a string
        """
        return self._id

    @property
    def name(self) -> str:
        """
        :return: the internal name of the process
        """
        return self._name

    @property
    def input_name(self) -> str:
        """
        :return: the name of the process for somebody using it for data entry
        """
        return self._input_name

    @property
    def output_name(self) -> str:
        """
        :return: the name of the process for somebody using the data entered by someone else (optional field)
        """
        return self._output_name

    @property
    def description(self) -> str:
        """
        :return: the description of process as a string
        """
        return self._description

    @property
    def internal_definition(self) -> str:
        """
        :return: the internal fim definition/documentation for the process
        """
        return self._internal_definition

    @property
    def relation(self) -> str:
        """
        :return: relation to other standards and laws
        """
        return self._relation





class FIMElement(ABC):
    def __init__(self, definition, fim_parser):
        """
        the representation of a fim structure
        :param definition: the fim structure definition as untangle xml object
        :param fim_parser: the current fim parser instance
        """
        self._definition = definition
        self._parsed_xml = definition
        self._fim_parser = fim_parser
        self._version = fim_parser._version
        self._parse()

    @abc.abstractmethod
    def _parse(self):
        pass



class FIMStructure(FIMElement):

    MAX_ITEMS_UNLIMITED = 9999

    def _parse(self):
        min_items, max_items = str(self._definition.xdf_anzahl.cdata).split(":")

        self._min_items = int(min_items)
        self._max_items = int(max_items) if max_items != "*" else self.MAX_ITEMS_UNLIMITED

        if len(self._definition.get_elements("xdf_bezug")) > 0:
            self._related_field = str(self._definition.xdf_bezug.cdata)
        else:
            self._related_field = None

        if len(self._definition.xdf_enthaelt.get_elements("xdf_datenfeld")) == 1:
            self._contains = FIMField(self._definition.xdf_enthaelt.xdf_datenfeld, self._fim_parser)
        elif len(self._definition.xdf_enthaelt.get_elements("xdf_datenfeldgruppe")) == 1:
            self._contains = FIMFieldGroup(self._definition.xdf_enthaelt.xdf_datenfeldgruppe, self._fim_parser)
        else:
            raise FIMParserError("FIMStructure contains unrecognised element")


    def __str__(self):
        return f"{str(self.contains)} - ({self.min_items}:{self.max_items})"

    @property
    def min_items(self) -> int:
        """
        integer min number of occurences of this item in form between 0 and n
        """
        return self._min_items


    @property
    def max_items(self) -> Union[str, int]:
        """
        integer max number of occurences of this item in form between 0 and unlimited
        """
        return self._max_items

    @property
    def related_field(self) -> str:
        """ name of related field or standard (e.g. XÖV-Kernkoponente.NameOrganisation.kurzbezeichnung)"""
        return self._related_field

    @property
    def contains(self):
        """
        content of the structure
        """
        return self._contains

    @property
    def id(self):
        return self.contains.id

    def to_json(self):
        if self.max_items < 2:
            return self._contains.to_json()
        else:
            return {
            "minItems": self.min_items,
            "maxItems": self.max_items,
            "type": "array",
            "items": self.contains.to_json()
            }


class FIMField(FIMElement, FIMHeaderMixin):
    def _parse(self):
        self._parse_header(self._definition)

        self._field_type = self._definition.xdf_feldart.code.cdata
        self._data_type = self._definition.xdf_datentyp.code.cdata
        self._validation_details = self._definition.xdf_praezisierung.cdata
        self._default_content = self._definition.xdf_inhalt.cdata

        self._reference_value_uri = None
        if self._field_type == "select":
            if self._version == FIMParser.FIM_VERSION_1:
                if self._definition.get_elements("xdf_codeliste") == 1:
                    self._reference_value_uri = self._definition.xdf_codeliste.xdf_kennung.cdata
            elif self._version == FIMParser.FIM_VERSION_2:
                if self._definition.get_elements("xdf_codelisteReferenz") == 1:
                    self._reference_value_uri = self._definition.xdf_codelisteReferenz.xdf_genericodeIdentification.xdf_canonicalIdentification.cdata

    @property
    def field_type(self):
        return self._field_type

    @property
    def data_type(self):
        """
        text Text
        date Datum
        bool Wahrheitswert
        num Nummer
        num_int Ganzzahl
        num_currency Geldbetrag
        file Anlage (Datei)
        obj Objekt (Blob)
        :return:
        """
        return self._data_type


    def to_json(self):
        mapping = {
        "text": {"type": "string"},
        "date": {"type": "string", "format": "date"},
        "bool": {"type": "boolean"},
        "num": {"type": "number"},
        "num_int": {"type": "integer"},
        "num_currency": {"type": "number"},
        "file": {"type": "string", "format": "data-url"},
        "obj": {"type": "string", "format": "data-url"},
        }
        if self.field_type == "input":
            a = mapping[self.data_type]
            a["title"] = self.name
            a["description"] = self.description
            return a
        else:
            return {
                "title": self.name,
                "description": self.description,
                "type": "string"
            }

    def __str__(self):
        return f'{self.name}[{self.field_type}, {self.data_type}, {self._reference_value_uri}]'

class FIMFieldGroup(FIMElement, FIMHeaderMixin):
    def _parse(self):
        self._parse_header(self._definition)

        self._fields = []
        for element in self._definition.xdf_struktur:
            self._fields.append(FIMStructure(element, self))

    @property
    def fields(self):
        return self._fields



    def to_json(self):
        base = {
            "title": self.name,
            "description": self.description,
            "type": "object",
            "properties": {}

            }
        for i in self.fields:
            base["properties"][i.contains.name] = i.to_json()

        return base

    def __str__(self):
        return f'{self.name} [{", ".join([str(e) for e in self.fields])}]'


class FIMParser(FIMHeaderMixin):
    FIM_VERSION_1 = "urn:xoev-de:fim:standard:xdatenfelder_1"
    FIM_VERSION_2 = "urn:xoev-de:fim:standard:xdatenfelder_2"

    FIM_VERSION_MAPPING = {
        "urn:xoev-de:fim:standard:xdatenfelder_1": FIM_VERSION_1,
        "urn:xoev-de:fim:standard:xdatenfelder_2": FIM_VERSION_2,
    }

    def __init__(self, fim_xml: str, override_version_check: str = None, no_parsing: bool = False):
        """
        init a new FIMParser
        :param fim_xml: xml of the fim file you want to parse as a string, a url or a filename
        :param override_version_check: override the fim version manually (see SUPPORTED_FIM_VERSIONS for options)
        :param no_parsing: used for tests
        """
        self._xml = fim_xml
        self._parsed_xml = untangle.parse(fim_xml)
        if not override_version_check:
            self._check_fim_version()
        else:
            self._version = override_version_check

        if not no_parsing:
            self._parse_header(self._parsed_xml.children[0].xdf_stammdatenschema)
            self._parse_structure()

    def _check_fim_version(self):
        """
        checks if the FIM file uses a supported fim version
        :raises: FIMParserError if FIM version is not in SUPPORTED_FIM_VERSIONS
        """
        if self.parsed_xml.children[0].get_attribute("xmlns:xdf") not in self.FIM_VERSION_MAPPING.values():
            raise FIMParserError("FIM File is in an unsupported version")
        self._version = self.FIM_VERSION_MAPPING[self.parsed_xml.children[0].get_attribute("xmlns:xdf")]


    def _parse_structure(self):
        """
        parse the form structure itself
        :return:
        """
        self._form = []
        for element in self.parsed_xml.children[0].xdf_stammdatenschema.xdf_struktur:
            self.form.append(FIMStructure(element, self))

    @property
    def xml(self) -> str:
        """get the xml provided as string"""
        return self._xml

    @property
    def parsed_xml(self):
        """the provided xml parsed by untangle"""
        return self._parsed_xml

    @property
    def legal_definition(self) -> str:
        """
        :return: the internal legal fim definition/documentation for the process
        """
        return self._relation

    @property
    def form(self) -> List:
        """
        :return: the FIMParser representation of the form
        """
        return self._form


    @property
    def to_json(self):
        base = {
            "title": self.input_name,
            "description": self.description,
            "type": "object",
            "properties": {}

            }
        for i in self.form:
            base["properties"][i.id] = i.to_json()

        return base