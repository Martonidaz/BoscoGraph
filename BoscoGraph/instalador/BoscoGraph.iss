; Instalador do BoscoGraph (Inno Setup 6).
; (Este arquivo está em UTF-8 com BOM: é assim que o Inno Setup lê os acentos certos.)
;
; Antes: gerar o executável (python construir.py, que também compila este arquivo se achar o Inno Setup).
; Para compilar só o instalador: abrir este arquivo no Inno Setup e apertar F9, ou na linha de comando:
;     ISCC.exe instalador\BoscoGraph.iss
; O resultado vai para instalador\saida\BoscoGraph-<versão>-instalador.exe
;
; As telas, nesta ordem (quem instala só clica em Avançar, "Eu aceito", Instalar e Concluir):
;   1. Boas-vindas: o agradecimento, por que o BoscoGraph foi feito e quem fez (a seção [Messages]);
;   2. Termos de uso (instalador\termos_de_uso.txt): "Eu aceito" e Instalar;
;   3. Fim: o agradecimento de novo, com "Abrir o BoscoGraph agora" já marcado.
; O resto usa o padrão, sem perguntar nada:
;   - PrivilegesRequired=lowest: instala só para quem está usando o computador, em
;     %LOCALAPPDATA%\Programs\BoscoGraph. Não pede senha de administrador (nem abre a janela do Controle
;     de Conta de Usuário), então funciona também num computador de laboratório;
;   - sem as telas de pasta, de menu Iniciar, de componentes, de tarefas e de "pronto para instalar";
;   - os atalhos no menu Iniciar e na área de trabalho são criados sempre;
;   - os arquivos .bosco abrem no BoscoGraph (duplo clique abre direto na visualização, como foi salvo);
;   - o leitor de texto (Tesseract, para importar fotos) vai junto se a pasta instalador\tesseract existir
;     na hora de compilar (veja o LEIAME).
; Os modelos do usuário ficam em %APPDATA%\BoscoGraph (o programa nunca grava na própria pasta).
; Desinstalar NÃO apaga essa pasta: os grafos salvos são do usuário, não do programa.
; As imagens do assistente (instalador\assistente_*.bmp, nas cores da paleta) são feitas pelo construir.py
; (instalador\gerar_icone.py); se não existirem, ficam as imagens padrão do Inno Setup.

#ifndef Versao
  #define Versao "7.3"
#endif
#define Nome "BoscoGraph"
#define Executavel "BoscoGraph.exe"
#define PastaDoPrograma "..\dist\BoscoGraph"
; SourcePath = a pasta deste arquivo .iss (o pré-processador do Inno Setup define)
#define TemOcr DirExists(SourcePath + "tesseract")
#define TemImagens FileExists(SourcePath + "assistente_100.bmp")

#if !FileExists(SourcePath + PastaDoPrograma + "\" + Executavel)
  #error "Executável não encontrado em dist\BoscoGraph. Rode antes: python construir.py"
#endif

