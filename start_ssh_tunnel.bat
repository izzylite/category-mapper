@echo off
echo 🚀 Starting SSH Tunnel for Database Connection
echo ================================================

echo 🔗 Creating SSH tunnel to database...
echo    SSH Server: ubuntu@88.223.94.231
echo    Local Port: 5433
echo    Remote Database: 35.197.215.50:5432
echo.

echo ⚠️  This will prompt for SSH password/key authentication
echo    Keep this window open to maintain the tunnel!
echo.

REM Create SSH tunnel
ssh -N -L 5433:35.197.215.50:5432 ubuntu@88.223.94.231

echo.
echo 🔒 SSH tunnel closed
pause
