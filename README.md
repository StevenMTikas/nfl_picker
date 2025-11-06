# NFL Picker

An AI-powered NFL team analysis and game prediction system using CrewAI.

## Quick Start

1. **Installation**: See [doc/user-guides/README.md](doc/user-guides/README.md)
2. **Usage**: See [doc/user-guides/USAGE_GUIDE.md](doc/user-guides/USAGE_GUIDE.md)
3. **Complete Documentation**: See [doc/README.md](doc/README.md)

## Documentation

All project documentation is organized in the [`doc/`](doc/) folder:

- **User Guides**: Setup and usage instructions
- **Development**: Technical details and change history  
- **Features**: Feature-specific documentation

## Running the Application

### Web Application (Recommended for Portfolio)

```bash
# Install dependencies
pip install -e .

# Run the web app
python run_web.py
# or
python app.py
```

Then open your browser to `http://localhost:5000`

### Desktop GUI Application

```bash
python run_gui.py
```

## Deployment

### Deploy to Render

The project includes a `render.yaml` configuration file. To deploy:

1. Push your code to GitHub
2. Connect your repository to Render
3. Render will automatically detect the configuration and deploy

**Build Command:** `pip install -e .`  
**Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`

---

*For complete documentation, see the [doc/](doc/) folder.*
