<!-- markdownlint-disable-file MD041 -->
Part 3 of my Ontographia series is up. Ontographia is an open-source tool for querying Neo4j in natural language: the LLM only writes an Intent JSON, and a deterministic Rust core checks it against the ontology and compiles parameter-bound Cypher.

Ontology validation stops names that do not exist, but not real names that are wrong. On 200- and 2,000-property ontologies, all 40 deliberately wrong Intents compiled cleanly.

Sending the model only the part of the ontology a question touches, with a fallback to the full schema, cut prompt tokens by about 91% at 2,000 properties. With Gemini 3.7 Flash it raised correct property choices by 12.5 points, and all 40 questions compiled. A re-run on the published package held that pattern with 3.7 and 3.8 Flash, though 3.8 scored lower than 3.7 on that setting in a single run.

On 15 public Neo4j schemas the pipeline runs end to end, but exact match on answers was about 3%. The article explains why, and what comes next.

Article: [LINK TO PART 3]
Repo: https://github.com/edgesentry/ontographia

#Neo4j #KnowledgeGraph #Cypher #LLM #Ontology #OpenSource #LLMEvaluation
