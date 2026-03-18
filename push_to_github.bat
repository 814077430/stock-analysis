@echo off
chcp 65001 >nul
echo ╔══════════════════════════════════════════════════════╗
echo ║        📤 推送到 GitHub - 快速脚本                    ║
echo ╚══════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

REM 检查是否已配置远程仓库
git remote -v | findstr "origin" >nul
if %errorlevel% equ 0 (
    echo [✓] 已配置远程仓库
    git remote -v
    echo.
    echo 是否直接推送？(Y/N)
    set /p confirm=
    if /i "%confirm%"=="Y" (
        goto push
    ) else (
        goto end
    )
)

echo [!] 未配置远程仓库
echo.
echo 请输入你的 GitHub 用户名：
set /p username=

if "%username%"=="" (
    echo ❌ 用户名不能为空
    goto end
)

echo.
echo 请选择仓库可见性:
echo   1. Public (公开)
echo   2. Private (私有)
set /p visibility=

if "%visibility%"=="2" (
    set repo_type=private
) else (
    set repo_type=public
)

echo.
echo [提示] 需要在 GitHub 手动创建仓库，或提供 Personal Access Token 自动创建
echo.
echo 是否使用 Personal Access Token 自动创建？(Y/N)
set /p use_token=

if /i "%use_token%"=="Y" (
    echo.
    echo 请输入 Personal Access Token:
    set /p token=
    
    if "%token%"=="" (
        echo ❌ Token 不能为空
        goto end
    )
    
    echo.
    echo [正在创建 GitHub 仓库...]
    
    REM 使用 API 创建仓库
    curl -X POST -H "Authorization: token %token%" ^
         -H "Accept: application/vnd.github.v3+json" ^
         https://api.github.com/user/repos ^
         -d "{\"name\":\"stock-analysis\",\"description\":\"股票分析系统 - 数据采集、技术分析、报告生成\",\"%repo_type%\":true}"
    
    echo.
    echo [✓] 仓库创建完成
)

echo.
echo [正在配置远程仓库...]
git remote add origin https://github.com/%username%/stock-analysis.git

:push
echo.
echo [正在推送代码到 GitHub...]
git branch -M main
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ╔══════════════════════════════════════════════════════╗
    echo ║  ✅ 推送成功！                                        ║
    echo ║                                                      ║
    echo ║  仓库地址：https://github.com/%username%/stock-analysis  ║
    echo ╚══════════════════════════════════════════════════════╝
) else (
    echo.
    echo ╔══════════════════════════════════════════════════════╗
    echo ║  ❌ 推送失败！请检查：                                ║
    echo ║  1. GitHub 用户名是否正确                            ║
    echo ║  2. 仓库是否已在 GitHub 创建                          ║
    echo ║  3. 是否有写入权限                                   ║
    echo ╚══════════════════════════════════════════════════════╝
)

:end
echo.
pause
