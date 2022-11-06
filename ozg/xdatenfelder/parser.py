import abc
import json
import untangle
from typing import List, Any, Union
from abc import ABC

from .fim_code_lists import FimCodeList


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
        self._description = self.set_none_if_empty(base_schema.xdf_beschreibung.cdata)
        self._input_name = self.set_none_if_empty(base_schema.xdf_bezeichnungEingabe.cdata)
        self._internal_definition = self.set_none_if_empty(base_schema.xdf_definition.cdata)
        self._relation = self.set_none_if_empty(base_schema.xdf_bezug.cdata)

        # optional fields by fim standard
        if len(element.get_elements("xdf_bezeichnungAusgabe")) > 0:
            self._output_name = base_schema.xdf_bezeichnungAusgabe
        else:
            self._output_name = None

        # TODO: parse status gueltigAb gueltigBis fachlicherErsteller versionshinweis freigabedatum veroeffentlichungsdatum
        # in FimParser itself

    EMPTY_VALUES = ["", ".", "-"]

    def set_none_if_empty(self, value):
        """
        XDatenfelder implementations are using a bunch of different ways to indicate that a field is empty
        we try to clean them if the empty value is not actually None so that there are no weired letters on the rendered
        forms
        :param value: the value that should be checked
        :return:
        """
        if value in self.EMPTY_VALUES:
            return None

        return value

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
        elif len(self._definition.get_elements("xdf_datenfeldgruppe")) == 1:
            self._contains = FIMFieldGroup(self._definition.xdf_datenfeldgruppe, self._fim_parser)
        else:
            raise FIMParserError("FIMStructure contains unrecognised element")

    def __str__(self):
        return f"{str(self.contains)} ({self.min_items}:{self.max_items})"

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

    @property
    def is_required(self):
        if self.min_items > 0:
            return True
        return False

    def to_json(self, defs, level=None):
        if isinstance(self.contains, FIMField):
            fim_structure_schema = self.contains.to_json()
        elif isinstance(self.contains, FIMFieldGroup):
            fim_structure_schema, defs = self.contains.to_json(defs)
        else:
            raise RuntimeError("Unknown element inside FIMStructure")

        # add containing element to defs
        if self.contains.id not in defs:
            defs[self.contains.id] = fim_structure_schema

        if self.max_items == 1 and self.min_items <= 1:
            # this FIMStructure consists of only one (optional or required) instance of the contained element
            # return only reference to defs
            element = {"$ref": "#/$defs/" + self.contains.id}
        else:
            # this FIMStrucutre consists of more than one instance of the contained element
            # return an array of elements of the contained element type
            element = {
                "minItems": self.min_items,
                "maxItems": self.max_items,
                "title": f"Liste von {self.contains.input_name}" if self.max_items > 1 else self.contains.input_name,
                "type": "array",
                "items": {"$ref": "#/$defs/" + self.contains.id}
            }

        if level == 0:
            element = {
                "title": self.contains.input_name,
                "description": self.contains.description,
                "type": "object",
                "properties": {
                    self.id: element
                }
            }

        return element, defs


