from ozg.xdatenfelder.parser import FIMParser
from ozg.xdatenfelder.fim_code_lists import FimCodeList

class TestFimParserInit:

    def test_open_file(self):
        # FIM Version 1
        parser = FIMParser(open("tests/fixtures/WaBeKa.xml").read())
        # FIM Version 2
        parser = FIMParser(open("tests/fixtures/BlaueKarte.xml").read())

    def test_header_v1(self):
        parser = FIMParser(open("tests/fixtures/WaBeKa.xml").read(), no_parsing=True)
        parser._parse_header(parser._parsed_xml.children[0].xdf_stammdatenschema)
        assert parser.id == "S00000036"
        assert parser.name == "Waffenbesitzkarte (WBK grün)"
        assert parser.output_name is None
        assert parser.input_name == "Waffenbesitzkarte nach § 10 Absatz 1 WaffG"
        assert parser.description == "Urkunde zur Bestätigung der Erlaubnis zum Erwerb und Besitz von Waffen und Munition nach § 10 Absatz 1 WaffG"
        assert parser.legal_definition == "Entspricht der Allgemeine Verwaltungsvorschrift zu Vordrucken des Waffengesetzes (WaffVordruckVwV) vom 30. Mai 2012 Anlage 1"
        assert parser.internal_definition == "Urkunde zur Bestätigung der Erlaubnis zum Erwerb und Besitz von Waffen und Munition nach § 10 Absatz 1 WaffG"


    def test_header_v2(self):
        parser = FIMParser(open("tests/fixtures/BlaueKarte.xml").read(), no_parsing=True)
        parser._parse_header(parser._parsed_xml.children[0].xdf_stammdatenschema)
        assert parser.id == "S00000121"
        assert parser.name == "Antrag Blaue Karte EU"
        assert parser.output_name is None
        assert parser.input_name == "Antrag auf Blaue Karte EU"
        assert parser.description is None
        assert parser.legal_definition == "§ 19a AufenthG"
        assert parser.internal_definition is None

    def test_form_parser_v1(self):
        parser = FIMParser(open("tests/fixtures/WaBeKa.xml").read())

        parser._parse_structure()
        for i in parser.form:
            print(i)
        print(parser.to_json)



    def test_form_parser_v2(self):
        parser = FIMParser(open("tests/fixtures/BlaueKarte.xml", ).read())
        parser._parse_structure()
        for i in parser.form:
            print(i)

        print(parser.to_json)

    def test_form_section_parser_v2(self):
        parser = FIMParser("https://gist.githubusercontent.com/LilithWittmann/d8a7bb6c64a25e1dd1a0989d9042b856/raw/3742311b29388474464b6bab0833cffaf5b56d2c/G60000086V1.0.xml")
        print(parser.to_json)

    def test_from_url(self):
        parser = FIMParser("https://raw.githubusercontent.com/LilithWittmann/ozg/master/tests/fixtures/BlaueKarte.xml")
        print(parser.to_json)


class TestFimCodeLists:
    
    def test_init(self):
        FimCodeList("urn:de:bund:destatis:bevoelkerungsstatistik:schluessel:staat")
        FimCodeList("urn:de:xoev:codeliste:erreichbarkeit")
