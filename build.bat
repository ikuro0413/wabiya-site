@echo off
REM Tailwind CSSをプリビルドするスクリプト
REM HTML編集後、このファイルをダブルクリックで wabiya.css を更新できる
tailwindcss.exe -c tailwind.config.js -i src.css -o wabiya.css --minify
echo.
echo ビルド完了: wabiya.css
pause
