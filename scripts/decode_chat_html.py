import json
import sys

from util import base85json2obj

if __name__ != "__main__":
    raise NotImplementedError("cannot be used as a module")

all_data = str(sys.stdin.read())
all_data = all_data.strip()

obj = base85json2obj(all_data)

frags = []
for message in obj:
    role = message["role"]
    assert role in {"system", "user", "assistant"}
    cur_html_fragment = f"<h3>{role.upper()}</h3>"
    content = message["content"]
    if isinstance(content, str):
        content_html = f'<div><pre style="white-space: pre-wrap; word-break: keep-all;">{content}</pre><div>'
    else:
        assert isinstance(content, list)
        content_html = "<div>"
        for e in content:
            assert e["type"] in {"text", "image_url"}
            if e["type"] == "text":
                content_html += f"<pre style=\"white-space: pre-wrap; word-break: keep-all;\">{e['text']}</pre><p>"
            elif e["type"] == "image_url":
                content_html += (
                    f"<img src={e['image_url']['url']} height=256></img>"
                )
    cur_html_fragment += "\n" + content_html + "\n"
    frags.append(cur_html_fragment)

print("\n\n<hr>\n\n".join(frags))
