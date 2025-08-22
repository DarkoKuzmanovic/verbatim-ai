# Vercel Deployment Guide

## Current Configuration

This project is configured for Vercel deployment with the following setup:

### Files Structure

```tree
├── api/
│   └── index.py          # Main FastAPI app for Vercel
├── vercel.json           # Vercel configuration
├── runtime.txt           # Python version specification
├── requirements.txt      # Python dependencies
└── .vercelignore        # Files to exclude from deployment
```

### Key Configuration Files

**vercel.json**: Defines build settings and routing
**runtime.txt**: Specifies Python 3.11.0
**api/index.py**: Contains the complete FastAPI application with embedded HTML

## Deployment Steps

1. **Set Environment Variables in Vercel Dashboard:**

   - `OPENROUTER_API_KEY`: Your OpenRouter API key

2. **Deploy to Vercel:**

   ```bash
   vercel --prod
   ```

3. **Test Endpoints:**
   - Root: `https://your-app.vercel.app/`
   - Health: `https://your-app.vercel.app/health`
   - Test: `https://your-app.vercel.app/api/test`
   - Transcript: `https://your-app.vercel.app/api/transcript`
   - Format: `https://your-app.vercel.app/api/format`

## Troubleshooting

### 404 Errors

- Check that `api/index.py` exists and contains the `handler = app` export
- Verify `vercel.json` routing configuration
- Ensure Python version in `runtime.txt` is supported

### Import Errors

- The app includes fallback import logic for Vercel's serverless environment
- All dependencies are bundled in the deployment

### Environment Variables

- Make sure `OPENROUTER_API_KEY` is set in Vercel dashboard
- Check the `/health` endpoint to verify configuration

## Local Testing

To test the Vercel-compatible version locally:

```bash
cd api
python -c "from index import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000)"
```

Then visit: <http://localhost:8000>
