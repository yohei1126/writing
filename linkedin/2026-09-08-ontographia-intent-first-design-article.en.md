<!-- markdownlint-disable-next-line MD041 -->
**Notes - do not paste (everything above the horizontal rule)**

- **Title (LinkedIn title field):** Intent-First Design and Implementation: Deterministic Cypher Assembly (Ontographia Part 2). This matches the Part 2 title already listed in Part 1. Alternative: The LLM Never Writes Cypher: Inside Ontographia's Intent-First Architecture (Ontographia Part 2).
- **Subtitle / headline:** The LLM writes only an Intent JSON. A deterministic Rust core validates it against the ontology and emits parameter-bound Cypher.
- **Cover image:** same style as the Part 1 cover (images/ontographia-part1-cover.jpg in yohei1126/writing), text "Ontographia Part 2: Intent-First Design and Implementation", saved as images/ontographia-part2-cover.jpg. Upload it in LinkedIn's cover field, then delete the cover [IMAGE] line at the top of the body.
- **Image 1, Intent-first pipeline diagram** (section "The Intent-first pipeline in six steps"): from the text diagram in section 1 of the Zenn article, or the docs Architecture page. If you upload it, delete the text diagram code block under the placeholder.
- **Image 2, research-to-Intent-layer mapping** (section "Three research ideas moved from Cypher to the Intent layer"): render the Mermaid flowchart in section 3 of the Zenn article to PNG.
- **Image 3 (optional), hybrid vs. Intent-first comparison table** (section "What changes for Agent Skills"): from the table in section 4 of the Zenn article. The text list already covers it, so this one can be skipped.
- **Feed post:** see 2026-09-08-ontographia-intent-first-design-post.en.md.
- **After publishing:** update the Part 2 line in Part 1's series overview with the new link.

---

[IMAGE: Cover image for Part 2, same style as the Part 1 cover (images/ontographia-part1-cover.jpg in yohei1126/writing). Suggested text: "Ontographia Part 2: Intent-First Design and Implementation". Suggested file: images/ontographia-part2-cover.jpg]

If an LLM writes your Cypher, you inherit its hallucinations. If it only picks from a template catalog, you inherit the catalog. Ontographia takes a third route: the LLM describes what the user wants as an Intent JSON document, and a deterministic, ontology-constrained compiler written in Rust turns that document into parameter-bound Cypher. The LLM never writes Cypher.

This article explains how the pipeline works, why the LLM and the database driver are kept out of the core, and how three ideas from recent Text2Cypher research carry over to the Intent layer. Everything here matches Ontographia v0.1.5.

**The Ontographia series**

