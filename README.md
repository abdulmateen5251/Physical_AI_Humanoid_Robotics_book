# Physical AI & Humanoid Robotics Learning Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()
[![Built with Docusaurus](https://img.shields.io/badge/Built%20with-Docusaurus-white.svg)](https://docusaurus.io/)

A **free, open-source documentation and learning platform** for Physical AI and Humanoid Robotics engineering built with Docusaurus.

## 📚 What This Is

A static documentation site with **20+ chapters** covering 4 robotics modules:

```
✅ Module 1: ROS 2 Fundamentals
✅ Module 2: Digital Twin & Gazebo Simulation  
✅ Module 3: NVIDIA Isaac Sim
✅ Module 4: Vision-Language-Action (VLA) Systems
```

**No database, no backend, no API** - just fast, modern documentation.

## 🚀 Quick Start

```bash
# 1. Clone repository
git clone https://github.com/abdulmateen5251/Physical_AI_Humanoid_Robotics_book.git
cd Physical_AI_Humanoid_Robotics_book

# 2. Install dependencies
cd frontend
npm install

# 3. Run locally
npm start

# 4. Open browser to http://localhost:3001
```

## 🛠️ Tech Stack

- **Docusaurus 3** - Static site generator
- **React 18** - UI components
- **Markdown** - Content format
- **Node.js** - Runtime

## 📖 Features

- ✅ **Full-text search** across all content
- ✅ **Dark mode** support
- ✅ **Responsive design** (mobile-friendly)
- ✅ **Fast performance** (static HTML)
- ✅ **Easy to contribute** (Markdown-based)
- ✅ **Version control** (Git-friendly)

## 📁 Project Structure

```
Physical_AI_Humanoid_Robotics_book/
├── frontend/                    # Docusaurus site
│   ├── docs/                    # Course content
│   │   ├── index.md             # Home page
│   │   ├── module-01-ros2/      # Module 1
│   │   ├── module-02-gazebo/    # Module 2
│   │   ├── module-03-isaac/     # Module 3
│   │   └── module-04-vla/       # Module 4
│   ├── src/                     # React components
│   ├── package.json             # Dependencies
│   └── docusaurus.config.js     # Configuration
│
└── specs/                       # Original specifications
```

## 🌐 Deploy

### Vercel (Recommended - Free)
```bash
# Push to GitHub, connect to Vercel
# Auto-deploys on every push
```

### Netlify
```bash
cd frontend && npm run build
# Upload frontend/build/ to Netlify
```

### GitHub Pages
```bash
cd frontend && npm run deploy
```

## 📝 Edit Content

Edit markdown files in `frontend/docs/`:

```bash
# Example: Add new chapter
frontend/docs/module-01-ros2/03-new-chapter.md

# Update sidebar in frontend/sidebars.js

# Changes appear instantly with npm start
```

## 🤝 Contribute

1. Fork repository
2. Create branch: `git checkout -b feat/new-content`
3. Add content to `frontend/docs/`
4. Test: `npm run build`
5. Push: `git push origin feat/new-content`
6. Open Pull Request

## 📄 License

- **Code**: MIT License
- **Content**: CC BY-SA 4.0 (educational content, shareable with attribution)

## 🔗 Links

- **GitHub**: https://github.com/abdulmateen5251/Physical_AI_Humanoid_Robotics_book
- **Docusaurus Docs**: https://docusaurus.io/
- **Edit this page**: See "Edit this page" link on every page

## ⚡ Commands

```bash
cd frontend

npm start         # Dev server (http://localhost:3001)
npm run build     # Production build
npm run serve     # Serve production build
npm run clean     # Clear build cache
```

## 🎯 Next Steps

1. **Read**: Explore the course modules
2. **Contribute**: Add more chapters or fix issues
3. **Share**: Deploy and share with others
4. **Learn**: Use as learning resource

---

**Status**: ✅ **Production Ready**  
**Last Updated**: December 7, 2025  
**Maintainer**: Abdul Mateen (@abdulmateen5251)


