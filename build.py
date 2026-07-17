import os
import subprocess
import shutil

def build_executable():
    # Clean up previous builds
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # Run PyInstaller with spec file
    cmd = [
        'pyinstaller',
        '--clean',
        'Script2Storyboard.spec'
    ]
    
    # Run PyInstaller
    subprocess.run(cmd)
    
    print("Build completed! Executable is in the 'dist' folder.")

if __name__ == "__main__":
    build_executable() 