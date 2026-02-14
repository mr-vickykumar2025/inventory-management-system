#define MyAppName "InventoryApp"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Karan Shroff"
#define MyAppExeName "InventoryApp.exe"

[Setup]
AppId={{AA69E0B2-5ACB-43FC-88F6-623F0778E57D}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputBaseFilename=InventoryAppSetup
Compression=lzma
SolidCompression=yes

[Files]
Source: "..\dist\InventoryApp\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
