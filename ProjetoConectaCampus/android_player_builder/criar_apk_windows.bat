@echo off
setlocal
cd /d "%~dp0"
echo Criando projeto Flutter moderno...
if not exist conecta_campus_player_ok (
  flutter create conecta_campus_player_ok
)
cd conecta_campus_player_ok
flutter pub add webview_flutter
copy /Y "..\main.dart" "lib\main.dart"
copy /Y "..\AndroidManifest.xml" "android\app\src\main\AndroidManifest.xml"
flutter clean
flutter pub get
flutter build apk --release --no-tree-shake-icons
echo.
echo APK gerado em:
echo %cd%\build\app\outputs\flutter-apk\app-release.apk
pause
