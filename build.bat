@echo off
echo ========================================
echo   Сборка TechReport.exe
echo ========================================
echo.

REM Проверка установки PyInstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [ОШИБКА] PyInstaller не установлен!
    echo Установите: pip install -r requirements.txt
    pause
    exit /b 1
)

echo [1/3] Очистка старых файлов сборки...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist TechReport.spec del TechReport.spec

echo [2/3] Компиляция приложения...
pyinstaller build.spec

if errorlevel 1 (
    echo.
    echo [ОШИБКА] Сборка завершилась с ошибкой!
    pause
    exit /b 1
)

echo.
echo [3/4] Создание папок для данных...
if not exist dist\database mkdir dist\database
if not exist dist\reports mkdir dist\reports
if not exist dist\templates mkdir dist\templates

echo [4/4] Копирование базы данных (если есть)...
if exist database\*.db (
    copy database\*.db dist\database\
    echo База данных скопирована в dist\database\
) else (
    echo База данных не найдена - будет создана при первом запуске
)

echo.
echo ========================================
echo   Сборка завершена успешно!
echo ========================================
echo.
echo Исполняемый файл: dist\TechReport.exe
echo.
echo ВАЖНО: База данных находится в dist\database\ СНАРУЖИ .exe
echo        Это позволяет редактировать структуру отчетов.
echo.
pause