class FIMField(FIMElement, FIMHeaderMixin):
    def _parse(self):
        self._parse_header(self._definition)

        self._field_type = self._definition.xdf_feldart.code.cdata
        self._data_type = self._definition.xdf_datentyp.code.cdata
        self._validation_details = self._definition.xdf_praezisierung.cdata
        self._default_value = self.set_none_if_empty(self._definition.xdf_inhalt.cdata)
        self._input_hint = self.set_none_if_empty(self._definition.xdf_hilfetextEingabe.cdata)
        self._output_hint = self.set_none_if_empty(self._definition.xdf_hilfetextAusgabe.cdata)

        self._reference_value_uri = None
        if self._field_type == "select":
            if self._version == FIMParser.FIM_VERSION_1:
                if len(self._definition.get_elements("xdf_codeliste")) == 1:
                    self._reference_value_uri = self._definition.xdf_codeliste.xdf_kennung.cdata
            elif self._version == FIMParser.FIM_VERSION_2:
                if len(self._definition.get_elements("xdf_codelisteReferenz")) == 1:
                    self._reference_value_uri = self._definition.xdf_codelisteReferenz.xdf_genericodeIdentification.xdf_canonicalIdentification.cdata
                    print(self._reference_value_uri)

    ELEMENT_TYPE = "field"

    @property
    def field_type(self):
        """xDatenfelder field_type"""
        return self._field_type

    @property
    def input_hint(self):
        return self._input_hint

    @property
    def output_hint(self):
        return self._output_hint

    @property
    def default_value(self):
        return self._default_value

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
        :return: one of th xDatenfelder data types
        """
        return self._data_type

    def to_json(self, level=None):
        """
        :return: json schema representation of the field
        """
        mapping = {
            "text": {"type": "string"},
            "date": {"type": "string", "format": "date"},
            "bool": {"type": "boolean"},
            "num": {"type": "number"},
            "num_int": {"type": "integer"},
            "num_currency": {"type": "number"},
            "file": {"type": "string", "x-display": "file"},
            "obj": {"type": "string", "x-display": "data-url"},
        }

        if self.field_type == "input":
            a = mapping[self.data_type]
            a["title"] = self.input_name if self.input_name else self.name
            if self._input_hint:
                a["description"] = self._input_hint

            if self._default_value:
                a["default"] = self.default_value

            if self._validation_details:
                try:
                    validation = json.loads(self._validation_details)
                    if "minLength" in validation:
                        a["minLength"] = int(validation["minLength"])
                    if "maxLength" in validation:
                        a["maxLength"] = int(validation["maxLength"])
                    if "pattern" in validation:
                        a["pattern"] = validation["pattern"]
                except ValueError:
                    pass
            return a
        elif self.field_type == "select":
            fim_code_list = FimCodeList(self._reference_value_uri)
            any_of = []
            for choice in fim_code_list.dataset:
                any_of.append(choice[1])

            schema = {
                "title": self.input_name if self.input_name else self.name,
                "type": "string",
                "enum": any_of,
            }

            if self._input_hint:
                schema["description"] = self._input_hint

            return schema
        elif self.field_type == "label":
            return {
                "title": self.input_name if self.input_name else self.name,
                "description": self.default_value,
                "type": "string",
                "x-display": "label"
            }
        else:
            schema = {
                "title": self.input_name if self.input_name else self.name,
                "type": "string"
            }

            if self._input_hint:
                schema["description"] = self._input_hint

            return schema

    def __str__(self):
        return f'FIMField[name = {self.name}, field_type = {self.field_type}, data_type = {self.data_type}, reference_value_uri = {self._reference_value_uri}]'


class FIMFieldGroup(FIMElement, FIMHeaderMixin):
    def _parse(self):
        self._parse_header(self._definition)

        self._fields = []
        for element in self._definition.xdf_struktur:
            self._fields.append(FIMStructure(element, self))

    @property
    def fields(self):
        """:returns a list of FIMFields/FIMFieldGroups"""
        return self._fields

    ELEMENT_TYPE = "field_group"

    def to_json(self, defs, level=None):
        """
        :return: a json-schema object
        """
        base = {
            "title": self.name,
            "type": "object",
            "properties": {},
            "required": []
        }

        if self.description:
            base["description"] = self.description

        last_element = None
        for fim_structure in self.fields:
            base["properties"][fim_structure.contains.id], defs = fim_structure.to_json(defs)

            if fim_structure.is_required:
                base["required"].append(fim_structure.contains.id)

        return base, defs

    def __str__(self):
        newline = '\n'
        return f'FIMGroup[name = {self.name}, fields = [\n- {(newline+"- ").join([str(e) for e in self.fields])}\n]]'


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
            if len(self.parsed_xml.children[0].get_elements("xdf_stammdatenschema")) > 0:
                self._parse_header(self._parsed_xml.children[0].xdf_stammdatenschema)
            else:
                self._name = "Data Fields"
                self._description = None
                self._input_name = None
                self._internal_definition = None
                self._relation = None

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
        if len(self.parsed_xml.children[0].get_elements("xdf_stammdatenschema")) > 0:
            for element in self.parsed_xml.children[0].xdf_stammdatenschema.xdf_struktur:
                self.form.append(FIMStructure(element, self))
        else:
            self.form.append(FIMFieldGroup( self.parsed_xml.children[0].xdf_datenfeldgruppe, self))

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
    def to_json(self, level=None):
        # create json schema skeleton
        json_schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": self.input_name,
            "description": self.description,
            "type": "object",
            "properties": {},
            "x-display": "expansion-panels"
        }

        # definitions
        defs = {}

        # add root properties and update fill definitions
        for fim_structure in self.form:
            json_schema["properties"][fim_structure.id], defs = fim_structure.to_json(defs)

        json_schema['$defs'] = defs

        return json_schema
