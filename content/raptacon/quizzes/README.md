# Quizzes

One file per quiz. A safety quiz is the written half of a tool sign-off: you pass the quiz, then a mentor
watches you use the tool and signs you off on the skill (`item`). A rules test (`kind: rules`) covers a
game manual; a mentor signs you off once you pass. The quiz never replaces the sign-off.

```yaml
quiz:
  id: band-saw                 # file name without .yml
  name: Band saw safety quiz
  kind: safety                 # safety (default) or rules
  item: tool-band-saw          # the skill this quiz is for
  pass: 100                    # percent needed to pass; retakes are unlimited
  authored_by: [{name, github?}]
  source: where the original questions came from
  intro: rules tests only - one line on what it covers
  reference: {label, url}      # rules tests only - the manual the answers come from
questions:
  - q: The question.
    choices: [A, B, C, D]      # shown shuffled
    answer: B                  # the correct choice, word for word
    # or answers: [A, C]       # "check all that apply": every listed choice, and only those
    why: One line on why, shown after a wrong answer.
    origin: schoology | form | new   # ported from Schoology or a team Google Form, or added for this bank
    review: true               # new or changed: a mentor should read it before it counts
```

A rules test's `why` cites the manual section or rule, so a mentor can check the answer.
Choices never refer to each other by letter ("both a and b"): the quiz shuffles them.
