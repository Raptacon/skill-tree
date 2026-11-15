# Safety quizzes

One file per quiz. Each quiz is the written half of a safety sign-off: you pass the quiz, then a mentor
watches you use the tool and signs you off on the skill (`item`). The quiz never replaces the sign-off.

```yaml
quiz:
  id: band-saw                 # file name without .yml
  name: Band saw safety quiz
  item: tool-band-saw          # the skill this quiz is for
  pass: 100                    # percent needed to pass; retakes are unlimited
  authored_by: [{name, github?}]
  source: where the original questions came from
questions:
  - q: The question.
    choices: [A, B, C, D]      # shown shuffled
    answer: B                  # the correct choice, word for word
    # or answers: [A, C]       # "check all that apply": every listed choice, and only those
    why: One line on why, shown after a wrong answer.
    origin: schoology | new    # ported from the Schoology test, or added for this bank
    review: true               # new or changed: a mentor should read it before it counts
```

Choices never refer to each other by letter ("both a and b"): the quiz shuffles them.
