# 贡献指南

感谢你对本项目的关注！我们欢迎任何形式的贡献，包括但不限于提交 Bug 报告、功能建议、文档改进和代码贡献。

## 如何贡献

### 报告 Bug

如果你发现了 Bug，请通过 [Issue](../../issues/new?template=bug_report.md) 提交，并尽量提供以下信息：

- 问题描述
- 复现步骤
- 期望行为与实际行为
- 运行环境（Python 版本、操作系统等）

### 功能建议

如果你有功能改进的想法，请通过 [Issue](../../issues/new?template=feature_request.md) 提交，并描述：

- 你的使用场景
- 期望的功能表现
- 可能的实现思路（可选）

### 代码贡献

1. **Fork** 本仓库
2. 创建你的功能分支：

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. 安装开发依赖：

   ```bash
   pip install -r requirements.txt
   ```

4. 进行修改并确保代码可以正常运行
5. 提交你的更改：

   ```bash
   git commit -m "feat: 简述你的更改"
   ```

6. 推送到你的 Fork：

   ```bash
   git push origin feature/your-feature-name
   ```

7. 创建 **Pull Request**

## 提交规范

建议使用以下提交信息格式：

| 类型 | 说明 |
|------|------|
| `feat` | 新功能 |
| `fix` | 修复 Bug |
| `docs` | 文档更新 |
| `refactor` | 代码重构（不影响功能） |
| `test` | 添加或更新测试 |
| `chore` | 构建或辅助工具变更 |

示例：

```
feat: 支持自定义工作时间范围
fix: 修复跨时区日期计算错误
docs: 更新 README 安装步骤
```

## 代码风格

- 遵循 [PEP 8](https://peps.python.org/pep-0008/) 代码规范
- 使用有意义的变量名和函数名
- 为公共函数添加文档字符串
- 保持代码简洁、可读

## 行为准则

参与本项目即表示你同意遵守我们的 [行为准则](CODE_OF_CONDUCT.md)。

## 疑问？

如果你在贡献过程中遇到任何问题，欢迎在 [Issue](../../issues) 中提问。
