"""Word -> PDF for exact previews, using the Microsoft Word installed on this machine.

Conversions are cached in output/previews/ by file and modified time and run one at a time.
If Word is unavailable the caller falls back to an approximate HTML rendering (mammoth).
"""
from __future__ import annotations

import hashlib
import threading
from pathlib import Path

from core.config import OUTPUT_DIR

PREVIEW_DIR = OUTPUT_DIR / "previews"
_LOCK = threading.Lock()


class RenderError(Exception):
    pass


def _cache_path(path: Path) -> Path:
    key = hashlib.sha1(f"{path.resolve()}|{path.stat().st_mtime_ns}".encode()).hexdigest()[:16]
    return PREVIEW_DIR / f"{path.stem}_{key}.pdf"


def word_available() -> bool:
    try:
        import pythoncom  # noqa: F401
        import win32com.client  # noqa: F401
    except Exception:
        return False
    return True


def to_pdf(path: str | Path) -> Path:
    """Exact PDF rendering of a .docx (cached). Raises RenderError when Word cannot do it."""
    src = Path(path)
    out = _cache_path(src)
    if out.exists():
        return out
    if not word_available():
        raise RenderError("Microsoft Word is not available on this machine.")
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    with _LOCK:
        if out.exists():
            return out
        import pythoncom
        import win32com.client
        pythoncom.CoInitialize()
        word = doc = None
        try:
            word = win32com.client.DispatchEx("Word.Application")      # private Word process
            word.Visible = False
            word.DisplayAlerts = 0
            doc = word.Documents.Open(str(src.resolve()), ReadOnly=True, AddToRecentFiles=False)
            doc.ExportAsFixedFormat(str(out.resolve()), 17)             # 17 = wdExportFormatPDF
        except Exception as exc:
            raise RenderError(f"Word could not convert this document: {exc}") from exc
        finally:
            try:
                if doc is not None:
                    doc.Close(False)
                if word is not None:
                    word.Quit()
            except Exception:
                pass
            pythoncom.CoUninitialize()
    if not out.exists():
        raise RenderError("Word did not produce a PDF for this document.")
    return out


def to_html(path: str | Path) -> str:
    """Approximate rendering used when Word is not available."""
    import mammoth
    with open(path, "rb") as fh:
        body = mammoth.convert_to_html(fh).value
    return ("<html><body style=\"font-family:Calibri,Segoe UI,sans-serif;max-width:780px;margin:24px auto;"
            f"padding:32px;background:#fff;line-height:1.5\">{body}</body></html>")
