"""
PLUX library loader with automatic platform detection.
"""
import platform
import sys
import os


def get_plux_binary_path():
    """
    Determine the correct PLUX API binary path based on OS, architecture, and Python version.
    
    Returns:
        str: The directory name containing the appropriate binary
    
    Raises:
        OSError: If the platform is not supported
    """
    system = platform.system()
    
    # MacOS
    if system == "Darwin":
        # Detect architecture
        machine = platform.machine()
        if machine == "arm64":
            # Apple Silicon (M1, M2, etc.)
            arch_prefix = "M1"
        else:
            # Intel
            arch_prefix = "Intel"
        
        # Get Python version (major.minor, e.g., "311" for 3.11)
        py_version = ''.join(platform.python_version_tuple()[:2])
        
        return f"{arch_prefix}_{py_version}"
    
    # Linux
    elif system == "Linux":
        machine = platform.machine()
        if machine == "x86_64":
            return "Linux64"
        elif machine == "aarch64":
            # Check Python version for ARM32/ARM64
            py_version = ''.join(platform.python_version_tuple()[:2])
            if py_version == "38":
                return "LinuxARM64_38"
            elif py_version == "39":
                return "LinuxARM64_39"
            else:
                return "LinuxARM64_38"  # fallback
        elif "arm" in machine:
            py_version = ''.join(platform.python_version_tuple()[:2])
            if py_version == "311":
                return "LinuxARM32_311"
            else:
                return "LinuxARM32"

    # Windows
    elif system == "Windows":
        arch = platform.architecture()[0][:2] # "32" or "64"
        py_version = ''.join(platform.python_version_tuple()[:2])
        return f"Win{arch}_{py_version}"
    
    raise OSError(f"Unsupported platform: {system}")


def load_plux_library(base_path="PLUX-API-Python3"):
    """
    Load the PLUX library by adding the correct binary path to sys.path.
    
    Args:
        base_path: Base directory containing PLUX binaries (relative to project root)
    
    Returns:
        module: The imported plux module
    
    Raises:
        ImportError: If the PLUX library cannot be imported
    """
    binary_path = get_plux_binary_path()
    
    # Get the project root directory (parent of utils directory)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    full_path = os.path.join(project_root, base_path, binary_path)
    
    if full_path not in sys.path:
        sys.path.append(full_path)
    
    try:
        import plux
        print(f"Successfully loaded PLUX library from: {full_path}")
        return plux
    except ImportError as e:
        raise ImportError(
            f"Failed to import PLUX library from {full_path}. "
            f"Please ensure the binaries are installed correctly. Error: {e}"
        )
