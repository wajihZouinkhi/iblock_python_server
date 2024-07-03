import PyInstaller.__main__
import os
    
PyInstaller.__main__.run([  
     'name-%s%' % 'name_of_your_executable file',
     '--onefile',
     '--windowed',
     os.path.join('C:\Users\wajih\OneDrive\Bureau\i-block1\python_robot/', 'python_server.py'), """your script and path to the script"""                                        
])