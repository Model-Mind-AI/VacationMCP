# Deploy VacationMCP to Render and Use with Cursor

This guide walks you through deploying your VacationMCP REST API to Render and configuring Cursor to use it locally via the MCP server.

---

## Part 1: Deploy to Render

### Step 1: Prepare Your Repository

1. **Ensure your code is committed and pushed to GitHub/GitLab/Bitbucket:**
   ```powershell
   git add .
   git commit -m "Ready for Render deployment"
   git push origin main
   ```

2. **Verify required files exist:**
   - ✅ `Dockerfile`
   - ✅ `render.yaml`
   - ✅ `requirements.txt`
   - ✅ `src/` directory with your app code

### Step 2: Create Render Account and Service

1. **Go to [render.com](https://render.com) and sign up/login**

2. **Create a New Web Service:**
   - Click "New +" → "Web Service"
   - Connect your Git repository (GitHub/GitLab/Bitbucket)
   - Select the repository containing your VacationMCP code

3. **Render will auto-detect `render.yaml`:**
   - Service name: `vacation-mcp` (or your preferred name)
   - Region: `oregon` (or your preferred region)
   - Plan: `Free` (as specified in render.yaml)
   - Render will detect Docker deployment from `render.yaml`

### Step 3: Configure Environment Variables

1. **In Render Dashboard, go to your service → Environment:**
   - Click "Add Environment Variable"
   - Key: `API_KEY`
   - Value: Generate a secure API key (e.g., use a password generator or `openssl rand -hex 32`)
   - **IMPORTANT**: Save this API key! You'll need it for Cursor configuration.

2. **Click "Save Changes"** - Render will automatically redeploy

### Step 4: Wait for Deployment

1. **Monitor the deployment:**
   - Go to "Events" tab in Render dashboard
   - Watch for "Build succeeded" and "Deploy succeeded"
   - First deployment may take 5-10 minutes

2. **Get your service URL:**
   - Once deployed, Render provides a URL like: `https://vacation-mcp.onrender.com`
   - Copy this URL - you'll need it for the MCP server

3. **Verify deployment:**
   ```powershell
   # Test health endpoint
   $renderUrl = "https://vacation-mcp.onrender.com"  # Replace with your URL
   Invoke-RestMethod -Uri "$renderUrl/health" -Method GET
   ```
   Expected: `{"status": "ok"}`

### Step 5: Test the API (Optional but Recommended)

```powershell
$renderUrl = "https://vacation-mcp.onrender.com"
$apiKey = "YOUR_API_KEY_HERE"

# Test balance endpoint
$headers = @{
    "X-API-Key" = $apiKey
    "X-Employee-Id" = "alice"
}
Invoke-RestMethod -Uri "$renderUrl/balance" -Method GET -Headers $headers
```

Expected: `{"hoursAvailable": 80}`

---

## Part 2: Set Up Local MCP Server for Cursor

### Step 1: Install Required Python Packages

Open PowerShell in your project directory:

```powershell
# Create virtual environment (if not already done)
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install MCP SDK and requests
pip install mcp requests
```

### Step 2: Verify MCP Server Script

Ensure `mcp_server.py` exists in your project root. If not, it should have been created from the previous guide.

Test it manually:

```powershell
# Set environment variables
$env:VACATION_API_URL="https://vacation-mcp.onrender.com"  # Your Render URL
$env:VACATION_API_KEY="YOUR_API_KEY_HERE"  # Your API key from Render

# Test the script (it will wait for stdio input, so Ctrl+C to exit)
python mcp_server.py
```

If you see import errors, install missing packages. If it starts without errors, you're good!

### Step 3: Configure Cursor MCP Settings

1. **Find Cursor's MCP configuration file:**
   - Windows location: `%APPDATA%\Cursor\User\globalStorage\mcp.json`
   - Full path example: `C:\Users\LorenHorsager\AppData\Roaming\Cursor\User\globalStorage\mcp.json`

2. **Create or edit the MCP configuration file:**

   If the file doesn't exist, create it. If it exists, add to the existing `mcpServers` object.

   ```json
   {
     "mcpServers": {
       "vacation-mcp": {
         "command": "python",
         "args": [
           "C:\\Users\\LorenHorsager\\source\\repos\\VacationMCP\\mcp_server.py"
         ],
         "env": {
           "VACATION_API_URL": "https://vacation-mcp.onrender.com",
           "VACATION_API_KEY": "YOUR_API_KEY_HERE"
         }
       }
     }
   }
   ```

   **Important Notes:**
   - Replace `C:\\Users\\LorenHorsager\\source\\repos\\VacationMCP\\mcp_server.py` with the **full absolute path** to your `mcp_server.py` file
   - Replace `https://vacation-mcp.onrender.com` with your actual Render service URL
   - Replace `YOUR_API_KEY_HERE` with the API key you set in Render
   - Use double backslashes (`\\`) in Windows paths
   - Use forward slashes (`/`) if you prefer: `C:/Users/LorenHorsager/source/repos/VacationMCP/mcp_server.py`

3. **Alternative: Use relative path with working directory:**

   If you want to use a relative path, you can specify the working directory:

   ```json
   {
     "mcpServers": {
       "vacation-mcp": {
         "command": "python",
         "args": ["mcp_server.py"],
         "cwd": "C:\\Users\\LorenHorsager\\source\\repos\\VacationMCP",
         "env": {
           "VACATION_API_URL": "https://vacation-mcp.onrender.com",
           "VACATION_API_KEY": "YOUR_API_KEY_HERE"
         }
       }
     }
     }
   }
   ```

### Step 4: Restart Cursor

1. **Close Cursor completely** (not just the window - exit the application)
2. **Reopen Cursor**
3. Cursor will load the MCP server configuration on startup

### Step 5: Verify MCP Server is Connected

1. **Check Cursor's MCP status:**
   - Look for MCP server connection status in Cursor's settings or status bar
   - Some versions show this in the bottom status bar

2. **Test with a query:**
   - In Cursor's chat, try: "Check vacation balance for employee alice"
   - If working, you should get a response about vacation hours

---

## Part 3: Testing the Integration

### Test the Complete Flow

1. **Check Balance:**
   ```
   Check vacation balance for employee alice
   ```
   Expected: Response showing "80 hours"

2. **Request Vacation:**
   ```
   Request vacation for alice from 2024-12-20 to 2024-12-22
   ```
   Expected: Response showing request status (Approved/Declined)

3. **List Requests:**
   ```
   Show all vacation requests for alice
   ```
   Expected: List of vacation requests with dates and status

### Troubleshooting

#### MCP Server Not Starting

**Check Cursor logs:**
- Look for error messages in Cursor's output/console
- Common issues:
  - Python not in PATH: Use full path to python.exe in `command`
  - Missing packages: Run `pip install mcp requests` in your venv
  - Wrong file path: Verify the path to `mcp_server.py` is correct

**Test manually:**
```powershell
$env:VACATION_API_URL="https://vacation-mcp.onrender.com"
$env:VACATION_API_KEY="YOUR_API_KEY"
python mcp_server.py
```
If this doesn't work, fix the issue before configuring Cursor.

#### API Connection Errors

**Verify Render service is running:**
```powershell
Invoke-RestMethod -Uri "https://vacation-mcp.onrender.com/health"
```

**Check API key:**
- Ensure the API key in Cursor config matches Render's `API_KEY` environment variable
- Case-sensitive! Ensure exact match

**Check Render service logs:**
- In Render dashboard → Your service → Logs
- Look for authentication errors or connection issues

#### Cursor Not Finding Tools

**Restart Cursor:**
- Fully close and reopen Cursor
- MCP servers are loaded on startup

**Check JSON syntax:**
- Validate your `mcp.json` file (use a JSON validator)
- Ensure no trailing commas
- Ensure all strings are properly quoted

**Verify MCP server is running:**
- Check Windows Task Manager for Python processes
- Look for processes running `mcp_server.py`

---

## Quick Reference

### Render Service URL
- Find it in: Render Dashboard → Your Service → Settings
- Format: `https://your-service-name.onrender.com`

### API Key
- Find it in: Render Dashboard → Your Service → Environment → `API_KEY`
- Keep this secret! Don't commit it to git.

### Cursor MCP Config Location
- Windows: `%APPDATA%\Cursor\User\globalStorage\mcp.json`
- Or: `C:\Users\YOUR_USERNAME\AppData\Roaming\Cursor\User\globalStorage\mcp.json`

### Project Files Needed
- `mcp_server.py` - Local MCP server script
- `src/` - Your FastAPI application code
- `Dockerfile` - For Render deployment
- `render.yaml` - Render configuration
- `requirements.txt` - Python dependencies

---

## Next Steps

Once everything is working:

1. **Test all MCP tools** through Cursor
2. **Create more employees** if needed (modify seed data in `src/app.py`)
3. **Monitor Render logs** for any issues
4. **Consider adding more features** to your vacation management system

If you encounter issues, check:
- Render service logs
- Cursor's MCP server logs
- Network connectivity to Render
- API key correctness

