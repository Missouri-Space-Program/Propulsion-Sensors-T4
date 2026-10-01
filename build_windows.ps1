$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    py -3 -m venv .venv
}

& .venv\Scripts\python.exe -m pip install --upgrade pip
& .venv\Scripts\python.exe -m pip install -r requirements-build.txt

if ($env:LABJACK_LJM_DLL) {
    Write-Host "Including LJM DLL: $env:LABJACK_LJM_DLL"
} else {
    Write-Warning "LABJACK_LJM_DLL is not set; the target PC must have LabJack LJM installed."
}

& .venv\Scripts\pyinstaller.exe --clean --noconfirm MSPPropulsionTest.spec
Write-Host "Built dist\MSPPropulsionTest\MSPPropulsionTest.exe"