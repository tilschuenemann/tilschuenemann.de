import json
import os
import time
from pathlib import Path
import random
from fontTools.ttLib import TTFont
import string
from jinja2 import Environment, FileSystemLoader
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

import os
import shutil
import random

from bs4 import BeautifulSoup, NavigableString
import string
from lxml import html
import json
from typing import Dict

from scripts.scrambling import scramble_font, scramble_html

env = Environment(
	loader=FileSystemLoader(["src"]),
	autoescape=True,
	trim_blocks=True,
	lstrip_blocks=True,
)

os.makedirs("out", exist_ok=True)
os.makedirs("out/projects", exist_ok=True)
os.makedirs("out/pages", exist_ok=True)
os.makedirs("out/assets", exist_ok=True)
os.makedirs("out/fonts", exist_ok=True)

shutil.copytree("src/assets", "out/assets", dirs_exist_ok=True)
shutil.copytree("src/fonts", "out/fonts", dirs_exist_ok=True)


class SiteBuilderHandler(FileSystemEventHandler):
	def __init__(self):
		super().__init__()

	def on_modified(self, event):
		if event.is_directory:
			return
		path = event.src_path
		build(path)


def build(path: Path) -> None:
	fpath = Path(path).relative_to(Path("src"))

	fpath_str = str(fpath)

	if fpath_str.startswith("_"):
		templates = [f for f in Path("src").rglob("*.html") if "_partials" not in f.parts]
		for template in templates:
			build(template)
		return

	template = env.get_template(fpath_str)
	output = template.render()

	if fpath.name == "sacrificing-accessibility-for-not-getting-web-scraped.html":
		translation_mapping = scramble_font()
		output = scramble_html(output, translation_mapping)
		shutil.copytree("src/fonts", "out/fonts", dirs_exist_ok=True)

	with open(f"out/{fpath_str}", "w") as f:
		f.write(output)
		print(f"Built: {fpath_str}")


if __name__ == "__main__":
	CF_PAGES = os.getenv("CF_PAGES")
	if CF_PAGES is None:
		event_handler = SiteBuilderHandler()
		observer = Observer()
		observer.schedule(event_handler, path=Path("src/"), recursive=True)
		observer.start()

		print("Running local watcher...")

		try:
			while True:
				time.sleep(1)
		except KeyboardInterrupt:
			observer.stop()
		observer.join()
	else:
		print("Running full static build for Cloudflare Pages...")
		for template in Path("src").rglob("*.html"):
			build(template)
