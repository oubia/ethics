# Azure Deployment Guide for Ethics RAG App

## Quick Summary

You're deploying your ethics RAG application to **Azure Container Instances (ACI)** using **Azure Container Registry (ACR)** to store Docker images, with **GitHub Actions** automating the build and push process.

---

## Your Azure Setup (Already Created ✅)

| Resource | Value |
|----------|-------|
| **Resource Group** | `ethics-rg` |
| **Container Registry** | `ethicsacr` |
| **Login Server** | `ethicsacr.azurecr.io` |
| **Username** | `ethicsacr` |
| **Region** | (Europe) Italy North |

---

## Step 1: Add GitHub Secrets (5 min)

Go to: **GitHub** → Your repo (`oubia/ethics`) → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these 3 secrets:

| Secret Name | Value |
|-------------|-------|
| `AZURE_REGISTRY_LOGIN_SERVER` | `ethicsacr.azurecr.io` |
| `AZURE_REGISTRY_USERNAME` | `ethicsacr` |
| `AZURE_REGISTRY_PASSWORD` | `9np5mEHKCSNJdALYNA16hZTAbm4Cc7l9BWKwCgd/cY+ACRD1f5lo` |

**Screenshot:**
```
Secret Name: AZURE_REGISTRY_LOGIN_SERVER
Secret Value: ethicsacr.azurecr.io
[Add secret]

Secret Name: AZURE_REGISTRY_USERNAME
Secret Value: ethicsacr
[Add secret]

Secret Name: AZURE_REGISTRY_PASSWORD
Secret Value: 9np5mEHKCSNJdALYNA16hZTAbm4Cc7l9BWKwCgd/cY+ACRD1f5lo
[Add secret]
```

---

## Step 2: Push Code to GitHub (2 min)

On your local machine (PowerShell):

```powershell
cd "d:\homy\Boss fight\Ethics\ethics"
git push origin main
```

**What happens:**
- GitHub Actions workflow starts automatically
- Builds your 3 Docker images (backend, frontend, ollama)
- Pushes them to Azure Container Registry (ACR)
- Workflow completes in ~5-10 minutes

**Watch the deployment:**
- Go to **GitHub** → **Actions**
- Click on the latest workflow run
- Watch logs in real-time

**Expected output:**
```
✅ All images built and pushed to ACR successfully!
Images available at:
  - ethicsacr.azurecr.io/ethics-frontend:latest
  - ethicsacr.azurecr.io/ethics-backend:latest
  - ethicsacr.azurecr.io/ethics-ollama:latest
```

---

## Step 3: Create Container Instance in Azure (5 min)

Once images are in ACR, create the container:

1. Go to **Azure Portal** → Search **"Container Instances"**
2. Click **"Create"**
3. Fill in:
   - **Subscription:** Your student subscription
   - **Resource group:** `ethics-rg`
   - **Container name:** `ethics-app`
   - **Region:** `(Europe) Italy North` (same as ACR)
   - **Image source:** `Azure Container Registry`
   - **Registry:** `ethicsacr`
   - **Image:** `ethics-frontend` (click dropdown and select)
   - **Image tag:** `latest`
   - **Size:** CPU: 2, Memory: 2 GB
4. Click **"Next: Ports"**
   - **Expose DNS name:** ✅ Check
   - **DNS name label:** `ethics-app`
   - **Ports:** `80`, `443` (Protocol: TCP)
5. Click **"Review + Create"** → **"Create"**

---

## Step 4: Get Your Public IP/FQDN (2 min)

Once the container is deployed (~2 min):

1. Go to **Azure Portal** → **Container Instances** → **ethics-app**
2. **Status** should show "Running"
3. Copy the **Public IP** or **FQDN**:
   - FQDN: `ethics-app.italynorth.azurecontainers.io` (or similar)
   - Public IP: `xxx.xxx.xxx.xxx`

You'll use this in Namecheap DNS.

---

## Step 5: Update Namecheap DNS (3 min)

1. Go to **Namecheap** → **Domain List** → **oubia.me** → **Manage** → **Advanced DNS**
2. **Add two A records:**

   **Record 1:**
   - **Type:** A Record
   - **Host:** `ethics`
   - **Value:** `YOUR_AZURE_PUBLIC_IP` (from Step 4)
   - **TTL:** Automatic
   - Click **Save**

   **Record 2:**
   - **Type:** A Record
   - **Host:** `api.ethics`
   - **Value:** `YOUR_AZURE_PUBLIC_IP` (same)
   - **TTL:** Automatic
   - Click **Save**

3. Click **"SAVE ALL CHANGES"** (green button at bottom)
4. **Wait 5–15 minutes** for DNS to propagate

---

## Step 6: Verify Your App is Live (5 min)

Once DNS propagates, test these URLs in your browser:

- **Frontend:** https://ethics.oubia.me
  - You should see your React app UI
- **API Docs:** https://api.ethics.oubia.me/docs
  - You should see FastAPI Swagger documentation

**Check SSL Certificate:**
- Click the 🔒 padlock in the browser address bar
- Should show "Secure" with a certificate

**If SSL fails:**
- DNS might not be fully propagated yet
- Wait a few more minutes and refresh
- Or test using the Azure FQDN directly (without SSL)

---

## Step 7: Future Updates (Automatic! ✨)

Every time you push to `main`:

1. GitHub Actions builds new images
2. Pushes them to ACR
3. **Manual step:** Update the container instance with new image in Azure Portal

**To update container:**
1. Azure Portal → Container Instances → ethics-app
2. Stop the container
3. Delete it
4. Create new one with latest image from ACR

**(Optional) Fully Automate with Azure CLI:**
You can add Azure credentials to GitHub secrets and fully automate the deployment. Ask if you want this setup later!

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **GitHub Actions fails** | Check workflow logs in GitHub Actions tab; ensure secrets are correct |
| **Images not in ACR** | Wait for workflow to complete; check Actions tab for errors |
| **Container won't start** | Check container logs in Azure Portal; verify image name is correct |
| **DNS not working** | Wait 5-15 min; verify A records are added in Namecheap; test with `nslookup ethics.oubia.me` |
| **SSL certificate errors** | Ensure DNS is propagated first; Let's Encrypt needs valid DNS |
| **App slow/timing out** | Azure Student credits might be rate-limited; check resource usage in Azure Portal |

---

## Useful Azure Portal Links

- Container Instances: https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.ContainerInstance%2FcontainerGroups
- Container Registry: https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.ContainerRegistry%2Fregistries
- Resource Groups: https://portal.azure.com/#view/HubsExtension/BrowseResource/resourceType/Microsoft.Resources%2Fsubscriptions%2FresourceGroups

---

## Cost Tracking

**Your app currently uses:**
- Container Instances: ~$35/month (2 vCPU, 2 GB RAM)
- Container Registry: ~$5/month (Basic tier)
- **Total:** ~$40/month (covered by $100 student credits)

**After 12 months:** $50/month student credits (still covers it!)

---

## Next Steps

1. ✅ Add GitHub Secrets (see Step 1)
2. ✅ Push to GitHub (see Step 2)
3. ⏳ Wait for workflow to complete
4. ⏳ Create Container Instance (see Step 3)
5. ⏳ Update Namecheap DNS (see Step 5)
6. ⏳ Test app is live (see Step 6)

**You're almost there!** 🚀
