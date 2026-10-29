# Wrong but Real: Evaluating Intent-First Cypher Generation at 2,000 Properties (Ontographia Part 3)

![Cover: ontology scale narrowed to a subset, then evaluation results](../../images/ontographia-part3-linkedin-cover.jpg)

> **Series overview: Ontographia**
>
> Teams that query a graph database such as Neo4j in natural language usually choose between letting an AI write the query and locking the system to handwritten templates. This series examines the common compromise (agent skills plus template selection) and proposes another split: the AI extracts a structured Intent, and an ontology-checked, deterministic pipeline compiles the Cypher ([Ontographia](https://github.com/edgesentry/ontographia)).
>
> * **Part 1: [The Graph AI Dilemma: Let LLMs Write Cypher or Suffer Template Maintenance Hell?](https://www.linkedin.com/pulse/graph-ai-dilemma-let-llms-write-cypher-suffer-template-yohei-onishi-hj8kc/)**. Production bottlenecks, research review, Intent-first hypothesis
> * **Part 2: [The LLM Never Writes Cypher: Intent-First Design and Implementation](https://www.linkedin.com/pulse/llm-never-writes-cypher-intent-first-design-part-2-yohei-onishi-oyroc/)**. How the split works in practice
> * **Part 3: Evaluation and Roadmap** *(This article)*. What the measurements support, what they do not, and what comes next
>
> * Documentation: [edgesentry.github.io/ontographia](https://edgesentry.github.io/ontographia/)
> * Repository: [github.com/edgesentry/ontographia](https://github.com/edgesentry/ontographia)

---

Ontology validation stops names that do not exist. It cannot stop a real name that is the wrong one. Once an ontology grows to a few hundred properties, those wrong-but-real names fill the prompt: in my stress test, all 40 deliberately wrong Intents compiled cleanly at 200 properties and again at 2,000.

What helped most was controlling what the model sees. Sending only the part of the ontology a question touches, with a fallback to the full schema, cut prompt tokens by about 91% on the 2,000-property ontology and raised correct property choices with a live model. That held with two Gemini Flash versions and on the published package. The newer model was not better on that setting, and exact match on a public-benchmark spot check was about 3%.

## Three hypotheses, with pass criteria fixed in advance

[Part 2](https://www.linkedin.com/pulse/llm-never-writes-cypher-intent-first-design-part-2-yohei-onishi-oyroc/) moved three ideas from Text-to-Cypher research to the Intent layer. I wrote a pass criterion for each into code before running anything:

* H1, ontology subsetting: on the 2,000-property ontology, the share of Intents that pick the right property (Property Hit) beats the full schema by at least 10 points, p95 prompt tokens drop by at least 30%, and compile success does not fall.
* H2, Intent repair from execution feedback: final execution success improves by at least 20 points.
* H3, staged retries: at least 30% fewer tokens on easy questions with no loss in quality.

A fourth question: does the ontology model work on schemas I did not write?

## Two tracks: a stress test I built and fifteen schemas I did not

Track A is a synthetic manufacturing domain with 40 questions, each with a gold Intent, at 16, 200, and 2,000 properties. The larger versions are padded with near-duplicates such as `plant_id` next to `plant_code` and `factory_id`, the overlap that builds up in enterprise graphs after years of system integration.

Most of Track A runs on a mechanical arm ("arm" as in one condition of a clinical trial): fixed simulation rules replace the live model, so a failure points at the pipeline rather than at sampling noise. It tests whether the control loops work, not how capable a model is. For H1 I also ran a live arm with Gemini Flash at temperature 0.

Track B uses 15 public database schemas from Neo4j's [text2cypher-2025v1](https://huggingface.co/datasets/neo4j/text2cypher-2025v1) dataset, from movies to healthcare.

## At 200 properties, wrong names compile cleanly

The baseline sends the full schema and feeds the pipeline Intents that pick a distractor. On the 16-property ontology there are no distractors, so validation rejected all 40 wrong names as unknown. On the 200- and 2,000-property ontologies, the same 40 wrong Intents passed validation and compiled, 40 of 40 both times. The validator can check that a name exists, not that it is the name the user meant. That is the silent false positive from Part 1, reproduced on demand. The full prompt also grows from 1,359 tokens to 2,460 to 13,710.

## Showing the model less: the result that held across models

Subsetting matches words in the question against ontology names, keeps the matched classes and the relationships that connect them, and sends only that. The recommended setting, `subset_fallback`, goes back to the full schema only if extraction or validation fails on the subset.

![Full schema: 13,710 tokens, Property Hit 0.82, 33 of 40 compiled. subset_fallback: 1,247 tokens, Property Hit 0.95, 40 of 40 compiled.](../../images/ontographia-part3-fig-a-subset-vs-full.jpg)

*Figure A. The same 2,000-property ontology sent two ways. Gemini 3.7 Flash, one live run, p95 prompt tokens.*

On the mechanical arm, Property Hit went from 0.50 to 1.00 with all 40 compiled, but the arm only errs on distractors it can see, so that mostly confirms the subset hides them. The live run is the stronger evidence. With Gemini 3.7 Flash, the full schema scored 0.82 Property Hit and compiled 33 of 40; `subset_fallback` scored 0.95 and compiled 40 of 40, a 12.5-point gain, so H1 passed live too. The subset alone did worse than the full schema (0.78, 32 of 40) because some questions needed vocabulary the exact-match subset missed. In production, subsetting needs the fallback.

After [v0.1.6](https://github.com/edgesentry/ontographia/releases/tag/v0.1.6) put the Intent layer on PyPI, I re-ran the live evaluation on the published package with the same settings and two models, Gemini 3.7 Flash and 3.8 Flash, one run each. With both, no output contained a name the model had not been shown, `subset_fallback` beat the full schema on Property Hit (by 30 points with 3.7, 16.25 with 3.8), and p95 tokens fell by about 90.5%.

![Gemini 3.7 Flash on subset_fallback: Property Hit 0.95, 40 of 40 compiled. Gemini 3.8 Flash: Property Hit 0.8875, 37 of 40 compiled. Single run per model.](../../images/ontographia-part3-fig-b-model-comparison.jpg)

*Figure B. The newer model was not better on the recommended setting. Published package, 2,000-property ontology, one run per model.*

The newer model improved the full schema (0.65 to 0.725 Property Hit) but scored lower on `subset_fallback`: 0.95 to 0.8875, and 40 of 40 to 37 of 40 compiled. Track B compile went from 39 of 60 to 36 of 60. If you swap models, re-run your evaluation on the configuration you actually use.

Two caveats. These are single runs, and the 3.7 full-schema score itself differed between the first live run and the re-run (0.82 and 0.65), so treat each gap as rough. And neither run had a "no ontology" condition, so the comparison shows how the way you send the same ontology changes accuracy and cost, not how much an ontology helps in the first place.

## Repair and staged retries work, on the mechanical arm

An Intent can be valid, compile, and still return nothing, for example because a filter uses a plant code that does not exist. Instead of asking the model to fix the failed Cypher, Ontographia hands back the execution result and asks for a corrected Intent, which is validated and compiled again. With the 40 gold Intents' filter values deliberately broken, final execution success was 0 without feedback and 1.00 with it, and every emitted query matched what the compiler builds.

The adaptive policy for H3 starts with the subset and one retry, and escalates to the full schema with up to five retries only when validation fails. On easy questions it matched an always-full-schema control (Property Hit 1.00, 40 of 40) at 1,247 instead of 13,710 p95 tokens. On hard questions it escalated every time and recovered, at 2 model calls on average instead of 1.

Both show that the loops recover when the correction is right; how often a real model gets the correction right is not yet measured.

## Fifteen public schemas load; answer quality is unproven

All 15 Track B schemas converted to the Canonical Ontology Model and loaded, with average coverage of 100% for relationship types, about 96% for node labels, and about 81% for properties. The gaps come mainly from inconsistent wording in the source schemas and noise in my extraction.

For answers, I sampled 60 questions (seed 53) for the movies and recommendations databases, ran them against `demo.neo4jlabs.com` with Gemini 3.7 Flash, and compared rows with the dataset's gold Cypher. 41 of 60 compiled (about 68%), and exact row-set matches were 1 of 38, about 3%. Each re-run also produced a single match.

That number is low, and it mixes Intent extraction errors, schema conversion gaps, and correct Cypher written differently from the gold query. It shows the pipeline runs end to end on someone else's schema, not that answer quality generalizes.

## What these results do not show

Each live condition ran once. H2 and H3 have no dedicated live runs, and everything live is Gemini. The end-to-end sample from Part 2 is small: one of four attempts answered the question.

The hallucination claim stays narrow. Names outside the ontology are stopped before anything reaches the database, but a real name chosen wrongly can still pass, and factual errors are out of scope. Subsetting lowers the chance of a wrong pick without eliminating it, and the exact-match subset still misses synonyms.

## Next: Intent-level gold answers, synonym-aware subsetting, real ontologies

No dates yet:

1. Gold answers written as Intents, and a metric that accepts semantically equivalent Cypher instead of an exact row match.
2. Subsetting that handles synonyms and spelling variants of domain terms.
3. Trials on real enterprise ontologies and production databases, covering H1 to H3 and the execution path.

The repository [roadmap](https://github.com/edgesentry/ontographia/blob/main/docs/roadmap.md) tracks these.

## Try the evaluation on your own ontology

Part 1 asked whether a natural-language interface could follow what users ask and still produce deterministic, auditable Cypher. At 2,000 properties, my answer is that validation alone is not enough: controlling what the model sees matters as much as checking what it writes.

`pip install "ontographia[llm]"` installs the experimental Intent layer. The harness and full result tables are under `examples/llm/eval/`, and the [Evaluation guide](https://edgesentry.github.io/ontographia/evaluation/) explains how to run each track. If you run Track A against your own schema, I would like to know where the subset missed vocabulary and which wrong-but-real names got through; issues are open on the [repository](https://github.com/edgesentry/ontographia).

---

*Open source project:* [github.com/edgesentry/ontographia](https://github.com/edgesentry/ontographia)
*Documentation:* [edgesentry.github.io/ontographia](https://edgesentry.github.io/ontographia/)
*Release notes:* [v0.1.6](https://github.com/edgesentry/ontographia/releases/tag/v0.1.6)
*Author:* Yohei Onishi
*Tags:* `#Neo4j #Cypher #KnowledgeGraph #GraphRAG #AIAgents #EnterpriseAI #LLMEvaluation`