- Part 1: [The Graph AI Dilemma: Let LLMs Write Cypher or Suffer Template Maintenance Hell?](https://www.linkedin.com/pulse/graph-ai-dilemma-let-llms-write-cypher-suffer-template-yohei-onishi-hj8kc/) The problem with template-selection hybrids, a review of recent research, and the Intent-first hypothesis.
- Part 2 (this article): Intent-First Design and Implementation. How the core and the app layer are separated, and how the implementation works.
- Part 3 (upcoming in English): Empirical Validation and Roadmap. Stress tests on large ontologies and validation on public data. The [Japanese version is on Zenn](https://zenn.dev/yohei/articles/2026-09-08-ontographia-eval-and-roadmap).

Repository: [github.com/edgesentry/ontographia](https://github.com/edgesentry/ontographia). Docs: [edgesentry.github.io/ontographia](https://edgesentry.github.io/ontographia/). This is an English adaptation of my [Japanese article on Zenn](https://zenn.dev/yohei/articles/2026-09-08-ontographia-intent-first-design).

# Where Part 1 left off

Teams that query a graph database such as Neo4j in natural language tend to swing between two options: let the LLM write Cypher directly, or lock the system down with a large catalog of handwritten queries and templates. The common compromise is Agent Skills plus per-use-case template selection.

In [Part 1](https://www.linkedin.com/pulse/graph-ai-dilemma-let-llms-write-cypher-suffer-template-yohei-onishi-hj8kc/) I argued that this hybrid looks safe but hits a structural wall. Its flexibility is measured in number of templates, so the maintenance cost moves onto the people who write them. Recent research from the Neo4j community (Schema Filtering, Iterative Refinement) helps, but it corrects queries after the fact and still assumes the LLM writes raw Cypher.

Part 1 ended with a question: can a system follow natural language and still execute and govern Cypher deterministically, without the work growing with the number of templates?

Ontographia answers it by drawing three boundaries:

- Natural-language flexibility goes into Intent JSON. The LLM writes no Cypher at all; its only job is to extract what the user wants to explore.
- Query assembly and governance are fully deterministic. Only Intents that pass ontology validation are compiled, through an AST, into Cypher (Cypher 25 by default), and every value is bound to a `$param_N` parameter.
- LLM calls, prompt control and the database execution loop live outside the core, in the app or agent layer. The engine stays an LLM-agnostic, driver-agnostic compiler, and ideas from recent research (Schema Filtering, Refinement) are applied at the Intent layer.

# The Intent-first pipeline in six steps

[IMAGE: Intent-first pipeline diagram. Ontology (YAML / Turtle) → Adapter → COM; app-layer LLM turns the question into Intent JSON; core validate_intent → build_ast → Emitter → { query, params } → Neo4j. Source: the text diagram in section 1 of the Zenn article (https://zenn.dev/yohei/articles/2026-09-08-ontographia-intent-first-design) or the diagram on the docs Architecture page (https://edgesentry.github.io/ontographia/architecture/). If you upload this image, delete the text diagram below.]

```text
[Ontology definition (YAML / Turtle)]
        |
   Adapter -> COM (Canonical Ontology Model)
        |                         |
  (vocabulary schema)     (strict vocabulary check)
        v                         v
 [App layer: LLM]          [Core: validate_intent]
  question -> Intent JSON -> valid? --no--> validation error (back to app layer)
                              | yes
                       [Core: build_ast]
                              |
                       [Core: Emitter]
                              |
                  { query, params }  (e.g. Cypher 25 + $param_0)
                              |
                       [Neo4j execution]
```

- Step 1. Normalize the ontology. An Adapter loads an ontology written in YAML, Turtle or another format and builds the COM (Canonical Ontology Model), the internal normalized representation. The COM is the single source of truth for vocabulary across the system.
- Step 2. Extract the Intent (app layer). Vocabulary constraints derived from the COM, in the form of an Intent JSON Schema, go into the prompt. The LLM reads the user's question and returns an Intent JSON describing what to explore, as structured output.
- Step 3. Validate the vocabulary (core: `validate_intent`). The core checks that every class, relationship and property in the Intent exists in the ontology. Unknown vocabulary and invalid joins stop here, and the error goes back to the app layer so the LLM can re-extract or retry.
- Step 4. Build the intermediate representation (core: `build_ast`). Only validated Intents become a dialect-independent Query AST. Filter values from user input are separated from the query string at this point and become parameters (`$param_0` and so on).
- Step 5. Emit the query (core: Emitter). The Emitter walks the AST and emits a `{ query, params }` pair for the chosen dialect (Cypher 25 for Neo4j by default). The same input always produces the same output.
- Step 6. Execute (app layer). The application hands the query and parameters to the Neo4j driver.

# Why this removes the template catalog

In the hybrid approach, people write a Cypher string in advance for each query pattern: a "supplier list" template, a "recursive BOM expansion" template, and so on.

With Intent-first, a query is a combination of JSON fields: the starting class (`start`), the relationships to traverse (`traverse`), the filters (`filter`) and the returned fields (`return`). Sorting (`order_by`), result limits (`limit` / `skip`) and an `optional` flag can be added when needed.

Since v0.1.5, any other key is a validation error that names the offending field. Earlier versions ignored unknown keys silently, so an LLM that wrote `filters` instead of `filter` got a query that built fine with the filter dropped. Now the Intent fails validation, and the app layer can hand the error back to the LLM for a retry. Dialect names follow the same rule: Python and the FFI/Go bindings reject an unknown dialect instead of falling back to `cypher25`.

As long as a question stays within the vocabulary the ontology defines, the LLM can express its exploration pattern as a combination of these fields, so a new pattern does not need a new template.

# What goes in the core and what stays out

The design principles come from the [Architecture guide](https://edgesentry.github.io/ontographia/architecture/):

- The ontology is the single source of truth. Class, relationship and property names are accepted only if they are defined in the COM.
- LLMs emit Intent, not Cypher. Query generation starts only after the schema-constrained JSON has been validated mechanically.
- Parameter binding is deterministic. User input and filter values always go into `$param_N`, and the structure of the pipeline gives them no path into the query string.
- Same input, same output. The same ontology, Intent and dialect always produce an identical `{ query, params }`.
- The core and the app layer are strictly separated. The core (`ontographia-core`, written in Rust) has no networking, no LLM API and no Neo4j driver.

## Why the core has no LLM and no driver

Many AI toolkits put LLM calls and database connectors inside the engine. Ontographia keeps them out on purpose (see [What is intentionally outside the core](https://edgesentry.github.io/ontographia/architecture/#what-is-intentionally-outside-the-core)), for three reasons.

A pure deterministic compiler is easy to test. AST and query-generation tests run in CI with no LLM and no database, so they cost no tokens and need no mocked LLM responses.

The guarantee that the LLM never rewrites a Cypher string is enforced by language and crate boundaries rather than by convention.

Because the core is small and has no I/O, bindings for Python, Go or WebAssembly can be thin wrappers around it.

## Why the out-of-core pieces still ship in examples/

Prompt construction, LLM calls, execution through the Neo4j driver, dynamic schema subsetting and execution feedback belong to whatever framework a production system uses (LangChain, LlamaIndex, an in-house agent platform). They are outside the scope of the core library by design.

Leaving them out entirely would cost something, though. Without them there would be no end-to-end (E2E) integration tests that include the app layer, no way to check the approach in a real environment, and engineers would have to guess how to call the core from an agent.

So the repository ships an out-of-core Python implementation in [`examples/`](https://github.com/edgesentry/ontographia/tree/main/examples), mainly `examples/llm/`. It lets us run E2E tests without touching the core's determinism, and it is a working reference for how to use the core library.

## Terms used in this article

- COM (Canonical Ontology Model): the internal data model that normalizes ontologies from several formats (native YAML, OWL, RDF and others).
- Intent JSON: the JSON format for exploration intent: which node to start from, which relationships to follow, how to filter and what to return.
- Query AST: a dialect-independent intermediate representation of the query, structured so that GQL support is possible later.
- Emitter: walks the AST and outputs a query string and parameter dictionary for a specific dialect (Cypher 25 by default, or Cypher 5). The GQL emitter is a prototype dialect only.

# Three research ideas moved from Cypher to the Intent layer

The Neo4j-related research covered in Part 1 (Schema Filtering, Iterative Refinement and Difficulty-Adaptive Spend) is useful, but all of it assumes the LLM writes Cypher. Ontographia applies the same ideas to Intent generation in the app layer (`examples/llm/`).

[IMAGE: Research-to-Intent-layer mapping diagram. Schema Filtering → 3.1 ontology subsetting of the extraction prompt; Iterative Refinement → 3.2 execution-feedback loop that repairs the Intent JSON; Adaptive Spend → 3.3 adaptive allocation (minimal resources first, full schema only for hard questions). Source: the Mermaid flowchart in section 3 of the Zenn article (https://zenn.dev/yohei/articles/2026-09-08-ontographia-intent-first-design); render it to PNG.]

## 1. Ontology subsetting with a full-schema fallback

Large enterprise ontologies can have hundreds or thousands of classes and properties. Putting all of them into the prompt drives up token usage and makes the LLM more likely to pick a property that looks right but isn't.

The app layer (`examples/llm/subset.py`) matches tokens in the user's question exactly against ontology element names, ignoring case and normalizing plurals. It then extracts the minimal topology that connects the matched classes (relationship closure), so the ontology in the prompt shrinks considerably.

If extraction or validation fails in the subset phase, the pipeline retries with the full schema. This switch is the `schema_policy` setting of the example pipeline (`examples/llm/pipeline.py`); the pip package and the Rust core do not have it.

`schema_policy` takes three values: `auto` (the default), `subset` and `full`. With `auto`, the pipeline tries the subset first and switches to the full schema if the subset phase hits an extraction failure, a `validate_intent` failure or an exception during repair. If no vocabulary in the question matches and the subset is empty, it uses the full schema from the start.

## 2. Correcting the Intent with execution feedback

An Intent can be valid against the ontology and compile cleanly (`Engine::build`) and still return zero rows on Neo4j, or the driver can raise an error on a data-type conversion.

Text2Cypher research usually handles this by handing the Cypher string back to the LLM to fix, which brings back the non-determinism this design is meant to remove.

The example app (`examples/llm/exec_feedback.py`) gives the LLM the execution result (zero rows or the error details) and asks it to revise the Intent JSON instead of the Cypher. The loop runs only when you pass `--execute --refine-on-exec`.

Each revised Intent goes through `validate_intent` and AST compilation again, so every query that runs still comes out of the deterministic compiler; there is no path for the LLM to edit a Cypher string. By default the loop runs at most 2 rounds (change it with `--max-exec-refines`), always uses the full schema, and stops as soon as a revised Intent fails validation.

## 3. Difficulty-adaptive spend

Most day-to-day business questions are single-node lookups or shallow traversals, and only some need complex joins. Sending a full-schema prompt and reserving a large retry budget (five attempts, say) for every question wastes tokens and adds latency.

The example pipeline (`examples/llm/pipeline.py`, called from `examples/run_llm_e2e.py`) starts with a small subset and a minimal retry budget (`initial_retries=1`). Only when the subset phase fails does it switch to the full schema and allow more retries (`escalated_retries=5`). The trigger is the same as in subsetting: a failure in extraction, validation or repair. Execution failures on Neo4j (errors or zero rows) do not trigger this escalation; the execution-feedback loop handles them.

The aim is to keep tokens and latency low for everyday questions and spend more retries only on hard ones. Part 3 covers the quantitative evaluation.

# What changes for Agent Skills

With Intent-first, the Skills (tool definitions) in an agent platform have much less to do. Comparing the template-selection hybrid with Intent-first:

- The LLM's task. Hybrid: classify which Cypher template to call. Intent-first: turn natural language into Intent JSON.
- What developers maintain. Hybrid: a growing catalog of Cypher templates. Intent-first: the ontology definition (COM) and the extraction prompt.
- Schema changes. Hybrid: find every affected template, fix it and regression-test it. Intent-first: update the ontology, and vocabulary validation follows.
- New questions. Hybrid: write and review a new template. Intent-first: handled directly, as long as the question is within the ontology's vocabulary.
- Query safety. Hybrid: depends on the template author. Intent-first: built into the pipeline, since vocabulary is validated and values are parameter-bound before any query string exists.

[IMAGE (optional): The comparison above as a two-column table image, "Template-selection hybrid vs. Intent-first (Ontographia)". Source: the table in section 4 of the Zenn article.]

Agent developers no longer have to produce near-identical Cypher templates and tune the prompt routing between them.

# Installing Ontographia and running the sample

You don't need to build from source. The CLI installs with Homebrew, and packages are released for Python, Go and Rust:

- CLI: `brew install ontographia` (after `brew tap edgesentry/tap`). Also `cargo install ontographia-cli`, or binaries from GitHub Releases.
- Python: `pip install ontographia` (on PyPI for Linux, macOS arm64 and Windows).
- Go: `go get github.com/edgesentry/ontographia/bindings/go` (cgo / FFI binding).
- Rust: `cargo add ontographia-core ontographia-adapters`. The crates `ontographia-core`, `ontographia-adapters`, `ontographia-schema` and `ontographia-cli` are on crates.io.

The repository [edgesentry/ontographia](https://github.com/edgesentry/ontographia) includes manufacturing-domain sample data. Clone it first:

```bash
git clone https://github.com/edgesentry/ontographia.git
cd ontographia
```

## A deterministic build with the CLI

Pass the sample ontology ([`examples/manufacturing.native.yaml`](https://github.com/edgesentry/ontographia/blob/main/examples/manufacturing.native.yaml)) and the sample Intent ([`examples/sample_intent.json`](https://github.com/edgesentry/ontographia/blob/main/examples/sample_intent.json)) to the CLI and it prints Cypher 25.

The sample Intent asks for the names of the suppliers of the parts that make up product SKU SPX-100:

```json
{
  "start": { "class": "Product", "alias": "product" },
  "traverse": [
    { "relationship": "has_part", "direction": "out",
      "to": { "class": "Part", "alias": "part" } },
    { "relationship": "supplied_by", "direction": "out",
      "to": { "class": "Supplier", "alias": "supplier" } }
  ],
  "filter": [
    { "alias": "product", "property": "sku", "op": "eq", "value": "SPX-100" }
  ],
  "return": [
    { "alias": "supplier", "property": "name", "as_name": "supplier_name" }
  ],
  "limit": 20,
  "optional": false
}
```

```bash
brew tap edgesentry/tap
brew install ontographia

ontographia build \
  --ontology examples/manufacturing.native.yaml \
  --intent examples/sample_intent.json \
  --json
```

Output:

```json
{
  "params": { "param_0": "SPX-100" },
  "query": "CYPHER 25\nMATCH (product:Product)-[:has_part]->(part:Part)-[:supplied_by]->(supplier:Supplier)\nFILTER product.sku = $param_0\nRETURN supplier.name AS supplier_name\nLIMIT 20"
}
```

The SKU value `SPX-100` never appears in the query text. It travels separately as `param_0`.

## End to end from Python: LLM extraction, build, Neo4j execution

[`examples/run_llm_e2e.py`](https://github.com/edgesentry/ontographia/blob/main/examples/run_llm_e2e.py) takes a natural-language question, extracts the Intent with an LLM, and runs it through to Neo4j. It is the E2E integration test for the app layer, and also a reference for embedding the core library (the Python package) in your own systems and agents.

```bash
uv sync

uv run python examples/run_llm_e2e.py \
  --question "Find all suppliers providing parts to Plant-1" \
  --execute \
  --refine-on-exec \
  --password ontographia
```

For the full steps, including the Neo4j container setup, see the [Neo4j walkthrough](https://edgesentry.github.io/ontographia/end-to-end-neo4j/) in the docs.

# Known limits at this stage

Intent-first covers questions that fit the ontology's vocabulary. A question that needs a class or relationship the ontology does not define fails validation instead of producing a query.

The project is pre-1.0, and releases can still break compatibility. [v0.1.5](https://github.com/edgesentry/ontographia/releases/tag/v0.1.5) made unknown Intent keys and unknown dialects errors, so Intents with extra or misspelled keys that built under earlier versions now fail validation. Check your Intents before upgrading.

Subsetting, adaptive spend and execution feedback live in the example app (`examples/llm/`), not in the released pip package or the Rust core. Execution feedback is capped at 2 rounds by default and stops when a revised Intent fails validation. GQL output is a prototype dialect.

The [public roadmap](https://edgesentry.github.io/ontographia/roadmap/) (`docs/roadmap.md`) groups upcoming work into Phases 0 to 5, tracked as epics #82 to #89, with dependencies but no dates. Phase 1 covers packaging this Intent layer as an optional Python extra (#84) and an MCP server (#85). Neither is in a release yet.

# Next: does this hold up at scale?

Ontographia keeps natural-language flexibility in the Intent layer and makes Cypher assembly deterministic, so supporting a new question no longer means writing a new template. Whether the design holds up against ontologies at real-world scale (thousands of properties) and public Text-to-Cypher benchmarks is a separate question.

Part 3 reports the quantitative results, including where the approach falls short, from a stress test with thousands of properties (Track A) and validation on public datasets (Track B). The English version is upcoming; the [Japanese version is on Zenn](https://zenn.dev/yohei/articles/2026-09-08-ontographia-eval-and-roadmap).

To try it now, start with the [Neo4j walkthrough](https://edgesentry.github.io/ontographia/end-to-end-neo4j/). Issues and feedback are welcome on the [repository](https://github.com/edgesentry/ontographia).
