# Wrong but Real: Evaluating Intent-First Cypher Generation at 2,000 Properties (Ontographia Part 3)

> **Series overview: Ontographia**
>
> Teams that query a graph database such as Neo4j in natural language usually choose between letting an AI write the query and locking the system to handwritten templates. This series examines the common compromise (agent skills plus template selection) and proposes another split: the AI extracts a structured Intent, and an ontology-checked, deterministic pipeline compiles the Cypher ([Ontographia](https://github.com/edgesentry/ontographia)).
>
> * **Part 1: [The Graph AI Dilemma: Let LLMs Write Cypher or Suffer Template Maintenance Hell?](https://www.linkedin.com/pulse/graph-ai-dilemma-let-llms-write-cypher-suffer-template-yohei-onishi-hj8kc/)**. Production bottlenecks, research review, Intent-first hypothesis
> * **Part 2: [The LLM Never Writes Cypher: Intent-First Design and Implementation]([LINK TO PART 2])**. How the split works in practice
> * **Part 3: Evaluation and Roadmap** *(This article)*. What the measurements support, what they do not, and what comes next
>
> * Documentation: [edgesentry.github.io/ontographia](https://edgesentry.github.io/ontographia/)
> * Repository: [github.com/edgesentry/ontographia](https://github.com/edgesentry/ontographia)

---

Ontology validation stops names that do not exist. It does nothing about a real name that is the wrong one. Once an ontology grows to a few hundred properties, those wrong-but-real names are everywhere in the prompt. In my stress test, every one of 40 deliberately wrong Intents compiled cleanly at 200 properties and again at 2,000.

What helped was sending the model only the part of the ontology that the question touches. On the 2,000-property ontology it cut prompt tokens by about 91%. With Gemini 3.7 Flash it raised the rate of correct property choices by 12.5 points while all 40 questions still compiled. This article covers those results, the weaker parts (exact match on a public-benchmark spot check is about 3%), a re-run on the published package with a newer model that did not come out better overall, and the roadmap.

Harness scripts, baselines, and full tables live under `examples/llm/eval/` in the repository. How to run each track is in the [Evaluation guide](https://edgesentry.github.io/ontographia/evaluation/).

## What Part 2 left to measure

[Part 2]([LINK TO PART 2]) moved three ideas from Text-to-Cypher research to the Intent layer: ontology subsetting, Intent repair from execution feedback, and staged retries that spend more only on hard questions. Each one is a hypothesis about cost or accuracy, so this part tests them as H1 to H3, plus a fourth question: does the Canonical Ontology Model work on schemas I did not write?

I fixed the pass criteria in code before running anything.

* **H1 (subsetting):** on the 2,000-property ontology, the share of Intents that picked the right property (Property Hit) beats the full schema by at least 10 points, p95 prompt tokens drop by at least 30%, and compile success does not fall.
* **H2 (repair):** final execution success improves by at least 20 points, and every emitted query matches what the compiler builds.
* **H3 (staged retries):** at least 30% fewer tokens on easy questions with no loss in quality.

## Two tracks, and why most of Track A is a mechanical arm

**Track A** is a synthetic stress test on a manufacturing domain. It uses 40 questions with gold Intents and three ontology sizes: small (16 properties), mid (200), and large (2,000). The larger versions are padded with near-duplicate distractors such as `plant_id` next to `plant_code` and `factory_id`, the kind of overlap that builds up in real enterprise graphs after years of system integration. Injecting them on purpose makes it possible to see when a wrong pick happens.

**Track B** uses public data: 15 database schemas from Neo4j's [text2cypher-2025v1](https://huggingface.co/datasets/neo4j/text2cypher-2025v1) dataset (movies, social graphs, supply chains, healthcare, and more). It answers the objection that the design only works on a schema I built for it.

Most of Track A runs on what I call a mechanical arm. "Arm" is the clinical-trial word for one experimental condition. The mechanical arm replaces the live model with fixed simulation rules, so a failure points at the pipeline (validator, subsetting, repair state machine) rather than at sampling noise or a silent model update. It tests whether the control loops work. It says nothing about how capable a real model is, so for H1 I also ran a live arm with Gemini 3.7 Flash through LiteLLM at temperature 0.

## At 200 properties, wrong names stop being errors

The baseline sends the full schema and feeds the pipeline Intents that pick a distractor instead of the right property.

On the small ontology there are no distractors, so a wrong name is simply unknown and validation rejected all 40. On mid and large, the same 40 wrong Intents passed validation and compiled to Cypher, 40 out of 40 in both cases. The validator can check that a name exists. It cannot check that the name is the one the user meant.

That is the silent false positive from Part 1, reproduced on demand. The full prompt also grows quickly: 1,359 tokens on small, 2,460 on mid, and 13,710 on large.

## Showing the model less: subsetting on the large ontology

Subsetting matches words in the question against ontology names, keeps the matched classes and the relationships needed to connect them, and sends only that. The recommended setting, `subset_fallback`, goes back to the full schema only if extraction or validation fails on the subset.

On the mechanical arm, with the large ontology:

* Property Hit went from 0.50 with the full schema to 1.00 with the subset, a 50-point gain.
* p95 prompt tokens went from 13,710 to 1,247, about 91% fewer.
* Compile success stayed at 40 out of 40, and the fallback never fired.

The arm is built so that only distractors visible in the prompt cause wrong picks. With the subset, no distractors were exposed, so it induced no errors. That confirms the subset removes distractors from the prompt. Whether a real model stops making mistakes is a separate question, which is why the live run matters more.

With Gemini 3.7 Flash on the large ontology, the full schema scored 0.82 Property Hit and compiled 33 of 40. `subset_fallback` scored 0.95 and compiled 40 of 40, a gain of 12.5 points with the same 1,247-token p95. H1 passed on the live arm too.

The subset on its own did worse: 0.78 and 32 of 40, about 5 points below the full schema, because some questions needed vocabulary the exact-match subset missed. That is the practical lesson of H1. Subsetting needs the fallback in production. The model never invented a near-duplicate name it had not been shown.

## Recovering from empty results without rewriting Cypher

An Intent can be valid, compile, and still return nothing, for example because a filter uses a plant code that does not exist. Text-to-Cypher research usually hands the failed Cypher back to the model to fix. Ontographia hands back the execution result and asks for a corrected Intent, which then goes through validation and compilation again.

To test the loop, I took the 40 gold Intents and broke only their filter values, so every query compiled and every simulated execution came back empty. Without feedback, final execution success was 0. With feedback, it was 1.00, and every emitted query matched what the compiler builds from the corrected Intent. Unbroken Intents were included as a control to check that repair does not fire when nothing is wrong.

H2 is supported on the mechanical arm. The arm shows that the loop recovers when the correction is right. How often a real model produces the right correction depends on the model, and I have not measured it live.

## Spending less on easy questions

The adaptive policy starts with the subset and one retry, and escalates to the full schema with up to five retries only when validation fails. The control always uses the full schema with five retries.

On easy questions on the large ontology, adaptive matched the control on quality (Property Hit 1.00, 40 of 40 compiled) and cut p95 tokens from 13,710 to 1,247, the same 91% reduction. On hard questions, built so the subset is missing needed vocabulary, adaptive escalated every time and recovered, at an average of 2 model calls instead of 1.

H3 is supported on the mechanical arm. The live H1 runs already use the same subset-first path (`schema_policy=auto`), so it does not require a separate difficulty classifier.

## Fifteen public Neo4j databases

All 15 Track B schemas converted to the Canonical Ontology Model and loaded, 15 out of 15. Average coverage was 100% for relationship types, about 96% for node labels, and about 81% for properties. The missing properties come mainly from inconsistent wording in the source schema text and from noise in my extraction, rather than from something the model cannot represent.

Loading a schema is the easy part, so I also ran a spot check of answers. I sampled 60 questions (seed 53) for the movies and recommendations databases, ran question to Intent to Cypher against `demo.neo4jlabs.com` with Gemini 3.7 Flash, and compared the rows with those returned by the dataset's gold Cypher. 41 of 60 compiled (about 68%). Exact row-set matches were 1 of 38, about 3%.

That number is low. The gold answers are Cypher, not Intents, so exact match mixes three things: Intent extraction errors, gaps in schema conversion, and Cypher that is correct but written differently from the gold query. The spot check shows that the pipeline runs end to end on someone else's schema. It is not a state-of-the-art claim, and it is not evidence that the design generalizes well on answer quality.

One more generalization step: the business-term repair rules that started as manufacturing heuristics now live in a YAML mapping, and tests confirm the same engine works with a non-manufacturing (movies) mapping.

## Re-running on the published package: Gemini 3.7 Flash vs 3.8 Flash

After [v0.1.6](https://github.com/edgesentry/ontographia/releases/tag/v0.1.6) shipped the Intent layer on PyPI, I repeated the live evaluation on the published `ontographia[llm]` package, with the same settings as before (temperature 0, Track A with 40 questions, Track B with 60 questions at seed 53) and two models: Gemini 3.7 Flash and 3.8 Flash. Each condition ran once.

With both models, in every condition, no output contained a name the model had not been shown. Changing the model does not change the mechanism: the vocabulary is listed in the prompt and the output is validated, so unknown names stop there.

How the ontology was sent made a bigger difference than which model read it. On the large ontology, `subset_fallback` beat `full` on Property Hit by 30 points with 3.7 and by 16.25 points with 3.8, and cut p95 prompt tokens by about 90.5% with both. The earlier result held on the published package.

Neither run had a "no ontology" condition, and `full` also puts the whole ontology in the prompt. So the result says that the same ontology gives different Property Hit and token counts depending on how it is sent. It says nothing about the gain from using an ontology at all.

The newer model did not win across the board. Moving from 3.7 to 3.8 helped `full` and `subset` alone (on large, `full` went from 0.65 to 0.725), but the recommended `subset_fallback` went down: Property Hit from 0.95 to 0.8875 and compile from 40 of 40 to 37 of 40. Track B compile went from 39 of 60 to 36 of 60. If you swap models, re-run your evaluation set; a newer version can be worse on the configuration you actually use.

## What these results do not show

Each live condition ran once, so I cannot say how stable any of these differences are. The mechanical arm results are about the pipeline's control flow, not about model quality, and H2 and H3 have no dedicated live runs. Track B exact match is weak evidence either way, and in all three runs it was a single match. The end-to-end sample from Part 2 is also small: one of four attempts answered the question.

The hallucination claim stays narrow. Names that are not in the ontology are stopped before anything reaches the database. A real name chosen wrongly can still pass, which is the whole point of the Track A baseline, and factual errors are out of scope. Subsetting reduces the chance of a wrong pick by hiding distractors. It does not eliminate it, and the exact-match subset still misses synonyms.

## What I measured, limits, and what's next

**What I measured:** H1 to H3 on the mechanical arm; live H1 with Gemini 3.7 Flash using `subset_fallback`; all 15 public schemas loaded; the execution-match spot check with its limits; a generalized repair mapping; and the re-run on the published package with two model versions.

**Limits:** no state-of-the-art claim on Track B execution match; no live results across model families (everything here is Gemini; other families are open for anyone to try); and no full live coverage of H2 and H3.

**What's next (no dates):**

1. Gold answers written as Intents, and a metric that accepts semantically equivalent Cypher instead of requiring an exact row match.
2. Subsetting that handles synonyms and spelling variants of domain terms, not only exact matches.
3. Trials on real enterprise ontologies and production databases, covering H1 to H3 and the execution path.

The repository [roadmap](https://github.com/edgesentry/ontographia/blob/main/docs/roadmap.md) lists what comes next.

## Try the evaluation on your own ontology

Part 1 asked whether a natural-language interface could follow what users ask and still produce deterministic, auditable Cypher. At 2,000 properties, my answer is that validation alone is not enough, and that controlling what the model sees matters as much as checking what it writes.

For commands, profiles, and how to record runs, use the [Evaluation guide](https://edgesentry.github.io/ontographia/evaluation/) and the scripts under `examples/llm/eval/` (including the H1 live arm). `pip install "ontographia[llm]"` installs the experimental Intent layer. If you run Track A against your own schema, I would like to know where the subset missed vocabulary and which wrong-but-real names got through; issues are open on the [repository](https://github.com/edgesentry/ontographia).

---

*Open source project:* [github.com/edgesentry/ontographia](https://github.com/edgesentry/ontographia)
*Documentation:* [edgesentry.github.io/ontographia](https://edgesentry.github.io/ontographia/)
*Release notes:* [v0.1.6](https://github.com/edgesentry/ontographia/releases/tag/v0.1.6)
*Author:* Yohei Onishi
*Tags:* `#Neo4j #Cypher #KnowledgeGraph #GraphRAG #AIAgents #EnterpriseAI #LLMEvaluation`
