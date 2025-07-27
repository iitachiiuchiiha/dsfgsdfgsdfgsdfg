:: Script Batch l'inchaa l-mashrou3 f Windows

:: 1. Kanqdado l-folder l-ra2issi o ndkhlo lih
mkdir "Advanced_Trading_System"
cd "Advanced_Trading_System"

:: 2. Kanqdado ga3 l-folders l-dakhlaniyin
mkdir "1_Strategies"
mkdir "2_Data_Handler"
mkdir "3_Backtesting_Engine"
mkdir "4_Risk_Management"
mkdir "5_Execution_Handler"
mkdir "6_GUI\static\css"
mkdir "6_GUI\static\js"
mkdir "6_GUI\templates"
mkdir "Config"
mkdir "Logs"

:: 3. Kanqdado l-files l-khawyin
echo. > "1_Strategies\__init__.py"
echo. > "1_Strategies\base_strategy.py"
echo. > "1_Strategies\elliott_waves.py"
echo. > "1_Strategies\ict_model.py"
echo. > "1_Strategies\sk_system.py"
echo. > "2_Data_Handler\__init__.py"
echo. > "2_Data_Handler\data_fetcher.py"
echo. > "3_Backtesting_Engine\__init__.py"
echo. > "3_Backtesting_Engine\backtester.py"
echo. > "4_Risk_Management\__init__.py"
echo. > "4_Risk_Management\risk_manager.py"
echo. > "5_Execution_Handler\__init__.py"
echo. > "5_Execution_Handler\broker_api.py"
echo. > "6_GUI\app.py"
echo. > "6_GUI\static\css\style.css"
echo. > "6_GUI\static\js\main.js"
echo. > "6_GUI\templates\index.html"
echo. > "Config\config.ini"
echo. > "Config\strategies.json"
echo. > "Logs\trading_log.log"
echo. > "main.py"

echo "Tam! L-Mashrou3 dyalk 'Advanced_Trading_System' t'qad b'naja7."