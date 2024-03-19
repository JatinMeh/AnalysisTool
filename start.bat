@ECHO OFF
set root=C:\Users\jatin\OneDrive\Desktop\StockAnalysisTool\AnalysisTool
call %root%\Scripts\activate.bat
cd C:\Users\jatin\OneDrive\Desktop\StockAnalysisTool
call streamlit run Dashboard.py
pause