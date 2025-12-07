# Physical AI & Humanoid Robotics Learning Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

A comprehensive **Docusaurus-based documentation and learning platform** for Physical AI and Humanoid Robotics engineering.

## 🎯 What This Project Is

This is a **static documentation site** built with Docusaurus 3 and React 18, featuring:

- ✅ **4 Complete Modules** of robotics course content
- ✅ **20+ Chapters** covering ROS 2, Gazebo, Isaac Sim, and VLA
- ✅ **Code Examples** with practical demonstrations
- ✅ **Responsive Design** (mobile, tablet, desktop)
- ✅ **Dark Mode Support** for comfortable reading
- ✅ **Full-Text Search** across all documentation
- ✅ **Easy Navigation** with sidebar and categories
- ✅ **Modern UI** built with React and TypeScript

## ⚡ Quick Start

### Prerequisites
- Node.js 18+
- npm or yarn

### Local Development

```bash
# Clone the repository
git clone https://github.com/abdulmateen5251/Physical_AI_Humanoid_Robotics_book.git
cd Physical_AI_Humanoid_Robotics_book

# Install frontend dependencies
cd frontend
npm install

# Start development server
npm start

# Site opens at http://localhost:3001
```

### Build for Production

```bash
cd frontend
npm run build

# Output: frontend/build/ (ready to deploy)
```

## 📚 Course Modules

### Module 1: ROS 2 Fundamentals ✅
- Introduction to ROS 2 and installation
- Nodes, Topics, and Services in rclpy
- Code examples and exercises

### Module 2: Digital Twin & Simulation ✅
- Gazebo simulator setup
- URDF & SDF file formats
- Sensor simulation
- ROS 2 integration with Gazebo
- Practical labs

### Module 3: NVIDIA Isaac Sim ✅
- Isaac ecosystem overview
- Synthetic data generation
- Isaac + ROS 2 integration
- Nav2 path planning
- Simulation-to-real transfer

### Module 4: Vision-Language-Action (VLA) ✅
- Whisper speech integration
- LLM planning & reasoning
- Safety validation
- VLA model training
- Vision-language applications

## 🏗️ Project Structure

```
Physical_AI_Humanoid_Robotics/
├── frontend/                    # Docusaurus documentation site
│   ├── docs/                    # Course content (modules 1-4)
│   ├── src/                     # React components & styling
│   ├── static/                  # Images, logos, assets
│   ├── package.json             # Node.js dependencies
│   └── docusaurus.config.js     # Site configuration
│
├── backend/                     # FastAPI backend (optional, for future APIs)
│   ├── app/                     # Application code
│   ├── tests/                   # Test suites
│   ├── requirements.txt         # Python dependencies
│   └── alembic/                 # Database migrations
│
└── specs/                       # Original specifications & planning
```

## 🚀 Deployment

### Deploy to Vercel (Recommended)
```bash
# Push to GitHub
git push origin main

# Connect repository in Vercel dashboard
# Vercel automatically deploys on every push
```

### Deploy to Netlify
```bash
cd frontend
npm run build
# Upload frontend/build/ to Netlify
```

### Deploy to GitHub Pages
```bash
cd frontend
npm run build
npm run deploy
```

## 📖 Documentation

See the [PROJECT_REPORT.md](PROJECT_REPORT.md) for comprehensive project details including:
- Complete architecture overview
- Technology stack used
- Development status
- Testing information
- Configuration guidelines

For setup and development instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md).

## 🔧 Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Frontend | Docusaurus | 3.9.2 |
| UI Framework | React | 18.x |
| Language | TypeScript | Latest |
| Styling | CSS Modules | Latest |
| Build Tool | Webpack | 5.x |
| Package Manager | npm | 10+ |
| Backend | FastAPI | 0.104.1 |
| Python | 3.11+ | - |
| Version Control | Git | Latest |

## 💡 What This Project Does NOT Have

- ❌ **No RAG Chatbot** - This is a static documentation site, not an AI-powered Q&A system
- ❌ **No User Accounts** - No authentication or user profiles
- ❌ **No Real-time Features** - Static content delivery only
- ❌ **No Database Requirements** - Fully static frontend
- ❌ **No API Integration** - Standalone documentation site

## 🧪 Development

### Running Tests
```bash
# Frontend build test
cd frontend
npm run build

# Check for broken links
npm run docusaurus build-prod
```

### Code Quality
```bash
# Format code
npm run format

# Lint check
npm run lint
```

## 🤝 Contributing

We welcome contributions! To contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Make your changes
4. Commit with clear messages: `git commit -m "feat: add new chapter"`
5. Push to your branch: `git push origin feat/your-feature`
6. Open a Pull Request

### Content Guidelines
- Write in clear, technical English
- Include code examples where applicable
- Add exercises at end of chapters
- Keep line length ~100 characters
- Use proper Markdown formatting

## 📄 License

**Code**: MIT License - see [LICENSE](LICENSE)  
**Content**: CC BY-SA 4.0 - Educational content is shareable with attribution

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/abdulmateen5251/Physical_AI_Humanoid_Robotics_book/issues)
- **Discussions**: [GitHub Discussions](https://github.com/abdulmateen5251/Physical_AI_Humanoid_Robotics_book/discussions)
- **Email**: abdulmateen5251@gmail.com

## 📈 Project Status

**Status**: ✅ **Production Ready**

- Frontend: Fully functional and deployed-ready
- Content: 20+ chapters across 4 modules
- Documentation: Complete
- Testing: Build validation passing
- Version: 1.0.0

## 🎓 Learning Path

1. **Start here**: Read Module 1 - Introduction
2. **Foundation**: Complete ROS 2 Fundamentals (Module 1)
3. **Simulation**: Learn Gazebo and digital twins (Module 2)
4. **Advanced**: Explore Isaac Sim and synthetic data (Module 3)
5. **Integration**: Master Vision-Language-Action systems (Module 4)

Each module has:
- Conceptual explanations
- Code examples you can run
- Practical exercises
- Links to further resources

## 🔄 Latest Updates (December 7, 2025)

- ✅ Removed Docker configuration (not needed for static site)
- ✅ Removed Chainlit RAG chatbot (out of scope)
- ✅ Updated documentation to reflect actual project
- ✅ Cleaned up unused dependencies
- ✅ Created comprehensive PROJECT_REPORT.md
- ✅ Project ready for deployment

---

**Last Updated**: December 7, 2025  
**Maintainer**: Abdul Mateen  
**Repository**: https://github.com/abdulmateen5251/Physical_AI_Humanoid_Robotics_book

