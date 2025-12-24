@echo off
echo Building SMS Sync v3...

cd c:\SMS\frontend
call npm install
call npm run build

cd c:\SMS\backend
copy "..\frontend\src\assets\ringtone.mp3" "ringtone.mp3"

:: Ensure dependencies
pip install pystray pillow win11toast pyinstaller

:: Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

:: Build config
:: --onedir: Easier to debug if assets are missing, faster startup than onefile
:: --noconsole: Hide terminal (use --windowed)
:: --icon: Set exe icon
:: --add-data: Include frontend and assets

pyinstaller --noconfirm ^
    --onedir ^
    --windowed ^
    --name "SMSSync_v4" ^
    --icon "c:\SMS\app_icon.ico" ^
    --add-data "c:\SMS\frontend\dist;frontend/dist" ^
    --add-data "c:\SMS\app_icon.ico;." ^
    --add-data "ringtone.mp3;." ^
    --hidden-import "pystray" ^
    --hidden-import "PIL" ^
    --hidden-import "win11toast" ^
    --clean ^
    app.py

echo Build complete. Moving to dist_v4...
cd c:\SMS
if not exist dist_v4 mkdir dist_v4
xcopy /E /I /Y "c:\SMS\backend\dist\SMSSync_v4" "c:\SMS\dist_v4\SMSSync_v4"

echo Done!
