# Research and positioning

Sources inspected during preparation on 8 November 2026. Links support the background described here; none establish that this newly built suite defeats any current model.

1. [HackerRank event](https://www.hackerrank.com/event/micro1-eval-hackathon): the event asks for original reproducible evaluations and recommends a small number of meaningful tasks. Its deadline is 9 November 2026, 05:15 GMT (10:45 IST).
2. [Participant guide](https://hrcdn.net/s3_pub/istreet-assets/R_8vs8ejamSPapSbUxmcWQ/Eval_Hackathon_Participant_Guide.pdf): reference answers, validated grading, repeated trials, transcripts, reproducibility, and participant review guide the package structure.
3. [Official FAQ](https://www.micro1.ai/hackathon/faq): submission consists of code/supporting files, a short video link, and a description. Check the live challenge instructions for exact fields and finalization behavior.
4. [Feast point-in-time joins](https://docs.feast.dev/getting-started/concepts/point-in-time-joins): historical features are reconstructed relative to entity timestamps. AsOf adds explicit fictional availability-time and correction semantics; it does not claim to reproduce Feast's full behavior.
5. [Anthropic evaluation guidance](https://www.anthropic.com/research/demystifying-evals-for-ai-agents): outcome-based grading, clean trials, and checking transcripts informed the evaluation protocol.
6. [Spider 2.0 repository](https://github.com/xlang-ai/Spider2): enterprise SQL evaluation already exists. AsOf is a small diagnostic suite about revision/filter ordering and interacting histories, not a replacement or scale comparison. No Spider tasks were imported.
7. [SQLite SELECT](https://www.sqlite.org/lang_select.html), [window functions](https://www.sqlite.org/windowfunctions.html), and [Python sqlite3](https://docs.python.org/3/library/sqlite3.html): primary documentation for local query execution and the reference queries.
8. [OpenRouter API reference](https://openrouter.ai/docs/api/reference/overview): optional chat-completions request format. API availability and prices are not assumed or bundled.

## Why this choice for this participant

The user's stated skills are Python, SQL, maths, and data analysis. Temporal SQL allows the participant to review concrete records and calculations rather than rely on a domain they do not know. It also avoids a fragile browser environment or complex distributed infrastructure near the deadline.

## Contribution to investigate

The proposed contribution is a small set of controlled, mechanically checked cases showing whether difficulties arise from individual temporal rules or their composition. This is a research hypothesis. Establishing a new model limitation requires real model runs and honest comparison with prior work.
