import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory

from api_wrapper import CompressionAPI

# Load .env from project root so GEMINI_API_KEY is available
load_dotenv(Path(__file__).resolve().parent / ".env")
from document_loader import extract_text_from_file
from llm_service import summarize_with_llm, chat_with_llm

app = Flask(__name__, static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024  # 32 MB max upload

# In-memory store for current document (used by chat and dashboard)
_current_result = None
_current_filename = None
_current_doc_text = None
_current_llm_summary = None
_chat_history = []  # list of {"role": "user"|"assistant", "content": "..."}


def _get_api_key():
    """API key from request (header or form) or from .env (GEMINI_API_KEY / GOOGLE_API_KEY)."""
    key = request.headers.get("X-API-Key") or request.form.get("api_key")
    if not key and request.is_json:
        try:
            key = (request.get_json(silent=True) or {}).get("api_key")
        except Exception:
            pass
    return (key or "").strip() or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""


@app.route("/")
def index():
    """Serve the main dashboard page."""
    return send_from_directory(".", "dashboard_live.html")


@app.route("/api/upload", methods=["POST"])
def upload():
    """
    Accept a file upload, extract text, run compression + LLM summarization.
    API key from .env (GEMINI_API_KEY).
    """
    global _current_result, _current_filename, _current_doc_text, _current_llm_summary, _chat_history

    try:
        if "file" not in request.files:
            return jsonify({"error": "No file in request"}), 400

        file = request.files["file"]
        if not file or not getattr(file, "filename", None) or file.filename.strip() == "":
            return jsonify({"error": "No file selected"}), 400

        chunk_strategy = request.form.get("chunk_strategy", "paragraph")
        api_key = _get_api_key()

        # Determine extension from filename (safe for Windows)
        filename = file.filename.strip()
        ext = os.path.splitext(filename)[1].lower()
        if ext not in (".txt", ".pdf", ".docx", ".doc"):
            return jsonify({"error": "Unsupported file type. Use .txt, .pdf, or .docx"}), 400
        suffix = ext

        # Write to temp file using stream (avoids Windows save/overwrite issues)
        tmp_path = None
        try:
            fd, tmp_path = tempfile.mkstemp(suffix=suffix)
            os.close(fd)
            with open(tmp_path, "wb") as f:
                f.write(file.stream.read())
            text = extract_text_from_file(tmp_path)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": f"Failed to read file: {str(e)}"}), 500
        finally:
            if tmp_path and os.path.isfile(tmp_path):
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

        if not text or not text.strip():
            return jsonify({"error": "No text could be extracted from the file"}), 400

        _current_doc_text = text
        _chat_history = []

        # Structured extraction (rule-based)
        try:
            api = CompressionAPI(chunk_strategy=chunk_strategy)
            result = api.compress_text(text)
        except Exception as e:
            return jsonify({"error": f"Compression failed: {str(e)}"}), 500

        # LLM summarization (if API key in .env)
        llm_summary = None
        if api_key:
            try:
                llm_summary = summarize_with_llm(text, api_key)
                _current_llm_summary = llm_summary
            except Exception as e:
                result["llm_summary_error"] = str(e)
                _current_llm_summary = None
        else:
            result["llm_summary_error"] = "No API key. Add GEMINI_API_KEY to your .env file and restart the app."
            _current_llm_summary = None

        result["llm_summary"] = llm_summary
        _current_result = result
        _current_filename = filename
        return jsonify(result)

    except Exception as e:
        import traceback
        return jsonify({
            "error": f"Upload failed: {str(e)}",
            "detail": traceback.format_exc() if app.debug else None,
        }), 500


@app.route("/api/chat", methods=["POST"])
def chat():
    """Chat with the LLM about the current document. Requires API key."""
    data = request.get_json() or {}
    question = (data.get("question") or "").strip()
    api_key = _get_api_key()

    if not question:
        return jsonify({"error": "No question provided", "answer": ""}), 400

    if not api_key:
        return jsonify({
            "error": "API key required for chat",
            "answer": "Set GEMINI_API_KEY in your .env file and restart the app.",
        }), 400

    if not _current_doc_text and not _current_llm_summary:
        return jsonify({
            "answer": "Please upload and summarize a document first, then ask your question.",
        })

    # Context: LLM summary + full doc (truncated in llm_service)
    context = (_current_llm_summary or "") + "\n\n---\n\n" + (_current_doc_text or "")

    try:
        answer = chat_with_llm(
            question=question,
            document_context=context,
            api_key=api_key,
            conversation_history=_chat_history,
        )
        _chat_history.append({"role": "user", "content": question})
        _chat_history.append({"role": "assistant", "content": answer})
        return jsonify({
            "answer": answer,
            "document": _current_filename or None,
        })
    except Exception as e:
        return jsonify({
            "answer": f"Error: {str(e)}",
            "document": _current_filename or None,
        })


@app.route("/api/status")
def status():
    """Return whether a document is loaded, LLM summary available, and if server has API key (.env)."""
    has_key = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
    return jsonify({
        "has_document": _current_result is not None,
        "filename": _current_filename,
        "has_llm_summary": bool(_current_llm_summary),
        "has_api_key": has_key,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
