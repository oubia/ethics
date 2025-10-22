# Azure Deployment - Next Steps (After Code Fix)

## Current Status

✅ Code fixes committed and pushed to GitHub (`main` branch)  
✅ Azure Container Registry (ACR) created: `ethicsacr.azurecr.io`  
✅ GitHub Actions workflow ready to build and push images  

**Now you need to:**

---

## Step 1: Verify GitHub Actions Workflow

The new code you pushed should trigger the GitHub Actions workflow to rebuild images with your fixes.

### Check Workflow Status:

1. Go to: https://github.com/oubia/ethics/actions
2. Look for a workflow run (should start automatically)
3. Wait for it to complete (~10-15 minutes)

**Expected Result:**
- ✅ All 3 images built successfully
- ✅ Images pushed to ACR:
  - `ethicsacr.azurecr.io/ethics-frontend:latest`
  - `ethicsacr.azurecr.io/ethics-backend:latest`
  - `ethicsacr.azurecr.io/ethics-ollama:latest`

---

## Step 2: Update Container Instance in Azure

Since you already have the Container Instance and ACR set up, you need to **update it with the new images**.

### Option A: Manual Update (Azure Portal)

1. Go to: https://portal.azure.com
2. Search for **"Container Instances"**
3. Find your container (probably `ethics-app`)
4. **Stop** the container
5. **Delete** the container
6. Click **"+ Create"** to create a new one:

**Fill in:**
- **Subscription:** Your student account
- **Resource Group:** `ethics-rg`
- **Container name:** `ethics-app`
- **Region:** `Italy North` (same as ACR)
- **Image source:** `Azure Container Registry`
- **Registry:** `ethicsacr`
- **Image:** Select `ethics-frontend` (the runner container)
- **Image tag:** `latest`
- **Size:** CPU: 2, Memory: 2GB

7. **Next: Networking**
   - ✅ Check "Expose DNS name"
   - **DNS name label:** `ethics-app`
   - **Ports:** Add 80 and 443 (TCP)

8. **Review + Create** → **Create**

**Wait ~2 minutes for it to start**

### Option B: Azure CLI (Faster)

If you have Azure CLI installed:

```bash
# Remove old container
az container delete \
  --resource-group ethics-rg \
  --name ethics-app \
  --yes

# Create new container with latest images
az container create \
  --resource-group ethics-rg \
  --name ethics-app \
  --image ethicsacr.azurecr.io/ethics-frontend:latest \
  --registry-login-server ethicsacr.azurecr.io \
  --registry-username ethicsacr \
  --registry-password <YOUR_PASSWORD> \
  --cpu 2 \
  --memory 2 \
  --ports 80 443 \
  --dns-name-label ethics-app
```

---

## Step 3: Get Public IP/FQDN

Once the container is running:

1. Go to: https://portal.azure.com
2. **Container Instances** → **ethics-app**
3. Copy the **FQDN** (something like `ethics-app.italynorth.azurecontainers.io`)
4. Or copy the **Public IP address**

---

## Step 4: Update DNS (If Not Already Done)

If your DNS is not already pointing to the container:

1. Go to: https://www.namecheap.com
2. Log in and go to **Domain List** → **oubia.me** → **Manage** → **Advanced DNS**
3. Add/Update A Records:

   ```
   Record 1:
   Type: A Record
   Host: ethics
   Value: <YOUR_AZURE_PUBLIC_IP>
   TTL: Automatic
   
   Record 2:
   Type: A Record
   Host: api.ethics
   Value: <YOUR_AZURE_PUBLIC_IP>
   TTL: Automatic
   ```

4. **Save all changes**
5. Wait 5-15 minutes for DNS propagation

---

## Step 5: Test Your Deployment

Once the container is running and DNS is updated, test:

```bash
# Test frontend
curl https://ethics.oubia.me

# Test backend API
curl https://api.ethics.oubia.me/docs

# Test Ollama is accessible
curl https://api.ethics.oubia.me/ollama/api/tags
```

Or open in browser:
- **Frontend:** https://ethics.oubia.me
- **API Docs:** https://api.ethics.oubia.me/docs

---

## What's New in This Deployment?

Your code fixes are now deployed:

✅ **Nginx PORT configuration** - Properly handles port binding  
✅ **Frontend Docker** - Now has nginx runner stage to serve React  
✅ **Whisper support** - Audio transcription works  
✅ **Better error handling** - Removed Bedrock fallback  

---

## Troubleshooting

### GitHub Actions workflow fails
- Check: https://github.com/oubia/ethics/actions
- Click on failed workflow to see error logs
- Common issue: Secrets not set correctly in GitHub

### Container won't start
- Go to Azure Portal → Container Instances → ethics-app
- Click **Containers** tab
- Check the logs for error messages
- Look for: Network issues, image not found, etc.

### DNS not working
```bash
# Test DNS resolution
nslookup ethics.oubia.me

# Should return your Azure public IP
# If not, DNS hasn't propagated yet - wait longer
```

### App not responding
- Verify container is running: `docker ps` (if SSH'd into it)
- Check Caddy logs if reverse proxy isn't routing correctly
- Verify all services (frontend, backend, ollama) are in the container

---

## Quick Reference: Your Azure Resources

| Resource | Value |
|----------|-------|
| **ACR** | `ethicsacr.azurecr.io` |
| **Resource Group** | `ethics-rg` |
| **Container Name** | `ethics-app` |
| **Region** | `Italy North` |
| **Frontend URL** | `https://ethics.oubia.me` |
| **Backend URL** | `https://api.ethics.oubia.me` |

---

## Next Actions (Checklist)

- [ ] Wait for GitHub Actions workflow to complete (10-15 min)
- [ ] Verify images in ACR are updated
- [ ] Delete old container instance
- [ ] Create new container with latest images
- [ ] Wait for container to start (~2 min)
- [ ] Get public IP/FQDN from Azure
- [ ] Update DNS in Namecheap (if needed)
- [ ] Wait for DNS propagation (5-15 min)
- [ ] Test URLs in browser
- [ ] Verify SSL certificates work
- [ ] Test chat functionality

---

## Cost Estimate

**Monthly cost:**
- Container Instances (2vCPU, 2GB RAM): ~$35/month
- Container Registry (Basic): ~$5/month
- **Total:** ~$40/month
- **Covered by:** Azure Student credits ($100/month for 12 months)

---

## Questions?

- **How do I SSH into the container?** 
  - Azure Portal → Container Instances → ethics-app → Containers → Select container → Click "Logs"
  - Or use: `az container exec --resource-group ethics-rg --name ethics-app --exec-command /bin/sh`

- **How do I see container logs?**
  - Azure Portal → Container Instances → ethics-app → Containers → Logs tab

- **Can I scale to multiple containers?**
  - Not directly with ACI - upgrade to Azure Kubernetes Service (AKS) for orchestration

- **How do I automate container updates?**
  - Add Azure credentials to GitHub Secrets and fully automate with GitHub Actions

---

**Ready to deploy? Start with Step 1!** 🚀
