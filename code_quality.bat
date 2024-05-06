@REM https://stackoverflow.com/questions/14286457/using-parameters-in-batch-files-at-windows-command-line
@echo off
IF "%~1"=="" (
echo ---------------STAP 1/3 = RUFF---------------
ruff check . --config .ruff.toml
ruff format . --config .ruff.toml
echo ---------------STAP 2/3 = MYPY----------------
python -m mypy app tests --ignore-missing-imports
echo ---------------STAP 3/3 = TESTS---------------
pytest tests
)


IF "%~1"=="ruff" (
echo ---------------RUFF---------------
ruff check . --config .ruff.toml
ruff format . --config .ruff.toml
)

IF "%~1"=="ruff-fix" (
echo ---------------RUFF FIX---------------
ruff check . --fix
)


IF "%~1"=="ruff-unsafe" (
echo ---------------RUFF UNSAFE---------------
ruff check . --unsafe-fixes
)


IF "%~1"=="mypy" (
echo ---------------MYPY---------------
python -m mypy app tests --ignore-missing-imports
)

IF "%~1"=="test" (
echo ---------------TESTS---------------
pytest tests
)

IF "%~1"=="coverage" (
echo ---------------COVERAGE---------------
pytest --cov=app --cov-report=html --cov-fail-under=79.3

IF EXIST htmlcov\index.html (
    echo Opening index.html in the default web browser...
    start htmlcov\index.html
) ELSE (
    echo The index.html file was not found.
)
)

IF "%~1"=="pre-commit" (
echo ---------------PRE-COMMIT---------------
pre-commit run --all-files
)
