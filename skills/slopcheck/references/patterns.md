# The patterns, in detail

Language-neutral explanations. The regexes live in `../scripts/lang/*.json`; this file
is the reasoning behind them, for writers and for pack authors.

## Negative parallelism

> "This is not a technical problem, but a cultural one."
> "Not just faster, but fundamentally different."
> "Rather than replacing people, it empowers them."

The most reliable single tell. It creates the shape of an insight without supplying one:
a thing is denied, a near-synonym is affirmed, and the reader feels a turn has happened.

Used once, deliberately, it is good rhetoric. The problem is density. A human writer
reaches for it when a genuine contrast is doing work. A model reaches for it as a
default cadence, which is why counting occurrences separates the two better than
judging any single instance.

**Budget: one per text.** Replace the rest with the direct claim.

## Rule of three

> "It improves accuracy, reduces error, and optimizes performance."

Ancient, effective, and in generated text it becomes the default shape of every list.
Three grammatically parallel items produce an even, closing cadence; repeated across
paragraphs it reads as a metronome.

Use two items, or four of unequal length and grammatical shape.

**Detection limit.** slopcheck only catches series of single words: `fast, cheap and
reliable`. Multi-word triads like "it improves accuracy, reduces error and optimizes
performance" are invisible to it, because every regex broad enough to catch them also
matched ordinary conditionals and appositions in testing. Counting them is a job for
the human eye. Precision was chosen over recall on purpose: see `CONTRIBUTING.md`.

## Signposting

> "It's important to note that..." · "In summary..." · "Here's the thing:"

Sentences about the text instead of sentences of the text. Models produce them because
they are trained on documents that scaffold themselves for skimmers.

Delete the phrase. Whatever follows it is the real sentence.

Special case: a formula borrowed from your own earlier writing becomes a tic on second
use. If you wrote "here's the uncomfortable part" once, it is spent.

## Inflated vocabulary

> delve · pivotal · robust · seamless · testament to · unlock · elevate · landscape ·
> realm · tapestry · foster · leverage · harness · plays a crucial role · paves the way

Words that claim importance the sentence has not earned. Each is legitimate somewhere.
Together, at density, they are the vocabulary of a text trying to sound like it matters.

Local equivalents exist in every language and are the first thing a new pack should
collect.

## Trailing participles

> "...adoption grew 40%, highlighting the growing importance of automation."

A clause bolted onto a finished sentence, asserting a consequence that was never argued.
It converts a fact into a conclusion for free.

Cut it, or promote it to its own sentence with a real subject, at which point you will
usually notice you cannot support it.

## Vague attribution

> "Experts say..." · "Studies show..." · "It is widely believed that..."

Authority with nothing behind it. Models generate these because the training data is
full of them and because they cannot cite what they do not have.

Name the source or drop the claim. Of every pattern here, this one is most often a
factual problem: the claim itself may be invented.

## Formulaic openers and closers

> "In today's rapidly evolving landscape..." · "In conclusion..." ·
> "At the end of the day, one thing is clear:"

The stock first and last lines. The closer is worse: models cannot resist restating the
thesis with symmetry, which is precisely where a human writer would say the thing they
have not worked out yet.

End on the unresolved part, or on a question you actually want answered.

## Formatting

Em dashes used as dramatic pauses, arrow bullets, bold on every other phrase, emoji as
section markers, curly quotes in plain-text contexts, headings that skip levels.

Mostly a density problem again. Note that some languages use the dash legitimately for
parenthetical clauses; packs should account for that.

## Rhythm

Human sentence lengths are bursty: a long winding one, then four words. Generated prose
clusters near the mean.

slopcheck reports the coefficient of variation of words per sentence. Below roughly
0.45, add one long sentence and one fragment. This threshold is a heuristic tuned on a
handful of fixtures, not a validated constant; treat it as a nudge.

## Copula avoidance

Models under-use plain "to be" and replace it with heavier constructions:
"the model performs an analysis of the data" instead of "the model analyzes the data".
The result is a noun-dense prose with fewer pronouns. Measured on English Wikipedia
submissions, the frequency drop exceeds 10%.

slopcheck reports the rate per 100 words as information, not as a finding, because the
floor varies by language and genre.
