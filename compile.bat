py -m PyInstaller --noconfirm --clean main.py
powershell -Command "Copy-Item -Path .\\img -Destination .\\dist\\main -Recurse"
powershell -Command "Copy-Item -Path .\\buttons.txt -Destination .\\dist\\main"
powershell -Command "Compress-Archive -Force -Path .\\dist\\main -DestinationPath dist.zip"