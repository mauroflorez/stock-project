# 🚀 Quick Start Guide

## Complete Setup in 5 Minutes

### Step 1: Install Ollama (2 minutes)

1. Go to https://ollama.com/download
2. Download for your OS (Mac/Windows/Linux)
3. Install and run

### Step 2: Download an AI Model (2 minutes)

Open terminal and run:
```bash
ollama pull llama3.1:8b
```

Wait for download to complete (~4.7 GB)

### Step 3: Install Python Packages (1 minute)

```bash
pip install -r requirements.txt
```

### Step 4: Test Everything

```bash
python test_setup.py
```

You should see all green checkmarks ✅

### Step 5: Run Your First Analysis!

```bash
python main.py
```

This will:
- Fetch Google (GOOGL) stock data
- Get recent news
- Run 4 AI agents
- Save results to `output/` folder

Takes about 2-5 minutes depending on your computer.

### Step 6: Generate HTML Report

```bash
python generate_report.py
```

### Step 7: View Results

Open `docs/index.html` in your browser!

## Troubleshooting

### "Ollama is not running"
```bash
# Start Ollama in a separate terminal
ollama serve
```

### "Model not found"
```bash
# Download the model
ollama pull llama3.1:8b
```

### "Module not found"
```bash
# Install dependencies
pip install -r requirements.txt
```

## What's Next?

1. **Add more stocks** - Edit `config.py`
2. **Try different models** - `ollama pull mistral` or `ollama pull deepseek-r1`
3. **Deploy to GitHub Pages** - See README.md
4. **Schedule daily runs** - Set up a cron job

## Need Help?

- Check README.md for detailed docs
- Run `python test_setup.py` to diagnose issues
- Make sure Ollama is running: `ollama serve`

---

**That's it! You now have a working AI stock analysis system running locally for FREE! 🎉**
