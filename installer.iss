[Setup]
AppName=PackageInstallerPro
AppVersion=1.0
DefaultDirName={pf}\PackageInstallerPro
DefaultGroupName=PackageInstallerPro
OutputDir=.
OutputBaseFilename=PackageInstallerProInstaller
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin

[Files]
Source: "dist\PackageInstallerPro.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\PackageInstallerProService.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "config.json"; DestDir: "{app}"; Flags: ignoreversion

[Run]
Filename: "{app}\PackageInstallerProService.exe"; Parameters: "install"; Flags: runhidden waituntilterminated
Filename: "{app}\PackageInstallerProService.exe"; Parameters: "start"; Flags: runhidden waituntilterminated
Filename: "{app}\PackageInstallerPro.exe"; Flags: nowait postinstall skipifsilent

[Icons]
Name: "{group}\PackageInstallerPro"; Filename: "{app}\PackageInstallerPro.exe"
Name: "{group}\Uninstall PackageInstallerPro"; Filename: "{uninstallexe}"

[UninstallRun]
Filename: "{app}\PackageInstallerProService.exe"; Parameters: "stop"; RunOnceId: "StopService"; Flags: runhidden
Filename: "{app}\PackageInstallerProService.exe"; Parameters: "remove"; RunOnceId: "RemoveService"; Flags: runhidden
