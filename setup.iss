    ; Script pour Inno Setup - HotelManager

    [Setup]
    ; NOTE: Les valeurs {cm:...} sont des constantes qui seront remplacées.
    AppName=SisoHotelManager
    AppVersion=1.0
    AppPublisher=SisoTech
    DefaultDirName={autopf}\HotelManager
    DisableProgramGroupPage=yes
    ; Le nom du fichier setup.exe qui sera généré
    OutputBaseFilename=setup-hotelmanager
    Compression=lzma
    SolidCompression=yes
    WizardStyle=modern

    [Languages]
    Name: "french"; MessagesFile: "compiler:Languages\French.isl"

    [Tasks]
    ; Propose à l'utilisateur de créer une icône sur le bureau
    Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

    [Files]
    ; C'est la partie la plus importante !
    ; Elle prend TOUT le contenu du dossier généré par PyInstaller et le met dans le dossier d'installation.
    Source: "dist\HotelManager\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
    ; -> {app} est le dossier d'installation (ex: C:\Program Files\HotelManager)

    [Icons]
    ; Raccourci dans le menu Démarrer
    Name: "{group}\HotelManager"; Filename: "{app}\HotelManager.exe"
    ; Raccourci sur le bureau (si la tâche "desktopicon" a été cochée)
    Name: "{autodesktop}\HotelManager"; Filename: "{app}\HotelManager.exe"; Tasks: desktopicon

    [Run]
    ; Propose de lancer l'application à la fin de l'installation
    Filename: "{app}\HotelManager.exe"; Description: "{cm:LaunchProgram,HotelManager}"; Flags: nowait postinstall skipifsilent
    
