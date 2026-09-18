# preload_patch.py
import importlib.metadata as _im

_original_version = _im.version
_original_distribution = _im.distribution

def _safe_version(pkg_name):
    try:
        return _original_version(pkg_name)
    except Exception:
        return "1.0.0"

def _safe_distribution(pkg_name):
    try:
        return _original_distribution(pkg_name)
    except StopIteration:
        raise _im.PackageNotFoundError(f"No package {pkg_name}")

_im.version = _safe_version
_im.distribution = _safe_distribution