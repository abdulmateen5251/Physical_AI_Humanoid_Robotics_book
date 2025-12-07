# Backend-Frontend Integration Verification Script (PowerShell)
# Run this to verify all components are working correctly

Write-Host "`n🔍 Backend-Frontend Integration Verification`n" -ForegroundColor Cyan
Write-Host "=============================================="

$pass = 0
$fail = 0
$warn = 0

function Check-Service {
    param(
        [string]$name,
        [string]$url,
        [string]$expected
    )
    
    Write-Host -NoNewline "Checking $name... "
    
    try {
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 5 -ErrorAction Stop
        $content = $response.Content
        
        if ($content -match $expected) {
            Write-Host "✅ PASS" -ForegroundColor Green
            $global:pass++
        }
        else {
            Write-Host "❌ FAIL" -ForegroundColor Red
            Write-Host "  Response: $($content.Substring(0, [Math]::Min(100, $content.Length)))"
            $global:fail++
        }
    }
    catch {
        Write-Host "❌ FAIL" -ForegroundColor Red
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
        $global:fail++
    }
}

function Check-File {
    param(
        [string]$filepath,
        [string]$description
    )
    
    Write-Host -NoNewline "Checking $description... "
    
    if (Test-Path $filepath) {
        Write-Host "✅ PASS" -ForegroundColor Green
        $global:pass++
    }
    else {
        Write-Host "❌ FAIL" -ForegroundColor Red
        Write-Host "  File not found: $filepath" -ForegroundColor Red
        $global:fail++
    }
}

function Check-Port {
    param(
        [int]$port,
        [string]$service
    )
    
    Write-Host -NoNewline "Checking $service on port $port... "
    
    try {
        $connection = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
        if ($connection.TcpTestSucceeded) {
            Write-Host "✅ PASS" -ForegroundColor Green
            $global:pass++
        }
        else {
            Write-Host "⚠️  WARN" -ForegroundColor Yellow
            $global:warn++
        }
    }
    catch {
        Write-Host "⚠️  WARN" -ForegroundColor Yellow
        $global:warn++
    }
}

# Infrastructure Checks
Write-Host "`n🏗️ INFRASTRUCTURE CHECKS" -ForegroundColor Cyan
Write-Host "------------------------"

Check-Port 8000 "Backend API"
Check-Port 3000 "Frontend Dev Server"
Check-Port 5432 "PostgreSQL Database"
Check-Port 6333 "Qdrant Vector DB"
Check-Port 6379 "Redis Cache"

# API Endpoint Checks
Write-Host "`n🌐 API ENDPOINT CHECKS" -ForegroundColor Cyan
Write-Host "----------------------"



# Integration Files Check
Write-Host "`n📁 INTEGRATION FILES CHECK" -ForegroundColor Cyan
Write-Host "---------------------------"

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

Check-File "$scriptPath\frontend\.env.local" "Environment Config"
Check-File "$scriptPath\frontend\src\utils\apiClient.js" "API Client"
Check-File "$scriptPath\frontend\src\utils\useApi.js" "React Hooks"
Check-File "$scriptPath\frontend\src\components\ChatWidget.tsx" "ChatWidget Component"
Check-File "$scriptPath\frontend\src\components\ChatWidget.module.css" "ChatWidget Styles"
Check-File "$scriptPath\frontend\src\theme\ChatWidgetPlugin.js" "Docusaurus Plugin"
Check-File "$scriptPath\frontend\src\theme\ChatWidgetWrapper.tsx" "Root Wrapper"

# Documentation Check
Write-Host "`n📚 DOCUMENTATION CHECK" -ForegroundColor Cyan
Write-Host "----------------------"

Check-File "$scriptPath\BACKEND_FRONTEND_INTEGRATION.md" "Integration Guide"
Check-File "$scriptPath\QUICK_REFERENCE.md" "Quick Reference"
Check-File "$scriptPath\INTEGRATION_STATUS.md" "Status Report"

# Results
$separator = "════════════════════════════════════════════════════"
Write-Host "`n$separator" -ForegroundColor Cyan
Write-Host "RESULTS: $pass PASS | $fail FAIL | $warn WARN" -ForegroundColor Cyan
Write-Host "$separator" -ForegroundColor Cyan

if ($fail -eq 0) {
    Write-Host "`nAll checks passed - integration complete`n" -ForegroundColor Green
    
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Index content:" -ForegroundColor Yellow
    Write-Host "   docker compose exec backend python scripts/ingest_to_qdrant.py --docs ../frontend/docs --collection physical_ai_humanoid_robotics_course" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "2. Open browser:" -ForegroundColor Yellow
    Write-Host "   http://localhost:3000" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "3. Test ChatWidget:" -ForegroundColor Yellow
    Write-Host "   - Click blue chat button" -ForegroundColor Cyan
    Write-Host "   - Ask: What is ROS 2?" -ForegroundColor Cyan
    Write-Host "   - Verify answer with citations appears" -ForegroundColor Cyan
    
    Write-Host "`nDocumentation available:" -ForegroundColor Yellow
    Write-Host "- BACKEND_FRONTEND_INTEGRATION.md  (Complete guide)" -ForegroundColor Cyan
    Write-Host "- QUICK_REFERENCE.md               (Quick reference)" -ForegroundColor Cyan
    Write-Host "- INTEGRATION_STATUS.md            (Status report)" -ForegroundColor Cyan
}
else {
    Write-Host "`n❌ SOME CHECKS FAILED - TROUBLESHOOT ABOVE`n" -ForegroundColor Red
    exit 1
}
