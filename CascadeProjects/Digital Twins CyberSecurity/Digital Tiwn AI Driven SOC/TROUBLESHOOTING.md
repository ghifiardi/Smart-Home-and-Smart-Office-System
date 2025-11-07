# 🔧 Troubleshooting Guide - Digital Twin SOC Showcase

## 🎯 Quick Fix Checklist

### ✅ Step 1: Verify You're on the Correct URL
Make sure you're accessing:
```
https://ghifiardi.github.io/digital_twin_SOC_sowcase/Digital-Twin-SOC-Showcase.html
```

**NOT:**
- `index.html` (different file)
- Cached version
- Local file

### ✅ Step 2: Clear Browser Cache
**Chrome/Edge:**
1. Press `Ctrl+Shift+Delete` (Windows) or `Cmd+Shift+Delete` (Mac)
2. Select "Cached images and files"
3. Click "Clear data"
4. Hard refresh: `Ctrl+Shift+R` or `Cmd+Shift+R`

**Safari:**
1. Safari menu → Clear History
2. Select "all history"
3. Hard refresh: `Cmd+Option+R`

**Firefox:**
1. Press `Ctrl+Shift+Delete`
2. Select "Cache"
3. Click "Clear Now"
4. Hard refresh: `Ctrl+F5`

### ✅ Step 3: Wait for GitHub Pages Update
GitHub Pages can take **2-5 minutes** to update after a push:
1. Check deployment status: https://github.com/ghifiardi/digital_twin_SOC_sowcase/actions
2. Wait 2-5 minutes after seeing "Deploy" action complete
3. Try accessing the URL again

### ✅ Step 4: Verify GitHub Pages is Enabled
1. Go to: https://github.com/ghifiardi/digital_twin_SOC_sowcase/settings/pages
2. Verify:
   - Source: **Deploy from a branch**
   - Branch: **main** / **(root)**
   - If not set, select `main` branch and save

### ✅ Step 5: Check Browser Console for Errors
1. Open DevTools: Press `F12` or `Cmd+Option+I`
2. Go to **Console** tab
3. Look for red error messages
4. Common issues:
   - **CORS errors**: Normal for local testing, should work on GitHub Pages
   - **404 errors**: File not found - check URL path
   - **JavaScript errors**: Check if scripts are loading

---

## 🎙️ Finding the Narration Panel

The **Live Activity Voice Guide** panel should appear:

### Location:
1. Scroll down to **"Step 4: Live Threat Response"** section
2. Look for a **prominent indigo/purple panel** with:
   - 🎙️ Icon
   - "Live Activity Voice Guide" title
   - "🔊 Enable Voice" button
   - Welcome text explaining the dashboard

### What to Look For:
- **Large indigo/purple gradient box**
- **Border with glow effect**
- **Microphone emoji (🎙️)** at the top
- **Two buttons**: "Enable Voice" and "Pause"

---

## 🔍 Verification Steps

### Test 1: File Exists
```bash
# Check if file is in repository
curl -I https://ghifiardi.github.io/digital_twin_SOC_sowcase/Digital-Twin-SOC-Showcase.html
```
Should return: `200 OK`

### Test 2: Content Verification
```bash
# Check if narration panel HTML exists
curl -s https://ghifiardi.github.io/digital_twin_SOC_sowcase/Digital-Twin-SOC-Showcase.html | grep -i "narrationText"
```
Should return: HTML code with `id="narrationText"`

### Test 3: JavaScript Loading
1. Open browser DevTools (F12)
2. Go to **Network** tab
3. Reload page
4. Verify:
   - `Digital-Twin-SOC-Showcase.html` loads (200 status)
   - No 404 errors
   - Tailwind CSS loads correctly

---

## 🐛 Common Issues & Solutions

