# github

## .github文件妙用

- 文件在项目根目录
- workflows子目录
- ISSUE_TEMPLATE 模版文件
- PULL_REQUEST_TEMPLATE模版文件
- CONTRIBUTING.md贡献者指南
- SECURITY.md安全漏洞相关
- labeler.yml自动打标签
- dependabot.yml 新版本发布自动pull请求机器人
```yml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "sunday"
    ignore:
      - dependency-name: "*"
        update-types: ["version-update:semver-major"]
  - package-ecosystem: "gradle"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "sunday"
    open-pull-requests-limit: 50
    ignore:
      - dependency-name: "*"
        update-types: ["version-update:semver-major"]
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "sunday"
    open-pull-requests-limit: 5
    ignore:
      - dependency-name: "*"
        update-types: ["version-update:semver-major"]
```
## .baseline文件夹

## 分支管理
明明风格：
小写字母-小写字母,仅使用字母数字，连接符-，避免使用特殊符号
- 主分支
    - master/main 主分支，包含准备发布的代码
    - develeop 开发分支，包含正在开发的代码和新功能

- 功能分支
  - feature/xxx
- bugfix修复分支
  - bugfix/xxx
- 热修复分支
  - hotfix/xxxx
- release发布分支
  - chore/xxx

## Github 协作开发方式

1. 创建一个 Issue，并可以增加相关的任务。

2. 针对 Issue 开发生成一个或多个 Pull Request。如果要关联对应的 Issue，只需要在 PR 的提交信息中增加 #num 即可。例如，若将 PR #4 与 Issue #3 关联，则提交信息需增加 "fixed #3"。若需要在 PR 合并后自动关闭关联的 Issue，则可使用以下方式：
   - Comment
   - Github Actions
   - 关键字：`close`, `closes`, `closed`, `fix`, `fixes`, `fixed`, `resolve`, `resolves`

3. PR 合并后，Issue 会自动关联对应的 PR，同时一个 Issue 也可以关联多个 PR。xx

