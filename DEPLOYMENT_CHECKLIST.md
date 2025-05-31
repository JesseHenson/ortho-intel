# 🚀 Quick Deployment Checklist

## ✅ Before Deployment

- [ ] Commit all changes to Git
- [ ] Push to GitHub repository
- [ ] Test local build: `cd src/frontend-react && npm run build`
- [ ] Have API keys ready (Anthropic, OpenAI, Perplexity, etc.)

## 🖥️ Backend Deployment (Railway)

1. **Sign up for Railway**: https://railway.app
2. **Create New Project** → **Deploy from GitHub repo**
3. **Select repository**: `ortho-intel`
4. **Add Environment Variables**:
   ```
   ANTHROPIC_API_KEY=your_key_here
   PERPLEXITY_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here
   ```
5. **Deployment should start automatically**
6. **Get your backend URL**: `https://your-app-name.railway.app`

## 🌐 Frontend Deployment (Vercel)

1. **Sign up for Vercel**: https://vercel.com
2. **Import Git Repository** → Select `ortho-intel`
3. **Configure Project**:
   - Framework: `Vite`
   - Root Directory: `src/frontend-react`
   - Build Command: `npm run build`
   - Output Directory: `dist`
   - Install Command: `npm install --legacy-peer-deps`
4. **Add Environment Variable**:
   ```
   VITE_API_BASE_URL=https://your-backend-app.railway.app
   ```
5. **Deploy**
6. **Get your frontend URL**: `https://your-app-name.vercel.app`

## 🔧 Post-Deployment

- [ ] Test the deployed frontend URL
- [ ] Test API endpoints: `https://your-backend-app.railway.app/docs`
- [ ] Run a sample analysis to verify everything works
- [ ] Share URLs with marketing firm/investors

## 💰 Cost Estimate

- **Railway**: Free tier, then ~$5/month
- **Vercel**: Free tier (sufficient for demos)
- **Total**: Free for demos, ~$5/month for production

## 🎯 Demo URLs to Share

```
Frontend: https://your-app-name.vercel.app
Backend API: https://your-backend-app.railway.app/docs
```

## 🚨 Troubleshooting

**Build fails**: Check TypeScript errors with `npm run build`
**API errors**: Check Railway logs and environment variables
**CORS issues**: Verify frontend URL is in backend CORS settings
**404 on routes**: Vercel should handle this automatically with vercel.json 