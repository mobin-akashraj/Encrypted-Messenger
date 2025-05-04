"""
Build script for Secure Messenger Application
Creates a standalone executable using PyInstaller
"""

import os
import sys
import shutil
import subprocess
import platform

def main():
    # Print welcome message
    print("=" * 60)
    print("Secure Messenger - Build Script")
    print("=" * 60)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("[✓] PyInstaller is installed")
    except ImportError:
        print("[!] PyInstaller is not installed. Installing now...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("[✓] PyInstaller installed successfully")
    
    # Check for required libraries
    required_libs = ["customtkinter", "cryptography", "pillow"]
    missing_libs = []
    
    for lib in required_libs:
        try:
            __import__(lib)
            print(f"[✓] {lib} is installed")
        except ImportError:
            missing_libs.append(lib)
    
    # Install missing libraries
    if missing_libs:
        print(f"[!] Installing missing libraries: {', '.join(missing_libs)}")
        for lib in missing_libs:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
            print(f"[✓] {lib} installed successfully")
    
    print("\nPreparing to build executable...")
    
    # Create build directory if it doesn't exist
    if not os.path.exists("build"):
        os.makedirs("build")
        print("[✓] Created build directory")
    
    # Determine the icon based on OS
    icon_option = []
    if platform.system() == "Windows":
        icon_path = os.path.join("resources", "icon.ico")
        if os.path.exists(icon_path):
            icon_option = ["--icon", icon_path]
            print(f"[✓] Using icon: {icon_path}")
    elif platform.system() == "Darwin":  # macOS
        icon_path = os.path.join("resources", "icon.icns")
        if os.path.exists(icon_path):
            icon_option = ["--icon", icon_path]
            print(f"[✓] Using icon: {icon_path}")
    
    # PyInstaller command
    app_name = "SecureMessenger"
    main_script = "app.py"  # Your main script file
    
    # Basic PyInstaller options
    pyinstaller_options = [
        "--name", app_name,
        "--onefile",  # Create a single executable
        "--windowed",  # Don't show console window
        "--clean",  # Clean PyInstaller cache
        "--noconfirm",  # Replace output directory without confirmation
        "--log-level", "WARN",  # Reduce log output
    ]
    
    # Add icon if available
    if icon_option:
        pyinstaller_options.extend(icon_option)
    
    # Add additional options to avoid antivirus flagging
    pyinstaller_options.extend([
        # Exclude debug and test modules
        "--exclude-module", "pytest",
        "--exclude-module", "unittest",
        "--exclude-module", "pdb",
        
        # Strip binaries to reduce size and avoid unnecessary signatures
        "--strip",
        
        # Don't include UPX (some antiviruses flag UPX-packed executables)
        "--noupx",
    ])
    
    # Add resources directory if it exists
    if os.path.exists("resources"):
        pyinstaller_options.extend(["--add-data", f"resources{os.pathsep}resources"])
        print("[✓] Including resources directory")
    
    # Add main script
    pyinstaller_options.append(main_script)
    
    print("\nBuilding executable with PyInstaller...")
    print(f"Command: pyinstaller {' '.join(pyinstaller_options)}")
    
    # Run PyInstaller
    try:
        subprocess.check_call([sys.executable, "-m", "PyInstaller"] + pyinstaller_options)
        print("\n[✓] Build completed successfully!")
        
        # Get output paths
        dist_path = os.path.abspath("dist")
        executable_path = os.path.join(dist_path, app_name + (".exe" if platform.system() == "Windows" else ""))
        
        print(f"\nExecutable created at: {executable_path}")
        print("\nBuild Information:")
        print(f"  - OS: {platform.system()} {platform.version()}")
        print(f"  - Python: {platform.python_version()}")
        
        # Get file size
        size_bytes = os.path.getsize(executable_path)
        size_mb = size_bytes / (1024 * 1024)
        print(f"  - File Size: {size_mb:.2f} MB")
        
    except subprocess.CalledProcessError as e:
        print(f"\n[✗] Build failed with error: {e}")
        return 1
    
    print("\n" + "=" * 60)
    print("Build complete! Your app is ready for distribution.")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())