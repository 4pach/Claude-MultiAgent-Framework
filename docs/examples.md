---
title: Examples
layout: default
nav_order: 5
---

# 💡 Examples

Real-world examples of using Claude MultiAgent Framework.

## Telegram Bot Example

### Basic AI Bot

```python
from claude_framework import TelegramBot, track_mcp_call

class AIBot(TelegramBot):
    def __init__(self, token):
        super().__init__(token)
        self.ai_service = self.get_ai_service()
    
    @track_mcp_call("telegram_bot", "ai_response")
    async def handle_message(self, message):
        # Process message with AI
        response = await self.ai_service.process(message.text)
        return response
    
    async def handle_photo(self, photo):
        # Process photo with vision AI
        analysis = await self.ai_service.analyze_image(photo)
        return f"I can see: {analysis}"

# Run the bot
bot = AIBot("YOUR_BOT_TOKEN")
bot.run()
```

### Advanced Bot with Commands

```python
from claude_framework import TelegramBot, CommandHandler

class AdvancedBot(TelegramBot):
    def __init__(self, token):
        super().__init__(token)
        self.add_handler(CommandHandler("start", self.start_command))
        self.add_handler(CommandHandler("help", self.help_command))
        self.add_handler(CommandHandler("analyze", self.analyze_command))
    
    async def start_command(self, update, context):
        welcome_text = "Welcome to Claude MultiAgent Bot!\n\nI can help you with:\n- AI text processing\n- Image analysis\n- Task automation"
        await update.message.reply_text(welcome_text)
    
    async def analyze_command(self, update, context):
        if not context.args:
            await update.message.reply_text("Please provide text to analyze")
            return
        
        text = " ".join(context.args)
        analysis = await self.ai_service.analyze_sentiment(text)
        await update.message.reply_text(f"Analysis: {analysis}")

bot = AdvancedBot("YOUR_BOT_TOKEN")
bot.run()
```

## Web API Example

### FastAPI Service

```python
from claude_framework import FastAPIApp, AutoMonitoring
from pydantic import BaseModel

app = FastAPIApp("AI Analysis API")

class AnalysisRequest(BaseModel):
    text: str
    language: str = "en"

class AnalysisResponse(BaseModel):
    sentiment: str
    confidence: float
    keywords: list

@app.post("/analyze", response_model=AnalysisResponse)
@AutoMonitoring.track_performance
async def analyze_text(request: AnalysisRequest):
    # AI analysis with automatic monitoring
    result = await ai_analyzer.process(
        text=request.text,
        language=request.language
    )
    
    return AnalysisResponse(
        sentiment=result.sentiment,
        confidence=result.confidence,
        keywords=result.keywords
    )

@app.get("/health")
async def health_check():
    stats = await app.get_health_stats()
    return {
        "status": "healthy",
        "uptime": stats.uptime,
        "memory_usage": stats.memory_usage
    }

# Run the API
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```

## ML Service Example

### Model Training Service

```python
from claude_framework import MLService, ExperimentTracker
import mlflow

class ModelTrainingService(MLService):
    def __init__(self):
        super().__init__()
        self.setup_mlflow()
    
    @ExperimentTracker.log_experiment
    async def train_model(self, config):
        # Start MLflow run
        with mlflow.start_run():
            # Log parameters
            mlflow.log_params(config)
            
            # Train model
            model = self.create_model(config)
            history = model.train()
            
            # Log metrics
            mlflow.log_metrics({
                "accuracy": history.accuracy,
                "loss": history.loss
            })
            
            # Log model
            mlflow.sklearn.log_model(model, "model")
            
            return model
    
    def create_model(self, config):
        # Your model creation logic
        return trained_model

# Usage
service = ModelTrainingService()
model = await service.train_model({
    "learning_rate": 0.01,
    "epochs": 100,
    "batch_size": 32
})
```

## CLI Tool Example

### Data Processing CLI

