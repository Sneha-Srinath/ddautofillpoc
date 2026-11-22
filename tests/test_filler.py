from core import engine
from core.filler import read_back, render_pages


def test_highlights_only_change_the_preview():
    res = engine.fill("tpl-c002", log=False)
    plain = render_pages(res.output_path, dpi=60)
    marked = render_pages(res.output_path, dpi=60, highlights={f.name: "#8A5A0B" for f in res.fields})
    assert len(plain) == len(marked) and plain[0] != marked[0]
    # the PDF on disk is untouched: rendering it again without highlights gives the same image
    assert render_pages(res.output_path, dpi=60)[0] == plain[0]
    assert read_back(res.output_path)["Telephone"] == "(601) 555-0142"
