<!-- markdownlint-disable-file MD041 -->
Part 2 of my Ontographia series is up. The idea: the LLM never writes Cypher. It writes an Intent JSON describing the user's question, and a deterministic Rust core checks every name against the ontology and compiles parameter-bound Cypher.

The article explains why the core has no LLM and no Neo4j driver, how Schema Filtering, Iterative Refinement and adaptive spend move from Cypher to the Intent, and what changes for Agent Skills when there is no template catalog.

It ends with the experimental MCP server from v0.1.6. In a real end-to-end run, a property name the ontology does not define was rejected before it reached the database. Only one of the four attempts succeeded end to end, though, and the article spells out what validation does not catch.

Part 3, with the evaluation numbers, comes next.

Article: https://www.linkedin.com/pulse/llm-never-writes-cypher-intent-first-design-part-2-yohei-onishi-oyroc/
Repo: https://github.com/edgesentry/ontographia

#Neo4j #KnowledgeGraph #Cypher #LLM #Ontology #OpenSource #MCP
