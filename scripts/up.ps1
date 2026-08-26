param(
    [switch]$NoCache
)

$ErrorActionPreference = "Stop"

# Docker Desktop/Compose on Windows can fail before the Dockerfile is evaluated
# when Compose delegates `up --build` to Buildx Bake. Disable that delegation
# for the local development stack and use the normal Compose build path.
$env:COMPOSE_BAKE = "false"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker CLI was not found. Start Docker Desktop and ensure 'docker' is on PATH."
}

Write-Host "Hybrid-Search: COMPOSE_BAKE=false (Windows compatibility mode)"

if ($NoCache) {
    docker compose build --no-cache
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    docker compose up -d
} else {
    docker compose up --build -d
}

exit $LASTEXITCODE
