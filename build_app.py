#!/usr/bin/env python3
"""
Build script for Apocalypse Nightmare game.
Creates a standalone executable using PyInstaller.

Enhanced Version Features:
- 6 different endings with ASCII art
- Character trust systems (Alex, Maya, Ben, Jake)
- Resource management (Knowledge, Tech Parts, Cash)
- Smart contextual hint system
- Quick start options
- Enhanced visual feedback
- Fixed text overwriting issues
- Dramatic pause effects
- Progress indicators
"""

import os
import sys
import subprocess
import shutil

def install_pyinstaller():
    """Install PyInstaller if not already installed."""
    try:
        import PyInstaller
        print("✅ PyInstaller is already installed")
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller installed successfully")

def clean_build_dirs():
    """Clean previous build directories."""
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🧹 Cleaning {dir_name}...")
            shutil.rmtree(dir_name)
    
    # Clean .spec files
    for file in os.listdir("."):
        if file.endswith(".spec"):
            print(f"🧹 Removing {file}...")
            os.remove(file)

def build_executable():
    """Build the standalone executable."""
    print("🔨 Building Apocalypse Nightmare executable...")
    
    # Use python -m pyinstaller to ensure we use the installed version
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # Single executable file
        "--name=ApocalypseNightmare",   # Executable name
        "--add-data=README.md;.",       # Include README
        "--hidden-import=colorama",     # Ensure colorama is included
        "--hidden-import=colorama.initialise",
        "--hidden-import=colorama.ansitowin32",
        "--hidden-import=colorama.winterm",
        "--hidden-import=colorama.win32",
        "--hidden-import=colorama.ansi",
        "--hidden-import=time",         # Ensure time module is included
        "--hidden-import=random",       # Ensure random module is included
        "--hidden-import=re",           # Ensure regex module is included
        "--clean",                      # Clean cache
        "main.py"                       # Main script
    ]
    
    # Add icon if available
    if os.path.exists("icon.ico"):
        cmd.insert(-1, "--icon=icon.ico")
    
    try:
        subprocess.check_call(cmd)
        print("✅ Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def create_installer_script():
    """Create a simple installer script."""
    installer_content = '''@echo off
echo ========================================
echo    APOCALYPSE NIGHTMARE - INSTALLER
echo ========================================
echo.
echo This will install the game to your desktop.
echo.
echo Features included:
echo - Multiple endings and story paths
echo - Character trust system
echo - Resource management (Knowledge, Tech Parts, Cash)
echo - ASCII art and visual effects
echo - Smart hint system
echo - Quick start options
echo.
pause

set "INSTALL_DIR=%USERPROFILE%\\Desktop\\Apocalypse Nightmare"
mkdir "%INSTALL_DIR%" 2>nul

copy "dist\\ApocalypseNightmare.exe" "%INSTALL_DIR%\\"
copy "README.md" "%INSTALL_DIR%\\"

echo.
echo ========================================
echo           INSTALLATION COMPLETE!
echo ========================================
echo.
echo The game is now available at: %INSTALL_DIR%
echo.
echo To play, double-click ApocalypseNightmare.exe
echo.
echo Game Features:
echo - 6 different endings to discover
echo - 4 unique characters with trust systems
echo - Multiple ways to achieve your goals
echo - Dramatic ASCII art for endings
echo - Contextual hints to guide you
echo.
pause
'''
    
    with open("install_game.bat", "w") as f:
        f.write(installer_content)
    print("✅ Created installer script: install_game.bat")

def main():
    """Main build process."""
    print("🚀 Apocalypse Nightmare - Application Builder")
    print("🎮 Enhanced Text Adventure Game")
    print("=" * 50)
    
    # Step 1: Install PyInstaller
    install_pyinstaller()
    
    # Step 2: Clean previous builds
    clean_build_dirs()
    
    # Step 3: Build executable
    if build_executable():
        print("\n🎉 Build successful!")
        print("📁 Executable location: dist/ApocalypseNightmare.exe")
        
        # Step 4: Create installer
        create_installer_script()
        
        print("\n📋 Next steps:")
        print("1. Test the executable: dist/ApocalypseNightmare.exe")
        print("2. Run installer: install_game.bat")
        print("3. Share the dist/ folder or installer")
        
        print("\n🎮 Game Features Included:")
        print("✅ 6 different endings (Missile Destroyed, Allies Escape, Solo Escape, etc.)")
        print("✅ 4 character trust systems (Alex, Maya, Ben, Jake)")
        print("✅ Resource management (Knowledge, Tech Parts, Cash)")
        print("✅ ASCII art for dramatic endings")
        print("✅ Smart contextual hint system")
        print("✅ Quick start options")
        print("✅ Enhanced visual feedback")
        print("✅ Fixed text overwriting issues")
        
        # Check file size
        exe_path = "dist/ApocalypseNightmare.exe"
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📊 Executable size: {size_mb:.1f} MB")
            
            # Additional build info
            print(f"\n🔧 Build Information:")
            print(f"📦 Dependencies: colorama, time, random, re")
            print(f"🎯 Target: Windows standalone executable")
            print(f"📁 Output: dist/ApocalypseNightmare.exe")
    else:
        print("\n❌ Build failed. Check the error messages above.")

if __name__ == "__main__":
    main() 