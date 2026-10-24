# The LLM Never Writes Cypher: Intent-First Design and Implementation (Ontographia Part 2)

> **Series overview: Ontographia**
>
> Teams that query a graph database such as Neo4j in natural language usually choose between letting an LLM write Cypher and restricting it to a catalog of handwritten templates. This series examines the common compromise (Agent Skills plus template selection) and proposes another split: the LLM extracts a structured Intent JSON, and an ontology-constrained, deterministic pipeline compiles the Cypher ([Ontographia](https://github.com/edgesentry/ontographia)).
>
> * **Part 1: [The Graph AI Dilemma: Let LLMs Write Cypher or Suffer Template Maintenance Hell?](https://www.linkedin.com/pulse/graph-ai-dilemma-let-llms-write-cypher-suffer-template-yohei-onishi-hj8kc/)**
>   *Focus: production bottlenecks, a review of recent research, and the Intent-first hypothesis*
> * **Part 2: Intent-First Design and Implementation: Deterministic Cypher Assembly** *(This article)*
>   *Focus: separation of the core and app layers, how the compiler works, and the execution loop*
> * **Part 3: Empirical Validation and Roadmap: Large-Scale Ontology Evaluation and External Validity** *(Upcoming)*
>   *Focus: stress tests on large ontologies and validation on public datasets*
>
> * Project documentation: [edgesentry.github.io/ontographia](https://edgesentry.github.io/ontographia/)
> * Open source repository: [github.com/edgesentry/ontographia](https://github.com/edgesentry/ontographia)

---

Part 1 ended with a question. Can a natural-language interface to a graph database follow what users actually ask, and still produce Cypher that is deterministic and auditable, without the engineering work growing with the number of templates?

Ontographia's answer is to give the LLM exactly one job. It reads the user's question and writes an Intent JSON document describing what to explore: where to start, which relationships to follow, how to filter, and what to return. A Rust core checks every name in that document against the ontology and compiles it into Cypher with all values bound as parameters. The LLM never writes Cypher, and nothing it writes reaches the database as query text.

This article covers how that pipeline works, why the LLM and the Neo4j driver are kept out of the core, how three ideas from recent Text2Cypher research move to the Intent layer, and what happened in v0.1.6 when the design met a real model and a real database.

## Where Part 1 left off

In [Part 1](https://www.linkedin.com/pulse/graph-ai-dilemma-let-llms-write-cypher-suffer-template-yohei-onishi-hj8kc/) I argued that the template-selection hybrid looks safe but hits a structural wall. Its flexibility is counted in templates, so every new kind of question means another template for someone to write, review and regression-test. Research from the Neo4j community, such as Schema Filtering and Iterative Refinement, helps, but it repairs queries after the fact and still assumes the LLM writes raw Cypher.

Ontographia moves the flexibility into the Intent and keeps query assembly deterministic: only Intents that pass ontology validation are compiled, through an AST, into Cypher (Cypher 25 by default). LLM calls, prompting and the database execution loop live outside the core, in the app or agent layer.

## How a question becomes Cypher

```text
Ontology (YAML / Turtle) -> Adapter -> COM (Canonical Ontology Model)
                                         |                  |
                              vocabulary schema      strict vocabulary check
                                         v                  v
App layer:  question -> LLM -> Intent JSON -> Core: validate_intent
                                               | fail -> error back to app layer
                                               v pass
                                    Core: build_ast -> Emitter
                                               v
                               { query, params } -> Neo4j (app layer)
```

An Adapter loads the ontology, written in YAML, Turtle or another format, and normalizes it into the COM, the internal model that is the single source of truth for vocabulary. The app layer puts a JSON Schema derived from the COM into the prompt, and the LLM returns an Intent as structured output.

The core then does three things. `validate_intent` checks that every class, relationship and property in the Intent exists in the ontology; unknown names and invalid joins stop there, and the error goes back to the app layer so the LLM can retry. `build_ast` turns a validated Intent into a dialect-independent Query AST and pulls filter values out into parameters. The Emitter walks the AST and produces a `{ query, params }` pair. The same ontology, Intent and dialect always produce the same output. Execution happens back in the app layer, through the Neo4j driver.

Here is the sample from the repository. The Intent asks for the suppliers of the parts that make up product SKU SPX-100:

```json
{
  "start": { "class": "Product", "alias": "product" },
  "traverse": [
    { "relationship": "has_part", "direction": "out", "to": { "class": "Part", "alias": "part" } },
    { "relationship": "supplied_by", "direction": "out", "to": { "class": "Supplier", "alias": "supplier" } }
  ],
  "filter": [{ "alias": "product", "property": "sku", "op": "eq", "value": "SPX-100" }],
  "return": [{ "alias": "supplier", "property": "name", "as_name": "supplier_name" }],
  "limit": 20,
  "optional": false
}
```

The CLI compiles it to:

```text
CYPHER 25
MATCH (product:Product)-[:has_part]->(part:Part)-[:supplied_by]->(supplier:Supplier)
FILTER product.sku = $param_0
RETURN supplier.name AS supplier_name
LIMIT 20

params: { "param_0": "SPX-100" }
```

`SPX-100` never appears in the query text. It travels separately as `param_0`.

## Why the template catalog goes away

In the hybrid approach, someone writes a Cypher string in advance for each query pattern: one template for a supplier list, another for a recursive BOM expansion, and so on.

In Ontographia a query is a combination of a few Intent fields: `start`, `traverse`, `filter` and `return`, plus optional `order_by`, `limit` / `skip` and an `optional` flag. Any question that stays inside the ontology's vocabulary can be expressed with those fields, so a new pattern does not need a new template.

The field set is closed. Since v0.1.5, an unknown key is a validation error that names the offending field. Before that, unknown keys were ignored, so an LLM that wrote `filters` instead of `filter` got a query that built fine with the filter silently dropped. Unknown dialect names are rejected the same way instead of falling back to `cypher25`.

## Why the core has no LLM and no database driver

The core (`ontographia-core`, in Rust) has no networking, no LLM API and no Neo4j driver. Many AI toolkits put LLM calls and database connectors inside the engine; Ontographia keeps them out on purpose ([Architecture guide](https://edgesentry.github.io/ontographia/architecture/)).

A pure compiler is easy to test. AST and query-generation tests run in CI with no LLM and no database, so they cost no tokens and need no mocked model responses. The rule that the LLM never edits a Cypher string is enforced by crate boundaries rather than by team convention. And because the core is small and does no I/O, bindings for Python, Go or WebAssembly can be thin wrappers around it.

Leaving everything else to the application has a cost, though. Prompting, LLM calls, execution and schema subsetting belong to whatever framework a production system already uses (LangChain, LlamaIndex, an in-house agent platform), but without a shared reference there is no common end-to-end path, and engineers have to guess how to wire the core into an agent. The project started with these helpers as example code in the repository. In v0.1.6 they became an installable, experimental Python extra, `ontographia[llm]`. Cypher still comes only from the core, after validation.

## Three research ideas, moved from Cypher to the Intent

The research covered in Part 1 (Schema Filtering, Iterative Refinement and Difficulty-Adaptive Spend) assumes the LLM writes Cypher. The Intent layer applies the same ideas to Intent extraction instead.

Schema Filtering becomes ontology subsetting. Large enterprise ontologies can have hundreds or thousands of classes and properties, and putting all of them in the prompt costs tokens and makes it easier for the model to pick a property that looks right but isn't. The Intent layer matches words in the question exactly against ontology element names (ignoring case and normalizing plurals), adds the minimal set of relationships that connects the matched classes, and sends only that subset. If extraction or validation fails on the subset, it retries with the full schema. If nothing in the question matches, it uses the full schema from the start.

Iterative Refinement becomes Intent repair. An Intent can pass validation, compile, and still return zero rows, or the driver can raise a type-conversion error. Text2Cypher research usually hands the Cypher back to the LLM to fix, which brings back the non-determinism this design removes. Here the LLM gets the execution result and revises the Intent JSON. The revised Intent goes through validation and compilation again, so every query that runs still comes from the compiler. The loop is opt-in, runs at most two rounds by default, and stops as soon as a revised Intent fails validation.

Difficulty-Adaptive Spend becomes staged retries. Most everyday questions are single-node lookups or shallow traversals. Extraction starts with the subset and a single retry, and only when that phase fails does it move to the full schema with up to five retries. Execution failures on Neo4j do not trigger this escalation; the repair loop handles those. The aim is to keep tokens and latency low for easy questions. Whether it works is a measurement question, and Part 3 has the numbers.

## What changes for Agent Skills

With Intent-first, an agent's Skills have much less to do. In the hybrid, the LLM classifies which template to call, and developers maintain a growing template catalog. Here the LLM turns a question into an Intent, and developers maintain the ontology and the extraction prompt.

Schema changes are where the difference shows most. In the hybrid, renaming a property means finding every affected template, fixing it and re-testing classification. In Ontographia you update the ontology and validation follows it. Query safety stops depending on whoever wrote each template, because names are checked and values are bound before any query string exists.

## v0.1.6 in practice: an MCP server and a real end-to-end run

v0.1.6 also added an experimental MCP (Model Context Protocol) server, `ontographia[mcp]`, with four tools: `list_ontology`, `intent_schema`, `build_cypher` and `execute`. The server does not call an LLM. The MCP client supplies the Intent JSON, and the server validates it before building Cypher, so the model still never writes Cypher when it runs inside an MCP client. Setup is in the [MCP docs](https://edgesentry.github.io/ontographia/mcp/).

All four tools worked when I ran them against a real setup, including replaying a saved Intent through `build_cypher` and `execute`. The `execute` integration tests also run in CI against a live Neo4j instance.

Separately, I ran questions end to end, from question to result rows, with Gemini 3.7 Flash and a local Neo4j. When the model put a property name that does not exist in the ontology into an Intent, for example `"name激as_name"`, the Intent failed validation, no Cypher was emitted, and the name never reached the database.

Answering the question was a different matter. I kept all four attempts, and only one succeeded end to end; that one returned two rows, MikroMotors and FormTech. Stopping a bad name and answering correctly are separate results, and in this small sample the second rate is low.

The protection is also narrow. Validation stops names that are not in the ontology. If the model picks a real name that is the wrong one for the question, the Intent passes; Part 1 called these silent false positives. Factual errors are out of scope too. This is not a claim that Ontographia prevents hallucination in general.

## Known limits

Intent-first covers questions that fit the ontology's vocabulary. A question that needs a class or relationship the ontology does not define fails validation instead of producing a query.

The project is pre-1.0, and releases can still break compatibility; v0.1.5 started rejecting Intents with unknown keys that earlier versions built. The Intent layer and the MCP server are experimental optional extras, and subsetting, adaptive retries and execution feedback live there, not in the Rust core. GQL output is a prototype. The [roadmap](https://github.com/edgesentry/ontographia/blob/main/docs/roadmap.md) lists what comes next, without dates.

## Next: does it hold up at scale?

Moving natural-language flexibility into the Intent and making Cypher assembly deterministic means a new kind of question no longer needs a new template. Whether that holds against ontologies with thousands of properties and public Text-to-Cypher benchmarks is a separate question. Part 3 reports a stress test at that scale and validation on public datasets, including where the approach falls short, plus a re-run on the published v0.1.6 package with two model versions.

To try it now, `pip install ontographia` installs the core, and `pip install "ontographia[llm]"` and `pip install "ontographia[mcp]"` add the experimental Intent layer and MCP server. The CLI is also on Homebrew (`brew tap edgesentry/tap && brew install ontographia`). The [Neo4j walkthrough](https://edgesentry.github.io/ontographia/end-to-end-neo4j/) runs the manufacturing sample end to end. If you try it on your own ontology, I would like to hear which questions failed validation and which passed but returned the wrong thing; issues are open on the [repository](https://github.com/edgesentry/ontographia).

---

*Open source project:* [github.com/edgesentry/ontographia](https://github.com/edgesentry/ontographia)
*Documentation:* [edgesentry.github.io/ontographia](https://edgesentry.github.io/ontographia/)
*Release notes:* [v0.1.6](https://github.com/edgesentry/ontographia/releases/tag/v0.1.6)
*Author:* Yohei Onishi
*Tags:* `#Neo4j #Cypher #KnowledgeGraph #GraphRAG #AIAgents #EnterpriseAI #MCP`
