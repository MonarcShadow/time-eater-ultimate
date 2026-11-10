# Automatiza Hedgehog Converter y Havok Converter (programas con ventana, sin línea de comandos):
# escribe su .ini con los parámetros, abre el programa, pulsa "Convert" por UI Automation,
# espera a que termine y lo cierra. Uso: . .\scripts\lib\conversores.ps1
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes

$script:BinLibgens = Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) "herramientas\libgens-sonicglvl\libgens-sonicglvl\bin"

function Get-VentanaProceso([int]$procId, [int]$segundos = 20) {
    $cond = New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ProcessIdProperty, $procId)
    $limite = (Get-Date).AddSeconds($segundos)
    while ((Get-Date) -lt $limite) {
        $w = [Windows.Automation.AutomationElement]::RootElement.FindFirst([Windows.Automation.TreeScope]::Children, $cond)
        if ($w) { return $w }
        Start-Sleep -Milliseconds 300
    }
    throw "No apareció la ventana del proceso $procId"
}

function Find-Control($ventana, [string]$automationId) {
    $cond = New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::AutomationIdProperty, $automationId)
    $e = $ventana.FindFirst([Windows.Automation.TreeScope]::Descendants, $cond)
    if (-not $e) { throw "No se encontró el control $automationId" }
    return $e
}

function Get-TextoControl($e) {
    try { return $e.GetCurrentPattern([Windows.Automation.ValuePattern]::Pattern).Current.Value } catch {}
    try { return $e.GetCurrentPattern([Windows.Automation.TextPattern]::Pattern).DocumentRange.GetText(-1) } catch {}
    return ""
}

# Cierra los cuadros de mensaje (QMessageBox) que abra el programa y devuelve su texto
function Close-Dialogos($procId) {
    $textos = @()
    $cond = New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ProcessIdProperty, $procId)
    foreach ($w in [Windows.Automation.AutomationElement]::RootElement.FindAll([Windows.Automation.TreeScope]::Children, $cond)) {
        $hijos = $w.FindAll([Windows.Automation.TreeScope]::Children, [Windows.Automation.Condition]::TrueCondition)
        foreach ($d in $hijos) {
            if ($d.Current.ControlType -eq [Windows.Automation.ControlType]::Window) {
                $textos += ($d.FindAll([Windows.Automation.TreeScope]::Descendants, [Windows.Automation.Condition]::TrueCondition) | ForEach-Object { $_.Current.Name } | Where-Object { $_ }) -join " "
                $ok = $d.FindFirst([Windows.Automation.TreeScope]::Descendants, (New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ControlTypeProperty, [Windows.Automation.ControlType]::Button)))
                if ($ok) { $ok.GetCurrentPattern([Windows.Automation.InvokePattern]::Pattern).Invoke() }
            }
        }
    }
    return $textos
}

function Invoke-ConversorGui([string]$exe, [string]$ini, [hashtable]$valores, [string]$idProgreso, [string]$archivoFinal, [int]$timeoutSeg = 600) {
    Get-Process ([IO.Path]::GetFileNameWithoutExtension($exe)) -ErrorAction SilentlyContinue | Stop-Process -Force
    # .ini: QSettings [General]; las rutas con "/" y las listas separadas por ", "
    $lineas = @("[General]") + ($valores.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" })
    [IO.File]::WriteAllLines((Join-Path $script:BinLibgens $ini), $lineas)
    $p = Start-Process (Join-Path $script:BinLibgens $exe) -WorkingDirectory $script:BinLibgens -PassThru
    try {
        # la ventana puede aparecer antes que sus controles: reintentar hasta encontrar el botón "Convert"
        $boton = $null
        $condBoton = New-Object Windows.Automation.AndCondition(
            (New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ControlTypeProperty, [Windows.Automation.ControlType]::Button)),
            (New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::NameProperty, "Convert")))
        $limiteUi = (Get-Date).AddSeconds(30)
        while (-not $boton -and (Get-Date) -lt $limiteUi) {
            Start-Sleep -Milliseconds 500
            $w = Get-VentanaProceso $p.Id
            $boton = $w.FindFirst([Windows.Automation.TreeScope]::Descendants, $condBoton)
        }
        if (-not $boton) { throw "No apareció el botón Convert de $exe" }
        Start-Sleep -Milliseconds 500
        $boton.GetCurrentPattern([Windows.Automation.InvokePattern]::Pattern).Invoke()
        $limite = (Get-Date).AddSeconds($timeoutSeg)
        $mensajes = @()
        do {
            Start-Sleep -Milliseconds 700
            $mensajes += Close-Dialogos $p.Id
            $hecho = ($archivoFinal -and (Test-Path $archivoFinal))
            $log = ""
            if ($idProgreso) { try { $log = Get-TextoControl (Find-Control $w $idProgreso) } catch {} }
            if ($log -match 'SUCCESS: Conversion complete|(?m)^\S+: ERROR') { $hecho = $true }
            if ($p.HasExited) { break }
        } while (-not $hecho -and (Get-Date) -lt $limite)
        Start-Sleep -Milliseconds 1500
        $mensajes += Close-Dialogos $p.Id
        return [pscustomobject]@{ Terminado = $hecho; Log = $log; Mensajes = ($mensajes | Where-Object { $_ }) }
    } finally {
        if (-not $p.HasExited) {
            try { (Get-VentanaProceso $p.Id 2).GetCurrentPattern([Windows.Automation.WindowPattern]::Pattern).Close() } catch {}
            Start-Sleep 1
            if (-not $p.HasExited) { $p | Stop-Process -Force }
        }
    }
}

function ConvertTo-RutaQt([string]$ruta) { return ([IO.Path]::GetFullPath($ruta)) -replace '\\', '/' }
