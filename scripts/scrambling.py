# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "bs4",
#     "fonttools",
# ]
# ///
import random
import string
from typing import Dict

from bs4 import BeautifulSoup
from fontTools.ttLib import TTFont


def scramble_font(seed: int = 1234) -> Dict[str, str]:
	random.seed(seed)
	font = TTFont("src/fonts/Mulish-Regular.ttf")

	# Pick a Unicode cmap (Windows BMP preferred)
	cmap_table = None
	for table in font["cmap"].tables:
		if table.isUnicode() and table.platformID == 3:
			break
	cmap_table = table

	cmap = cmap_table.cmap

	# Filter codepoints for a-z and A-Z
	codepoints = [cp for cp in cmap.keys() if chr(cp) in string.ascii_letters]
	glyphs = [cmap[cp] for cp in codepoints]

	shuffled_glyphs = glyphs[:]
	random.shuffle(shuffled_glyphs)

	# Create new mapping
	scrambled_cmap = dict(zip(codepoints, shuffled_glyphs, strict=True))
	cmap_table.cmap = scrambled_cmap

	translation_mapping = {}
	for original_cp, original_glyph in zip(codepoints, glyphs, strict=True):
		for new_cp, new_glyph in scrambled_cmap.items():
			if new_glyph == original_glyph:
				translation_mapping[chr(original_cp)] = chr(new_cp)
				break

	font.save("src/fonts/Mulish-Regular-scrambled.ttf")

	return translation_mapping


def scramble_html(
	input: str,
	translation_mapping: Dict[str, str],
) -> str:
	def apply_cipher(text):
		repl = "".join(translation_mapping.get(c, c) for c in text)
		return repl

	# Read HTML file
	soup = BeautifulSoup(input, "html.parser")

	# Find all main elements
	main_elements = soup.find_all("main")
	skip_tags = {"code", "h1", "h2"}

	# Apply cipher only to text within main
	for main in main_elements:
		for elem in main.find_all(string=True):
			if elem.parent.name not in skip_tags:
				elem.replace_with(apply_cipher(elem))

	return str(soup)
