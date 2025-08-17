[Setup]
AppName=PackageInstallerPro
AppVersion=1.0
AppVerName=PackageInstallerPro 1.0
DefaultDirName={autopf}\PackageInstallerPro
DefaultGroupName=PackageInstallerPro
OutputDir=.
OutputBaseFilename=PackageInstallerProInstaller
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
MinVersion=0,6.2
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
; Updated: Added 'Tasks: not portable' to ensure service is only installed when uninstall is available, preventing leftovers
Filename: "{app}\PackageInstallerProService.exe"; Parameters: "install"; Flags: runhidden waituntilterminated; Tasks: not portable
Filename: "{app}\PackageInstallerProService.exe"; Parameters: "start"; Flags: runhidden waituntilterminated; Tasks: not portable
Filename: "{app}\PackageInstallerPro.exe"; Description: "{cm:LaunchProgram,PackageInstallerPro}"; Flags: nowait postinstall skipifsilent

[Icons]
Name: "{group}\PackageInstallerPro"; Filename: "{app}\PackageInstallerPro.exe"
Name: "{group}\Uninstall PackageInstallerPro"; Filename: "{uninstallexe}"; Tasks: not portable
Name: "{autodesktop}\PackageInstallerPro"; Filename: "{app}\PackageInstallerPro.exe"; Tasks: desktopicon

[UninstallRun]
Filename: "{app}\PackageInstallerProService.exe"; Parameters: "stop"; RunOnceId: "StopService"; Flags: runhidden; Tasks: not portable
Filename: "{app}\PackageInstallerProService.exe"; Parameters: "remove"; RunOnceId: "RemoveService"; Flags: runhidden; Tasks: not portable

[Registry]
Root: HKLM; Subkey: "Software\PackageInstallerPro"; ValueType: string; ValueName: "Version"; ValueData: "1.0"; Flags: uninsdeletekey; Tasks: not portable

[Code]
function CompareVersion(ver1, ver2: String): Integer;
var
  P, N1, N2: Integer;
  s1, s2: String;
begin
  Result := 0;
  s1 := ver1;
  s2 := ver2;
  while (Result = 0) and ((s1 <> '') or (s2 <> '')) do
  begin
    P := Pos('.', s1);
    if P > 0 then
    begin
      N1 := StrToIntDef(Copy(s1, 1, P - 1), 0);
      Delete(s1, 1, P);
    end
    else if s1 <> '' then
    begin
      N1 := StrToIntDef(s1, 0);
      s1 := '';
    end
    else
      N1 := 0;

    P := Pos('.', s2);
    if P > 0 then
    begin
      N2 := StrToIntDef(Copy(s2, 1, P - 1), 0);
      Delete(s2, 1, P);
    end
    else if s2 <> '' then
    begin
      N2 := StrToIntDef(s2, 0);
      s2 := '';
    end
    else
      N2 := 0;

    if N1 < N2 then
      Result := -1
    else if N1 > N2 then
      Result := 1;
  end;
end;

function InitializeSetup: Boolean;
var
  ExistingVersion: String;
begin
  Result := True;
  if RegQueryStringValue(HKLM, 'Software\PackageInstallerPro', 'Version', ExistingVersion) then
  begin
    if CompareVersion(ExistingVersion, '1.0') > 0 then
    begin
      MsgBox('A newer version is already installed. Setup will exit.', mbError, MB_OK);
      Result := False;
    end;
  end;
end;
