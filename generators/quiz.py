#!/usr/bin/env python3
"""Render a page per quiz (content/<team>/quizzes/*.yml: safety quizzes and game
rules tests) as quiz-<id>.html:
questions and choices shuffled on every attempt, retakes until the pass mark,
the "why" for each miss, and on a pass a QR code for that skill's pre-filled
sign-off form - the mentor watches the practical and signs off. The quiz never
records anything; the sign-off does."""

import json

from jinja2 import Environment, FileSystemLoader

import checklist
import common
import overview


def main():
    ctx = checklist.load_ctx()
    team = common.load_team()
    env = Environment(loader=FileSystemLoader(common.TEMPLATES), trim_blocks=True, lstrip_blocks=True)
    common.copy_brand_assets()
    for qid, doc in common.load_quizzes().items():
        q = doc["quiz"]
        item = ctx["all_items"].get(q["item"])
        if item is None:
            raise SystemExit(f"quiz {qid}: no item {q['item']}")
        signoff = common.signoff_link(item, ctx["trees"], team)
        questions = [{"q": x["q"], "choices": x["choices"], "answers": x.get("answers") or [x["answer"]], "why": x["why"]} for x in doc["questions"]]
        common.write_html(
            env, "quiz.html.j2", f"quiz-{qid}.html",
            team=team["team"], season=ctx["season"], quiz=q, item=item, count=len(questions), safety=q.get("kind", "safety") == "safety",
            data=json.dumps({"pass": q.get("pass", 100), "questions": questions}).replace("</", "<\\/"),
            signoff=signoff, signoff_qr=overview.qr_data_uri(signoff) if signoff else None,
            authors=", ".join(a["name"] for a in q.get("authored_by", [])),
        )


if __name__ == "__main__":
    main()
