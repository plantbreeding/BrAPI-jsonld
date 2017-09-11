# BrAPI JSON-LD experimentations

See the [JSON-LD official specs](https://www.w3.org/TR/json-ld/) for reference.

## Approach 1: BrAPI centric

The BrAPI centric approach strategy is to model the whole BrAPI in JSON-LD without relying on external ontologies. This model would use a IRIs prefixed by the brapi.org domain (something like `https://brapi.org/rdf/`).

This JSON-LD BrAPI model can then be mapped to standard ontologies via `@type` (`rdf:type`), `owl:sameAs` or any other property.

Under the `brapi-centric` folder you can find the following:

- `context` => JSON-LD contexts
  - `brapi.jsonld` => Describing the base BrAPI model (result, metadata, etc.)
  - `Germplasm.jsonld` => Describing the BrAPI germplasm model

- `germplasm-example.jsonld` => Example of BrAPI data extended with JSON-LD ([See in JSON-LD playground](https://json-ld.org/playground/#startTab=tab-expanded&json-ld=https%3A%2F%2Fraw.githubusercontent.com%2Fplantbreeding%2FBrAPI-jsonld%2Fmaster%2Fbrapi-centric%2Fgermplasm-example.jsonld))

- `ontology-mapping-graph.jsonld` => Example mapping of germplasm model to other ontologies (xsd, wikidata, schema.org) using `rdf:type` ([See in JSON-LD playground](https://json-ld.org/playground/#startTab=tab-expanded&json-ld=https%3A%2F%2Fraw.githubusercontent.com%2Fplantbreeding%2FBrAPI-jsonld%2Fmaster%2Fbrapi-centric%2Fontology-mapping-graph.jsonld))

## Approach 2: Based on external ontologies

Another approach for BrAPI JSON-LD is to develop the model based on other ontologies. This model would rely on ontologies like MIAPPE (pheno metadata), CropOntology (MCPD & variables), etc. Some BrAPI property might have to be defined in the `brapi.org` namespace.

Under the `external-ontology` folder you can find the following:

- `context` => JSON-LD contexts
  - `brapi.jsonld` => Describing the base BrAPI model (result, metadata, etc.)
  - `Germplasm.jsonld` => Describing the BrAPI germplasm model based on standard ontologies

- `germplasm-example.jsonld` => Example of BrAPI data extended with JSON-LD ([See in JSON-LD playground](https://json-ld.org/playground/#startTab=tab-expanded&json-ld=https%3A%2F%2Fraw.githubusercontent.com%2Fplantbreeding%2FBrAPI-jsonld%2Fmaster%2Fexternal-ontology%2Fgermplasm-example.jsonld))