[Setup]
; O AppId identifica o programa para o Windows (atualizar, desinstalar). Nunca mude depois de publicar.
AppId={{D0C94D73-3AEF-49A6-AF90-E9EC68CE9E07}
AppName={#Nome}
AppVersion={#Versao}
AppVerName={#Nome} {#Versao}
AppPublisher=BoscoGraph
DefaultDirName={autopf}\{#Nome}
DefaultGroupName={#Nome}
PrivilegesRequired=lowest
DisableWelcomePage=no
LicenseFile=termos_de_uso.txt
DisableDirPage=yes
DisableProgramGroupPage=yes
DisableReadyPage=yes
OutputDir=saida
OutputBaseFilename={#Nome}-{#Versao}-instalador
SetupIconFile=boscograph.ico
UninstallDisplayIcon={app}\{#Executavel}
UninstallDisplayName={#Nome}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
#if TemImagens
; Vários tamanhos, separados por vírgula: o Inno Setup escolhe o que combina com a escala da tela
WizardImageFile=assistente_100.bmp,assistente_150.bmp,assistente_200.bmp,assistente_250.bmp
WizardSmallImageFile=assistente_pequena_100.bmp,assistente_pequena_150.bmp,assistente_pequena_200.bmp,assistente_pequena_250.bmp
#endif
; O executável é de 64 bits (gerado por um Python de 64 bits)
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
; Fecha o BoscoGraph aberto antes de atualizar os arquivos
CloseApplications=yes
; Avisa o Windows que as associações de arquivo mudaram (o ícone dos .bosco aparece na hora)
ChangesAssociations=yes

[Languages]
Name: "portugues"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Messages]
; A tela de boas-vindas e a do fim (%n = quebra de linha)
WelcomeLabel1=Bem-vindo ao BoscoGraph!
WelcomeLabel2=Obrigado por usar o BoscoGraph {#Versao}.%n%nEle nasceu de um desafio da disciplina de Teoria dos Grafos: mostrar na tela, e não no terminal, o grafo sendo montado e a busca andando por ele. Hoje são doze algoritmos para estudar passo a passo e linha a linha, com o código em seis linguagens.%n%nCriado por: Daniel Marton Barbosa%nCo-criadores: Breno Ryan de Andrade Fernandes, João Vitor Ferreira Azevedo Pereira e Mariana Gonçalves de Freitas Ribeiro%nEntusiastas (os professores): Bruno Bustamante Ferreira Leonor e Warner Brezolin
FinishedHeadingLabel=Tudo pronto!
FinishedLabelNoIcons=O BoscoGraph foi instalado.%n%nObrigado por usar o BoscoGraph. Bons estudos!
FinishedLabel=O BoscoGraph foi instalado e está no menu Iniciar e na área de trabalho.%n%nObrigado por usar o BoscoGraph. Bons estudos!

[Files]
; A pasta inteira gerada pelo PyInstaller (o .exe e a pasta _internal com o Python e os recursos)
Source: "{#PastaDoPrograma}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
#if TemOcr
; O Tesseract vai para {app}\tesseract, onde o BoscoGraph procura (importacao/imagem.py, carregar_ocr)
Source: "tesseract\*"; DestDir: "{app}\tesseract"; Flags: ignoreversion recursesubdirs createallsubdirs
#endif

[Icons]
; AppUserModelID igual ao do programa (visual/aplicativo.py): a janela aberta e o atalho fixado na
; barra de tarefas ficam no mesmo botão
Name: "{autoprograms}\{#Nome}"; Filename: "{app}\{#Executavel}"; AppUserModelID: "{#Nome}"
Name: "{autodesktop}\{#Nome}"; Filename: "{app}\{#Executavel}"; AppUserModelID: "{#Nome}"

[Registry]
; A associação da extensão .bosco (o jeito que a documentação do Inno Setup recomenda). HKA = a parte do
; registro do usuário (a instalação é "só para mim").
;   .bosco                        -> o tipo "BoscoGraph.Arquivo"
;   BoscoGraph.Arquivo            -> o nome que o Explorer mostra, o ícone e o comando de abrir
;   "%1"                          -> o caminho do arquivo clicado (o boscograph.py abre o .bosco que recebe)
Root: HKA; Subkey: "Software\Classes\.bosco"; ValueType: string; ValueName: ""; ValueData: "BoscoGraph.Arquivo"; \
    Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\.bosco\OpenWithProgids"; ValueType: string; ValueName: "BoscoGraph.Arquivo"; \
    ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\BoscoGraph.Arquivo"; ValueType: string; ValueName: ""; \
    ValueData: "Arquivo do BoscoGraph"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\BoscoGraph.Arquivo\DefaultIcon"; ValueType: string; ValueName: ""; \
    ValueData: "{app}\{#Executavel},0"
Root: HKA; Subkey: "Software\Classes\BoscoGraph.Arquivo\shell\open\command"; ValueType: string; ValueName: ""; \
    ValueData: """{app}\{#Executavel}"" ""%1"""
Root: HKA; Subkey: "Software\Classes\Applications\{#Executavel}\SupportedTypes"; ValueType: string; \
    ValueName: ".bosco"; ValueData: ""; Flags: uninsdeletekey

[Run]
Filename: "{app}\{#Executavel}"; Description: "Abrir o BoscoGraph agora"; Flags: nowait postinstall skipifsilent
