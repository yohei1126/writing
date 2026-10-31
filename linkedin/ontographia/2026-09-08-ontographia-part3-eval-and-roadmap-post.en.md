<!-- markdownlint-disable-file MD041 -->
Part 3 of my Ontographia series is up. Ontographia is an open-source tool for querying Neo4j in natural language: the LLM only writes an Intent JSON, and a deterministic Rust core checks it against the ontology and compiles parameter-bound Cypher.

Ontology validation stops names that do not exist, but not real names that are wrong. On 200- and 2,000-property ontologies, all 40 deliberately wrong Intents compiled cleanly.

Sending the model only the part of the ontology a question touches, with a fallback to the full schema, cut prompt tokens by about 91% at 2,000 properties (13,765 to 1,301 p95). In a live evaluation with Gemini 3.8 Flash (large n=5), it lifted correct property choices by +19.5 points on average over the full schema, with every run supporting the hypothesis.

On 15 public Neo4j schemas the pipeline runs end to end, but exact match on answers was about 3%. The article explains why, and what comes next.

Article: [LINK TO PART 3]
Repo: https://github.com/edgesentry/ontographia

#Neo4j #KnowledgeGraph #Cypher #LLM #Ontology #OpenSource #LLMEvaluation
