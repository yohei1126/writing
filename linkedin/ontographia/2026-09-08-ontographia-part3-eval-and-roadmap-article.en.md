# Wrong but Real: Evaluating Intent-First Cypher Generation at 2,000 Properties (Ontographia Part 3)

![Cover: ontology scale narrowed to a subset, then evaluation results](../../images/ontographia-part3-linkedin-cover.jpg)

> **Series overview: Ontographia**
>
> Teams that query a graph database such as Neo4j in natural language usually choose between letting an AI write the query and locking the system to handwritten templates. This series examines the common compromise (agent skills plus template selection) and proposes another split: the AI extracts a structured Intent, and an ontology-checked, deterministic pipeline compiles the Cypher ([Ontographia](https://github.com/edgesentry/ontographia)).
>
> * **Part 1: [The Graph AI Dilemma: Let LLMs Write Cypher or Suffer Template Maintenance Hell?](https://www.linkedin.com/pulse/graph-ai-dilemma-let-llms-write-cypher-suffer-template-yohei-onishi-hj8kc/)**. Production bottlenecks, research review, Intent-first hypothesis
> * **Part 2: [The LLM Never Writes Cypher: Intent-First Design and Implementation](https://www.linkedin.com/pulse/llm-never-writes-cypher-intent-first-design-part-2-yohei-onishi-oyroc/)**. How the split works in practice
> * **Part 3: Evaluation and Roadmap** *(This article)*. What the measurements support, what they do not, and what comes next
> * Japanese edition: [Zenn article](https://zenn.dev/yohei/articles/2026-09-08-ontographia-eval-and-roadmap)
>
> * Documentation: [edgesentry.github.io/ontographia](https://edgesentry.github.io/ontographia/)
> * Repository: [github.com/edgesentry/ontographia](https://github.com/edgesentry/ontographia)

---

Ontology validation stops names that do not exist. It cannot stop a real name that is the wrong one. Once an ontology grows to a few hundred properties, those wrong-but-real names fill the prompt: in my stress test, all 40 deliberately wrong Intents compiled cleanly at 200 properties and again at 2,000.

What helped most was controlling what the model sees. Sending only the part of the ontology a question touches, with a fallback to the full schema, cut prompt tokens by about 91% on the 2,000-property ontology (13,765 to 1,301 p95) and raised correct property choices by an average of 19.5 points in a live evaluation with Gemini 3.8 Flash. But subsetting alone has high variance and requires the fallback, and exact match on a public-benchmark spot check was about 3%.

## Three hypotheses, with pass criteria fixed in advance

[Part 2](https://www.linkedin.com/pulse/llm-never-writes-cypher-intent-first-design-part-2-yohei-onishi-oyroc/) moved three ideas from Text-to-Cypher research to the Intent layer. I wrote a pass criterion for each into code before running anything:

* H1, ontology subsetting: on the 2,000-property ontology, the share of Intents that pick the right property (Property Hit) beats the full schema by at least 10 points, p95 prompt tokens drop by at least 30%, and compile success does not fall.
* H2, Intent repair from execution feedback: final execution success improves by at least 20 points.
* H3, staged retries: at least 30% fewer tokens on easy questions with no loss in quality.

A fourth question: does the ontology model work on schemas I did not write?

## Two tracks: a stress test I built and fifteen schemas I did not

Track A is a synthetic manufacturing domain with 40 questions, each with a gold Intent, at 16, 200, and 2,000 properties. The larger versions are padded with near-duplicates such as `plant_id` next to `plant_code` and `factory_id`, the overlap that builds up in enterprise graphs after years of system integration.

Most of Track A runs as a deterministic simulation arm ("arm" as in one experimental condition of a trial): fixed simulation rules replace the live model, so a failure points at the pipeline rather than at sampling noise. It tests whether the control loops work, not how capable a model is. For H1, I also ran live LLM evaluations with Gemini 3.8 Flash (`ontographia-gemini-3.8` via LiteLLM, PyPI `ontographia[llm]==0.1.6`, temperature 0).

Track B uses 15 public database schemas from Neo4j's [text2cypher-2025v1](https://huggingface.co/datasets/neo4j/text2cypher-2025v1) dataset, from movies to healthcare.

## At 200 properties, wrong names compile cleanly

The baseline sends the full schema and feeds the pipeline Intents that pick a distractor. On the 16-property ontology there are no distractors, so validation rejected all 40 wrong names as unknown. On the 200- and 2,000-property ontologies, the same 40 wrong Intents passed validation and compiled, 40 of 40 both times. The validator can check that a name exists, not that it is the name the user meant. That is the silent false positive from Part 1, reproduced on demand. The full prompt also grows from 1,359 tokens to 2,460 to 13,710.

## Showing the model less: live evaluation at 2,000 properties

Subsetting matches words in the question against ontology names, keeps the matched classes and the relationships that connect them, and sends only that. The recommended setting, `subset_fallback`, goes back to the full schema only if extraction or validation fails on the subset.

In deterministic simulation, Property Hit went from 0.50 to 1.00 with all 40 compiled, and p95 tokens dropped from 13,710 to 1,247 (~91%). But the simulation only errs on distractors it can see, so that mostly confirms the subset hides them.

Live LLM evaluation provides the real test. Using Gemini 3.8 Flash on the published package (`ontographia[llm]==0.1.6`, temperature 0), I evaluated the 2,000-property ontology across 5 repeated runs (large n=5, mean ± sample sd). Every run supported the hypothesis.

On the full schema, Property Hit was 0.683 ± 0.069, compile success was 28.4 ± 3.0 of 40, and p95 prompt tokens reached 13,765.

With `subset_fallback`, Property Hit reached 0.878 ± 0.065, compile success rose to 36.4 ± 2.3 of 40, and p95 prompt tokens dropped to 1,301. That is an average gain of +19.5 points in Property Hit and a 90.5% token reduction (about 91%), while falling back to the full schema only 17.0% ± 2.7% of the time. Neither configuration produced invented names or near-duplicate confusions that were not in the schema.

Subsetting alone without fallback scored 0.720 ± 0.086 Property Hit and 29.8 ± 3.7 compiled. Because an exact-match subset occasionally misses vocabulary, subsetting alone exhibits high variance (sd = 0.086). In production, the fallback mechanism is essential.

A smaller 200-property evaluation (mid n=3) showed the same pattern: full scored 0.683 ± 0.031 (p95 tokens 2,515), subset scored 0.717 ± 0.051, and `subset_fallback` scored 0.858 ± 0.038 (p95 tokens 1,301), with all verdicts supporting H1.

One caveat remains: neither condition had a "no ontology" baseline, so the comparison shows how the way you send the same ontology changes accuracy and cost, not how much an ontology helps in the first place.

## Repair and staged retries work in deterministic simulation

An Intent can be valid, compile, and still return nothing, for example because a filter uses a plant code that does not exist. Instead of asking the model to fix the failed Cypher, Ontographia hands back the execution result and asks for a corrected Intent, which is validated and compiled again. With the 40 gold Intents' filter values deliberately broken, final execution success was 0 without feedback and 1.00 with it, and every emitted query matched what the compiler builds.

The adaptive policy for H3 starts with the subset and one retry, and escalates to the full schema with up to five retries only when validation fails. On easy questions it matched an always-full-schema control (Property Hit 1.00, 40 of 40) at 1,247 instead of 13,710 p95 tokens. On hard questions it escalated every time and recovered, at 2 model calls on average instead of 1.

Both show that the loops recover when the correction is right; how often a real model gets the correction right is not yet measured.

## Fifteen public schemas load; answer quality is unproven

All 15 Track B schemas converted to the Canonical Ontology Model and loaded, with average coverage of 100% for relationship types, about 96% for node labels, and about 81% for properties. The gaps come mainly from inconsistent wording in the source schemas and noise in my extraction.

For answers, I sampled 60 questions (seed 53) for the movies and recommendations databases, ran them against `demo.neo4jlabs.com` with Gemini 3.7 Flash, and compared rows with the dataset's gold Cypher. 41 of 60 compiled (about 68%), and exact row-set matches were 1 of 38, about 3%. Each re-run also produced a single match.

That number is low, and it mixes Intent extraction errors, schema conversion gaps, and correct Cypher written differently from the gold query. It shows the pipeline runs end to end on someone else's schema, not that answer quality generalizes.

## What these results do not show

While H1 now has repeated live runs (mid n=3, large n=5), H2 and H3 have no dedicated live runs, and all live evaluation is Gemini 3.8 Flash. The end-to-end sample from Part 2 is small: one of four attempts answered the question.

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
