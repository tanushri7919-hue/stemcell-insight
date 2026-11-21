# database package
import os as _os
import sys as _sys

# Detect if Streamlit Cloud is running this file as the entry point
# (happens when deployment was configured with database/__init__.py instead of app.py)
# When Streamlit runs a script, it executes the file content directly.
# When this file is imported as a package, the check below won't trigger.
def _is_streamlit_entry():
    """Check if this file is being executed as a Streamlit app entry point."""
    try:
        # Streamlit adds its runtime to sys.modules before executing the script
        if 'streamlit' in _sys.modules or 'streamlit.runtime' in _sys.modules:
            # Check if we're the main script (not being imported as a package)
            import inspect
            frame = inspect.currentframe()
            # If called from module level of this file being run as script
            if frame and frame.f_back and frame.f_back.f_globals.get('__name__') == '__main__':
                return True
            # Alternative check: if streamlit's script runner is in the call stack
            if any('script_runner' in str(getattr(f, 'filename', '')) for f in inspect.stack()):
                return True
    except Exception:
        pass
    return False

if _is_streamlit_entry():
    _root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
    if _root not in _sys.path:
        _sys.path.insert(0, _root)
    _app_path = _os.path.join(_root, "app.py")
    with open(_app_path, encoding="utf-8") as _f:
        exec(compile(_f.read(), _app_path, "exec"))
