<!-- markdownlint-disable-file MD041 -->
Part 3 of my Ontographia series is up. Ontographia is an open-source tool for querying Neo4j in natural language where the LLM only writes an Intent JSON, and a deterministic Rust core checks it against the ontology and compiles parameter-bound Cypher.

This part is the evaluation. Three results:

1. On a 2,000-property ontology, sending only the part of the ontology the question touches cut prompt tokens by about 91%. On a deterministic simulation it raised correct property choices by 50 points.
2. With Gemini 3.7 Flash, the same approach with a fallback to the full schema raised correct property choices by 12.5 points, and all 40 questions compiled.
3. All 15 public Neo4j benchmark schemas loaded into Ontographia's ontology model. The exact-match spot check on answers came out at about 3%, and the article explains why that metric is limited here.

It also covers a re-run with Gemini 3.8 Flash, which did worse than 3.7 on the recommended setting in a single run, what the results do not show, and the roadmap.

Article: [LINK TO PART 3]
Repo: https://github.com/edgesentry/ontographia

#Neo4j #KnowledgeGraph #Cypher #LLM #Ontology #OpenSource #LLMEvaluation