### Issue 1: "Page Not Found" (404)
**Cause:** File not deployed or wrong URL
**Solution:**
1. Verify file exists in repository
2. Check GitHub Pages settings
3. Wait 2-5 minutes after deployment
4. Try: `https://ghifiardi.github.io/digital_twin_SOC_sowcase/Digital-Twin-SOC-Showcase.html`

### Issue 2: Narration Panel Not Visible
**Cause:** CSS not loading or panel hidden
**Solution:**
1. Check browser console for CSS errors
2. Verify Tailwind CSS CDN is loading
3. Try incognito/private window
4. Check if panel is scrolled out of view

### Issue 3: Voice Narration Not Working
**Cause:** Browser doesn't support Web Speech API
**Solution:**
1. **Text narration always works** - you'll see text updates
2. Voice requires:
   - Chrome/Edge: ✅ Full support
   - Safari: ✅ Full support  
   - Firefox: ⚠️ Limited support
3. Check browser permissions for speech

### Issue 4: Old Version Showing
**Cause:** Browser cache
**Solution:**
1. Clear cache (see Step 2 above)
2. Try incognito/private window
3. Add `?v=2` to URL: `...Showcase.html?v=2`

### Issue 5: JavaScript Errors
**Cause:** Scripts not loading or conflicts
**Solution:**
1. Check browser console (F12)
2. Verify all scripts load:
   - Tailwind CSS CDN
   - Fonts (Google Fonts)
3. Disable browser extensions temporarily

---

## 📱 Testing on Different Devices

### Desktop (Chrome/Edge)
✅ Best experience
- Full voice support
- All features work
- Clear narration panel

### Mobile (iOS Safari)
✅ Good experience
- Voice support available
- Responsive design
- Touch-friendly controls

### Mobile (Android Chrome)
✅ Good experience
- Voice support available
- May need to enable permissions
- Scroll to find narration panel

---

## 🚀 Force Refresh GitHub Pages

If updates aren't showing:

1. **Trigger Rebuild:**
   - Make a small change to file
   - Commit and push
   - Wait 2-5 minutes

2. **Check Actions:**
   - Go to: https://github.com/ghifiardi/digital_twin_SOC_sowcase/actions
   - Verify deployment completed successfully

3. **Clear CDN Cache:**
   - GitHub Pages uses CDN caching
   - Wait 5-10 minutes for full cache refresh
   - Or use: `?nocache=` + timestamp

---

## 📞 Still Not Working?

### Quick Diagnostic Commands

1. **Check file exists:**
```bash
curl -I https://ghifiardi.github.io/digital_twin_SOC_sowcase/Digital-Twin-SOC-Showcase.html
```

2. **Check file content:**
```bash
curl -s https://ghifiardi.github.io/digital_twin_SOC_sowcase/Digital-Twin-SOC-Showcase.html | grep -c "narrationText"
```
Should return: `3` or higher

3. **Check GitHub Pages status:**
Visit: https://github.com/ghifiardi/digital_twin_SOC_sowcase/settings/pages

---

## ✅ Expected Behavior

When working correctly, you should see:

1. **Page loads** without errors
2. **Narration panel** visible in "Step 4: Live Threat Response" section
3. **"Enable Voice" button** clickable
4. **Welcome text** explaining the dashboard
5. **When you click "Live Threat Response":**
   - Narration text updates in real-time
   - Explains each step (ADA, TAA, CRA)
   - Voice narration plays (if enabled)
   - Timeline shows threat response actions

---

## 🎯 Quick Test Checklist

- [ ] Correct URL: `...Digital-Twin-SOC-Showcase.html`
- [ ] Browser cache cleared
- [ ] Waited 2-5 minutes after deployment
- [ ] GitHub Pages enabled in settings
- [ ] No console errors (F12)
- [ ] Narration panel visible (indigo/purple box)
- [ ] "Enable Voice" button present
- [ ] Can click "Live Threat Response" button
- [ ] Narration text updates when demo runs

---

*Last updated: November 7, 2024*