```python
from claude_framework import CLITool, RichConsole
import click

class DataProcessorCLI(CLITool):
    def __init__(self):
        super().__init__()
        self.console = RichConsole()
    
    @click.command()
    @click.argument("input_file")
    @click.argument("output_file")
    @click.option("--format", default="json", help="Output format")
    def process_data(self, input_file, output_file, format):
        """Process data file with AI analysis"""
        
        self.console.print(f"Processing {input_file}...")
        
        # Process with progress bar
        with self.console.progress() as progress:
            task = progress.add_task("Processing...", total=100)
            
            # Your processing logic
            data = self.load_data(input_file)
            processed = self.process_with_ai(data, progress, task)
            self.save_data(processed, output_file, format)
        
        self.console.print(f"✅ Processed data saved to {output_file}")
    
    def process_with_ai(self, data, progress, task):
        processed_data = []
        for i, item in enumerate(data):
            # AI processing
            result = self.ai_service.process(item)
            processed_data.append(result)
            
            # Update progress
            progress.update(task, completed=i+1)
        
        return processed_data

# Create CLI app
cli = DataProcessorCLI()
cli.run()
```

## Desktop App Example

### Tkinter GUI Application

```python
from claude_framework import DesktopApp, AsyncProcessor
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class AIDesktopApp(DesktopApp):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.processor = AsyncProcessor()
    
    def setup_ui(self):
        self.root = tk.Tk()
        self.root.title("Claude MultiAgent Desktop App")
        self.root.geometry("800x600")
        
        # Create UI elements
        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()
    
    def create_main_frame(self):
        # Input frame
        input_frame = ttk.Frame(self.root)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Text input
        ttk.Label(input_frame, text="Enter text for AI analysis:").pack(anchor=tk.W)
        self.text_input = tk.Text(input_frame, height=10)
        self.text_input.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Analyze", command=self.analyze_text).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_text).pack(side=tk.LEFT, padx=5)
        
        # Results
        ttk.Label(input_frame, text="Results:").pack(anchor=tk.W, pady=(10, 0))
        self.results_text = tk.Text(input_frame, height=10, state=tk.DISABLED)
        self.results_text.pack(fill=tk.BOTH, expand=True, pady=5)
    
    async def analyze_text(self):
        text = self.text_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter text to analyze")
            return
        
        # Show processing
        self.status_label.config(text="Processing...")
        self.root.update()
        
        try:
            # AI analysis
            result = await self.processor.analyze_text(text)
            
            # Display results
            self.results_text.config(state=tk.NORMAL)
            self.results_text.delete("1.0", tk.END)
            self.results_text.insert("1.0", result)
            self.results_text.config(state=tk.DISABLED)
            
            self.status_label.config(text="Analysis complete")
        
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")
            self.status_label.config(text="Ready")
    
    def clear_text(self):
        self.text_input.delete("1.0", tk.END)
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        self.results_text.config(state=tk.DISABLED)

# Run the app
app = AIDesktopApp()
app.run()
```

## Configuration Examples

### Environment Configuration

```python
# config/development.py
DEVELOPMENT_CONFIG = {
    'debug': True,
    'log_level': 'DEBUG',
    'agents': {
        'architect': {'enabled': True, 'max_tasks': 2},
        'engineer': {'enabled': True, 'max_tasks': 3}
    },
    'monitoring': {
        'enabled': True,
        'database': 'sqlite:///dev_monitoring.db'
    }
}

# config/production.py
PRODUCTION_CONFIG = {
    'debug': False,
    'log_level': 'INFO',
    'agents': {
        'architect': {'enabled': True, 'max_tasks': 5},
        'engineer': {'enabled': True, 'max_tasks': 10}
    },
    'monitoring': {
        'enabled': True,
        'database': 'postgresql://user:pass@localhost/monitoring'
    }
}
```

### Custom Agent Example

```python
from claude_framework import BaseAgent, track_mcp_call

class DataScienceAgent(BaseAgent):
    role = "DataScientist"
    
    def __init__(self):
        super().__init__()
        self.models = self.load_models()
    
    @track_mcp_call("data_science", "analyze_dataset")
    async def analyze_dataset(self, dataset):
        # Perform statistical analysis
        stats = await self.calculate_statistics(dataset)
        
        # Generate insights
        insights = await self.generate_insights(stats)
        
        # Create visualizations
        charts = await self.create_visualizations(dataset, stats)
        
        return {
            'statistics': stats,
            'insights': insights,
            'visualizations': charts
        }
    
    async def calculate_statistics(self, dataset):
        # Your statistical analysis logic
        return statistics
    
    async def generate_insights(self, stats):
        # AI-powered insight generation
        return insights
    
    async def create_visualizations(self, dataset, stats):
        # Chart generation logic
        return charts

# Register custom agent
from claude_framework import Framework

framework = Framework()
framework.register_agent('data_scientist', DataScienceAgent)
```

These examples demonstrate the flexibility and power of the Claude MultiAgent Framework across different application types and use cases.
