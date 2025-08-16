[Setup]
AppName=PackageInstallerPro
AppVersion=1.0
AppVerName=PackageInstallerPro 1.0
DefaultDirName={pf}\PackageInstallerPro
DefaultGroupName=PackageInstallerPro
OutputDir=.
OutputBaseFilename=PackageInstallerProInstaller
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
MinVersion=10.0  ; Windows 10+
DisableProgramGroupPage=yes
Uninstallable=not IsTaskSelected('portable')

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "portable"; Description: "Portable mode (no uninstaller, no registry changes)"; Flags: unchecked

[Files]
Source: "dist\PackageInstallerPro.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\PackageInstallerProService.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "config.json"; DestDir: "{app}"; Flags: ignoreversion

[Run]
Filename: "{app}\PackageInstallerProService.exe"; Parameters: "install"; Flags: runhidden waituntilterminated
Filename: "{app}\PackageInstallerProService.exe"; Parameters: "start"; Flags: runhidden waituntilterminated
Filename: "{app}\PackageInstallerPro.exe"; Description: "{cm:LaunchProgram,PackageInstallerPro}"; Flags: nowait postinstall skipifsilent

[Icons]
Name: "{group}\PackageInstallerPro"; Filename: "{app}\PackageInstallerPro.exe"
Name: "{group}\Uninstall PackageInstallerPro"; Filename: "{uninstallexe}"; Tasks: not portable
Name: "{autodesktop}\PackageInstallerPro"; Filename: "{app}\PackageInstallerPro.exe"; Tasks: desktopicon

[UninstallRun]
Filename: "{app}\PackageInstallerProService.exe"; Parameters: "stop"; RunOnceId: "StopService"; Flags: runhidden; Tasks: not portable
Filename: "{app}\PackageInstallerProService.exe"; Parameters: "remove"; RunOnceId: "RemoveService"; Flags: runhidden; Tasks: not portable

[Registry]
Root: HKLM; Subkey: "Software\PackageInstallerPro"; ValueType: string; ValueName: "Version"; ValueData: "{appversion}"; Flags: uninsdeletekey; Tasks: not portable

[Code]
function CompareVersion(ver1, ver2: String): Integer;
var
  P, N1, N2: Integer;
begin
  Result := 0;
  while (Result = 0) and ((ver1 <> '') or (ver2 <> '')) do
  begin
    P := Pos('.', ver1);
    if P > 0 then
    begin
      N1 := StrToInt(Copy(ver1, 1, P - 1));
      Delete(ver1, 1, P);
    end
    else if ver1 <> '' then
    begin
      N1 := StrToInt(ver1);
      ver1 := '';
    end
    else
      N1 := 0;
    P := Pos('.', ver2);
    if P > 0 then
    begin
      N2 := StrToInt(Copy(ver2, 1, P - 1));
      Delete(ver2, 1, P);
    end
    else if ver2 <> '' then
    begin
      N2 := StrToInt(ver2);
      ver2 := '';
    end
    else
      N2 := 0;
    if N1 < N2 then Result := -1
    else if N1 > N2 then Result := 1;
  end;
end;

function InitializeSetup: Boolean;
var
  ExistingVersion: String;
begin
  if RegQueryStringValue(HKLM, 'Software\PackageInstallerPro', 'Version', ExistingVersion) then
  begin
    if CompareVersion(ExistingVersion, '1.0') > 0 then
    begin
      MsgBox('A newer version is already installed. Setup will exit.', mbError, MB_OK);
      Result := False;
      Exit;
    end;
  end;
  Result := True;
end;