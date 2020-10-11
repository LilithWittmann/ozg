# 🥔 Onlinezugangsgesetz Tools 🥔 
---
Currently this package only includes a parser and converter to jsonschema-forms for the [xDatenfelder](https://www.xrepository.de/api/xrepository/urn:xoev-de:fim:standard:xdatenfelder_2.0:dokument:XDatenfelder_Spezifikation) format.

## Installation
 
```
pip install ozg
```

```python
from ozg.xdatenfelder.parser import FIMParser
import json
# parses your XDatenfelder file/url/string
parser = FIMParser("https://fimportal.de/detail?tx_fimportalcatalog_fimsearch%5Baction%5D=download&tx_fimportalcatalog_fimsearch%5Bcontroller%5D=CatalogEntry&tx_fimportalcatalog_fimsearch%5BdocumentIndex%5D=1&tx_fimportalcatalog_fimsearch%5Bid%5D=DS00000123&cHash=0760c920aa906ab17ecef77281781f09")

# dumps your spec as a json-schema-form
print(json.dumps(parser.to_json))


```

## Features
- [x] Basic parsing of XDatenfelder
  - [X] v1
  - [X] v2
- [ ] Implementation of select fields with external lists
- [X] (basic) XDatenfelder transformation to [jsonschema-form](https://react-jsonschema-form.readthedocs.io/)
- [ ] conversions from json to xöv xml documents
- [ ] xzufi standard