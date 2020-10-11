from fim.parser import FIMParser

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
        assert parser.description == ""
        assert parser.legal_definition == "§ 19a AufenthG"
        assert parser.internal_definition == ""

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

    def test_from_url(self):
        parser = FIMParser("https://fimportal.de/detail?tx_fimportalcatalog_fimsearch%5Baction%5D=download&tx_fimportalcatalog_fimsearch%5Bcontroller%5D=CatalogEntry&tx_fimportalcatalog_fimsearch%5BdocumentIndex%5D=1&tx_fimportalcatalog_fimsearch%5Bid%5D=DS00000123&cHash=0760c920aa906ab17ecef77281781f09")
        print(parser.to_json)
