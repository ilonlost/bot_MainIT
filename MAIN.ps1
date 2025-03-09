param (
    [string]$Username,
    [string]$Password
)

# Преобразование пароля в SecureString
$SecurePassword = ConvertTo-SecureString -AsPlainText $Password -Force
$Credential = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $Username, $SecurePassword

# Запуск задач на брокерах, шаг 1 - подготовка к перезагрузке
Invoke-Command -ComputerName 11-vm-rdcb01.agrohold.ru -Credential $Credential -FilePath 'C:\Scripts\Autoreboot_RDS_FK\CR-RRT-WCB-RDHM.ps1'
Invoke-Command -ComputerName 11-vm-rdcb02.agrohold.ru -Credential $Credential -FilePath 'C:\Scripts\Autoreboot_RDS_FK\CR-RRT-WCB-RDHM.ps1'
Invoke-Command -ComputerName 11-vm-rds01.agrohold.ru -Credential $Credential -FilePath 'C:\Scripts\Autoreboot_RDS_FK\CR-RRT-OCB-RDHM.ps1'
Invoke-Command -ComputerName 11-vm-rds02.agrohold.ru -Credential $Credential -FilePath 'C:\Scripts\Autoreboot_RDS_FK\CR-RRT-OCB-RDHM.ps1'
Invoke-Command -ComputerName 11-vm-ecoplan01.agrohold.ru -Credential $Credential -FilePath 'C:\Scripts\Autoreboot_RDS_FK\CR-RRT-OCB-RDHM.ps1'
Invoke-Command -ComputerName 11-vm-qual01.agrohold.ru -Credential $Credential -FilePath 'C:\Scripts\Autoreboot_RDS_FK\CR-RRT-OCB-RDHM.ps1'

# Перезагрузка серверов
Invoke-Command -ComputerName 11-vm-rddb01.agrohold.ru -Credential $Credential -ScriptBlock {Restart-Computer -Force}
Invoke-Command -ComputerName 11-vm-rdfs01.agrohold.ru -Credential $Credential -ScriptBlock {Restart-Computer -Force}
Invoke-Command -ComputerName 11-vm-rdcb01.agrohold.ru -Credential $Credential -ScriptBlock {Restart-Computer -Force}
Invoke-Command -ComputerName 11-vm-rdcb02.agrohold.ru -Credential $Credential -ScriptBlock {Restart-Computer -Force}
Invoke-Command -ComputerName 11-vm-rds01.agrohold.ru -Credential $Credential -ScriptBlock {Restart-Computer -Force}
Invoke-Command -ComputerName 11-vm-rds02.agrohold.ru -Credential $Credential -ScriptBlock {Restart-Computer -Force}
Invoke-Command -ComputerName 11-vm-ecoplan01.agrohold.ru -Credential $Credential -ScriptBlock {Restart-Computer -Force}
Invoke-Command -ComputerName 11-vm-qual01.agrohold.ru -Credential $Credential -ScriptBlock {Restart-Computer -Force}

# Проверка статуса серверов
Start-Sleep -Seconds 300
Test-NetConnection 11-vm-rdcb01.agrohold.ru
Test-NetConnection 11-vm-rdcb02.agrohold.ru
Test-NetConnection 11-vm-rddb01.agrohold.ru
Test-NetConnection 11-vm-rdfs01.agrohold.ru
Test-NetConnection 11-vm-rds01.agrohold.ru
Test-NetConnection 11-vm-rds02.agrohold.ru
Test-NetConnection 11-vm-ecoplan01.agrohold.ru
Test-NetConnection 11-vm-qual01.agrohold.ru

# Уведомление о завершении
Write-Output "Перезагрузка фермы RDS завершена."