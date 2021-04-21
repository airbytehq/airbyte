# In order to run this, follow first install powershell via `brew install powershell`.
# Then run `pwsh` to invoke powershell.
# Once in the powershell, run this file and follow instructions to generate a refresh token.

$clientId = "db41b09d-6e50-4f4a-90ac-5a99caefb52f"

Start-Process "https://login.live-int.com/oauth20_authorize.srf?client_id=$clientId&scope=bingads.manage&response_type=code&redirect_uri=https://login.live-int.com/oauth20_desktop.srf&prompt=login"

$code = Read-Host "Grant consent in the browser, and then enter the code here (see ?code=UseThisCode&...)"

# Get the initial access and refresh tokens.

$response = Invoke-WebRequest https://login.live-int.com/oauth20_token.srf -ContentType application/x-www-form-urlencoded -Method POST -Body "client_id=$clientId&scope=bingads.manage&code=$code&grant_type=authorization_code&redirect_uri=https%3A%2F%2Flogin.live-int.com%2Foauth20_desktop.srf"

$oauthTokens = ($response.Content | ConvertFrom-Json)
Write-Output "Access token: " $oauthTokens.access_token
Write-Output "Access token expires in: " $oauthTokens.expires_in
Write-Output "Refresh token: " $oauthTokens.refresh_token

# The access token will expire e.g., after one hour.
# Use the refresh token to get new access and refresh tokens.

$response = Invoke-WebRequest https://login.live-int.com/oauth20_token.srf -ContentType application/x-www-form-urlencoded -Method POST -Body "client_id=$clientId&scope=bingads.manage&code=$code&grant_type=refresh_token&refresh_token=$($oauthTokens.refresh_token)"

$oauthTokens = ($response.Content | ConvertFrom-Json)
Write-Output "Access token: " $oauthTokens.access_token
Write-Output "Access token expires in: " $oauthTokens.expires_in
Write-Output "Refresh token: " $oauthTokens.refresh_token
