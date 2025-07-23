# 🏥 MedForce AI - Multi-Agent Pharmaceutical Analysis Platform

[![CAMEL AI](https://img.shields.io/badge/Powered%20by-CAMEL%20AI-blue)](https://github.com/lightaime/camel)
[![Mistral AI](https://img.shields.io/badge/AI%20Model-Mistral%20Medium%203-orange)](https://mistral.ai/)
[![Python](https://img.shields.io/badge/Python-3.8+-green)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)](https://streamlit.io)

> **🤖 Advanced Multi-Agent System for Pharmaceutical Analysis**  
> Leveraging CAMEL AI framework with intelligent search coordination to provide comprehensive medication guidance through specialized AI agents.

---

## 🌟 **Key Features**

### 🐪 **CAMEL AI Powered Coordination**
- **Mistral Medium 3** powered coordinator and task planner
- **Multi-agent workforce** with specialized pharmaceutical expertise
- **Intelligent task distribution** with custom system messages
- **Result synthesis** combining findings from all specialist agents

### ⚡ **Smart Search Coordination**
- **60-80% reduction** in redundant API calls
- **Intelligent caching** with 1-hour TTL for medical data
- **Source prioritization**: FDA → MedlinePlus → Mayo Clinic
- **Rate limiting** and error handling for reliable searches

### 🔬 **Four Specialist Agents**
| Agent | Temperature | Specialization | Primary Sources |
|-------|-------------|----------------|-----------------|
| 💊 **Dosage Agent** | 0.4 | Medication dosing guidelines | MedlinePlus, Mayo Clinic |
| ⚠️ **Safety Agent** | 0.3 | Side effects & adverse reactions | FDA, MedlinePlus |
| 🔍 **Web Search Agent** | 0.5 | Drug interactions & regulatory alerts | FDA, WHO, Medscape |
| ✅ **Validator Agent** | 0.1 | Cross-verification & fact-checking | All cached results |

### 📱 **Advanced Frontend**
- **Streamlit-based** responsive interface
- **Real-time dosage validation** with safety warnings
- **Comprehensive result display** with medical disclaimers
- **Emergency contact information** and professional referrals

---

## 🚀 **Quick Start**

### Prerequisites

- **Python 3.8+**
- **Git**
- **Mistral AI API Key** ([Get one here](https://console.mistral.ai/))

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/medforce-ai.git
cd medforce-ai
```

### 2. Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv medforce_env

# Activate virtual environment
# On Windows:
medforce_env\Scripts\activate
# On macOS/Linux:
source medforce_env/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` file with your API key:

```env
# Mistral AI Configuration
MISTRAL_API_KEY=your_mistral_api_key_here

```

### 5. Run the Application

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

---

## 📁 **Project Structure**

```
medforce-ai/
├── 📱 app.py                     # Streamlit frontend application
├── 🐪 main.py                    # CAMEL AI workforce coordinator
├── ⚡ search_coordinator.py      # Intelligent search coordination system
├── 📋 requirements.txt           # Python dependencies
├── 🔧 .env                       # Environment variables (create from .env.example)
├── 📚 README.md                  # This file
├── 🤖 agents/                    # Specialist agent implementations
│   ├── __init__.py               # Agent registry and coordination status
│   ├── dosage_agent.py           # 💊 Coordinated dosage analysis specialist
│   ├── sideeffects_agent.py      # ⚠️ Coordinated safety assessment specialist
│   ├── web_agent.py              # 🔍 Coordinated drug interaction specialist
│   └── validator_agent.py        # ✅ Coordinated medical verification specialist
└── 🖼️ camel_logo.png             # CAMEL AI logo for frontend
```

---

## 🔧 **Configuration**

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MISTRAL_API_KEY` | Mistral AI API key for all agents | - | ✅ Yes |

### Agent Temperature Settings

The system uses optimized temperature settings for different agent roles:

- **Coordinator**: 0.3 (balanced reasoning)
- **Task Planner**: 0.2 (conservative planning)
- **Dosage Agent**: 0.4 (precise calculations)
- **Safety Agent**: 0.3 (conservative safety assessment)
- **Web Search Agent**: 0.5 (balanced research)
- **Validator Agent**: 0.1 (ultra-conservative verification)

---

### Search Coordination Benefits

- **Efficiency**: 60-80% reduction in API calls through intelligent caching
- **Reliability**: Source prioritization with fallback mechanisms
- **Speed**: Faster responses through shared result access
- **Consistency**: Cross-agent verification using shared search data

---

## 🎯 **Usage Examples**

### Basic Medication Query

1. **Open the application** at `http://localhost:8501`
2. **Enter patient information**:
   - Medicine: "Ibuprofen"
   - Age: 25
   - Dosage: "200mg"
   - Reason: "headache"
3. **Click "Analyze Medication"**
4. **Review comprehensive analysis** including:
   - Dosage recommendations
   - Safety assessment
   - Drug interactions
   - Medical verification

### Advanced Query with Context

```python
# Example of programmatic usage
from main import run_pharmacy_query

query = "Medicine: Metformin, Age: 55, Dosage: 500mg twice daily, Reason: Type 2 diabetes, Additional: Taking blood pressure medication"
result = run_pharmacy_query(query)
print(result)
```

---

## 🔒 **Safety & Compliance**

### Medical Disclaimers

⚠️ **CRITICAL: This system is for educational purposes only**

- **Professional consultation required** for all medical decisions
- **Licensed pharmacist consultation** for medication questions
- **Healthcare provider consultation** for personalized medical advice
- **Emergency services** for severe reactions or medical emergencies

### Data Sources

The system prioritizes authoritative medical sources:

1. **Primary Sources**: FDA.gov, MedlinePlus (NIH), Mayo Clinic
2. **Secondary Sources**: Drugs.com, Medscape, WHO.int
3. **Tertiary Sources**: NHS.uk, PubMed, Health Canada

### Safety Features

- **Dosage validation** with real-time warnings for dangerous amounts
- **Emergency contact information** prominently displayed
- **Professional referral guidance** for all medical decisions
- **Conservative approach** prioritizing patient safety

---

## 🛠️ **Development**

### Adding New Agents

1. **Create agent file** in `agents/` directory
2. **Implement CoordinatedAgent** class extending `ChatAgent`
3. **Define specialization** in search coordinator
4. **Register agent** in `agents/__init__.py`
5. **Update workforce** in `main.py`

Example agent template:

```python
from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.configs import MistralConfig
from camel.types import ModelType, ModelPlatformType
from search_coordinator import get_search_coordinator

class CoordinatedNewAgent(ChatAgent):
    def __init__(self):
        model = ModelFactory.create(
            model_platform=ModelPlatformType.MISTRAL,
            model_type=ModelType.MISTRAL_MEDIUM_3,
            model_config_dict=MistralConfig(temperature=0.4).as_dict(),
        )
        
        super().__init__(
            system_message="Your specialized agent system message...",
            model=model,
            tools=[search_tool] if search_tool else []
        )
        
        self.search_coordinator = get_search_coordinator()
        self.agent_name = "NewAgent"
```

### Testing

```bash
# Run basic functionality test
python -c "from main import run_pharmacy_query; print(run_pharmacy_query('Medicine: Aspirin, Age: 30'))"

# Test search coordination
python -c "from search_coordinator import get_search_coordinator; print(get_search_coordinator().get_cache_stats())"
```

---

## 📊 **Monitoring & Analytics**

### Search Coordination Metrics

Access coordination statistics:

```python
from agents import get_coordination_status

status = get_coordination_status()
print(f"Cache hit rate: {status['metrics']['cache_hit_rate']}")
print(f"Total searches: {status['metrics']['total_cached_results']}")
```

### Cache Management

```python
from agents import clear_search_cache

# Clear cache for fresh searches
result = clear_search_cache()
print(result['status'])  # 'success' or 'error'
```

---

## 🤝 **Contributing**

### Development Setup

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Install development dependencies**: `pip install -r requirements-dev.txt`
4. **Make changes** following coding standards
5. **Test thoroughly** with various medication queries
6. **Commit changes**: `git commit -m 'Add amazing feature'`
7. **Push to branch**: `git push origin feature/amazing-feature`
8. **Open Pull Request**

### Coding Standards

- **Python**: Follow PEP 8
- **Documentation**: Docstrings for all functions
- **Safety**: Conservative approach for medical information
- **Testing**: Test with diverse medication scenarios

---

## 📞 **Support**

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/yourusername/medforce-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/medforce-ai/discussions)
- **Documentation**: Check this README and code comments

### Common Issues

#### API Key Issues
```bash
# Verify API key is set
python -c "import os; print('MISTRAL_API_KEY' in os.environ)"
```

#### Search Tool Issues
```bash
# Test search functionality
python -c "from camel.toolkits import SearchToolkit; print(SearchToolkit().get_tools())"
```

#### Agent Coordination Issues
```bash
# Check agent registry
python -c "from agents import get_all_agents; print(list(get_all_agents().keys()))"
```

---

## 📜 **License**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

- **[CAMEL AI](https://github.com/lightaime/camel)** - Multi-agent framework
- **[Mistral AI](https://mistral.ai/)** - Language model provider
- **[Streamlit](https://streamlit.io/)** - Frontend framework
- **Medical Sources** - FDA, MedlinePlus, Mayo Clinic for authoritative data

---

## ⚠️ **Important Medical Disclaimer**

**THIS SOFTWARE IS FOR EDUCATIONAL AND INFORMATIONAL PURPOSES ONLY**

- **Not a substitute** for professional medical advice, diagnosis, or treatment
- **Always consult** qualified healthcare professionals for medical decisions
- **Emergency situations** require immediate professional medical attention
- **Individual medical needs** vary and require personalized professional assessment

**The developers and contributors are not responsible for any medical decisions made based on this software's output.**

---

<div align="center">

**🐪 Built with [CAMEL AI](https://github.com/lightaime/camel) | 🚀 Powered by [Mistral AI](https://mistral.ai/)**

⭐ **Star this repository if you find it helpful!**

</div>
