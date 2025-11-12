#!/bin/bash

echo "========================================"
echo "  Сборка TechReport"
echo "========================================"
echo ""

# Проверка установки PyInstaller
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "[ОШИБКА] PyInstaller не установлен!"
    echo "Установите: pip3 install -r requirements.txt"
    exit 1
fi

echo "[1/3] Очистка старых файлов сборки..."
rm -rf build dist TechReport.spec

echo "[2/3] Компиляция приложения..."
pyinstaller build.spec

if [ $? -ne 0 ]; then
    echo ""
    echo "[ОШИБКА] Сборка завершилась с ошибкой!"
    exit 1
fi

echo ""
echo "[3/3] Создание папок для данных..."
mkdir -p dist/database
mkdir -p dist/reports
mkdir -p dist/templates

echo ""
echo "========================================"
echo "  Сборка завершена успешно!"
echo "========================================"
echo ""
echo "Исполняемый файл: dist/TechReport"
echo ""
