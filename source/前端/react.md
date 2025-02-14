# React

## CRA

```bash
npx create-react-app my-react-app
cd my-react-app
npm start
```
```
my-react-app/
├─ public/                 # 静态资源
├─ src/
│  ├─ assets/             # 图片/字体等资源
│  ├─ components/         # 通用组件
│  ├─ features/           # 业务模块（推荐 feature-based 结构）
│  │  ├─ auth/            # 认证模块
│  │  ├─ dashboard/       # 仪表盘模块
│  ├─ hooks/              # 自定义 Hooks
│  ├─ layouts/            # 页面布局
│  ├─ pages/              # 路由级页面组件
│  ├─ store/              # 全局状态管理
│  ├─ styles/             # 全局样式
│  ├─ utils/              # 工具函数
│  └─ main.jsx            # 应用入口
   └─ index.js            # 应用入口
   └─ App.js              # 应用组件
├─ .env                   # 环境变量
├─ package.json           # 依赖
└─ Dockerfile             # 容器化部署

```
## Vite

## 功能

- 路由：react-router-dom
- 状态管理：useState + Context API/Redux Toolkit / Zustand / MobX
- API 交互
- 样式方案Storybook
- 构建配置
    - Webpack 自定义配置（通过 react-app-rewired）
    - 环境变量管理（.env.development, .env.production）
    - 代码分割（React.lazy + Suspense）
- 代码质量
  - ESLint + Prettier 代码规范
  - Husky + lint-staged 提交前检查
  - TypeScript 类型系统（强烈推荐）
## 开源框架
- Electron
- Tauri
- Flutter
