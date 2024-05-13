@ECHO OFF
set root={root path}
call %root%\Scripts\activate.bat
cd {Root Folder}
call streamlit run Dashboard.py
pause
