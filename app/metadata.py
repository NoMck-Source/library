import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


def extract_epub_metadata(epub_path: str | Path) -> dict[str, str | None]:
    """Extracts metadata from an EPUB file."""
    epub_path = Path(epub_path)
    if not epub_path.exists():
        raise FileNotFoundError(epub_path)

    with zipfile.ZipFile(epub_path, "r") as zf:
        # Find package document (OPF) file path
        container = zf.read("META-INF/container.xml")
        tree = ET.fromstring(container)
        rootfile_el = tree.find(
            ".//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile"
        )
        if rootfile_el is None:
            raise ValueError("OPF rootfile not found in container.xml")
        opf_path = rootfile_el.attrib["full-path"]

        # Read metadata from OPF file
        opf_data = zf.read(opf_path)
        opf_tree = ET.fromstring(opf_data)
        ns = {"dc": "http://purl.org/dc/elements/1.1/"}

        # Extract metadata
        title_el = opf_tree.find(".//dc:title", ns)
        author_el = opf_tree.find(".//dc:creator", ns)

        # Return metadata as dictionary
        return {
            "title": title_el.text if title_el is not None else None,
            "author": author_el.text if author_el is not None else None,
            "path": str(epub_path),
        }
