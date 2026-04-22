# 个人技术笔记

> 基于 Sphinx 的个人技术知识库，支持 Markdown 和 reStructuredText 格式

[![Documentation Status](https://readthedocs.org/projects/mynoteissues/badge/?version=latest)](https://mynoteissues.readthedocs.io/en/latest/?badge=latest)

## 简介

这是我的个人技术笔记项目，记录了在编程、技术栈、前端、DevOps、架构、算法、读书和业务等方面的学习笔记和经验总结。

## 在线阅读

📖 [在线文档](https://mynoteissues.readthedocs.io/)

## 本地构建

### 环境要求

- Python 3.8+
- pip

### 快速开始

```bash
# 克隆项目
git clone https://github.com/waveletbob/mynoteIssues.git
cd mynoteIssues

# 安装依赖
pip install -r requirements.txt

# 构建文档
make html

# 启动本地预览
python -m http.server -d build/html
```

访问 http://localhost:8000 查看文档

### 实时预览

```bash
sphinx-autobuild source build
```

## 目录结构

```
├── 编程/          # 编程语言和规范
├── 技术栈/        # 技术框架和工具
├── 前端/          # 前端开发技术
├── devops/       # DevOps和运维
├── 架构/          # 系统架构设计
├── 算法/          # 算法和人工智能
├── 读书/          # 读书笔记
└── 业务/          # 业务知识
```

## 技术栈

- **文档生成**: Sphinx 7.0+
- **Markdown支持**: MyST Parser
- **HTML主题**: ReadTheDocs Theme
- **代码高亮**: Pygments
- **自动构建**: ReadTheDocs

## 主要特性

- ✅ 支持 Markdown 和 reStructuredText 格式
- ✅ 响应式设计，支持移动端阅读
- ✅ 内置搜索功能
- ✅ 代码块复制按钮
- ✅ 数学公式支持
- ✅ 自动在 ReadTheDocs 构建
- ✅ 支持多版本管理

## 最近更新

### 2024年优化
- 升级到 Sphinx 7.0 和 MyST Parser
- 统一图片资源管理
- 优化目录结构和导航
- 添加现代化文档组件

详细更新内容请查看 [OPTIMIZATION.md](OPTIMIZATION.md)

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

Copyright © 2023 waveletbob
